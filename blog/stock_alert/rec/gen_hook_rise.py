#!/usr/bin/env python3
"""상승(신고가) 쇼츠 상단 훅 PNG. 1080x440, 투명. line1: 시장+신고가(초록)+TOP5+📈, line2: 노랑 주차."""
import os
from PIL import Image, ImageDraw, ImageFont
ROOT=os.path.join(os.path.dirname(__file__),'..')
FONT=os.path.join(ROOT,'..','fonts','BlackHanSans-Regular.ttf')
EMOJI='/snap/gnome-42-2204/245/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
OUT=os.path.join(ROOT,'assets','shorts')
W,H=1080,440
WHITE=(248,248,245); GREEN=(56,190,110); YELLOW=(255,216,61); STK=(20,20,20)
def emoji_img(ch,px):
    f=ImageFont.truetype(EMOJI,109)
    im=Image.new('RGBA',(140,140),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.text((70,70),ch,font=f,anchor='mm',embedded_color=True)
    bb=im.getbbox(); im=im.crop(bb)
    s=px/im.height; return im.resize((int(im.width*s),px),Image.LANCZOS)
def make(fname, segs, line2, emoji, s1=74, s2=60):
    img=Image.new('RGBA',(W,H),(0,0,0,0)); dr=ImageDraw.Draw(img)
    f1=ImageFont.truetype(FONT,s1); f2=ImageFont.truetype(FONT,s2)
    em=emoji_img(emoji,int(s1*0.86))
    # line1 총폭
    widths=[dr.textlength(t,font=f1) for t,_ in segs]
    gap=14; tot=sum(widths)+gap+em.width
    x=(W-tot)//2; y1=120
    for (t,col),w in zip(segs,widths):
        dr.text((x,y1),t,font=f1,fill=col,stroke_width=8,stroke_fill=STK,anchor='lm')
        x+=w
    img.alpha_composite(em,(int(x+gap),int(y1-em.height//2)))
    # line2
    dr.text((W//2,y1+96),line2,font=f2,fill=YELLOW,stroke_width=7,stroke_fill=STK,anchor='mm')
    img.save(os.path.join(OUT,fname)); print(fname, img.size)
make('hook_US_rise.png', [("미국 주식 ",WHITE),("신고가",GREEN),(" TOP5",WHITE)], "2026년 week 30", "📈")
make('hook_KR_rise.png', [("한국 주식 ",WHITE),("신고가",GREEN),(" TOP3",WHITE)], "2026년 week 30", "📈")
make('hook_EU_rise.png', [("유럽 주식 ",WHITE),("신고가",GREEN),(" TOP5",WHITE)], "2026년 week 30", "📈")
