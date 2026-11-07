# Crea lo sfondo del menu di avvio (640x480): mare scuro, logo e nome SofiOS
from PIL import Image, ImageDraw, ImageFont
import sys
W,H=640,480
top=(11,39,64); bot=(5,16,34)
im=Image.new('RGB',(W,H))
d=ImageDraw.Draw(im)
for y in range(H):
    t=y/(H-1); d.line([(0,y),(W,y)],fill=tuple(int(top[i]+(bot[i]-top[i])*t) for i in range(3)))
logo=Image.open('docs/logo-sofios.png').convert('RGBA').resize((112,112),Image.LANCZOS)
im.paste(logo,((W-112)//2,22),logo)
f=ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-SemiBold.otf',30)
t='SofiOS'; w=d.textlength(t,font=f)
d.text(((W-w)/2,140),t,font=f,fill=(230,241,255))
im.save(sys.argv[1])
