/*
 * params.js: numeric URL-hash parameters, so any page can be deep-linked
 * (page.html#a=1&b=-3&c=2) and PP.embed() can preset values.
 * Exposes window.PPParams = { read, write, flag }.
 */
(function (global) {
  "use strict";

  const current = () => new URLSearchParams(global.location.hash.slice(1));

  /** Numbers for `keys` found in the hash; missing or non-numeric keys are omitted. */
  function read(keys) {
    const params = current();
    const out = {};
    for (const key of keys) {
      if (params.has(key) && params.get(key) !== "" && Number.isFinite(Number(params.get(key)))) out[key] = Number(params.get(key));
    }
    return out;
  }

  /** Replace `values` in the hash without adding history entries; other keys are kept. */
  function write(values) {
    const params = current();
    for (const [key, value] of Object.entries(values)) params.set(key, value);
    global.history.replaceState(null, "", `#${params.toString()}`);
  }

  /** True when the hash contains key=1 / key=true (e.g. #embed=1). */
  function flag(key) {
    const value = current().get(key);
    return value === "1" || value === "true";
  }

  global.PPParams = { read, write, flag };
})(window);
