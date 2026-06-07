/*
 * DEV-ONLY panel injector — test the FigureFlow Copilot drawer on a LIVE Odoo
 * (including Odoo Online, where custom modules can't be installed) without
 * publishing the module. Paste this whole file into the browser DevTools
 * console while on your Odoo page. It injects the same drawer + iframe + record
 * detection the OWL systray widget ships, pointed at your LOCAL FigureFlow.
 *
 * Record detection uses Odoo's web client services — turn on Developer Mode
 * (Settings > Developer Tools > Activate, or append ?debug=1) so __WOWL_DEBUG__
 * is exposed. Without it the panel still loads; it just shows "open a record".
 *
 * Mixed content note: an https Odoo page may load an http://localhost iframe —
 * browsers treat localhost as trustworthy, so this is allowed.
 */
(() => {
  const PANEL = "http://localhost:3000/embed/panel"; // ← your local FigureFlow
  const ORIGIN = new URL(PANEL).origin;

  // Re-running just toggles the existing drawer.
  const existing = document.getElementById("ff-toggle");
  if (existing) {
    existing.click();
    return;
  }

  // The real FigureFlow mark (same path as the app sidebar logo).
  const FF_MARK =
    '<svg viewBox="0 0 1024 1024" width="24" height="24" xmlns="http://www.w3.org/2000/svg">' +
    '<g transform="translate(0,1024) scale(0.1,-0.1)" fill="#7c3aed"><path d="M0 5120 l0 ' +
    '-5120 5120 0 5120 0 0 5120 0 5120 -5120 0 -5120 0 0 -5120z m6470 2512 c146 -45 241 ' +
    '-102 335 -204 69 -73 102 -130 142 -243 l28 -80 3 -482 3 -483 -63 39 c-142 89 -339 ' +
    '116 -472 65 -19 -7 -19 1 -14 326 7 377 4 399 -58 463 -53 54 -89 70 -159 71 -80 0 ' +
    '-124 -16 -174 -66 -76 -77 -76 -81 -76 -605 l1 -463 -274 0 -273 0 3 568 c4 553 4 568 ' +
    '25 625 99 263 272 413 548 478 111 26 378 21 475 -9z m-1177 -257 l1 -260 -395 -5 ' +
    'c-385 -5 -395 -6 -436 -28 -77 -41 -138 -117 -157 -197 -4 -16 -7 -170 -7 -342 l1 -311 ' +
    '-113 5 c-89 5 -125 2 -172 -11 -78 -23 -161 -66 -216 -111 l-44 -38 -3 462 c-2 507 0 ' +
    '535 57 672 75 179 244 327 449 394 94 30 142 33 591 31 l443 -1 1 -260z m1379 -1456 ' +
    'c119 -25 224 -102 273 -200 100 -197 17 -437 -186 -534 -86 -41 -160 -52 -247 -36 ' +
    '-129 24 -222 92 -277 204 -99 201 -28 424 167 523 101 51 174 63 270 43z m-812 -22 c0 ' +
    '-1 -11 -31 -24 -67 -81 -222 -246 -376 -456 -424 -49 -12 -141 -16 -375 -17 -170 -1 ' +
    '-346 -5 -391 -9 -119 -11 -207 -61 -263 -148 -55 -87 -55 -91 -56 -682 l0 -545 -273 -3 ' +
    '-273 -2 3 657 3 658 24 70 c71 211 196 357 384 450 130 63 124 63 950 64 411 1 747 0 ' +
    '747 -2z m100 -1322 l0 -575 -270 0 -270 0 0 560 c0 308 3 559 8 558 4 0 16 3 27 8 18 8 ' +
    '17 9 -10 15 -16 4 93 7 243 8 l272 1 0 -575z"/></g></svg>';

  const btn = document.createElement("button");
  btn.id = "ff-toggle";
  btn.title = "FigureFlow";
  btn.innerHTML = FF_MARK;
  Object.assign(btn.style, {
    position: "fixed", top: "40%", right: "0", zIndex: "2147483647",
    width: "44px", height: "48px", padding: "0",
    display: "flex", alignItems: "center", justifyContent: "center",
    background: "#fff", border: "1px solid rgba(0,0,0,.1)", borderRight: "0",
    borderRadius: "10px 0 0 10px", cursor: "pointer",
    boxShadow: "-2px 2px 12px rgba(0,0,0,.15)",
  });
  document.body.appendChild(btn);

  const drawer = document.createElement("div");
  Object.assign(drawer.style, {
    position: "fixed", top: "0", right: "0", height: "100vh",
    width: "400px", maxWidth: "92vw", zIndex: "2147483646",
    boxShadow: "-8px 0 28px rgba(0,0,0,.35)", background: "#0e1a2b",
    transform: "translateX(100%)", transition: "transform .18s ease",
  });
  const frame = document.createElement("iframe");
  frame.src = PANEL;
  frame.allow = "clipboard-write";
  Object.assign(frame.style, { width: "100%", height: "100%", border: "0" });
  drawer.appendChild(frame);
  document.body.appendChild(drawer);

  let open = false;
  let ready = false;
  let lastKey = null;

  btn.onclick = () => {
    open = !open;
    drawer.style.transform = open ? "translateX(0)" : "translateX(100%)";
    if (open) { lastKey = null; post(); }
  };

  function currentRecord() {
    try {
      const c = window.odoo?.__WOWL_DEBUG__?.root?.env?.services?.action
        ?.currentController;
      const p = c?.props;
      if (p?.resModel && p?.resId) {
        return {
          source: "odoo",
          model: p.resModel,
          id: String(p.resId),
          instanceHint: { host: location.host, db: window.odoo?.info?.db || "" },
        };
      }
    } catch (e) {
      /* debug mode off — fall through */
    }
    return null;
  }

  function post() {
    if (!ready) return;
    const r = currentRecord();
    const key = r ? `${r.model}:${r.id}` : "none";
    if (key === lastKey) return;
    lastKey = key;
    frame.contentWindow?.postMessage({ type: "FF_RECORD", record: r }, ORIGIN);
  }

  window.addEventListener("message", (e) => {
    if (e.origin !== ORIGIN) return;
    if (e.data?.type === "FF_EMBED_READY") {
      ready = true;
      lastKey = null;
      post();
    }
  });

  setInterval(() => { if (open) post(); }, 1200);
  console.log("[FF] panel injected — click ◆ FF (top-right). Enable Odoo Developer Mode for live record detection.");
})();
