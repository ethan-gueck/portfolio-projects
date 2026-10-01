import math

import pytest

from general.plotting import fit_viewport, nice_step


@pytest.mark.parametrize("span, step", [(10, 2), (8, 1), (0.9, 0.2), (300, 50)])
def test_nice_step(span, step):
    assert math.isclose(nice_step(span), step)


def test_fit_viewport_covers_points_and_curve():
    f = lambda x: x**3 - 2 * x  # noqa: E731
    view = fit_viewport([-1.5, 0, 1.5], f, always_include_y=[0])
    assert view.x_min <= -1.5 and view.x_max >= 1.5
    for i in range(41):
        x = view.x_min + (view.x_max - view.x_min) * i / 40
        assert view.y_min <= f(x) <= view.y_max
    assert view.x_min % view.x_step == 0 and view.y_max % view.y_step == 0  # snapped to ticks
