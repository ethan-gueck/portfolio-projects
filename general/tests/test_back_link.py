"""Every page built with render_page leads back to Ethan's NN, once, at the start of the masthead bar."""

from general.web.page import BACK_LINK, add_back_link, render_page

TEMPLATE = """<!doctype html><html><head><style>{{styles}}</style></head><body>
<header class="masthead"><div class="masthead__bar"><span class="masthead__kicker">K</span><a href="/">site</a></div></header>
</body></html>"""


def test_back_link_is_first_in_the_bar():
    document = render_page(TEMPLATE, title="T")
    bar = document.split('<div class="masthead__bar">')[1]
    assert bar.lstrip().startswith(BACK_LINK)
    assert document.count('class="masthead__back"') == 1
    assert 'href="https://ethan-gueck.github.io/#nn"' in bar


def test_back_link_can_be_left_out_and_is_never_doubled():
    assert 'class="masthead__back"' not in render_page(TEMPLATE, title="T", back=False)
    once = add_back_link('<div class="masthead__bar"></div>')
    assert add_back_link(once) == once


def test_pages_without_a_bar_are_unchanged():
    assert add_back_link("<p>no bar</p>") == "<p>no bar</p>"
