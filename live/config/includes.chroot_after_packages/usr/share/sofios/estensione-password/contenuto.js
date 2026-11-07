// Password di SofiOS: quando un sito chiede una password, propone l'app Password.
(function () {
  "use strict";
  var api = (typeof browser !== "undefined" ? browser : chrome);
  var bolla = null;
  var campoAttuale = null;

  function creaBolla() {
    var host = document.createElement("div");
    host.style.cssText = "all:initial;position:absolute;z-index:2147483647;";
    var ombra = host.attachShadow({ mode: "closed" });
    ombra.innerHTML =
      '<style>' +
      '.b{box-sizing:border-box;width:300px;background:#0b2740;color:#e6f1ff;border:1px solid #1e4f7c;' +
      'border-radius:14px;padding:12px 14px;font:13px/1.35 Inter,system-ui,sans-serif;' +
      'box-shadow:0 10px 30px rgba(0,0,0,.35);display:flex;gap:12px;align-items:flex-start}' +
      'img{width:40px;height:40px;border-radius:10px;flex:none}' +
      '.t{font-weight:700;color:#ffd479;margin-bottom:2px;font-size:13px}' +
      '.d{color:#b9d3ee;margin-bottom:8px}' +
      'button{font:600 12px Inter,system-ui,sans-serif;border:0;border-radius:8px;padding:6px 12px;cursor:pointer}' +
      '.s{background:#ffd479;color:#0b2740}.n{background:#12365a;color:#e6f1ff;margin-left:6px}' +
      '</style>' +
      '<div class="b"><img alt="">' +
      '<div><div class="t">Password di SofiOS</div>' +
      '<div class="d">Cerca o salva questa password nella tua cassaforte.</div>' +
      '<button class="s">Apri Password</button><button class="n">Non ora</button></div></div>';
    ombra.querySelector("img").src = api.runtime.getURL("logo.png");
    ombra.querySelector(".n").addEventListener("click", chiudi);
    ombra.querySelector(".s").addEventListener("click", function () {
      try { api.runtime.sendMessage({ azione: "apri-password", sito: location.hostname }); } catch (e) {}
      chiudi();
    });
    return host;
  }

  function chiudi() {
    if (bolla && bolla.parentNode) bolla.parentNode.removeChild(bolla);
    bolla = null;
  }

  function mostra(campo) {
    if (bolla && campoAttuale === campo) return;
    chiudi();
    campoAttuale = campo;
    bolla = creaBolla();
    var r = campo.getBoundingClientRect();
    bolla.style.left = (window.scrollX + r.left) + "px";
    bolla.style.top = (window.scrollY + r.bottom + 8) + "px";
    document.documentElement.appendChild(bolla);
  }

  document.addEventListener("focusin", function (e) {
    var t = e.target;
    if (t && t.tagName === "INPUT" && t.type === "password") mostra(t);
  }, true);
  document.addEventListener("mousedown", function (e) {
    if (bolla && e.target !== campoAttuale && !bolla.contains(e.target)) chiudi();
  }, true);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") chiudi(); }, true);
})();
