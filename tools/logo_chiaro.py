#!/usr/bin/env python3
"""Versione chiara del logo SofiOS (cielo chiaro, stesso faro e stessa onda). Uso: logo_chiaro.py docs/logo-sofios.png docs/logo-sofios-chiaro.png"""
import sys
import numpy as np
from PIL import Image
a = np.asarray(Image.open(sys.argv[1]).convert("RGBA")).astype(float); rgb = a[..., :3]; al = a[..., 3:]
H = rgb.shape[0]
lum = rgb.mean(axis=2, keepdims=True)
y = np.linspace(0, 1, H)[:, None, None]
cielo = np.array([214, 234, 253.]) * (1 - y) + np.array([150, 226, 236.]) * y
d = np.clip(1 - lum / 175, 0, 1) ** 0.8
rosso = np.clip((rgb[..., 0:1] - rgb[..., 2:3] - 25) / 50, 0, 1)      # il rosso del faro resta
d = d * (1 - rosso)
d = d * (1 - 0.2 * np.clip((y - 0.72) / 0.2, 0, 1))
out = rgb * (1 - d) + cielo * d
Image.fromarray(np.concatenate([np.clip(out, 0, 255), al], axis=2).astype(np.uint8), "RGBA").save(sys.argv[2], optimize=True)
