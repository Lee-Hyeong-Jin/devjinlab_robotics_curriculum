"""The runnable code examples of a lesson.

A lesson's Python examples are fenced ```` ```python ```` blocks in its Markdown body. A reader
had to copy each one by hand to run it, and nothing checked that they still run. This module
pulls them out (``rc example``) and says which can run on their own — the ones that import
nothing beyond the standard library and the small numeric stack the course asks for — so they
can be executed as tests.

Pure functions: no I/O, no subprocess. Running an example is ``content.example_runner``.
"""

from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass

RUNNABLE_PACKAGES = frozenset({"numpy", "scipy"})
"""Third-party packages an example may import and still be run by ``rc example --run`` and
the test suite. Everything else (ROS 2 client libraries, simulators, deep-learning frameworks)
needs an environment this project does not provide: those examples are shown, not run."""

_FENCE = re.compile(
    r"^(?P<indent>[ \t]{0,3})(?P<ticks>`{3,}|~{3,})[ \t]*(?P<info>[^\n`]*)\n"
    r"(?P<code>.*?)"
    r"^(?P=indent)(?P=ticks)[ \t]*$",
    re.DOTALL | re.MULTILINE,
)
_PYTHON = frozenset({"python", "py", "python3"})


@dataclass(frozen=True, slots=True)
class Example:
    """One Python example of a lesson."""

    index: int
    """1-based position among the lesson's Python examples."""
    code: str
    imports: tuple[str, ...]
    """Top-level packages the code imports, sorted (``("heapq", "numpy")``)."""
    syntax_error: str | None = None
    """Why the code does not parse, if it does not."""

    @property
    def missing(self) -> tuple[str, ...]:
        """Imported packages that are neither standard library nor in the runnable set."""
        return tuple(
            name
            for name in self.imports
            if name not in sys.stdlib_module_names and name not in RUNNABLE_PACKAGES
        )

    @property
    def runnable(self) -> bool:
        """Whether the example can run with Python and :data:`RUNNABLE_PACKAGES` alone."""
        return self.syntax_error is None and not self.missing


def _imports(tree: ast.AST) -> tuple[str, ...]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".", 1)[0])
    return tuple(sorted(names))


def extract_examples(body: str) -> list[Example]:
    """Every ```` ```python ```` block of a lesson body, in order.

    Args:
        body: The lesson's Markdown, without front matter.

    Returns:
        The examples with their imports. A block that does not parse is returned with
        ``syntax_error`` set and no imports, never dropped: a broken example is a finding.
    """
    examples: list[Example] = []
    for match in _FENCE.finditer(body):
        info = match["info"].strip().split()
        if not info or info[0].lower() not in _PYTHON:
            continue
        indent = match["indent"]
        lines = match["code"].splitlines()
        code = "\n".join(
            line[len(indent) :] if line.startswith(indent) else line for line in lines
        ).rstrip()
        code += "\n"
        try:
            tree = ast.parse(code)
        except SyntaxError as exc:
            examples.append(Example(len(examples) + 1, code, (), f"line {exc.lineno}: {exc.msg}"))
            continue
        examples.append(Example(len(examples) + 1, code, _imports(tree)))
    return examples


def as_script(lesson_id: str, examples: list[Example], *, title: str | None = None) -> str:
    """The examples of one lesson as a single ``.py`` file, each under a comment header.

    Examples are separated, not merged: later ones may redefine names, and a reader should be
    able to see where each begins. The file runs top to bottom.
    """
    head = [f"# Examples from the lesson {lesson_id}" + (f": {title}" if title else "")]
    needs = sorted({name for example in examples for name in example.imports} & RUNNABLE_PACKAGES)
    if needs:
        head.append(f"# Needs: pip install {' '.join(needs)}")
    parts = ["\n".join(head) + "\n"]
    for example in examples:
        note = (
            "" if example.runnable else f"  (not runnable here: needs {', '.join(example.missing)})"
        )
        parts.append(f"# --- example {example.index}{note} ---\n{example.code}")
    return "\n\n".join(parts)
