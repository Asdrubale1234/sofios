#!/usr/bin/env python3
"""Sofi Labs: prepara le cartelle pronte da caricare, una per ogni social, nelle misure giuste.
Uso:  python3 tools/social.py CARTELLA_SCELTE CARTELLA_USCITA
CARTELLA_SCELTE contiene i file scelti (nomi fissi):
   icona.png (quadrata) · marchio-scuro.png e marchio-chiaro.png (simbolo + scritta, sfondo uniforme) · sigillo-scuro.png e sigillo-chiaro.png (facoltativi)
   banner-youtube.jpg (16:9) · banner-largo-scuro.jpg e banner-largo-chiaro.jpg (21:9) · sito-header.jpg (21:9) · miniatura.jpg (16:9)
   verticale.jpg (9:16, per storie e post)   -- se un file manca, si salta cio' che lo usa."""
import os, sys
import numpy as np
from PIL import Image, ImageFilter
SC, OUT = sys.argv[1], sys.argv[2]
def apri(n):
    p = os.path.join(SC, n)
    return Image.open(p).convert("RGBA") if os.path.exists(p) else None
def togli_sfondo(im, tol=26):
    """il marchio nasce su sfondo uniforme: il colore degli angoli diventa trasparente (con bordo morbido)"""
    a = np.asarray(im.convert("RGB")).astype(float); ang = np.median(np.array([a[2, 2], a[2, -3], a[-3, 2], a[-3, -3]]), axis=0)
    d = np.sqrt(((a - ang) ** 2).sum(axis=2)); al = np.clip((d - tol) / 28.0, 0, 1)
    out = im.convert("RGBA"); out.putalpha(Image.fromarray((al * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)))
    bb = out.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()
    return out.crop(bb) if bb else out
def riempi(im, w, h, cx=0.5, cy=0.5):
    """ritaglia nel rapporto giusto e porta alla misura"""
    r = w / h; iw, ih = im.size
    if iw / ih > r: nw = int(ih * r); x = int((iw - nw) * cx); im = im.crop((x, 0, x + nw, ih))
    else: nh = int(iw / r); y = int((ih - nh) * cy); im = im.crop((0, y, iw, y + nh))
    return im.resize((w, h), Image.LANCZOS)
def metti(base, logo, largo=None, alto=None, pos=(0.5, 0.5)):
    """mette il logo (trasparente) sul fondale: larghezza o altezza massima, posizione in frazioni"""
    s = min((largo or 10**6) / logo.width, (alto or 10**6) / logo.height); l = logo.resize((max(1, int(logo.width * s)), max(1, int(logo.height * s))), Image.LANCZOS)
    b = base.convert("RGBA"); b.alpha_composite(l, (int((b.width - l.width) * pos[0]), int((b.height - l.height) * pos[1]))); return b.convert("RGB")
def salva(im, cart, nome, q=92):
    d = os.path.join(OUT, cart); os.makedirs(d, exist_ok=True); p = os.path.join(d, nome)
    (im.convert("RGB") if nome.endswith(".jpg") else im).save(p, quality=q, optimize=True); print("  ", cart + "/" + nome, "x".join(map(str, im.size)))
icona = apri("icona.png")
mar_s, mar_c = apri("marchio-scuro.png"), apri("marchio-chiaro.png")
mar_s = togli_sfondo(mar_s) if mar_s else None; mar_c = togli_sfondo(mar_c) if mar_c else None
sig_s, sig_c = apri("sigillo-scuro.png"), apri("sigillo-chiaro.png")
sig_s = togli_sfondo(sig_s) if sig_s else None; sig_c = togli_sfondo(sig_c) if sig_c else None
yt, larg_s, larg_c, head, mini, vert = (apri(n) for n in ("banner-youtube.jpg", "banner-largo-scuro.jpg", "banner-largo-chiaro.jpg", "sito-header.jpg", "miniatura.jpg", "verticale.jpg"))
def pieno(n):
    """foto profilo: l'icona riempie tutto il quadrato (i social la tagliano a cerchio o a quadrato): via gli angoli arrotondati"""
    if not icona: return None
    w, h = icona.size; m = int(w * 0.075); return icona.crop((m, m, w - m, h - m)).resize((n, n), Image.LANCZOS)
def tonda(n, raggio=0.225):
    """icona con gli angoli arrotondati trasparenti (favicon, icona dei prodotti)"""
    if not icona: return None
    from PIL import ImageDraw
    im = icona.resize((n, n), Image.LANCZOS).convert("RGBA"); k = 4; m = Image.new("L", (n * k, n * k), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, n * k - 1, n * k - 1), int(n * k * raggio), fill=255); im.putalpha(m.resize((n, n), Image.LANCZOS)); return im
def quad(n): return pieno(n)
print("Preparo le cartelle in", OUT)
for cart, n, nome in (("YouTube", 800, "foto-canale-800x800.png"), ("Facebook", 1080, "foto-profilo-1080x1080.png"), ("Instagram", 1080, "foto-profilo-1080x1080.png"), ("X", 400, "foto-profilo-400x400.png"),
                      ("LinkedIn", 400, "logo-azienda-400x400.png"), ("TikTok", 200, "foto-profilo-200x200.png"), ("Telegram", 512, "foto-canale-512x512.png"), ("WhatsApp", 640, "foto-profilo-640x640.png")):
    if icona: salva(quad(n), cart, nome)
# YouTube
if yt and mar_s:
    salva(metti(riempi(yt, 2560, 1440), mar_s, largo=1100, alto=360), "YouTube", "banner-2560x1440.jpg")
if icona: salva(tonda(150), "YouTube", "filigrana-150x150.png")
if mini: salva(riempi(mini, 1280, 720), "YouTube", "miniatura-modello-1280x720.jpg")
# Facebook, X, LinkedIn: copertine (il logo sta al centro e piccolo: il telefono taglia i lati)
if larg_s and mar_s:
    salva(metti(riempi(larg_s, 1640, 624), mar_s, largo=620, alto=250), "Facebook", "copertina-1640x624.jpg")
    salva(metti(riempi(larg_s, 1500, 500), mar_s, largo=560, alto=220), "X", "intestazione-1500x500.jpg")
    salva(metti(riempi(larg_s, 1584, 396), mar_s, largo=520, alto=190), "LinkedIn", "copertina-personale-1584x396.jpg")
    salva(metti(riempi(larg_s, 1128, 191, cy=0.8), mar_s, largo=340, alto=110), "LinkedIn", "copertina-azienda-1128x191.jpg")
# Instagram: post e storia (sfondo verticale se c'e', altrimenti il largo)
fond = vert or yt
if fond and icona:
    salva(metti(riempi(fond, 1080, 1350), tonda(420), largo=420), "Instagram", "post-1080x1350.jpg")
    salva(metti(riempi(fond, 1080, 1920), tonda(480), largo=480, pos=(0.5, 0.42)), "Instagram", "storia-1080x1920.jpg")
# Sito
if icona:
    for n in (32, 180, 512): salva(tonda(n), "Sito", "favicon-%dx%d.png" % (n, n))
if head and mar_s:
    salva(metti(riempi(head, 2560, 1100), mar_s, largo=1000, alto=420, pos=(0.5, 0.5)), "Sito", "intestazione-2560x1100.jpg")
if (larg_s or head) and mar_s:
    salva(metti(riempi(head or larg_s, 1200, 630), mar_s, largo=760, alto=300), "Sito", "anteprima-condivisione-1200x630.jpg")
for nome, im in (("logo-orizzontale-scuro.png", mar_s), ("logo-orizzontale-chiaro.png", mar_c), ("sigillo-prodotto-scuro.png", sig_s), ("sigillo-prodotto-chiaro.png", sig_c)):
    if im: salva(im, "Prodotti-e-sito", nome)
if icona: salva(tonda(1024), "Prodotti-e-sito", "icona-1024x1024.png")
print("Fatto.")
