// Cassaforte Password - parte "di sfondo": parla con il programma Cassaforte Password tramite il collegamento locale.
const HOST = "org.sofios.cassaforte";
const proposte = {};   // schede -> password appena inviata in un modulo (in memoria, mai su disco)

function chiedi(r) {
  return browser.runtime.sendNativeMessage(HOST, r).catch(() => ({ ok: false, errore: "non_aperta" }));
}

browser.runtime.onMessage.addListener((m, mittente) => {
  const scheda = mittente.tab ? mittente.tab.id : m.scheda;
  const url = mittente.tab ? mittente.tab.url : m.url;
  switch (m.op) {
    case "cerca": return chiedi({ op: "cerca", url });
    case "compila": return chiedi({ op: "compila", url, id: m.id });
    case "apri": return chiedi({ op: "apri" });
    case "proposta":      // il contenuto ha visto un modulo con password: ricordo per un minuto
      proposte[scheda] = { utente: m.utente, password: m.password, url, quando: Date.now() };
      return Promise.resolve({ ok: true });
    case "proposta?": {
      const p = proposte[scheda];
      if (!p || Date.now() - p.quando > 60000) { delete proposte[scheda]; return Promise.resolve({ ok: true, proposta: null }); }
      return chiedi({ op: "controlla", url: p.url, utente: p.utente, password: p.password })
        .then(r => (r.ok && r.stato !== "uguale") ? { ok: true, proposta: { utente: p.utente, stato: r.stato } } : { ok: true, proposta: null });
    }
    case "salva": {
      const p = proposte[scheda]; delete proposte[scheda];
      if (!p) return Promise.resolve({ ok: false });
      return chiedi({ op: "salva", url: p.url, utente: p.utente, password: p.password });
    }
    case "scarta": delete proposte[scheda]; return Promise.resolve({ ok: true });
    case "riempi-da-popup":
      return chiedi({ op: "compila", url: m.url, id: m.id }).then(r => {
        if (r.ok) browser.tabs.sendMessage(m.scheda, { op: "riempi", utente: r.utente, password: r.password });
        return { ok: r.ok };
      });
  }
});
browser.tabs.onRemoved.addListener(id => { delete proposte[id]; });
