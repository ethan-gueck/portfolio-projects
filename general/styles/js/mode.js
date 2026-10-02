/*
 * mode.js: dark mode on topic pages. ethan-gueck.github.io's moon/sun button saves
 * localStorage "pp-theme" = "dark"; topic pages share that origin, so a snippet in <head>
 * (web/page.py) sets <html data-mode="dark"> before paint and the page's
 * [data-mode="dark"] stylesheet takes over. This runs before the page's own scripts and
 * swaps the stage palette in the page config for the dark one, so canvases draw in it too.
 * Changing the mode in another tab reloads the page into the new mode.
 */
(function (global) {
  "use strict";
  const html = document.documentElement;
  if (html.dataset.mode === "dark") {
    const tag = document.getElementById("pp-config");
    if (tag) {
      const config = JSON.parse(tag.textContent);
      if (config.theme_dark) {
        config.theme = config.theme_dark;
        tag.textContent = JSON.stringify(config);
      }
    }
  }
  global.addEventListener("storage", (event) => {
    if (event.key === "pp-theme" && (event.newValue === "dark") !== (html.dataset.mode === "dark")) global.location.reload();
  });
})(window);
