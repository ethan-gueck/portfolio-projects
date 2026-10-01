import html
import re

import pytest

from general.web import CodeFile, render_page
from general.web.code import code_viewer, highlight_js, highlight_python, python_sections

PY = '''"""Doc."""

import math


def _clean(v: float) -> float:
    return round(v, 10)  # tidy


@dataclass
class Point:
    x: float


def slope(x1, y1, x2, y2):
    """Rise over run."""
    return (y2 - y1) / (x2 - x1) if x2 != x1 else None
'''


def _text(markup: str) -> str:
    return html.unescape(re.sub(r"</?span[^>]*>", "", markup))


def test_python_is_split_per_top_level_definition():
    assert [name for name, _ in python_sections(PY)] == ["module", "_clean", "Point", "slope"]
    assert python_sections(PY)[2][1].startswith("@dataclass")


@pytest.mark.parametrize("source", [PY, 'x = f"{a!r} {{b}} {c:.2f}"\n'])
def test_python_highlighting_keeps_the_code_exact(source):
    marked = highlight_python(source)
    assert _text(marked) == source and '<span class="tok-kw">return</span>' in highlight_python(PY)


def test_js_highlighting_keeps_the_code_exact():
    source = "const m = (y2 - y1) / (x2 - x1); // slope\nfunction f(x) { return `x=${x}`; }\n"
    assert _text(highlight_js(source)) == source
    assert '<span class="tok-fn">f</span>' in highlight_js(source)


def test_viewer_lists_each_file_and_function(tmp_path):
    py, js = tmp_path / "slope.py", tmp_path / "slope_math.js"
    py.write_text(PY)
    js.write_text("const slope = (a) => a;\n")
    button, dialog = code_viewer([CodeFile(py, "Source of truth"), CodeFile(js, "Runs in this page")], "Slope")
    assert "data-code-open" in button
    assert dialog.count('role="tab"') == 2 and ">slope.py<" in dialog and ">slope_math.js<" in dialog
    assert 'href="#pp-code-0-slope"' in dialog and 'id="pp-code-0-slope"' in dialog
    assert "Source of truth" in dialog


def test_render_page_adds_the_popup_where_the_button_goes(tmp_path):
    py = tmp_path / "core.py"
    py.write_text(PY)
    template = tmp_path / "t.html"
    template.write_text("<body><main>{{code_button}}</main></body>")
    document = render_page(template, title="Slope", code=[CodeFile(py)])
    assert document.index("data-code-open") < document.index('<dialog class="code-modal"') < document.index("</body>")
    template.write_text("<body><main></main></body>")
    with pytest.raises(ValueError):
        render_page(template, title="Slope", code=[CodeFile(py)])


def test_only_shows_the_chosen_functions_in_that_order(tmp_path):
    assert [n for n, _ in python_sections(PY, ("slope", "_clean"))] == ["slope", "_clean"]
    py = tmp_path / "slope.py"
    py.write_text(PY)
    _, dialog = code_viewer([CodeFile(py, "The formula", only=("slope",))], "Slope")
    assert 'id="pp-code-0-slope"' in dialog and "_clean" not in dialog and "Point" not in dialog
    assert 'role="tab"' not in dialog  # one file: no tabs
    with pytest.raises(ValueError):
        python_sections(PY, ("nope",))


def test_constants_can_be_shown(tmp_path):
    assert python_sections("RANK = {'^': 4}\n\ndef f():\n    pass\n", ("RANK",)) == [("RANK", "RANK = {'^': 4}")]


def test_constants_after_the_functions_get_their_own_block():
    source = "import math\n\n\ndef f(x):\n    return x\n\n\n# Higher goes first.\nRANK = {'^': 4}\n"
    assert python_sections(source) == [("module", "import math"), ("f", "def f(x):\n    return x"), ("RANK", "# Higher goes first.\nRANK = {'^': 4}")]


def test_split_false_shows_one_block_without_the_docstring(tmp_path):
    py = tmp_path / "formula.py"
    py.write_text(PY)
    _, dialog = code_viewer([CodeFile(py, split=False)], "Slope")
    assert dialog.count('<figure class="code-block">') == 1 and 'class="code-modal__chip"' not in dialog
    assert "Doc." not in dialog and "slope" in dialog


def test_only_can_include_the_module_overview():
    assert [n for n, _ in python_sections(PY, ("module", "slope"))] == ["module", "slope"]
