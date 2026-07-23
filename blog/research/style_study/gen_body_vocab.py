# -*- coding: utf-8 -*-
"""혼잡스 본문 일러스트 '어휘' 재현 — 캐릭터 제스처 + 스팟 일러스트(손/미니피규어/소품/로봇).
검증된 클린 웹툰 STYLE 재사용. 스팟은 CHAR 없이 흰 배경 단독 아이콘."""
import json, urllib.request, time, os
API="http://127.0.0.1:8188"
STYLE=("Clean minimalist Korean webtoon manhwa line art illustration, thin uniform confident black ink outlines, "
 "flat pure black and white, no cross-hatching, no gradient, no color, minimal interior shading, "
 "high contrast, pure white background, vector-like clean linework, editorial explainer illustration, no text. ")
CHAR=("A young Korean office worker man in his early 30s, neat short black hair, crisp white dress shirt with a "
 "loosened dark solid black necktie, clean shaven, flat simple webtoon face, upper body three-quarter view. ")

def gen(name, seed, scene, char=False, w=1280, h=720):
    prompt=STYLE+(CHAR if char else "")+scene
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
    OUT="style_corpus/vocab"; os.makedirs(OUT,exist_ok=True)
    for _ in range(120):
        time.sleep(2); hi=json.load(urllib.request.urlopen(f"{API}/history/{pid}"))
        if pid in hi:
            for n in hi[pid]["outputs"].values():
                for im in n.get("images",[]):
                    u=f"{API}/view?filename={im['filename']}&subfolder={im.get('subfolder','')}&type=output"
                    p=os.path.join(OUT,f"{name}.png"); open(p,"wb").write(urllib.request.urlopen(u).read())
                    print("SAVED",name); return
    print("timeout",name)

# (name, seed, scene, char?)
VOCAB=[
 # 캐릭터 제스처
 ("v_point", 401,"pointing to the side with his index finger, presenting gesture, empty space on left.",True),
 ("v_thumbsup",402,"giving a big thumbs up with a confident smile, empty space on left.",True),
 ("v_stop",  403,"raising one open palm forward in a stop gesture, slightly worried face.",True),
 # 손 + 소품
 ("v_hand_a4",411,"a single hand holding up a blank A4 paper sheet, isolated line-art icon centered on white, nothing else.",False),
 ("v_hand_phone",412,"a single hand holding a smartphone taking a photo, isolated line-art icon centered on white.",False),
 ("v_hand_pointer",413,"a single hand holding a long thin teacher pointer stick pointing to the right, isolated line-art on white.",False),
 # 미니 피규어
 ("v_sleep",421,"a tiny simple person lying down sleeping with small Zzz marks, minimalist line-art figure on white.",False),
 ("v_crowd",422,"three tiny simple people cheering with both arms raised up, minimalist line-art figures on white.",False),
 ("v_podium",423,"a tiny person standing at a podium presenting to a small seated audience, minimalist line-art scene on white.",False),
 # 소품/은유
 ("v_robot",431,"a cute simple friendly robot character standing, rounded body, minimalist black line-art on white.",False),
 ("v_money",432,"a neat stack of cash bundles and a few coins, minimalist line-art icon centered on white.",False),
 ("v_store",433,"a small simple storefront shop building with an awning, minimalist line-art icon on white.",False),
]
for name,seed,scene,ch in VOCAB:
    gen(name,seed,scene,ch)
print("DONE")
