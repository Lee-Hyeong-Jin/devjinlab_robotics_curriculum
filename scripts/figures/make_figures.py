#!/usr/bin/env python3
"""Generate the lesson figures (SVG) under ``curriculum/``.

    uv run python scripts/figures/make_figures.py          # write every figure
    uv run python scripts/figures/make_figures.py --check  # fail if a file would change

Each figure is computed from the formulas of the lesson it belongs to — the plots run the same
model as the lesson's example code — so a figure cannot drift from the text without this
script noticing (``--check`` runs in the test suite). Labels are symbols and numbers only, so
one file serves every language; the sentence that explains a figure is its alt text in the
lesson. Licence: CC BY 4.0, like the rest of ``curriculum/``.
"""

from __future__ import annotations

import argparse
import math
import sys
from collections.abc import Callable
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from svgplot import ACCENT, BLUE, INK, MUTED, ORANGE, RED, Canvas  # noqa: E402

GRID_DARK = "#cbd5e1"

ROOT = Path(__file__).resolve().parents[2]
EXPERT = ROOT / "curriculum" / "robotics-expert"


def frame(
    c: Canvas,
    origin: tuple[float, float],
    theta: float,
    name: str,
    size: float = 0.7,
    label_at: tuple[float, float] = (-0.16, -0.16),
) -> None:
    """A 2D coordinate frame: x axis in red, y axis in blue, its name at the origin."""
    ox, oy = origin
    ct, st = math.cos(theta), math.sin(theta)
    c.arrow(origin, (ox + size * ct, oy + size * st), color=RED, width=2.2)
    c.arrow(origin, (ox - size * st, oy + size * ct), color=BLUE, width=2.2)
    c.dot(origin, radius=3)
    c.text((ox + label_at[0], oy + label_at[1]), name, size=13, anchor="middle", bold=True)


# -- M1 ---------------------------------------------------------------------------------------


def m1_vectors_order() -> str:
    """Rotate-then-scale against scale-then-rotate: the lesson's example, drawn."""
    th = np.deg2rad(30)
    rot = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    scl = np.diag([2.0, 1.0])
    square = np.array([[0, 1, 1, 0], [0, 0, 1, 1]], dtype=float)
    a = scl @ rot @ square
    b = rot @ scl @ square
    c = Canvas(520, 380, -1.3, 2.7, -0.3, 2.6, title="Order of two linear maps")
    c.grid(0.5)
    c.axes(ticks_x=(1, 2), ticks_y=(1, 2))
    c.polyline(square.T, color=MUTED, width=1.6, dash="5 4", close=True)
    c.polyline(a.T, color=ACCENT, width=2.2, close=True, fill=ACCENT, opacity=0.12)
    c.polyline(b.T, color=BLUE, width=2.2, close=True, fill=BLUE, opacity=0.10)
    c.swatch(300, 26, MUTED, "square", dash="5 4")
    c.swatch(300, 46, ACCENT, "a = S R  (rotate, scale)")
    c.swatch(300, 66, BLUE, "b = R S  (scale, rotate)")
    c.note(492, 346, "area(a) = area(b) = det S = 2", anchor="end")
    return c.render()


def m1_rotation_axes() -> str:
    """The columns of a rotation matrix are the rotated axes."""
    psi = np.deg2rad(35)
    c = Canvas(460, 380, -0.9, 1.45, -0.35, 1.45, title="Columns of a rotation matrix")
    c.grid(0.5)
    c.arrow((0, 0), (1.25, 0), color=MUTED, width=1.6)
    c.arrow((0, 0), (0, 1.25), color=MUTED, width=1.6)
    c.text((1.25, 0), "x", color=MUTED, dx=6, dy=4, italic=True)
    c.text((0, 1.25), "y", color=MUTED, dx=-4, dy=-8, anchor="end", italic=True)
    x_tip = (math.cos(psi), math.sin(psi))
    y_tip = (-math.sin(psi), math.cos(psi))
    c.arrow((0, 0), x_tip, color=RED, width=2.4)
    c.arrow((0, 0), y_tip, color=BLUE, width=2.4)
    c.text(x_tip, "x′ = (cos ψ, sin ψ)", color=RED, dx=8, dy=-4)
    c.text(y_tip, "y′ = (−sin ψ, cos ψ)", color=BLUE, dx=-4, dy=-10, anchor="middle")
    c.arc((0, 0), 0.38, 0, psi, color=INK)
    c.text((0.46 * math.cos(psi / 2), 0.46 * math.sin(psi / 2)), "ψ", dy=4, italic=True)
    c.line((x_tip[0], 0), x_tip, color=RED, width=1, dash="3 3")
    c.line((y_tip[0], 0), y_tip, color=BLUE, width=1, dash="3 3")
    c.note(230, 366, "R(ψ) = [ x′  y′ ]  — each column is one rotated axis", anchor="middle")
    return c.render()


def m1_frames() -> str:
    """World, robot and sensor frames of the lesson's example, and the point seen by the sensor."""
    c = Canvas(520, 400, -0.6, 3.4, -0.5, 2.5, title="A point carried through three frames")
    c.grid(0.5)
    frame(c, (0, 0), 0.0, "{w}", size=0.8)
    robot, sensor, point = (2.0, 1.0), (2.0, 1.1), (2.0, 1.6)
    frame(c, robot, math.pi / 2, "{r}", size=0.55, label_at=(0.2, -0.14))
    frame(c, sensor, math.pi / 2, "{s}", size=0.3, label_at=(-0.22, 0.02))
    c.arrow((0, 0), robot, color=MUTED, width=1.4, dash="5 4", head=7)
    c.text((1.0, 0.5), "T_wr", color=MUTED, dx=6, dy=14, italic=True)
    c.dot(point, color=ORANGE, radius=5)
    c.text(point, "p   (0.5, 0) in {s}", color=ORANGE, dx=10, dy=4)
    c.text(point, "(2, 1.6) in {w}", color=ORANGE, dx=10, dy=20)
    c.line((0, 1.6), point, color=ORANGE, width=1, dash="3 3")
    c.line((2.0, 0), (2.0, 1.0), color=MUTED, width=1, dash="3 3")
    c.axes(ticks_x=(1, 2, 3), ticks_y=(1, 2))
    c.note(500, 386, "p_w = T_wr · T_rs · p_s", anchor="end")
    return c.render()


# -- M2 ---------------------------------------------------------------------------------------


def _arm(
    c: Canvas,
    base: tuple[float, float],
    lengths: tuple[float, ...],
    angles: tuple[float, ...],
    color: str = INK,
    width: float = 5,
    dash: str | None = None,
) -> list[tuple[float, float]]:
    """Draw a planar serial arm; returns the joint positions, base first."""
    points = [base]
    total = 0.0
    for length, angle in zip(lengths, angles, strict=True):
        total += angle
        x, y = points[-1]
        points.append((x + length * math.cos(total), y + length * math.sin(total)))
    c.polyline(points, color=color, width=width, dash=dash)
    for point in points[:-1]:
        c.dot(point, color="#ffffff", radius=5)
        c.circle(point, 5 / c.scale(), color=color, width=2)
    c.dot(points[-1], color=color, radius=4)
    return points


def m2_dh_arm() -> str:
    """The lesson's two-link arm: link lengths, joint angles, and where the hand ends up."""
    l1, l2 = 0.5, 0.3
    t1, t2 = np.deg2rad(30), np.deg2rad(45)
    c = Canvas(500, 400, -0.15, 0.85, -0.12, 0.72, title="Two-link planar arm")
    c.grid(0.1)
    c.axes(x_label="x₀", y_label="y₀", ticks_x=(0.2, 0.4, 0.6, 0.8), ticks_y=(0.2, 0.4, 0.6))
    base, elbow, hand = _arm(c, (0.0, 0.0), (l1, l2), (t1, t2))
    c.line(base, (0.3, 0.0), color=MUTED, width=1, dash="3 3")
    c.arc(base, 0.14, 0, t1, color=ACCENT)
    c.text((0.17, 0.035), "θ₁ = 30°", color=ACCENT, size=12)
    ext = (elbow[0] + 0.2 * math.cos(t1), elbow[1] + 0.2 * math.sin(t1))
    c.line(elbow, ext, color=MUTED, width=1, dash="3 3")
    c.arc(elbow, 0.1, t1, t1 + t2, color=ACCENT)
    c.text((elbow[0] + 0.12, elbow[1] + 0.1), "θ₂ = 45°", color=ACCENT, size=12)
    c.text(((base[0] + elbow[0]) / 2, (base[1] + elbow[1]) / 2), "a₁ = 0.5", dx=10, dy=18, size=12)
    c.text(((elbow[0] + hand[0]) / 2, (elbow[1] + hand[1]) / 2), "a₂ = 0.3", dx=-64, dy=0, size=12)
    c.text(hand, f"({hand[0]:.3f}, {hand[1]:.3f})", color=ORANGE, dx=8, dy=-8, size=12)
    c.dot(hand, color=ORANGE, radius=5)
    c.note(480, 388, "T₀₂ = T₀₁(θ₁) · T₁₂(θ₂)", anchor="end")
    return c.render()


def m2_workspace() -> str:
    """Reachable set of the two-link arm: a ring between |a1 - a2| and a1 + a2."""
    l1, l2 = 0.5, 0.3
    c = Canvas(460, 440, -0.95, 0.95, -0.95, 0.95, title="Workspace of the two-link arm")
    c.grid(0.25)
    c.circle((0, 0), l1 + l2, color=ACCENT, width=2, fill=ACCENT, opacity=0.12)
    c.circle((0, 0), abs(l1 - l2), color=ACCENT, width=2, fill="#ffffff", opacity=1.0)
    c.axes(ticks_x=(-0.5, 0.5), ticks_y=(-0.5, 0.5))
    _arm(c, (0.0, 0.0), (l1, l2), (np.deg2rad(30), np.deg2rad(45)), width=4)
    _arm(c, (0.0, 0.0), (l1, l2), (np.deg2rad(160), np.deg2rad(-150)), color=MUTED, width=3)
    diag = math.sqrt(0.5)
    c.text(
        ((l1 + l2) * diag, (l1 + l2) * diag),
        "r = a₁ + a₂ = 0.8",
        color=ACCENT,
        dx=-4,
        dy=-8,
        size=12,
        anchor="middle",
    )
    c.text(
        (0.0, -abs(l1 - l2)), "r = |a₁ − a₂| = 0.2", color=ACCENT, anchor="middle", dy=16, size=12
    )
    return c.render()


def m2_ik_two_solutions() -> str:
    """One target, two arm poses: the elbow-down and elbow-up solutions of the lesson."""
    c = Canvas(460, 420, -0.5, 1.7, -0.45, 1.6, title="Two inverse-kinematics solutions")
    c.grid(0.5)
    c.axes()
    _arm(c, (0.0, 0.0), (1.0, 1.0), (0.0, np.pi / 2), color=ACCENT)
    _arm(c, (0.0, 0.0), (1.0, 1.0), (np.pi / 2, -np.pi / 2), color=BLUE)
    c.dot((1.0, 1.0), color=ORANGE, radius=6)
    c.text((1.0, 1.0), "target (1, 1)", color=ORANGE, dx=10, dy=-8)
    c.text((1.0, 0.0), "θ = (0°, 90°)", color=ACCENT, dx=8, dy=20)
    c.text((0.0, 1.0), "θ = (90°, −90°)", color=BLUE, dx=10, dy=-12)
    c.line((0, 0), (1, 1), color=MUTED, width=1, dash="4 4")
    return c.render()


# -- M3 ---------------------------------------------------------------------------------------


def m3_diff_drive() -> str:
    """Top view of a differential-drive robot turning about its instantaneous centre."""
    wheel_base, radius = 0.6, 1.2  # drawn large so the geometry is readable
    c = Canvas(520, 380, -1.75, 1.25, -0.55, 1.65, title="Differential-drive geometry")
    c.grid(0.5)
    icc = (-radius, 0.0)
    c.arc(icc, radius, -0.15, 1.15, color=MUTED, width=1.4)
    c.arc(icc, radius - wheel_base / 2, -0.15, 1.15, color=GRID_DARK, width=1)
    c.arc(icc, radius + wheel_base / 2, -0.15, 1.15, color=GRID_DARK, width=1)
    # body and wheels at heading 90 degrees (pointing up), centre at the origin
    c.circle((0, 0), 0.36, color=INK, width=2, fill="#f3f4f6", opacity=1.0)
    for side, name, omega in ((-1, "L", "ω_L"), (1, "R", "ω_R")):
        x = side * wheel_base / 2
        c.polyline(
            [(x - 0.05, -0.16), (x + 0.05, -0.16), (x + 0.05, 0.16), (x - 0.05, 0.16)],
            color=INK,
            width=1.5,
            close=True,
            fill=INK,
            opacity=0.85,
        )
        length = 0.3 if side < 0 else 0.6
        c.arrow((x, 0.2), (x, 0.2 + length), color=BLUE, width=2)
        c.text(
            (x, 0.2 + length),
            f"r·{omega}",
            color=BLUE,
            dx=6 if side > 0 else -6,
            dy=-4,
            anchor="start" if side > 0 else "end",
            size=12,
        )
        c.text((x, -0.3), name, anchor="middle", size=12)
    c.arrow((0, 0), (0, 0.48), color=RED, width=2.4)
    c.text((0, 0.48), "v", color=RED, dx=-12, dy=2, italic=True)
    c.dot(icc, color=ORANGE, radius=5)
    c.text(icc, "ICC", color=ORANGE, dx=-8, dy=20, anchor="middle")
    c.line(icc, (0, 0), color=ORANGE, width=1.2, dash="4 4")
    c.text((-radius / 2, 0), "R = v / ω", color=ORANGE, anchor="middle", dy=-8)
    c.line((-wheel_base / 2, -0.42), (wheel_base / 2, -0.42), color=MUTED, width=1)
    c.text((0, -0.42), "L", color=MUTED, anchor="middle", dy=16, italic=True)
    c.arc(icc, 0.3, 0.1, 0.9, color=ORANGE)
    c.text((icc[0] + 0.34, 0.24), "ω", color=ORANGE, italic=True)
    c.note(500, 30, "v = r(ω_R + ω_L)/2", anchor="end", color=INK)
    c.note(500, 50, "ω = r(ω_R − ω_L)/L", anchor="end", color=INK)
    return c.render()


def _wrap(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


def _heading_response(
    kp: float, ki: float, kd: float, seconds: float = 5.0, dt: float = 0.01
) -> list[tuple[float, float]]:
    """The lesson's heading loop: same PID, same saturation, same constant disturbance."""
    target, theta, integral, previous, u_max, disturbance = math.pi / 2, 0.0, 0.0, None, 3.0, -0.3
    out = [(0.0, 0.0)]
    for k in range(int(seconds / dt)):
        error = _wrap(target - theta)
        rate = 0.0 if previous is None else _wrap(theta - previous) / dt
        previous = theta
        u = kp * error + ki * integral - kd * rate
        u_sat = max(-u_max, min(u_max, u))
        if u == u_sat:
            integral += error * dt
        theta += (u_sat + disturbance) * dt
        out.append(((k + 1) * dt, math.degrees(theta)))
    return out


def m3_pid_step() -> str:
    """Heading step responses of the lesson's P, PI and PID controllers."""
    c = Canvas(540, 360, -0.3, 5.2, -8, 104, pad=34, title="Step response of the heading loop")
    c.grid(1.0, 10.0)
    c.axes(x_label="t [s]", y_label="θ [deg]", ticks_x=(1, 2, 3, 4, 5), ticks_y=(30, 60, 90))
    c.line((0, 90), (5.1, 90), color=MUTED, width=1.4, dash="6 4")
    c.text((5.1, 90), "target 90°", color=MUTED, anchor="end", dy=-6, size=12)
    for (kp, ki, kd), color in (((4, 0, 0), BLUE), ((4, 2, 0), ACCENT), ((4, 2, 0.2), RED)):
        c.polyline(_heading_response(kp, ki, kd)[::4], color=color, width=2)
    c.swatch(250, 170, BLUE, "P   (4, 0, 0): stops 4.3° short")
    c.swatch(250, 192, ACCENT, "PI  (4, 2, 0): error → 0")
    c.swatch(250, 214, RED, "PID (4, 2, 0.2)")
    c.note(250, 240, "constant disturbance −0.3 rad/s, |ω| ≤ 3 rad/s")
    return c.render()


def _square_run(eps: float) -> list[tuple[float, float]]:
    """The lesson's go-to-goal controller driving the square of waypoints."""
    waypoints = [(1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)]
    x = y = theta = 0.0
    index, dt, out = 0, 0.02, [(0.0, 0.0)]
    for _ in range(int(60.0 / dt)):
        last = index == len(waypoints) - 1
        gx, gy = waypoints[index]
        rho = math.hypot(gx - x, gy - y)
        alpha = _wrap(math.atan2(gy - y, gx - x) - theta)
        if rho < (0.005 if last else eps):
            if last:
                break
            index += 1
            continue
        v = min(rho, 0.2) * max(math.cos(alpha), 0.0)
        x, y, theta = (
            x + v * math.cos(theta) * dt,
            y + v * math.sin(theta) * dt,
            theta + 4 * alpha * dt,
        )
        out.append((x, y))
    return out


def m3_square_path() -> str:
    """Waypoint following around a square for two switching radii."""
    c = Canvas(460, 440, -0.3, 1.3, -0.3, 1.3, title="Waypoint following around a square")
    c.grid(0.25)
    c.axes(ticks_x=(0.5, 1), ticks_y=(0.5, 1))
    square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    c.polyline(square, color=MUTED, width=1.4, dash="5 4", close=True)
    c.polyline(_square_run(0.2)[::3], color=BLUE, width=2)
    c.polyline(_square_run(0.05)[::3], color=ACCENT, width=2)
    for point in square[1:]:
        c.dot(point, color=ORANGE, radius=5)
    c.circle((1, 1), 0.2, color=BLUE, width=1, dash="3 3")
    c.swatch(150, 215, ACCENT, "ε = 0.05 m")
    c.swatch(150, 235, BLUE, "ε = 0.20 m")
    c.arrow((0.35, -0.12), (0.65, -0.12), color=MUTED, width=1.2, head=7)
    return c.render()


FIGURES: dict[Path, Callable[[], str]] = {
    EXPERT / "m2-kinematics/figures/dh-parameters-two-link.svg": m2_dh_arm,
    EXPERT / "m2-kinematics/figures/forward-kinematics-workspace.svg": m2_workspace,
    EXPERT / "m2-kinematics/figures/inverse-kinematics-two-solutions.svg": m2_ik_two_solutions,
    EXPERT / "m3-mobile-robots-control/figures/differential-drive-icc.svg": m3_diff_drive,
    EXPERT / "m3-mobile-robots-control/figures/pid-control-step.svg": m3_pid_step,
    EXPERT / "m3-mobile-robots-control/figures/path-following-square.svg": m3_square_path,
    EXPERT / "m1-math-physics/figures/vectors-matrices-order.svg": m1_vectors_order,
    EXPERT / "m1-math-physics/figures/rotation-representations-axes.svg": m1_rotation_axes,
    EXPERT / "m1-math-physics/figures/coordinate-transforms-frames.svg": m1_frames,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if any file would change")
    args = parser.parse_args()
    stale = []
    for path, build in FIGURES.items():
        text = build()
        if args.check:
            if not path.is_file() or path.read_text("utf-8") != text:
                stale.append(path.relative_to(ROOT))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"{path.relative_to(ROOT)}  {len(text.encode()) / 1000:.1f} kB")
    if stale:
        print("out of date (run scripts/figures/make_figures.py):", *stale, sep="\n  ")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
