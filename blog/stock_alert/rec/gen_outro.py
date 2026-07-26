#!/usr/bin/env python3
"""쇼츠 엔드카드(9:16): 배투실 마크 + '매주 업데이트' + 구독 CTA."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT=os.path.join(os.path.dirname(__file__),'..')
FONT=os.path.join(ROOT,'..','fonts','BlackHanSans-Regular.ttf')
EMOJI='/snap/gnome-42-2204/245/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
OUT=os.path.join(ROOT,'assets','shorts')
BATU=os.path.join(OUT,'batusil_label.png')
W,H=1080,1920
YELLOW=(255,216,61); WHITE=(245,245,242); RED=(214,58,48); STK=(18,18,18); INK=(28,24,20)
def emoji(ch,px):
    f=ImageFont.truetype(EMOJI,109); im=Image.new('RGBA',(140,140),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.text((70,70),ch,font=f,anchor='mm',embedded_color=True); im=im.crop(im.getbbox())
    s=px/im.height; return im.resize((int(im.width*s),px),Image.LANCZOS)
def ctext(dr,cx,cy,t,f,fill,stk=8):
    dr.text((cx,cy),t,font=f,fill=fill,stroke_width=stk,stroke_fill=STK,anchor='mm')

img=Image.new('RGB',(W,H),(22,20,17))
dr=ImageDraw.Draw(img)
# 은은한 상/하 그라데이션
for y in range(H):
    t=abs(y-H/2)/(H/2); a=int(28*t); dr.line([(0,y),(W,y)],fill=(22+ int(6*t),20+int(4*t),17))
# 배투실 마크(크게, 중앙 상단)
bt=Image.open(BATU).convert('RGBA'); bw=460; bt=bt.resize((bw,int(bt.height*bw/bt.width)),Image.LANCZOS)
img.paste(bt,((W-bw)//2,300),bt)
by=300+bt.height
f_big=ImageFont.truetype(FONT,110); f_mid=ImageFont.truetype(FONT,58); f_small2=ImageFont.truetype(FONT,42)

def cline(cy, segs, font, fill, esize, stroke=7, gap=14):
    """텍스트/이모지 혼합 라인을 가로중앙 배치. segs=[('t',str)|('e',emoji_char)]."""
    parts=[]
    for kind,val in segs:
        if kind=='t': parts.append(('t',val,dr.textlength(val,font=font)))
        else:
            im=emoji(val,esize); parts.append(('e',im,im.width))
    tot=sum(p[2] for p in parts)+gap*(len(parts)-1); x=(W-tot)/2
    for kind,val,w in parts:
        if kind=='t': dr.text((x,cy),val,font=font,fill=fill,stroke_width=stroke,stroke_fill=STK,anchor='lm')
        else: img.paste(val,(int(x),int(cy-val.height/2)),val)
        x+=w+gap

# 헤드라인 + 트로피
cline(by+130, [('t','매주 새로운 랭킹'),('e','🏆')], f_big, YELLOW, 92, stroke=9)
# 서브: 시장 국기
cline(by+265, [('e','🇺🇸'),('t','미국'),('e','🇰🇷'),('t','한국'),('e','🇪🇺'),('t','유럽'),('e','📊'),('t','ETF')],
      f_mid, WHITE, 50, stroke=7, gap=13)
# 데이터 태그라인(차분)
ctext(dr,W//2,by+345,"전고점 · 신고가 데이터 리포트",f_small2,(180,180,178),5)
# 구독 유도(아래 화살표) + 버튼
cline(by+455, [('t','놓치지 않으려면'),('e','👇')], ImageFont.truetype(FONT,46), WHITE, 44, stroke=6)
btn_w,btn_h=560,150; bx0=(W-btn_w)//2; by0=by+520
dr.rounded_rectangle([bx0,by0,bx0+btn_w,by0+btn_h],radius=42,fill=RED)
bell=emoji("🔔",64); f_cta=ImageFont.truetype(FONT,70)
lbl="구독하기"; tw=dr.textlength(lbl,font=f_cta); gap=20; tot=tw+gap+bell.width
sx=(W-tot)//2; cy=by0+btn_h//2
dr.text((sx,cy),lbl,font=f_cta,fill=WHITE,anchor='lm')
img.paste(bell,(int(sx+tw+gap),int(cy-bell.height//2)),bell)
img.save(os.path.join(OUT,'outro_card.png')); print('outro_card.png', img.size)
