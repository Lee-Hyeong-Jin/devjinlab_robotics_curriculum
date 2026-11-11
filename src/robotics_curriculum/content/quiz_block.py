"""Quiz blocks inside a lesson body (PRD FR-4.1 and appendix C.1).

A lesson defines its quiz as one or more fenced ```` ```quiz ```` blocks. Each block is a
YAML mapping::

    ```quiz
    activity: m1-vectors-matrices-quiz     # the `kind: quiz` activity this block belongs to
    questions:                             # (optional when the lesson has exactly one)
      - id: q1
        type: single                       # single | multiple | truefalse | short
        prompt: "두 벡터의 내적이 0이면 두 벡터는?"
        choices: ["평행하다", "직교한다", "같은 벡터다", "영벡터다"]
        answer: 1                          # 0-based; multiple: [idx, ...]; truefalse: bool;
        explanation: "내적이 0이면 사잇각이 90°이므로 직교한다."   # short: ["answer", ...]
        concept: { front: "내적이 0인 두 벡터의 관계", back: "직교(사잇각 90°)" }
        tags: [linear-algebra]
    ```

For compatibility with platform-design §3.4 a block may also be a bare YAML list of
questions (``questions`` only) and ``multi`` is accepted as an alias of ``multiple``.

The front-matter ``activities`` entry of kind ``quiz`` is metadata (time estimate,
checklist); the body blocks are the questions themselves. :func:`parse_quiz` is the single
entry point used by the validator, the CLI, and the site builder.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from robotics_curriculum.content.models import ID_PATTERN, ActivityKind, Lesson

QUIZ_FENCE = re.compile(r"^(?P<fence>`{3,}|~{3,})\s*quiz\s*$")

QuestionType = Literal["single", "multiple", "truefalse", "short"]
TYPE_LABELS: dict[str, str] = {
    "single": "객관식",
    "multiple": "다중선택",
    "truefalse": "O/X",
    "short": "단답",
}
_TYPE_ALIASES = {"multi": "multiple"}


class QuizParseError(Exception):
    """A quiz block could not be parsed; ``messages`` lists every problem found."""

    def __init__(self, messages: list[str]) -> None:
        self.messages = messages
        super().__init__("\n".join(messages))


class _QuizModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Concept(_QuizModel):
    """An author-defined key-concept flashcard attached to a question."""

    front: str = Field(min_length=1)
    back: str = Field(min_length=1)


class QuizQuestion(_QuizModel):
    """One question of a lesson quiz."""

    id: Annotated[str, Field(pattern=ID_PATTERN)]
    type: QuestionType
    prompt: str = Field(min_length=1)
    choices: list[str] = Field(default_factory=list)
    answer: int | bool | list[int] | list[str]
    explanation: str = Field(min_length=1)
    concept: Concept | None = None
    tags: list[str] = Field(default_factory=list)

    @field_validator("type", mode="before")
    @classmethod
    def _alias_type(cls, value: object) -> object:
        return _TYPE_ALIASES.get(value, value) if isinstance(value, str) else value

    @model_validator(mode="after")
    def _check_answer_shape(self) -> QuizQuestion:
        kind, answer = self.type, self.answer
        if kind in ("single", "multiple"):
            if len(self.choices) < 2:
                raise ValueError(f"{kind} question needs at least 2 choices")
            if any(not choice for choice in self.choices):
                raise ValueError("choices must not be empty strings")
            n = len(self.choices)
            if kind == "single":
                if not isinstance(answer, int) or isinstance(answer, bool):
                    raise ValueError("single answer must be a 0-based choice index")
                if not 0 <= answer < n:
                    raise ValueError(f"single answer {answer} is out of range 0..{n - 1}")
            else:
                if not isinstance(answer, list) or not answer:
                    raise ValueError("multiple answer must be a non-empty list of choice indexes")
                indexes = [a for a in answer if isinstance(a, int) and not isinstance(a, bool)]
                if len(indexes) != len(answer):
                    raise ValueError("multiple answer must contain only choice indexes")
                if any(not 0 <= a < n for a in indexes):
                    raise ValueError(f"multiple answer {answer}: index out of range 0..{n - 1}")
                if len(set(indexes)) != len(indexes):
                    raise ValueError("multiple answer must not repeat an index")
        elif kind == "short":
            if self.choices:
                raise ValueError("short question must not have choices")
            if not isinstance(answer, list) or not answer:
                raise ValueError("short answer must be a non-empty list of accepted strings")
            if any(not isinstance(a, str) or not a.strip() for a in answer):
                raise ValueError("short answer strings must not be empty")
        else:  # truefalse
            if self.choices:
                raise ValueError("truefalse question must not have choices")
            if not isinstance(answer, bool):
                raise ValueError("truefalse answer must be true or false")
        return self

    @property
    def accepted_short(self) -> list[str]:
        """Accepted answers of a ``short`` question (empty for other types)."""
        if self.type != "short" or not isinstance(self.answer, list):
            return []
        return [str(a) for a in self.answer]

    @property
    def correct_indexes(self) -> set[int]:
        """Correct choice indexes of a ``single``/``multiple`` question (empty otherwise)."""
        if self.type == "single" and isinstance(self.answer, int):
            return {self.answer}
        if self.type == "multiple" and isinstance(self.answer, list):
            return {int(a) for a in self.answer}
        return set()

    @property
    def type_label(self) -> str:
        return TYPE_LABELS[self.type]

    def answer_text(self) -> str:
        """Human-readable correct answer (grading feedback, card backs, site pages)."""
        if self.type == "single":
            index = next(iter(self.correct_indexes))
            return f"{index + 1}. {self.choices[index]}"
        if self.type == "multiple":
            return ", ".join(f"{i + 1}. {self.choices[i]}" for i in sorted(self.correct_indexes))
        if self.type == "short":
            return " / ".join(self.accepted_short)
        return "O (참)" if self.answer else "X (거짓)"


class QuizBlock(_QuizModel):
    """One ```` ```quiz ```` block: its activity reference and questions."""

    activity: Annotated[str, Field(pattern=ID_PATTERN)] | None = None
    questions: list[QuizQuestion] = Field(min_length=1)


@dataclass(frozen=True, slots=True)
class LessonQuiz:
    """Every quiz question of a lesson, in order, grouped by block."""

    lesson_id: str
    blocks: list[QuizBlock] = field(default_factory=list)

    @property
    def questions(self) -> list[QuizQuestion]:
        return [q for block in self.blocks for q in block.questions]

    def question(self, question_id: str) -> QuizQuestion | None:
        return next((q for q in self.questions if q.id == question_id), None)

    def activity_ids(self, lesson: Lesson) -> list[str]:
        """Quiz activity ids this quiz belongs to (resolved per :func:`resolve_activity`)."""
        found: list[str] = []
        for block in self.blocks:
            activity = resolve_activity(block, lesson)
            if activity is not None and activity not in found:
                found.append(activity)
        return found


def extract_quiz_blocks(body: str) -> list[str]:
    """Return the raw text inside every ```` ```quiz ```` fence of ``body``, in order."""
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
        match = QUIZ_FENCE.match(line.strip())
        if match:
            current, closing = [], match["fence"]
    return blocks


def has_quiz(body: str) -> bool:
    return bool(extract_quiz_blocks(body))


def parse_quiz(lesson: Lesson) -> LessonQuiz:
    """Parse every quiz block of ``lesson``; raise :class:`QuizParseError` on any problem.

    Problems reported: invalid YAML, unknown ``type``, ``answer`` out of range or of the wrong
    shape, missing ``explanation``, duplicate question ids across the lesson, and an
    ``activity`` that is missing (when the lesson has several quiz activities) or does not name
    a ``kind: quiz`` activity of the lesson.
    """
    messages: list[str] = []
    blocks: list[QuizBlock] = []
    seen: set[str] = set()
    quiz_activities = [a.id for a in lesson.activities if a.kind is ActivityKind.QUIZ]
    for number, raw in enumerate(extract_quiz_blocks(lesson.body), 1):
        where = f"quiz block {number}"
        block = _parse_block(raw, where, messages)
        if block is None:
            continue
        for question in block.questions:
            if question.id in seen:
                messages.append(f"{where}: duplicate question id '{question.id}'")
            seen.add(question.id)
        if block.activity is None:
            if len(quiz_activities) > 1:
                messages.append(
                    f"{where}: 'activity' is required because the lesson has "
                    f"{len(quiz_activities)} quiz activities ({', '.join(quiz_activities)})"
                )
        elif block.activity not in quiz_activities:
            messages.append(
                f"{where}: activity '{block.activity}' is not a 'kind: quiz' activity of the lesson"
            )
        blocks.append(block)
    if messages:
        raise QuizParseError(messages)
    return LessonQuiz(lesson.id, blocks)


def resolve_activity(block: QuizBlock, lesson: Lesson) -> str | None:
    """The quiz activity id a block records against (explicit, or the lesson's only one)."""
    if block.activity is not None:
        return block.activity
    quiz_activities = [a.id for a in lesson.activities if a.kind is ActivityKind.QUIZ]
    return quiz_activities[0] if len(quiz_activities) == 1 else None


def _parse_block(raw: str, where: str, messages: list[str]) -> QuizBlock | None:
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        messages.append(f"{where}: invalid YAML: {exc}")
        return None
    if isinstance(data, list):  # platform-design §3.4 shorthand
        data = {"questions": data}
    if not isinstance(data, dict):
        messages.append(f"{where}: expected a mapping with 'questions' (or a list of questions)")
        return None
    try:
        return QuizBlock.model_validate(data)
    except ValidationError as exc:
        for err in exc.errors():
            messages.append(f"{where}: {_describe(err['loc'], err['msg'])}")
        return None


def _describe(loc: tuple[int | str, ...], msg: str) -> str:
    """``('questions', 0, 'answer')`` -> ``question 1: answer: ...`` (union noise stripped)."""
    parts = list(loc)
    prefix = ""
    if len(parts) >= 2 and parts[0] == "questions" and isinstance(parts[1], int):
        prefix = f"question {parts[1] + 1}"
        parts = parts[2:]
        # pydantic reports each union member for `answer`; keep only the field name.
        if parts and parts[0] == "answer":
            parts = ["answer"]
    rest = ".".join(str(p) for p in parts)
    detail = msg.removeprefix("Value error, ")
    return ": ".join(p for p in (prefix, rest, detail) if p)
