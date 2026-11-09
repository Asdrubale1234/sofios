// Cassaforte Password - dentro le pagine: pulsante accanto ai campi password, riempimento e proposta di salvataggio.
(() => {
  if (window.__cassaforte) return; window.__cassaforte = true;
  const BLU = "#0b2740", GIALLO = "#ffd479";
  const logo = browser.runtime.getURL("logo.png");
  let menu = null;

  const visibile = el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el); return r.width > 20 && r.height > 10 && s.visibility !== "hidden" && s.display !== "none"; };
  const campiPassword = () => [...document.querySelectorAll('input[type="password"]')].filter(visibile);
  function campoUtente(pw) {
    const tutti = [...document.querySelectorAll('input:not([type]), input[type="text"], input[type="email"], input[type="tel"]')].filter(visibile);
    let scelto = null;
    for (const c of tutti) { if (c.compareDocumentPosition(pw) & Node.DOCUMENT_POSITION_FOLLOWING) scelto = c; }
    return scelto;
  }
  function imposta(el, valore) {
    const p = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value");
    p.set.call(el, valore);
    el.dispatchEvent(new Event("input", { bubbles: true })); el.dispatchEvent(new Event("change", { bubbles: true }));
  }
  function riempi(utente, password) {
    const pw = campiPassword()[0]; if (!pw) return;
    const u = campoUtente(pw); if (u && utente) imposta(u, utente);
    imposta(pw, password);
  }
  browser.runtime.onMessage.addListener(m => { if (m.op === "riempi") riempi(m.utente, m.password); });

  function chiudiMenu() { if (menu) { menu.remove(); menu = null; } }
  function stileBase(el) { el.style.cssText = "all:initial;font-family:Inter,system-ui,sans-serif;"; }
  function apriMenu(campo) {
    chiudiMenu();
    const r = campo.getBoundingClientRect();
    menu = document.createElement("div"); menu.id = "cassaforte-menu";
    menu.style.cssText = `position:fixed;z-index:2147483647;left:${Math.max(8, r.left)}px;top:${r.bottom + 4}px;min-width:${Math.max(240, r.width)}px;max-width:360px;background:${BLU};color:#e6f1ff;border-radius:12px;box-shadow:0 8px 28px rgba(0,0,0,.4);padding:8px;font:13px Inter,system-ui,sans-serif;`;
    const t = document.createElement("div"); t.textContent = "Cassaforte Password"; t.style.cssText = "font-weight:700;padding:4px 8px 6px;color:#fff;"; menu.appendChild(t);
    const corpo = document.createElement("div"); corpo.textContent = "Cerco…"; corpo.style.cssText = "padding:4px 8px;color:#8fb3d4;"; menu.appendChild(corpo);
    document.documentElement.appendChild(menu);
    browser.runtime.sendMessage({ op: "cerca" }).then(r => {
      corpo.textContent = ""; corpo.style.padding = "0";
      if (!r.ok) {
        const msg = document.createElement("div"); msg.style.cssText = "padding:4px 8px 8px;";
        msg.textContent = r.errore === "negato" ? "Hai scelto di non consentire al browser. Apri la Cassaforte per cambiare idea." : "La Cassaforte è chiusa. Aprila e inserisci la password principale.";
        corpo.appendChild(msg); corpo.appendChild(bottone("Apri Cassaforte", () => { browser.runtime.sendMessage({ op: "apri" }); chiudiMenu(); })); return;
      }
      if (!r.voci.length) { const n = document.createElement("div"); n.textContent = "Nessuna password salvata per questo sito."; n.style.cssText = "padding:4px 8px 8px;color:#8fb3d4;"; corpo.appendChild(n); return; }
      for (const v of r.voci) {
        const b = bottone((v.titolo || "(senza nome)") + (v.utente ? " — " + v.utente : ""), () => {
          browser.runtime.sendMessage({ op: "compila", id: v.id }).then(x => { if (x.ok) riempi(x.utente, x.password); chiudiMenu(); });
        }, true); b.dataset.id = v.id; corpo.appendChild(b);
      }
    });
  }
  function bottone(testo, f, lista) {
    const b = document.createElement("button"); b.type = "button"; b.textContent = testo;
    b.style.cssText = lista ? "display:block;width:100%;text-align:left;background:transparent;color:#e6f1ff;border:0;border-radius:8px;padding:8px;font:13px Inter,system-ui,sans-serif;cursor:pointer;"
                            : `display:block;margin:4px 8px;background:${GIALLO};color:${BLU};border:0;border-radius:9px;padding:7px 14px;font:700 13px Inter,system-ui,sans-serif;cursor:pointer;`;
    b.addEventListener("mouseenter", () => { if (lista) b.style.background = "#1e6fa8"; }); b.addEventListener("mouseleave", () => { if (lista) b.style.background = "transparent"; });
    b.addEventListener("click", e => { e.preventDefault(); e.stopPropagation(); f(); }); return b;
  }

  function aggiungiPulsanti() {
    for (const pw of campiPassword()) {
      if (pw.dataset.cassaforte) continue; pw.dataset.cassaforte = "1";
      const p = document.createElement("img"); p.src = logo; p.className = "cassaforte-pulsante"; p.title = "Cassaforte Password";
      p.style.cssText = "position:fixed;z-index:2147483646;width:20px;height:20px;border-radius:5px;cursor:pointer;";
      const posiziona = () => { const r = pw.getBoundingClientRect(); p.style.left = (r.right - 26) + "px"; p.style.top = (r.top + (r.height - 20) / 2) + "px"; p.style.display = visibile(pw) ? "block" : "none"; };
      posiziona(); addEventListener("scroll", posiziona, true); addEventListener("resize", posiziona);
      new ResizeObserver(posiziona).observe(pw);
      p.addEventListener("mousedown", e => { e.preventDefault(); e.stopPropagation(); apriMenu(pw); });
      document.documentElement.appendChild(p);
    }
  }
  aggiungiPulsanti(); new MutationObserver(aggiungiPulsanti).observe(document.documentElement, { childList: true, subtree: true });
  document.addEventListener("mousedown", e => { if (menu && !menu.contains(e.target) && !(e.target.className || "").toString().includes("cassaforte-pulsante")) chiudiMenu(); });

  // ricorda un modulo con password inviato, per proporre il salvataggio nella pagina dopo
  document.addEventListener("submit", e => {
    const f = e.target; if (!(f instanceof HTMLFormElement)) return;
    const pw = [...f.querySelectorAll('input[type="password"]')].find(x => x.value);
    if (!pw) return;
    const u = campoUtente(pw);
    browser.runtime.sendMessage({ op: "proposta", utente: u ? u.value : "", password: pw.value });
  }, true);

  // pagina nuova: c'e' una proposta in sospeso?
  if (!campiPassword().length) {
    browser.runtime.sendMessage({ op: "proposta?" }).then(r => {
      if (!r || !r.ok || !r.proposta) return;
      const b = document.createElement("div"); b.id = "cassaforte-proposta";
      b.style.cssText = `position:fixed;z-index:2147483647;right:16px;top:16px;max-width:340px;background:${BLU};color:#e6f1ff;border-radius:14px;box-shadow:0 8px 28px rgba(0,0,0,.4);padding:14px;font:13px Inter,system-ui,sans-serif;`;
      const t = document.createElement("div"); t.style.cssText = "margin-bottom:10px;line-height:1.4;";
      const nome = r.proposta.utente ? " di «" + r.proposta.utente + "»" : "";
      t.textContent = r.proposta.stato === "aggiornata" ? "Vuoi aggiornare nella Cassaforte la password" + nome + "?" : "Vuoi salvare nella Cassaforte la password" + nome + "?";
      const riga = document.createElement("div"); riga.style.cssText = "display:flex;gap:8px;";
      riga.appendChild(bottone("Salva", () => { browser.runtime.sendMessage({ op: "salva" }).then(x => { t.textContent = x && x.ok ? "Fatto: password salvata." : "Non sono riuscito a salvare: apri e sblocca la Cassaforte."; riga.remove(); setTimeout(() => b.remove(), 2500); }); }));
      riga.appendChild(bottone("Non ora", () => { browser.runtime.sendMessage({ op: "scarta" }); b.remove(); }));
      b.appendChild(t); b.appendChild(riga); document.documentElement.appendChild(b);
    });
  }
})();
