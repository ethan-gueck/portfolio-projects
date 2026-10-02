/*
 * stage_settings.js — the gear menu in the corner of an animation stage (web/settings.py).
 *
 * The menu is a <details>, so it opens and closes without script; this only
 * closes it on a click outside it or on Escape (focus returns to the gear).
 */
(function () {
  "use strict";
  const menus = () => document.querySelectorAll("details.stage-settings[open]");
  document.addEventListener("click", (event) => {
    menus().forEach((menu) => { if (!menu.contains(event.target)) menu.open = false; });
  });
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    menus().forEach((menu) => { menu.open = false; menu.querySelector("summary").focus(); });
  });
})();
