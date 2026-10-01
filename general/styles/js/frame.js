/*
 * frame.js: child side of PP.embed(). When the page runs inside an iframe it
 * adds .is-embedded to <html> (hides the masthead) and reports its height to
 * the parent so the frame grows to fit, with no scrollbars.
 */
(function (global) {
  "use strict";
  if (global.parent === global) return;
  document.documentElement.classList.add("is-embedded");
  let last = 0;
  const report = () => {
    const height = Math.ceil(document.documentElement.scrollHeight);
    if (height === last) return;
    last = height;
    global.parent.postMessage({ type: "pp:resize", height, href: global.location.href }, "*");
  };
  new ResizeObserver(report).observe(document.documentElement);
  global.addEventListener("load", report);
})(window);
