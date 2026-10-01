"""Sticky camera helpers in manim_canvas.js (Manim.view)."""

import json

import pytest

from general.jsrun import AVAILABLE, run_js
from general.styles import JS_DIR

pytestmark = pytest.mark.skipif(not AVAILABLE, reason="no JavaScript runtime (node or osascript)")

VIEW = {"x_min": -4, "x_max": 4, "y_min": -2, "y_max": 10, "x_step": 1, "y_step": 2}


def view_call(expression: str):
    return run_js([JS_DIR / "manim_canvas.js"], f"(function (V, cur) {{ return {expression}; }})(window.Manim.view, {json.dumps(VIEW)})")


def test_small_change_keeps_camera():
    ideal = {**VIEW, "x_min": -3.5, "x_max": 4.5}
    assert view_call(f"V.follow(cur, {json.dumps(ideal)}, [[0, 1], [1, 3]])") is None


def test_escaping_point_moves_camera_with_slack():
    ideal = {"x_min": 0, "x_max": 12, "y_min": -2, "y_max": 10, "x_step": 2, "y_step": 2}
    target = view_call(f"V.follow(cur, {json.dumps(ideal)}, [[9, 1]])")
    assert target["x_min"] <= 0 and target["x_max"] >= 12  # at least the ideal window
    assert target["x_max"] - target["x_min"] > 12          # plus slack
    assert target["x_min"] % target["x_step"] == 0          # snapped to ticks


def test_shrunken_content_zooms_in():
    tiny = {"x_min": -0.5, "x_max": 0.5, "y_min": -0.5, "y_max": 0.5, "x_step": 0.2, "y_step": 0.2}
    assert view_call(f"V.follow(cur, {json.dumps(tiny)}, [[0, 0]])") is not None


def test_lerp_endpoints():
    other = {"x_min": 0, "x_max": 8, "y_min": 0, "y_max": 4, "x_step": 2, "y_step": 1}
    start, end = view_call(f"[V.lerp(cur, {json.dumps(other)}, 0), V.lerp(cur, {json.dumps(other)}, 1)]")
    assert {k: start[k] for k in ("x_min", "x_max", "y_min", "y_max")} == {k: VIEW[k] for k in ("x_min", "x_max", "y_min", "y_max")}
    assert end == other


SPRING = r"""
(function (damp) {
  var pos = 0, vel = 0, target = 10, dt = 1 / 60, trace = [];
  for (var i = 0; i < 180; i++) {
    if (i === 15) target = 20;               // retarget mid-move, like a slider drag
    var r = damp(pos, target, vel, 0.3, dt);
    trace.push({ pos: r[0], vel: r[1], retarget: i === 15, prevVel: vel });
    pos = r[0]; vel = r[1];
  }
  return trace;
})(window.Manim.smoothDamp)
"""


def test_spring_camera_is_smooth_and_settles():
    trace = run_js([JS_DIR / "manim_canvas.js"], SPRING)
    positions = [t["pos"] for t in trace]
    assert all(b >= a - 1e-9 for a, b in zip(positions, positions[1:]))  # never reverses or overshoots
    assert max(positions) <= 20 + 1e-6
    assert abs(positions[-1] - 20) < 1e-3                                  # settles on the final target
    kick = next(t for t in trace if t["retarget"])
    assert kick["vel"] >= kick["prevVel"] * 0.9                            # keeps its speed when retargeted


def test_ticks_follow_visible_span():
    steps = run_js([JS_DIR / "manim_canvas.js"], "[4, 10, 35, 120].map(function (s) { return window.Manim.niceStep(s); })")
    assert steps == [0.5, 2, 5, 20]
