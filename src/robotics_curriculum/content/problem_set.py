"""Problem-set blocks inside a lesson body (research track, lesson-standard.md §11-3).

A lesson defines problems to work through as one or more fenced ```` ```problemset ````
blocks. Each block is a YAML mapping::

    ```problemset
    activity: m-oc-ilqr-exercise      # the `kind: exercise` activity it belongs to
                                      # (optional when the lesson has exactly one)
    problems:
      - id: p1
        type: derivation              # derivation | proof | numerical | implementation |
                                      # counterexample | paper
        stars: 2                      # 1 (routine) | 2 | 3 (research-level)
        prompt: "..."
        refers_to: ["R2"]             # "핵심 결과" numbers the problem builds on
        solution_policy: sketch       # sketch | full | rubric | answer
        solution: "..."               # what `solution_policy` promises
        tolerance: 1.0e-6             # `numerical` only: how close counts as right
    ```

This is deliberately **not** a quiz. A quiz question is graded automatically and feeds the
SM-2 scheduler; a derivation or a proof cannot be, and putting one in a ```` ```quiz ````
block would both break grading and pollute the flashcard deck (lesson-standard.md §10). So
nothing here is graded, nothing becomes a card, and the structure is all that is validated —
the solution is prose for the reader.

:func:`parse_problem_sets` is the single entry point for the validator, the CLI and the site.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from robotics_curriculum.content.models import ID_PATTERN, ActivityKind, Lesson

PROBLEMSET_FENCE = re.compile(r"^(?P<fence>`{3,}|~{3,})\s*problemset\s*$")

ProblemType = Literal[
    "derivation", "proof", "numerical", "implementation", "counterexample", "paper"
]
#: How much of the solution the lesson publishes. ``rubric`` grades one's own attempt.
SolutionPolicy = Literal["sketch", "full", "rubric", "answer"]

#: A lesson's problem set should be substantial but finishable, and should mix kinds of work
#: (lesson-standard.md §11-3). Outside these bounds `rc validate` warns — it is editorial
#: advice, not a broken file.
MIN_PROBLEMS = 4
MAX_PROBLEMS = 8
MIN_TYPES = 3


class ProblemSetParseError(Exception):
    """A problem-set block could not be parsed; ``messages`` lists every problem found."""

    def __init__(self, messages: list[str]) -> None:
        self.messages = messages
        super().__init__("\n".join(messages))


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Problem(_Model):
    """One problem. Never graded, so there is no ``answer`` — only a published solution."""

    id: Annotated[str, Field(pattern=ID_PATTERN)]
    type: ProblemType
    stars: int = Field(ge=1, le=3, description="1 routine, 2 substantial, 3 research-level.")
    prompt: str = Field(min_length=1)
    refers_to: list[str] = Field(
        default_factory=list, description='"핵심 결과" numbers this problem builds on, e.g. R2.'
    )
    solution_policy: SolutionPolicy
    solution: str | None = Field(
        default=None, description="Matches `solution_policy`; absent means none is published."
    )
    tolerance: float | None = Field(
        default=None, gt=0, description="`numerical` only: how close an answer counts as right."
    )

    @model_validator(mode="after")
    def _numerical_needs_an_answer(self) -> Problem:
        if self.type == "numerical":
            missing = [
                name
                for name, value in (("solution", self.solution), ("tolerance", self.tolerance))
                if value is None
            ]
            if missing:
                # Without both, a reader cannot tell whether their number is right, which is
                # the only thing a numerical problem is for.
                raise ValueError(
                    f"a 'numerical' problem needs {' and '.join(missing)} "
                    f"(the expected value and how close counts)"
                )
        if self.tolerance is not None and self.type != "numerical":
            raise ValueError(
                f"'tolerance' only applies to a 'numerical' problem, not '{self.type}'"
            )
        return self


class ProblemSetBlock(_Model):
    """One ```` ```problemset ```` block: its activity reference and problems."""

    activity: Annotated[str, Field(pattern=ID_PATTERN)] | None = None
    problems: list[Problem] = Field(min_length=1)


@dataclass(frozen=True, slots=True)
class LessonProblemSets:
    """Every problem of a lesson, in order, grouped by block."""

    lesson_id: str
    blocks: list[ProblemSetBlock] = field(default_factory=list)

    @property
    def problems(self) -> list[Problem]:
        return [p for block in self.blocks for p in block.problems]

    @property
    def types(self) -> set[str]:
        return {p.type for p in self.problems}

    def activity_ids(self, lesson: Lesson) -> list[str]:
        found: list[str] = []
        for block in self.blocks:
            activity = resolve_activity(block, lesson)
            if activity is not None and activity not in found:
                found.append(activity)
        return found


def extract_problem_set_blocks(body: str) -> list[str]:
    """The raw text inside every ```` ```problemset ```` fence of ``body``, in order."""
    blocks: list[str] = []
    current: list[str] | None = None
    closing: str | None = None
    for line in body.splitlines():
        if current is not None:
            if closing is not None and line.strip() == closing:
                blocks.append("\n".join(current))
                current, closing = None, None
            else:
                current.append(line)
            continue
        match = PROBLEMSET_FENCE.match(line.strip())
        if match:
            current, closing = [], match["fence"]
    return blocks


def has_problem_set(body: str) -> bool:
    return bool(extract_problem_set_blocks(body))


def resolve_activity(block: ProblemSetBlock, lesson: Lesson) -> str | None:
    """The exercise activity a block records against (explicit, or the lesson's only one)."""
    if block.activity is not None:
        return block.activity
    exercises = [a.id for a in lesson.activities if a.kind is ActivityKind.EXERCISE]
    return exercises[0] if len(exercises) == 1 else None


def _parse_block(raw: str, where: str, messages: list[str]) -> ProblemSetBlock | None:
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        messages.append(f"{where}: invalid YAML: {exc}")
        return None
    if isinstance(data, list):  # the same shorthand a quiz block allows
        data = {"problems": data}
    if not isinstance(data, dict):
        messages.append(f"{where}: expected a YAML mapping with 'problems'")
        return None
    try:
        return ProblemSetBlock.model_validate(data)
    except Exception as exc:
        for line in str(exc).splitlines():
            text = line.strip()
            if text and not text.startswith("For further information"):
                messages.append(f"{where}: {text}")
        return None


def parse_problem_sets(lesson: Lesson) -> LessonProblemSets:
    """Parse every problem-set block of ``lesson``; raise on any structural problem.

    Reported: invalid YAML, an unknown ``type`` or ``solution_policy``, a ``numerical``
    problem without its expected value and tolerance, duplicate problem ids across the
    lesson, and an ``activity`` that is missing (when the lesson has several exercise
    activities) or does not name a ``kind: exercise`` activity of the lesson.
    """
    messages: list[str] = []
    blocks: list[ProblemSetBlock] = []
    seen: set[str] = set()
    exercises = [a.id for a in lesson.activities if a.kind is ActivityKind.EXERCISE]
    for number, raw in enumerate(extract_problem_set_blocks(lesson.body), 1):
        where = f"problemset block {number}"
        block = _parse_block(raw, where, messages)
        if block is None:
            continue
        for problem in block.problems:
            if problem.id in seen:
                messages.append(f"{where}: duplicate problem id '{problem.id}'")
            seen.add(problem.id)
        if block.activity is None:
            if len(exercises) > 1:
                messages.append(
                    f"{where}: 'activity' is required because the lesson has "
                    f"{len(exercises)} exercise activities ({', '.join(exercises)})"
                )
        elif block.activity not in exercises:
            messages.append(
                f"{where}: 'activity' {block.activity!r} is not a 'kind: exercise' activity "
                f"of this lesson"
                + (f" (have {', '.join(exercises)})" if exercises else " (it has none)")
            )
        blocks.append(block)
    if messages:
        raise ProblemSetParseError(messages)
    return LessonProblemSets(lesson_id=lesson.id, blocks=blocks)


def shape_advice(sets: LessonProblemSets) -> list[str]:
    """Editorial warnings about the set's size and variety (never errors).

    Separate from :func:`parse_problem_sets` because a set of three problems is a complete,
    loadable lesson — just one the standard would like to see grown.
    """
    problems = sets.problems
    if not problems:
        return []
    advice: list[str] = []
    if len(problems) < MIN_PROBLEMS:
        advice.append(
            f"has {len(problems)} problem(s); the standard asks for {MIN_PROBLEMS}-{MAX_PROBLEMS}"
        )
    elif len(problems) > MAX_PROBLEMS:
        advice.append(
            f"has {len(problems)} problems; the standard asks for "
            f"{MIN_PROBLEMS}-{MAX_PROBLEMS}, so consider splitting the lesson"
        )
    if len(sets.types) < MIN_TYPES:
        advice.append(
            f"uses {len(sets.types)} problem type(s) ({', '.join(sorted(sets.types))}); "
            f"the standard asks for at least {MIN_TYPES}"
        )
    return advice
