#!/usr/bin/env python3
"""Sfondo del tema chiaro: mare di giorno con il sole (pendant del mare con le stelle del tema scuro).
Uso: mare_sole.py [file-uscita.png] [larghezza altezza]   (richiede numpy e Pillow)"""
import sys
import numpy as np
from PIL import Image, ImageFilter
W,H=(int(sys.argv[2]),int(sys.argv[3])) if len(sys.argv) > 3 else (1920,1080); HZ=H//2
y=np.arange(H)[:,None]*np.ones((1,W)); x=np.ones((H,1))*np.arange(W)[None,:]
def mix(a,b,t): 
    t=np.clip(t,0,1)[...,None]; return np.array(a)*(1-t)+np.array(b)*t
img=np.zeros((H,W,3))
# cielo: azzurro alto, quasi bianco caldo all'orizzonte
cielo=mix((150,200,245),(238,246,252),(y/HZ)**1.4)
# sole + alone
sx,sy,r=1430,300,62
d=np.hypot(x-sx,y-sy)
alone=np.exp(-(d/230)**2)[...,None]
cielo=cielo*(1-0.55*alone)+np.array((255,236,170))*0.55*alone
alone2=np.exp(-(d/110)**2)[...,None]
cielo=cielo*(1-0.7*alone2)+np.array((255,244,200))*0.7*alone2
disco=np.clip((r-d)/2.5+0.5,0,1)[...,None]
cielo=cielo*(1-disco)+np.array((255,250,225))*disco
img[:HZ]=cielo[:HZ]
# mare: 4 strati con onde, dal turchese chiaro (orizzonte) al blu (vicino)
mare=mix((120,200,225),(40,120,185),(y-HZ)/(H-HZ))
img[HZ:]=mare[HZ:]
cols=[(95,185,220),(70,160,210),(50,135,195),(35,110,175)]
bases=[630,715,815,925]
rng=np.random.default_rng(3)
for k,(c,b) in enumerate(zip(cols,bases)):
    ph=rng.uniform(0,6); 
    curva=b+14*np.sin(x[0]/310+ph)+8*np.sin(x[0]/137+ph*2)
    m=(y>=curva[None,:])
    strato=mix(c,tuple(int(v*0.88) for v in c),(y-b)/(H-b))
    img=np.where(m[...,None],strato,img)
    fil=np.abs(y-curva[None,:])<1.3
    img=np.where(fil[...,None],img*0.8+np.array((255,255,255))*0.2,img)
# riflesso del sole sul mare: striscia di luce che si allarga verso il basso
for yy in range(HZ,H):
    t=(yy-HZ)/(H-HZ); larg=40+t*170
    prof=np.exp(-((np.arange(W)-sx)/larg)**2)
    onda=0.5+0.5*np.sin(yy/5.0+np.arange(W)/60.0)
    f=prof*(0.55*(1-t*0.6))*(0.35+0.65*onda)
    img[yy]=img[yy]*(1-f[:,None])+np.array((255,244,205))*f[:,None]
out=Image.fromarray(np.clip(img,0,255).astype('uint8'))
out.save(sys.argv[1] if len(sys.argv) > 1 else 'mare_sole.png')
