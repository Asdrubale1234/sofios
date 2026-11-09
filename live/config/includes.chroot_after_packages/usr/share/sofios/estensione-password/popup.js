const c = document.getElementById("c");
function bott(t, f, p) { const b = document.createElement("button"); b.textContent = t; if (p) b.className = "p"; b.onclick = f; return b; }
browser.tabs.query({ active: true, currentWindow: true }).then(([scheda]) => {
  if (!scheda || !/^https?:/.test(scheda.url || "")) { c.textContent = "Apri una pagina web per usare le password."; return; }
  browser.runtime.sendMessage({ op: "cerca", scheda: scheda.id, url: scheda.url }).then(r => {
    c.textContent = "";
    if (!r.ok) {
      const t = document.createElement("div"); t.className = "t"; t.textContent = r.errore === "negato" ? "Il browser non è ancora consentito: apri la Cassaforte." : "La Cassaforte è chiusa."; c.appendChild(t);
      c.appendChild(bott("Apri Cassaforte", () => { browser.runtime.sendMessage({ op: "apri" }); window.close(); }, true)); return;
    }
    if (!r.voci.length) { const t = document.createElement("div"); t.className = "t"; t.textContent = "Nessuna password salvata per questo sito."; c.appendChild(t); }
    for (const v of r.voci) c.appendChild(bott((v.titolo || "(senza nome)") + (v.utente ? " — " + v.utente : ""), () => {
      browser.runtime.sendMessage({ op: "riempi-da-popup", scheda: scheda.id, url: scheda.url, id: v.id }).then(() => window.close());
    }));
    c.appendChild(bott("Apri Cassaforte", () => { browser.runtime.sendMessage({ op: "apri" }); window.close(); }, true));
  });
});
