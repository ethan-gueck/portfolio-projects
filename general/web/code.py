"""'View the code' popup: shows the code for the math a page is about.

A page lists the file that holds its math (the Python ``core/`` module, the
source of truth) and, with ``only``, just the functions that compute the
page's expression (for the quadratic formula: ``discriminant`` and ``roots``).
It puts ``{{code_button}}`` in its template; render_page() adds the dialog,
with a link to the whole file on GitHub. Highlighting happens at build time,
so the page needs no extra scripts.
"""

from __future__ import annotations

import ast
import html
import io
import itertools
import keyword
import re
import tokenize
from dataclasses import dataclass
from pathlib import Path

DIALOG_ID = "pp-code"


@dataclass(frozen=True)
class CodeFile:
    """One file shown in the popup; ``note`` says what it is ("Source of truth")."""

    path: Path
    note: str = ""
    only: tuple[str, ...] = ()  # Python: the top-level functions / constants to show, in this order (default: all)
    split: bool = True  # Python: an overview and one block per function, with an index; False shows the file as one block

    @property
    def language(self) -> str:
        return "python" if Path(self.path).suffix == ".py" else "javascript"


# ---- highlighting -----------------------------------------------------------

_BUILTINS = {"abs", "max", "min", "round", "sorted", "len", "range", "float", "int", "str", "list", "dict", "tuple", "zip", "map", "sum", "isinstance", "print", "super", "enumerate", "any", "all"}


def _span(kind: str, text: str) -> str:
    return f'<span class="tok-{kind}">{html.escape(text)}</span>'


def highlight_python(source: str) -> str:
    """HTML for ``source`` with keyword, string, comment, number and name spans."""
    lines = source.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    out, pos, previous = [], 0, ""
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except (tokenize.TokenError, SyntaxError):
        return html.escape(source)
    for tok in tokens:
        if tok.type in (tokenize.ENDMARKER, tokenize.INDENT, tokenize.DEDENT) or not tok.string:
            continue
        start = offsets[tok.start[0] - 1] + tok.start[1]
        end = offsets[tok.end[0] - 1] + tok.end[1]
        out.append(html.escape(source[pos:start]))
        text = source[start:end]
        if tok.type == tokenize.COMMENT:
            out.append(_span("com", text))
        elif tok.type == tokenize.STRING or tok.type == getattr(tokenize, "FSTRING_START", -1):
            out.append(_span("str", text))
        elif tok.type in (getattr(tokenize, "FSTRING_MIDDLE", -1), getattr(tokenize, "FSTRING_END", -1)):
            out.append(_span("str", text))
        elif tok.type == tokenize.NUMBER:
            out.append(_span("num", text))
        elif tok.type == tokenize.NAME and keyword.iskeyword(text):
            out.append(_span("kw", text))
        elif tok.type == tokenize.NAME and previous in ("def", "class"):
            out.append(_span("fn", text))
        elif tok.type == tokenize.NAME and text in _BUILTINS:
            out.append(_span("bi", text))
        else:
            out.append(html.escape(text))
        pos = end
        if tok.type == tokenize.NAME:
            previous = text
        elif tok.type not in (tokenize.NL, tokenize.NEWLINE, tokenize.COMMENT):
            previous = ""
    out.append(html.escape(source[pos:]))
    text = "".join(out)
    # Token positions inside f-strings can drift on some Python versions; never show altered code.
    if html.unescape(re.sub(r"</?span[^>]*>", "", text)) != source:
        return html.escape(source)
    return text


_JS_KEYWORDS = (
    "const let var function return if else for of in while do new class extends throw try catch finally typeof "
    "instanceof break continue switch case default null undefined true false this"
).split()
_JS_TOKEN = re.compile(
    r"(?P<com>//[^\n]*|/\*[\s\S]*?\*/)"
    r"|(?P<str>`(?:\\.|[^`\\])*`|\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*')"
    r"|(?P<num>\b\d+(?:\.\d+)?(?:e[+-]?\d+)?n?\b)"
    r"|(?P<word>[A-Za-z_$][\w$]*)"
)


def highlight_js(source: str) -> str:
    out, pos, previous = [], 0, ""
    for match in _JS_TOKEN.finditer(source):
        out.append(html.escape(source[pos:match.start()]))
        kind, text = match.lastgroup, match.group()
        if kind == "word":
            if text in _JS_KEYWORDS:
                kind = "kw"
            elif previous == "function":
                kind = "fn"
            else:
                kind = ""
            previous = text
        out.append(_span(kind, text) if kind else html.escape(text))
        pos = match.end()
    out.append(html.escape(source[pos:]))
    return "".join(out)


# ---- splitting --------------------------------------------------------------

def python_code(source: str) -> str:
    """The file as one block, without its module docstring."""
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    first = tree.body[0] if tree.body else None
    if isinstance(first, ast.Expr) and isinstance(getattr(first, "value", None), ast.Constant) and isinstance(first.value.value, str):
        lines = lines[first.end_lineno :]
    return "".join(lines).strip("\n")


def _assigned_name(node) -> str | None:
    target = node.targets[0] if isinstance(node, ast.Assign) and len(node.targets) == 1 else getattr(node, "target", None)
    return target.id if isinstance(target, ast.Name) else None


def python_sections(source: str, only: tuple[str, ...] = ()) -> list[tuple[str, str]]:
    """``(name, code)`` for the module preamble and each top-level def/class, in file order.

    With ``only``, just those top-level functions, classes or constants, in that order.
    """
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    if only:
        found = {}
        for node in tree.body:
            name = node.name if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) else (
                _assigned_name(node) if isinstance(node, (ast.Assign, ast.AnnAssign)) else None)
            if name in only:
                start = (node.decorator_list[0].lineno if getattr(node, "decorator_list", None) else node.lineno) - 1
                found[name] = "".join(lines[start : node.end_lineno]).rstrip("\n")
        if "module" in only:  # the overview: the docstring and imports, up to the first definition
            # Section comments between the imports and the first def belong to the sections, not the overview.
            head = list(itertools.takewhile(lambda n: not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)), tree.body))
            found["module"] = "".join(lines[: head[-1].end_lineno if head else 0]).strip("\n")
        missing = [n for n in only if n not in found]
        if missing:
            raise ValueError(f"Not defined at the top level of the file: {', '.join(missing)}")
        return [(n, found[n]) for n in only]
    # After the first definition, named constants (e.g. PRECEDENCE = {...}) get blocks of their own too.
    defs = [i for i, n in enumerate(tree.body) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    nodes = [n for i, n in enumerate(tree.body) if (defs and i >= defs[0]) and (
        isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        or (isinstance(n, (ast.Assign, ast.AnnAssign)) and _assigned_name(n)))]
    sections = []
    first = min((n.decorator_list[0].lineno if getattr(n, "decorator_list", None) else n.lineno) for n in nodes) if nodes else len(lines) + 1
    preamble = "".join(lines[: first - 1]).strip("\n")
    if preamble:
        sections.append(("module", preamble))
    for node in nodes:
        decorators = getattr(node, "decorator_list", None)
        start = (decorators[0].lineno if decorators else node.lineno) - 1
        # Comments directly above a constant belong to it.
        while not decorators and start > 0 and lines[start - 1].lstrip().startswith("#"):
            start -= 1
        name = getattr(node, "name", None) or _assigned_name(node)
        sections.append((name, "".join(lines[start : node.end_lineno]).rstrip("\n")))
    return sections


# ---- markup -----------------------------------------------------------------

_CODE_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 7l-5 5 5 5M16 7l5 5-5 5M14 4l-4 16"/></svg>'
_CLOSE_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>'
_SLUG = re.compile(r"[^a-z0-9]+")


def _source_link(path: Path) -> str:
    """'View on GitHub' for files inside the project being built, when its repo is known."""
    from ..api.build import site_settings  # local import: api.build imports web
    from ..api.registry import find_root

    root = find_root()
    try:
        rel = Path(path).resolve().relative_to(root).as_posix()
    except ValueError:
        return ""
    repo = site_settings(root).get("repo")
    return f' · <a href="{html.escape(repo)}/blob/main/{html.escape(rel)}" target="_blank" rel="noopener">View the full file on GitHub</a>' if repo else ""


def code_viewer(files: list[CodeFile] | tuple[CodeFile, ...], title: str) -> tuple[str, str]:
    """``(button, dialog)`` HTML for the popup."""
    tabs, panels = [], []
    single = len(files) == 1
    for i, file in enumerate(files):
        path = Path(file.path)
        source = path.read_text()
        name = html.escape(path.name)
        tabs.append(
            f'<button class="code-modal__tab" type="button" role="tab" id="{DIALOG_ID}-tab-{i}" aria-controls="{DIALOG_ID}-file-{i}"'
            f' aria-selected="{"true" if i == 0 else "false"}">{name}</button>'
        )
        if file.language == "python" and not (file.split or file.only):
            body = f'<figure class="code-block"><pre><code>{highlight_python(python_code(source))}</code></pre></figure>'
        elif file.language == "python":
            sections = python_sections(source, file.only)
            index = "" if len(sections) <= 1 else "".join(
                f'<a class="code-modal__chip" href="#{DIALOG_ID}-{i}-{_SLUG.sub("-", n.lower())}">{html.escape(n)}</a>' for n, _ in sections
            )
            blocks = "".join(
                f'<figure class="code-block" id="{DIALOG_ID}-{i}-{_SLUG.sub("-", n.lower())}"><figcaption>{html.escape(n)}</figcaption>'
                f'<pre><code>{highlight_python(code)}</code></pre></figure>'
                for n, code in sections
            )
            body = (f'<nav class="code-modal__index" aria-label="Functions in {name}">{index}</nav>' if index else "") + blocks
        else:
            body = f'<figure class="code-block"><pre><code>{highlight_js(source)}</code></pre></figure>'
        meta = html.escape(file.note) + _source_link(path)
        panels.append(
            f'<section class="code-modal__file" id="{DIALOG_ID}-file-{i}"'
            + ("" if single else f' role="tabpanel" aria-labelledby="{DIALOG_ID}-tab-{i}"')
            + f'{"" if i == 0 else " hidden"}>'
            f'<p class="code-modal__meta">{meta}</p>{body}</section>'
        )
    button = f'<button class="btn code-open" type="button" data-code-open="{DIALOG_ID}">{_CODE_ICON}View the code</button>'
    dialog = f"""
  <dialog class="code-modal" id="{DIALOG_ID}" aria-labelledby="{DIALOG_ID}-title">
    <div class="code-modal__head">
      <h2 class="code-modal__title" id="{DIALOG_ID}-title">The code behind {html.escape(title)}</h2>
      <button class="code-modal__close" type="button" data-code-close aria-label="Close">{_CLOSE_ICON}</button>
    </div>
    {"" if single else f'<div class="code-modal__tabs" role="tablist" aria-label="Files">{"".join(tabs)}</div>'}
    <div class="code-modal__body">{"".join(panels)}</div>
  </dialog>
  <script>
    // Open/close the code popup, switch files, and jump to a function inside the dialog.
    (function () {{
      var dlg = document.getElementById("{DIALOG_ID}");
      if (!dlg || !dlg.showModal) return;
      document.querySelectorAll("[data-code-open]").forEach(function (b) {{ b.addEventListener("click", function () {{ dlg.showModal(); }}); }});
      dlg.querySelector("[data-code-close]").addEventListener("click", function () {{ dlg.close(); }});
      dlg.addEventListener("click", function (e) {{ if (e.target === dlg) dlg.close(); }});
      var tabs = dlg.querySelectorAll(".code-modal__tab");
      tabs.forEach(function (tab) {{
        tab.addEventListener("click", function () {{
          tabs.forEach(function (t) {{
            var on = t === tab;
            t.setAttribute("aria-selected", String(on));
            document.getElementById(t.getAttribute("aria-controls")).hidden = !on;
          }});
          dlg.querySelector(".code-modal__body").scrollTop = 0;
        }});
      }});
      dlg.querySelectorAll(".code-modal__chip").forEach(function (a) {{
        a.addEventListener("click", function (e) {{
          e.preventDefault();
          var target = document.getElementById(a.getAttribute("href").slice(1));
          var body = dlg.querySelector(".code-modal__body"), index = a.closest(".code-modal__index");
          // Land just below the sticky function index, whatever height it wraps to.
          if (target) body.scrollTop += target.getBoundingClientRect().top - body.getBoundingClientRect().top - index.offsetHeight - 8;
        }});
      }});
    }})();
  </script>
"""
    return button, dialog
