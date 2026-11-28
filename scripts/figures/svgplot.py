"""A very small SVG drawing helper for lesson figures.

The figures are diagrams and plots of a few dozen elements. Writing the SVG directly keeps
them dependency-free, small (a few kB), and exactly reproducible: ``make_figures.py`` computes
every coordinate from the same formulas the lessons teach.

Coordinates are given in *data* units with y pointing up; :class:`Canvas` maps them to the
SVG's pixel grid. Figures are drawn on white with dark ink so they read in either theme (the
site shows them on a white card).
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from html import escape

INK = "#1f2933"
MUTED = "#6b7280"
GRID = "#e5e7eb"
ACCENT = "#0b7a6b"
BLUE = "#1d4ed8"
RED = "#b91c1c"
ORANGE = "#b45309"
PURPLE = "#6d28d9"
FONT = "font-family=\"Helvetica, Arial, 'Noto Sans KR', sans-serif\""


def _n(value: float) -> str:
    """A number with at most two decimals and no trailing zeros."""
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return "0" if text in ("-0", "") else text


@dataclass
class Canvas:
    """A drawing area: data rectangle ``[x0, x1] x [y0, y1]`` mapped into ``width x height`` px."""

    width: int
    height: int
    x0: float
    x1: float
    y0: float
    y1: float
    pad: int = 28
    title: str = ""
    parts: list[str] = field(default_factory=list)

    # -- mapping -----------------------------------------------------------------------------

    def px(self, x: float) -> float:
        return self.pad + (x - self.x0) / (self.x1 - self.x0) * (self.width - 2 * self.pad)

    def py(self, y: float) -> float:
        return (
            self.height
            - self.pad
            - (y - self.y0) / (self.y1 - self.y0) * (self.height - 2 * self.pad)
        )

    def scale(self) -> float:
        """Pixels per data unit along x."""
        return (self.width - 2 * self.pad) / (self.x1 - self.x0)

    # -- primitives --------------------------------------------------------------------------

    def line(
        self,
        a: Sequence[float],
        b: Sequence[float],
        color: str = INK,
        width: float = 1.5,
        dash: str | None = None,
    ) -> None:
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<line x1="{_n(self.px(a[0]))}" y1="{_n(self.py(a[1]))}" x2="{_n(self.px(b[0]))}" '
            f'y2="{_n(self.py(b[1]))}" stroke="{color}" stroke-width="{_n(width)}"{extra}/>'
        )

    def polyline(
        self,
        points: Iterable[Sequence[float]],
        color: str = INK,
        width: float = 2,
        dash: str | None = None,
        close: bool = False,
        fill: str = "none",
        opacity: float = 1.0,
    ) -> None:
        coords = " ".join(f"{_n(self.px(x))},{_n(self.py(y))}" for x, y in points)
        tag = "polygon" if close else "polyline"
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        if fill != "none":
            extra += f' fill-opacity="{_n(opacity)}"'
        self.parts.append(
            f'<{tag} points="{coords}" fill="{fill}" stroke="{color}" '
            f'stroke-width="{_n(width)}" stroke-linejoin="round"{extra}/>'
        )

    def arrow(
        self,
        a: Sequence[float],
        b: Sequence[float],
        color: str = INK,
        width: float = 2,
        head: float = 9,
        dash: str | None = None,
    ) -> None:
        """A line from ``a`` to ``b`` with a filled arrowhead at ``b``."""
        ax, ay, bx, by = self.px(a[0]), self.py(a[1]), self.px(b[0]), self.py(b[1])
        angle = math.atan2(by - ay, bx - ax)
        length = math.hypot(bx - ax, by - ay)
        if length < 1e-6:
            return
        # Stop the shaft at the base of the head so the tip stays sharp.
        sx, sy = bx - head * 0.9 * math.cos(angle), by - head * 0.9 * math.sin(angle)
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<line x1="{_n(ax)}" y1="{_n(ay)}" x2="{_n(sx)}" y2="{_n(sy)}" stroke="{color}" '
            f'stroke-width="{_n(width)}"{extra}/>'
        )
        left = (bx - head * math.cos(angle - 0.42), by - head * math.sin(angle - 0.42))
        right = (bx - head * math.cos(angle + 0.42), by - head * math.sin(angle + 0.42))
        self.parts.append(
            f'<polygon points="{_n(bx)},{_n(by)} {_n(left[0])},{_n(left[1])} '
            f'{_n(right[0])},{_n(right[1])}" fill="{color}"/>'
        )

    def dot(self, p: Sequence[float], color: str = INK, radius: float = 4) -> None:
        self.parts.append(
            f'<circle cx="{_n(self.px(p[0]))}" cy="{_n(self.py(p[1]))}" r="{_n(radius)}" '
            f'fill="{color}"/>'
        )

    def circle(
        self,
        p: Sequence[float],
        radius: float,
        color: str = INK,
        width: float = 1.5,
        dash: str | None = None,
        fill: str = "none",
        opacity: float = 1.0,
    ) -> None:
        """A circle whose radius is in data units."""
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        if fill != "none":
            extra += f' fill-opacity="{_n(opacity)}"'
        self.parts.append(
            f'<circle cx="{_n(self.px(p[0]))}" cy="{_n(self.py(p[1]))}" '
            f'r="{_n(radius * self.scale())}" fill="{fill}" stroke="{color}" '
            f'stroke-width="{_n(width)}"{extra}/>'
        )

    def arc(
        self,
        center: Sequence[float],
        radius: float,
        start: float,
        end: float,
        color: str = INK,
        width: float = 1.5,
    ) -> None:
        """A circular arc from angle ``start`` to ``end`` (radians, counter-clockwise)."""
        steps = max(8, int(abs(end - start) / 0.05))
        points = [
            (
                center[0] + radius * math.cos(start + (end - start) * i / steps),
                center[1] + radius * math.sin(start + (end - start) * i / steps),
            )
            for i in range(steps + 1)
        ]
        self.polyline(points, color=color, width=width)

    def text(
        self,
        p: Sequence[float],
        label: str,
        color: str = INK,
        size: int = 13,
        anchor: str = "start",
        dx: float = 0,
        dy: float = 0,
        italic: bool = False,
        bold: bool = False,
    ) -> None:
        style = (' font-style="italic"' if italic else "") + (' font-weight="600"' if bold else "")
        self.parts.append(
            f'<text x="{_n(self.px(p[0]) + dx)}" y="{_n(self.py(p[1]) + dy)}" fill="{color}" '
            f'font-size="{size}" text-anchor="{anchor}" {FONT}{style}>{escape(label)}</text>'
        )

    def note(
        self,
        x_px: float,
        y_px: float,
        label: str,
        color: str = MUTED,
        size: int = 12,
        anchor: str = "start",
    ) -> None:
        """Text placed in pixel coordinates (legends, captions)."""
        self.parts.append(
            f'<text x="{_n(x_px)}" y="{_n(y_px)}" fill="{color}" font-size="{size}" '
            f'text-anchor="{anchor}" {FONT}>{escape(label)}</text>'
        )

    def swatch(
        self, x_px: float, y_px: float, color: str, label: str, dash: str | None = None
    ) -> None:
        """A legend entry: a short line in ``color`` followed by ``label``."""
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<line x1="{_n(x_px)}" y1="{_n(y_px - 4)}" x2="{_n(x_px + 22)}" y2="{_n(y_px - 4)}" '
            f'stroke="{color}" stroke-width="2.5"{extra}/>'
        )
        self.note(x_px + 28, y_px, label, color=INK)

    # -- axes --------------------------------------------------------------------------------

    def grid(self, step_x: float, step_y: float | None = None) -> None:
        step_y = step_y or step_x
        x = math.ceil(self.x0 / step_x) * step_x
        while x <= self.x1 + 1e-9:
            self.line((x, self.y0), (x, self.y1), color=GRID, width=1)
            x += step_x
        y = math.ceil(self.y0 / step_y) * step_y
        while y <= self.y1 + 1e-9:
            self.line((self.x0, y), (self.x1, y), color=GRID, width=1)
            y += step_y

    def axes(
        self,
        x_label: str = "x",
        y_label: str = "y",
        ticks_x: Sequence[float] = (),
        ticks_y: Sequence[float] = (),
        origin: Sequence[float] = (0.0, 0.0),
    ) -> None:
        ox, oy = origin
        self.arrow((self.x0, oy), (self.x1, oy), color=MUTED, width=1.2, head=7)
        self.arrow((ox, self.y0), (ox, self.y1), color=MUTED, width=1.2, head=7)
        self.text((self.x1, oy), x_label, color=MUTED, size=12, anchor="end", dy=-6, italic=True)
        self.text((ox, self.y1), y_label, color=MUTED, size=12, dx=6, dy=10, italic=True)
        for x in ticks_x:
            self.line((x, oy), (x, oy), color=MUTED)
            self.text((x, oy), _n(x), color=MUTED, size=11, anchor="middle", dy=15)
        for y in ticks_y:
            self.text((ox, y), _n(y), color=MUTED, size=11, anchor="end", dx=-6, dy=4)

    # -- output ------------------------------------------------------------------------------

    def render(self) -> str:
        head = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" '
            f'width="{self.width}" height="{self.height}" role="img">'
        )
        title = f"<title>{escape(self.title)}</title>" if self.title else ""
        background = f'<rect width="{self.width}" height="{self.height}" fill="#ffffff"/>'
        return "\n".join([head, title, background, *self.parts, "</svg>"]) + "\n"
