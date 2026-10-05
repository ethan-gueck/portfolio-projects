/*
 * mode.js: dark mode on topic pages. The moon/sun button (here in the masthead, or on
 * ethan-gueck.github.io) saves localStorage "pp-theme" = "dark"; topic pages share that
 * origin, so a snippet in <head> (web/page.py) sets <html data-mode="dark"> and the dark tab
 * icon before paint, and the page's [data-mode="dark"] stylesheet takes over. This runs
 * before the page's own scripts and swaps the stage palette in the page config for the dark
 * one, so canvases draw in it too. Canvases keep the palette they started with, so switching
 * (here or in another tab) reloads the page into the new mode; inputs live in the URL hash.
 */
(function (global) {
  "use strict";
  const KEY = "pp-theme";
  const html = document.documentElement;
  const tag = document.getElementById("pp-config");
  const config = tag ? JSON.parse(tag.textContent) : {};
  if (html.dataset.mode === "dark" && config.theme_dark) {
    config.theme = config.theme_dark;
    tag.textContent = JSON.stringify(config);
  }
  global.addEventListener("storage", (event) => {
    if (event.key === KEY && (event.newValue === "dark") !== (html.dataset.mode === "dark")) global.location.reload();
  });

  // The toggle, at the right of the masthead bar (only on pages built with a dark palette).
  const bar = document.querySelector(".masthead__bar");
  if (!bar || !config.theme_dark) return;
  const dark = html.dataset.mode === "dark";
  const button = document.createElement("button");
  button.type = "button";
  button.className = "theme-toggle";
  button.setAttribute("aria-pressed", String(dark));
  button.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
  button.title = dark ? "Light mode" : "Dark mode";
  button.innerHTML =
    '<svg class="theme-toggle__moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5a8.5 8.5 0 1 0 11 11z"/></svg>' +
    '<svg class="theme-toggle__sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6"/></svg>';
  button.addEventListener("click", () => {
    try { global.localStorage.setItem(KEY, dark ? "light" : "dark"); } catch (e) { return; }
    global.location.reload();
  });
  // Keep the bar's two ends: the kicker on the left, the site link and the button on the right.
  const actions = document.createElement("span");
  actions.className = "masthead__actions";
  const link = bar.querySelector(":scope > a");
  if (link) actions.appendChild(link);
  actions.appendChild(button);
  bar.appendChild(actions);
})(window);
