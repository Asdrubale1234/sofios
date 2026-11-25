"""Lo stile delle icone colorate di SofiOS («Apple»): quadrato morbido con sfumatura, filo di luce, riflesso in alto e simbolo bianco con ombra leggera."""
PALETTE = {"blu": ("#4da3ff", "#0a6cdf"), "azzurro": ("#7ad7ff", "#0a84ff"), "verde": ("#4be06a", "#1f9d40"), "arancio": ("#ffc040", "#ff8a00"),
           "rosa": ("#ff6fa0", "#ff2d55"), "viola": ("#c27bff", "#7a3fe0"), "petrolio": ("#5fd0d8", "#1d8f9a"), "rosso": ("#ff6b60", "#ff3b30"), "grigio": ("#a2a2a8", "#636366")}

def _tinta(colore):
    """sceglie la famiglia di colore piu' vicina a un colore #rrggbb (quelli vecchi delle icone)"""
    import colorsys
    c = colore.lstrip("#"); r, g, b = (int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)); h, l, s = colorsys.rgb_to_hls(r, g, b); h *= 360
    if s < 0.18: return "grigio"
    if h < 15 or h >= 345: return "rosso"
    if h < 45: return "arancio"
    if h < 70: return "arancio"
    if h < 165: return "verde"
    if h < 195: return "petrolio"
    if h < 215: return "azzurro"
    if h < 255: return "blu"
    if h < 300: return "viola"
    return "rosa"

def quadrato(colore_a, glifo):
    a, b = PALETTE[_tinta(colore_a)]
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="128" height="128">'
      '<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>'
      '<linearGradient id="v" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".28"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
      '<linearGradient id="b" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>'
      '<rect width="24" height="24" rx="5.4" fill="url(#g)"/>'
      '<path d="M0,12 V5.4 A5.4,5.4 0 0 1 5.4,0 H18.6 A5.4,5.4 0 0 1 24,5.4 V12 Z" fill="url(#v)"/>'
      '<rect x="0.12" y="0.12" width="23.76" height="23.76" rx="5.3" fill="none" stroke="url(#b)" stroke-width="0.25"/>'
      '<g transform="translate(5.28 5.55) scale(0.56)" fill="none" stroke="#000" stroke-opacity=".22" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">%s</g>'
      '<g transform="translate(5.28 5.28) scale(0.56)" fill="none" stroke="#fff" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">%s</g></svg>') % (a, b, glifo, glifo)
