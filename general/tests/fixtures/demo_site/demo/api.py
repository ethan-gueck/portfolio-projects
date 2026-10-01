from pathlib import Path

from general.api import JSModule, Page, Topic
from general.styles import BASE
from general.web import render_page, write_page

HERE = Path(__file__).resolve().parent


def double(x: float) -> float:
    """Twice x."""
    return 2 * x


def _build_page(output_path, theme=None):
    return write_page(render_page(HERE / "page.html", title="Demo", theme=theme, bundle=BASE), output_path)


TOPIC = Topic(
    title="Demo",
    description="Fixture topic.",
    modules=(JSModule(name="demo", global_name="DemoMath", scripts=(HERE / "demo_math.js",), functions={"double": double}),),
    pages=(Page(name="demo", title="Demo", build=_build_page, params=("x",), example={"x": 2}),),
    cards=("A1.1",),
)
