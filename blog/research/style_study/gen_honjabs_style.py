# -*- coding: utf-8 -*-
"""혼잡스 '클린 웹툰 라인아트' 그림체 재현 테스트 — ComfyUI Flux(flux1-schnell-fp8).
기존 animation_style(따뜻한 세피아 해칭)과 별개의 STYLE 변형을 실험."""
import json, urllib.request, time, sys, os
API="http://127.0.0.1:8188"

# 혼잡스 그림체 STYLE 후보 (클린 흑백 웹툰 라인아트)
STYLE=("Clean minimalist Korean webtoon manhwa line art illustration, thin uniform confident black ink outlines, "
 "flat pure black and white, no cross-hatching, no gradient, no color, minimal interior shading, "
 "solid black hair mass with a few white gap strokes, simple expressive caricature face, "
 "high contrast, pure white background, vector-like clean linework, editorial thumbnail illustration. ")
CHAR=("A young Korean office worker man in his early 30s, neat short black hair, wearing a crisp white dress "
 "shirt with a loosened dark necktie, clean shaven, simple facial features, upper body three-quarter view. ")

def gen(name, seed, scene, w=1280, h=720):
    prompt=STYLE+CHAR+scene
    wf={"3":{"class_type":"CheckpointLoaderSimple","inputs":{"ckpt_name":"flux1-schnell-fp8.safetensors"}},
     "4":{"class_type":"CLIPTextEncode","inputs":{"text":prompt,"clip":["3",1]}},
     "5":{"class_type":"CLIPTextEncode","inputs":{"text":"","clip":["3",1]}},
     "6":{"class_type":"EmptySD3LatentImage","inputs":{"width":w,"height":h,"batch_size":1}},
     "7":{"class_type":"KSampler","inputs":{"model":["3",0],"positive":["4",0],"negative":["5",0],
          "latent_image":["6",0],"seed":int(seed),"steps":4,"cfg":1.0,"sampler_name":"euler","scheduler":"simple","denoise":1.0}},
     "8":{"class_type":"VAEDecode","inputs":{"samples":["7",0],"vae":["3",2]}},
     "9":{"class_type":"SaveImage","inputs":{"images":["8",0],"filename_prefix":name}}}
    pid=json.load(urllib.request.urlopen(urllib.request.Request(API+"/prompt",
        data=json.dumps({"prompt":wf}).encode(),headers={"Content-Type":"application/json"})))["prompt_id"]
    OUT="style_corpus/gen"; os.makedirs(OUT,exist_ok=True)
    for _ in range(120):
        time.sleep(2); hi=json.load(urllib.request.urlopen(f"{API}/history/{pid}"))
        if pid in hi:
            for n in hi[pid]["outputs"].values():
                for im in n.get("images",[]):
                    u=f"{API}/view?filename={im['filename']}&subfolder={im.get('subfolder','')}&type=output"
                    p=os.path.join(OUT,f"{name}.png"); open(p,"wb").write(urllib.request.urlopen(u).read())
                    print("SAVED",p); return p
    print("timeout",name)

# 3종 표정/구도 테스트 (혼잡스 대표 포즈)
TESTS=[
 ("honstyle_neutral", 101, "neutral calm expression looking at viewer, plain composition, empty space on the left for text."),
 ("honstyle_shock",   202, "shocked surprised face with open mouth and one hand touching his cheek, big empty space on left."),
 ("honstyle_think",   303, "thoughtful worried expression, hand on chin, looking slightly up, empty space on left for text."),
]
for name,seed,scene in TESTS:
    gen(name,seed,scene)
print("DONE")
