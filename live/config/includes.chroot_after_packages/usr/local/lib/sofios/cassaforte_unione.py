"""Unione di due cassaforti (formato KeePass) modificate su dispositivi diversi. Regola uguale su PC e tablet:
 1. Si lavora per voce, riconosciuta dal suo codice unico (UUID), non dal nome.
 2. Se una voce c'e' solo in una cassaforte: si aggiunge all'altra, a meno che l'altra non l'abbia eliminata DOPO l'ultima modifica.
 3. Se una voce e' in tutte e due: vince l'ultima modifica; la versione che perde NON si butta, finisce nella cronologia della voce.
 4. Le voci eliminate restano eliminate (elenco DeletedObjects). Una voce modificata dopo l'eliminazione torna in vita.
 5. Mai perdere una voce: nel dubbio si tiene.
 6. Il risultato si salva con copia di sicurezza (.bak) e scrittura atomica (file temporaneo e poi rinomina)."""
import base64, copy, os, shutil
from pykeepass import PyKeePass

def _b64(u): return base64.b64encode(u.bytes).decode()

def _eliminati(kp):
    out = {}
    for d in kp.tree.getroot().findall("./Root/DeletedObjects/DeletedObject"):
        try: out[d.findtext("UUID")] = kp._decode_time(d.findtext("DeletionTime"))
        except Exception: out[d.findtext("UUID")] = None
    return out

def _nodo_eliminati(kp):
    root = kp.tree.getroot().find("./Root")
    n = root.find("DeletedObjects")
    if n is None:
        import lxml.etree as E
        n = E.SubElement(root, "DeletedObjects")
    return n

def _gruppo(kp, percorso):
    g = kp.root_group
    for nome in percorso:
        figlio = next((x for x in g.subgroups if x.name == nome), None)
        g = figlio or kp.add_group(g, nome)
    return g

def _versioni(el):
    """le versioni passate (cronologia) di una voce, per data di modifica"""
    h = el.find("History")
    return [] if h is None else list(h.findall("Entry"))

def _tempo(kp, el):
    t = el.find("Times/LastModificationTime")
    try: return kp._decode_time(t.text)
    except Exception: return None

def _con_cronologia(kp, vincente_el, perdente_el):
    """copia della voce vincente, con in cronologia la sua storia piu' la versione perdente"""
    nuovo = copy.deepcopy(vincente_el)
    import lxml.etree as E
    h = nuovo.find("History")
    if h is None: h = E.SubElement(nuovo, "History")
    presenti = {x.findtext("Times/LastModificationTime") for x in h.findall("Entry")}
    vecchia = copy.deepcopy(perdente_el)
    storia_vecchia = vecchia.find("History")
    if storia_vecchia is not None: vecchia.remove(storia_vecchia)
    for v in ([vecchia] + (_versioni(perdente_el) if perdente_el is not None else [])):
        t = v.findtext("Times/LastModificationTime")
        if t not in presenti and t != nuovo.findtext("Times/LastModificationTime"):
            h.append(copy.deepcopy(v)); presenti.add(t)
    return nuovo

def parametri_nuova(kp):
    """parametri di cifratura delle cassaforti NUOVE, uguali su PC e tablet: KDBX 4, AES-256, Argon2d 32 MiB / 4 passaggi / parallelismo 2, gzip.
    Ogni dispositivo apre comunque le cassaforti con parametri diversi (sono scritti nel file)."""
    p = kp.kdbx.header.value.dynamic_header.kdf_parameters.data.dict
    p["M"].value = 32 * 1024 * 1024; p["I"].value = 4; p["P"].value = 2

def elimina_voce(kp, voce):
    """elimina una voce e lo ricorda nell'elenco DeletedObjects, cosi' l'unione non la fa tornare dall'altro dispositivo"""
    import datetime, lxml.etree as E
    u = _b64(voce.uuid); voce.delete()
    nodo = _nodo_eliminati(kp)
    for x in nodo.findall("DeletedObject"):
        if x.findtext("UUID") == u: nodo.remove(x)
    x = E.SubElement(nodo, "DeletedObject"); E.SubElement(x, "UUID").text = u
    E.SubElement(x, "DeletionTime").text = kp._encode_time(datetime.datetime.now(datetime.timezone.utc))

def modificata(voce):
    """da chiamare dopo ogni modifica di una voce: aggiorna la data di ultima modifica, su cui l'unione decide chi vince"""
    voce.touch(modify=True)

def unisci(locale, remoto, password, uscita=None, keyfile=None):
    """unisce la cassaforte `remoto` dentro `locale` e salva in `uscita` (di norma lo stesso file di `locale`). Ritorna un riassunto."""
    L = PyKeePass(locale, password=password, keyfile=keyfile); R = PyKeePass(remoto, password=password, keyfile=keyfile)
    uscita = uscita or locale
    elL = {_b64(e.uuid): e for e in L.entries}; elR = {_b64(e.uuid): e for e in R.entries}
    delL = _eliminati(L); delR = _eliminati(R)
    agg = rim = vinte = tenute = 0
    for u, er in elR.items():
        if u not in elL:
            d = delL.get(u); tr = _tempo(R, er._element)
            if d is not None and tr is not None and d >= tr: continue          # eliminata qui dopo l'ultima modifica
            g = _gruppo(L, er.parentgroup.path)
            g._element.append(copy.deepcopy(er._element)); agg += 1
            delL.pop(u, None)
        else:
            el = elL[u]; tl, tr = _tempo(L, el._element), _tempo(R, er._element)
            if tr is not None and tl is not None and tr > tl:                    # vince il remoto
                g = _gruppo(L, er.parentgroup.path)
                nuovo = _con_cronologia(L, er._element, el._element)
                el._element.getparent().remove(el._element); g._element.append(nuovo); vinte += 1
            else:                                                                  # vince il locale, ma la versione remota resta in cronologia
                if tr is not None and tl is not None and tr < tl:
                    nuovo = _con_cronologia(L, el._element, er._element)
                    if len(_versioni(nuovo)) != len(_versioni(el._element)):
                        el._element.getparent().replace(el._element, nuovo)
                tenute += 1
    for u, el in list(elL.items()):
        if u not in elR:
            d = delR.get(u); tl = _tempo(L, el._element)
            if d is not None and tl is not None and d >= tl:                      # eliminata sull'altro dopo l'ultima modifica
                el._element.getparent().remove(el._element); rim += 1
    # elenco delle eliminate: unione, senza le voci tornate in vita
    nodo = _nodo_eliminati(L); vive = {_b64(e.uuid): e for e in L.entries}
    tutte = dict(delR); tutte.update({k: v for k, v in delL.items() if v is not None and (tutte.get(k) is None or v > tutte[k])})
    for d in list(nodo): nodo.remove(d)
    import lxml.etree as E
    for u, t in tutte.items():
        if u in vive: continue
        x = E.SubElement(nodo, "DeletedObject"); E.SubElement(x, "UUID").text = u
        E.SubElement(x, "DeletionTime").text = L._encode_time(t) if t is not None else ""
    # salvataggio sicuro
    if os.path.exists(uscita): shutil.copy2(uscita, uscita + ".bak")
    tmp = uscita + ".tmp"; L.save(tmp); os.replace(tmp, uscita)
    return {"aggiunte": agg, "rimosse": rim, "vinte_dal_remoto": vinte, "tenute_locali": tenute}


def unisci_conflitti(file, password):
    """unisce le copie «cassaforte.sync-conflict-*.kdbx» create dalla sincronizzazione quando due dispositivi hanno salvato nello stesso momento.
    Le copie unite vanno in Password/.conflitti. Se la password e' diversa, la copia resta dov'e'. Ritorna (unite, non_riuscite)."""
    import glob
    cartella = os.path.dirname(file); unite = non = 0
    for c in sorted(glob.glob(os.path.join(cartella, "cassaforte.sync-conflict-*.kdbx"))):
        try:
            unisci(file, c, password)
            d = os.path.join(cartella, ".conflitti"); os.makedirs(d, exist_ok=True)
            dest = os.path.join(d, os.path.basename(c)); n = 1
            while os.path.exists(dest): dest = os.path.join(d, "%d-%s" % (n, os.path.basename(c))); n += 1
            shutil.move(c, dest); unite += 1
        except Exception:
            non += 1
    return unite, non
