"""Lesson code examples: extraction, ``rc example``, and that every example really runs (#49).

A third-party tutorial rots quietly: an example breaks and nobody is told. Here every Python
example of every lesson, in both languages, is executed, so a broken one fails the gate.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from robotics_curriculum.cli import app as cli_app
from robotics_curriculum.content.example_runner import run_example
from robotics_curriculum.content.examples import (
    RUNNABLE_PACKAGES,
    Example,
    as_script,
    extract_examples,
)
from robotics_curriculum.progress import ProgressService

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / "curriculum"
LANGS = ("ko", "en")

BODY = """\
Intro.

```python
import numpy as np
from heapq import heappush

print(np.eye(2).trace())
```

```bash
rc example m1
```

   ```py
   import rclpy
   from geometry_msgs.msg import Twist
   ```

~~~python title="broken"
def f(:
~~~

```text
import os
```
"""


def test_only_python_blocks_are_examples_and_they_keep_their_order() -> None:
    examples = extract_examples(BODY)
    assert [e.index for e in examples] == [1, 2, 3]
    first, ros, broken = examples
    assert first.code.startswith("import numpy as np\n") and first.code.endswith("trace())\n")
    assert first.imports == ("heapq", "numpy")
    assert first.runnable and first.missing == ()
    # An indented fence loses its indentation; a ROS example is shown but cannot run here.
    assert ros.code == "import rclpy\nfrom geometry_msgs.msg import Twist\n"
    assert ros.missing == ("geometry_msgs", "rclpy") and not ros.runnable
    # A block that does not parse is reported, never silently dropped.
    assert broken.syntax_error is not None and "line 1" in broken.syntax_error
    assert not broken.runnable
    assert extract_examples("no code here") == []


def test_the_runnable_set_is_small_and_named() -> None:
    assert RUNNABLE_PACKAGES == {"numpy", "scipy"}
    assert Example(1, "import torch\n", ("torch",)).missing == ("torch",)
    assert Example(1, "import math\n", ("math",)).runnable


def test_as_script_is_one_file_with_a_header_per_example() -> None:
    script = as_script("m1-x", extract_examples(BODY), title="Vectors")
    assert script.startswith(
        "# Examples from the lesson m1-x: Vectors\n# Needs: pip install numpy\n"
    )
    assert "# --- example 1 ---\nimport numpy as np" in script
    assert "# --- example 2  (not runnable here: needs geometry_msgs, rclpy) ---" in script


def test_run_example_reports_output_failure_and_isolation(tmp_path: Path) -> None:
    ok = run_example("print(6 * 7)\n")
    assert (ok.returncode, ok.stdout) == (0, "42\n")
    bad = run_example("raise ValueError('nope')\n")
    assert bad.returncode != 0 and "ValueError: nope" in bad.stderr
    slow = run_example("import time\ntime.sleep(5)\n", timeout=0.5)
    assert slow.returncode == 124 and "timed out" in slow.stderr
    # It runs in an empty directory of its own, not where the caller is.
    where = run_example("import os\nprint(os.listdir('.'))\n")
    assert where.stdout.strip() == "['example.py']"


def _cli(*args: str) -> tuple[int, str]:
    base = ["--curriculum", str(CURRICULUM), "--lang", "en"]
    result = CliRunner().invoke(cli_app, [*base, "example", *args])
    return result.exit_code, result.output


def test_rc_example_prints_saves_and_runs(tmp_path: Path) -> None:
    code, printed = _cli("m1-vectors-matrices")
    assert code == 0 and "import numpy as np" in printed
    assert printed.startswith("# Examples from the lesson m1-vectors-matrices")

    target = tmp_path / "vectors.py"
    code, said = _cli("m1-vectors-matrices", "--out", str(target))
    assert code == 0 and "saved 1 example(s)" in said
    assert run_example(target.read_text("utf-8")).returncode == 0

    code, ran = _cli("m1-vectors-matrices", "--run")
    assert code == 0 and "running example 1/1" in ran

    code, missing = _cli("no-such-lesson")
    assert code == 1


def _all_examples() -> list[tuple[str, str, Example]]:
    found: list[tuple[str, str, Example]] = []
    for course in ProgressService.load_curriculum(CURRICULUM):
        for module in course.modules:
            for lesson in module.lessons:
                for lang in LANGS:
                    for example in extract_examples(lesson.localized(lang).body):
                        found.append((lesson.id, lang, example))
    return found


ALL_EXAMPLES = _all_examples()


def test_every_lesson_has_the_same_examples_in_both_languages() -> None:
    """A translation changes prose, not code: the two versions must not drift apart."""
    by_lesson: dict[str, dict[str, list[str]]] = {}
    for lesson_id, lang, example in ALL_EXAMPLES:
        by_lesson.setdefault(lesson_id, {}).setdefault(lang, []).append(example.imports.__repr__())
    for lesson_id, versions in by_lesson.items():
        assert versions.get("ko") == versions.get("en"), lesson_id
    assert len(ALL_EXAMPLES) >= 150


@pytest.mark.parametrize(
    ("lesson_id", "lang", "example"),
    ALL_EXAMPLES,
    ids=[f"{lesson_id}[{lang}]#{example.index}" for lesson_id, lang, example in ALL_EXAMPLES],
)
def test_every_lesson_example_runs(lesson_id: str, lang: str, example: Example) -> None:
    assert example.syntax_error is None, example.syntax_error
    if not example.runnable:
        pytest.skip(f"needs {', '.join(example.missing)} (shown to the reader, not run here)")
    outcome = run_example(example.code)
    assert outcome.returncode == 0, outcome.stderr[-2000:]
