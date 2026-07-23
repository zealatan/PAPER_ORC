# -*- coding: utf-8 -*-
"""배당/백테스트 콘텐츠용 3세트 일러스트 — 혼잡스 클린 웹툰 스타일(로컬 Flux). 제출만."""
import json, urllib.request
API="http://127.0.0.1:8188"
STYLE=("Clean minimalist Korean webtoon manhwa line art illustration, thin uniform confident black ink outlines, "
 "flat pure black and white, no cross-hatching, no gradient, no color, minimal interior shading, "
 "high contrast, pure white background, vector-like clean linework, editorial explainer illustration, no text. ")
# 우리 배당 채널 캐릭터: 친근한 중년 한국 남성 투자 멘토(안경+니트가디건) — 혼잡스 젊은직장인과 구분
HOST=("A friendly middle-aged Korean man in his 50s, neat gray-streaked hair, round glasses, wearing a soft "
 "knit cardigan over a collared shirt, warm approachable face, flat simple webtoon face, upper body three-quarter view. ")
RETIREE=("An elderly Korean man in his late 60s, thin gray hair, gentle wrinkles, round glasses, simple cardigan, "
 "flat simple webtoon face, upper body. ")

def submit(name, seed, scene, w=1280, h=720):
    wf={"3":{"class_type":"CheckpointLoaderSimple","inputs":{"ckpt_name":"flux1-schnell-fp8.safetensors"}},
     "4":{"class_type":"CLIPTextEncode","inputs":{"text":STYLE+scene,"clip":["3",1]}},
     "5":{"class_type":"CLIPTextEncode","inputs":{"text":"","clip":["3",1]}},
     "6":{"class_type":"EmptySD3LatentImage","inputs":{"width":w,"height":h,"batch_size":1}},
     "7":{"class_type":"KSampler","inputs":{"model":["3",0],"positive":["4",0],"negative":["5",0],
          "latent_image":["6",0],"seed":int(seed),"steps":4,"cfg":1.0,"sampler_name":"euler","scheduler":"simple","denoise":1.0}},
     "8":{"class_type":"VAEDecode","inputs":{"samples":["7",0],"vae":["3",2]}},
     "9":{"class_type":"SaveImage","inputs":{"images":["8",0],"filename_prefix":"set_"+name}}}
    urllib.request.urlopen(urllib.request.Request(API+"/prompt",
        data=json.dumps({"prompt":wf}).encode(),headers={"Content-Type":"application/json"}))
    print("queued",name)

JOBS=[
 # ── SET A: 배당/백테스트 콘텐츠 은유 세트 ──
 ("A_retiree_worry",601, RETIREE+"looking worried while examining a line chart on a sheet of paper, empty space on left."),
 ("A_retiree_happy",602, RETIREE+"smiling with relief and confidence, arms gently crossed, empty space on left."),
 ("A_money_tree",603, "a money tree with round coins as its leaves in a pot, isolated line-art icon centered on white."),
 ("A_reservoir",604, "a large water reservoir tank with a tap draining water, water level dropping, asset metaphor, isolated line-art on white."),
 ("A_hourglass",605, "an hourglass where gold coins pour down instead of sand into a growing pile, isolated line-art centered on white."),
 ("A_deposit",606, "coins dropping into a piggy bank next to a bankbook, dividend deposit metaphor, isolated line-art on white."),
 ("A_chart_up",607, "a line chart trending upward with an arrow at the end, isolated line-art icon centered on white."),
 ("A_calendar_coins",608, "a wall calendar with a coin stack beside each week, monthly dividend metaphor, isolated line-art on white."),
 # ── SET B: 씬별(두 은퇴자 A vs B 스토리) ──
 ("B1_two_retirees",611, "two elderly Korean men standing back to back, one looking worried and one looking content, line-art on white."),
 ("B2_spender",612, RETIREE+"standing beside tall stacks of cash, spending freely, line-art on white."),
 ("B3_saver",613, RETIREE+"standing beside a growing money tree, frugal and reinvesting, line-art on white."),
 ("B4_bankrupt_chart",614, "a line chart crashing down to zero with an empty wallet, bankruptcy metaphor, isolated line-art on white."),
 ("B5_survive_chart",615, "a line chart staying high and growing with a stack of coins remaining, survival metaphor, isolated line-art on white."),
 ("B6_heatmap",616, "a 3 by 3 grid heatmap of small squares, some filled some empty, survival table metaphor, isolated line-art on white."),
 # ── SET C: 채널 캐릭터 시트 (동일 시드 555, 6표정) ──
 ("C_neutral",555, HOST+"calm neutral expression looking at viewer."),
 ("C_explain",555, HOST+"explaining and pointing to the side with one hand, friendly."),
 ("C_surprised",555, HOST+"surprised expression with raised eyebrows and open mouth."),
 ("C_confident",555, HOST+"giving a confident thumbs up with a warm smile."),
 ("C_worried",555, HOST+"worried concerned expression, slight frown."),
 ("C_think",555, HOST+"thoughtful expression with a hand on his chin, looking up."),
]
for name,seed,scene in JOBS: submit(name,seed,scene)
print("ALL QUEUED", len(JOBS))
