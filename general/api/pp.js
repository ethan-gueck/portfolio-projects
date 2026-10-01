/*
 * pp.js: client for the Portfolio Projects static API (served by GitHub Pages).
 *
 *   <script src="https://ethan-gueck.github.io/algebra/api/v1/pp.js"></script>   (any domain site)
 *
 *   await PP.list()                                        // modules + pages in the manifest
 *   const q = await PP.use("a1/quadratic");        // load a module, call it directly
 *   q.solve(1, -3, 2)
 *   await PP.call("a1/quadratic", "solve", 1, -3, 2)
 *   PP.embed(el, "a1/quadratic", { a: 1, b: -3, c: 2 })   // interactive page in an auto-sized iframe
 *   PP.useTheme("portfolio")                               // add the theme + shared CSS to this page
 *
 * All paths come from manifest.json next to this file, so the client works
 * wherever the site is hosted (Pages, a local `python -m general serve`, ...).
 */
(function (global) {
  "use strict";

  const SCRIPT_URL = new URL(document.currentScript ? document.currentScript.src : "api/v1/pp.js", global.location.href);
  const SITE_ROOT = new URL("../../", SCRIPT_URL);  // pp.js lives at <root>/api/v1/pp.js
  const loaded = new Map();
  let manifestPromise = null;

  function manifest() {
    if (!manifestPromise) {
      manifestPromise = fetch(new URL("manifest.json", SCRIPT_URL)).then((response) => {
        if (!response.ok) throw new Error(`PP: manifest request failed (${response.status})`);
        return response.json();
      });
    }
    return manifestPromise;
  }

  const url = (path) => new URL(path, SITE_ROOT).href;

  function loadScript(src) {
    if (!loaded.has(src)) {
      loaded.set(src, new Promise((resolve, reject) => {
        const tag = document.createElement("script");
        tag.src = src;
        tag.onload = resolve;
        tag.onerror = () => reject(new Error(`PP: failed to load ${src}`));
        document.head.appendChild(tag);
      }));
    }
    return loaded.get(src);
  }

  async function entry(kind, id) {
    const m = await manifest();
    const item = m[kind][id];
    if (!item) throw new Error(`PP: unknown ${kind.slice(0, -1)} "${id}". Available: ${Object.keys(m[kind]).join(", ")}`);
    return item;
  }

  /** Load a module's scripts (once) and return its API object. */
  async function use(id) {
    const mod = await entry("modules", id);
    for (const script of mod.scripts) await loadScript(url(script));
    const api = global[mod.global];
    if (!api) throw new Error(`PP: module "${id}" did not define window.${mod.global}`);
    return api;
  }

  /** Call one function of a module. */
  async function call(id, fn, ...args) {
    const api = await use(id);
    if (typeof api[fn] !== "function") throw new Error(`PP: "${id}" has no function "${fn}"`);
    return api[fn](...args);
  }

  async function list() {
    const m = await manifest();
    return { modules: m.modules, pages: m.pages, themes: Object.keys(m.themes) };
  }

  /**
   * Embed an interactive page in `container` as an iframe that sizes itself to its content.
   * `params` preset the page (URL hash); options: { theme, height, title }.
   * Returns { iframe, set(params) }; set() updates the page's values in place.
   */
  async function embed(container, id, params = {}, options = {}) {
    const page = await entry("pages", id);
    const path = options.theme && page.themes && page.themes[options.theme] ? page.themes[options.theme] : page.path;
    const hash = () => new URLSearchParams({ ...params, embed: 1 }).toString();
    const iframe = document.createElement("iframe");
    iframe.src = `${url(path)}#${hash()}`;
    iframe.title = options.title || page.title;
    iframe.loading = "lazy";
    iframe.style.cssText = `width:100%;border:0;display:block;height:${options.height || 640}px;`;
    const onMessage = (event) => {
      if (event.source === iframe.contentWindow && event.data && event.data.type === "pp:resize" && !options.height) {
        iframe.style.height = `${event.data.height}px`;
      }
    };
    global.addEventListener("message", onMessage);
    (typeof container === "string" ? document.querySelector(container) : container).appendChild(iframe);
    return {
      iframe,
      set(next) {
        Object.assign(params, next);
        iframe.contentWindow.location.hash = hash();
      },
      destroy() { global.removeEventListener("message", onMessage); iframe.remove(); },
    };
  }

  /** Add a theme's variables plus the shared stylesheets to the current page. */
  async function useTheme(name = null, { shared = true } = {}) {
    const m = await manifest();
    const theme = name || m.defaultTheme;
    const hrefs = [m.themes[theme], ...(shared ? m.styles : [])];
    for (const href of hrefs) {
      const full = url(href);
      if (document.querySelector(`link[href="${full}"]`)) continue;
      const link = document.createElement("link");
      link.rel = "stylesheet";
      link.href = full;
      document.head.appendChild(link);
    }
    return theme;
  }

  global.PP = { version: 1, root: SITE_ROOT.href, manifest, list, use, call, embed, useTheme };
})(window);
