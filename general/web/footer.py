"""The call to action, footer and floating contact bar from ethan-gueck.github.io,
added to every built page.

render_page() inserts ``site_footer(title)`` before ``</body>`` (or at a
``{{footer}}`` placeholder). Styles: styles/css/components/site-footer.css,
part of every bundle. Edit contact details in CONTACT only.
"""

from __future__ import annotations

import html
from datetime import date

CONTACT = {
    "name": "Ethan Gueck",
    "email": "e.gueck1@gmail.com",
    "linkedin": "https://linkedin.com/in/ethan-gueck-447967194",
    "github": "https://github.com/ethan-gueck",
    "portfolio": "https://ethan-gueck.github.io/",
}

_MAIL_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18v12H3z"/><path d="M3 7l9 6 9-6"/></svg>'
_LINKEDIN_ICON = (
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path class="fill" d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.5h4V21H3z'
    "M9.5 9.5h3.8v1.6h.05c.53-1 1.83-2.05 3.77-2.05 4.03 0 4.78 2.65 4.78 6.1V21h-4v-5.1c0-1.22-.02-2.78-1.7-2.78-1.7 0-1.96 "
    '1.33-1.96 2.7V21h-4z"/></svg>'
)


def site_footer(title: str, year: int | None = None) -> str:
    """Call-to-action block and site footer; ``title`` names the page in the citation."""
    c = {k: html.escape(v) for k, v in CONTACT.items()}
    year = year or date.today().year
    github_label = c["github"].removeprefix("https://")
    return f"""
  <div class="container pp-cta">
    <aside class="cta" aria-label="Contact">
      <h2 class="cta__title">Let’s work together</h2>
      <p class="cta__text">Working on utility, telecom, or industrial data, or want to compare notes on a project? Reach out to me directly or connect with me on LinkedIn.</p>
      <div class="cta__actions">
        <a class="cta__btn cta__btn--primary" href="mailto:{c["email"]}">{_MAIL_ICON}Email me</a>
        <a class="cta__btn cta__btn--secondary" href="{c["linkedin"]}" target="_blank" rel="noopener">{_LINKEDIN_ICON}Connect on LinkedIn</a>
      </div>
    </aside>
  </div>
  <footer class="site-footer">
    <div class="container site-footer__inner">
      <div>
        <p class="site-footer__heading">Suggested citation</p>
        <p class="site-footer__cite">Gueck, E. ({year}). <em>{html.escape(title)}.</em> Portfolio of Ethan Gueck. {github_label}</p>
      </div>
      <div>
        <p class="site-footer__heading">Correspondence</p>
        <p><a href="mailto:{c["email"]}">{c["email"]}</a></p>
        <p><a href="{c["linkedin"]}" target="_blank" rel="noopener">LinkedIn</a></p>
        <p><a href="{c["github"]}" target="_blank" rel="noopener">{github_label}</a></p>
      </div>
    </div>
    <p class="container site-footer__fine">&copy; {year} {c["name"]}. Part of <a href="{c["portfolio"]}#nn">Ethan’s NN</a> on <a href="{c["portfolio"]}">{c["portfolio"].removeprefix("https://").rstrip("/")}</a>.</p>
  </footer>
  <aside class="contact-bar" aria-label="Contact Ethan">
    <div class="container contact-bar__inner">
      <p class="contact-bar__text">Have a project in mind? <span class="contact-bar__more">Reach out to me or connect with me on LinkedIn.</span></p>
      <div class="contact-bar__actions">
        <a class="cta__btn cta__btn--primary" href="mailto:{c["email"]}">{_MAIL_ICON}Email me</a>
        <a class="cta__btn cta__btn--secondary" href="{c["linkedin"]}" target="_blank" rel="noopener">{_LINKEDIN_ICON}LinkedIn</a>
      </div>
    </div>
  </aside>
  <script>
    // Hide the contact bar just before the footer scrolls into view, as on ethan-gueck.github.io.
    (function () {{
      var bar = document.querySelector(".contact-bar"), footer = document.querySelector(".site-footer");
      if (!bar || !footer || !("IntersectionObserver" in window)) return;
      new IntersectionObserver(function (entries) {{
        var atFooter = entries[0].isIntersecting;
        bar.classList.toggle("is-hidden", atFooter);
        bar.toggleAttribute("inert", atFooter);  // keep hidden buttons out of the tab order
      }}, {{ rootMargin: "0px 0px 90px 0px" }}).observe(footer);
    }})();
  </script>
"""
