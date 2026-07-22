#!/usr/bin/env python3
"""배투실 애니메이션(일러스트) 스타일 생성기 — ComfyUI Flux(flux1-schnell-fp8).
바이블의 STYLE+캐릭터를 앞에 붙여 씬 일러스트를 생성. 캐릭터별 고정 시드로 일관성.

사용: python generate.py <name> <seed> "<scene prompt in English>" [A|B|none]
예:   python generate.py hook_A 101 "holding an empty money sack, coins vanishing, luxury room, shocked" A
출력: animation_style/out/<name>.png
"""
import json, urllib.request, time, sys, os
API="http://127.0.0.1:8188"
STYLE=("Pen and ink hand-drawn editorial cartoon illustration in a warm vintage storybook style, bold confident "
 "black linework with dense cross-hatching shading, warm sepia and muted gold tones on aged cream paper background, "
 "friendly slightly-exaggerated caricature faces, consistent soft flat lighting, no text no words no signature. ")
CHARS={
 "A":"A plump elderly Korean gentleman, bald on top with gray hair on the sides, bushy gray eyebrows, small gray mustache, thick round tortoiseshell glasses, formal three-piece pinstripe suit with a bow tie. ",
 "B":"A slim elderly Korean man with a full head of neat gray hair, clean-shaven, thin round wire glasses, gentle smile lines, simple beige knit cardigan over a plain collared shirt. ",
 "none":"",
}
OUT=os.path.join(os.path.dirname(__file__),"..","out")

def generate(name, seed, scene, char="none", w=1280, h=720):
    prompt=STYLE+CHARS.get(char,"")+scene
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
    os.makedirs(OUT,exist_ok=True)
    for _ in range(120):
        time.sleep(2); hi=json.load(urllib.request.urlopen(f"{API}/history/{pid}"))
        if pid in hi:
            for n in hi[pid]["outputs"].values():
                for im in n.get("images",[]):
                    u=f"{API}/view?filename={im['filename']}&subfolder={im.get('subfolder','')}&type=output"
                    p=os.path.join(OUT,f"{name}.png"); open(p,"wb").write(urllib.request.urlopen(u).read())
                    print("SAVED",p); return p
    print("timeout",name)

if __name__=="__main__":
    name,seed,scene=sys.argv[1],sys.argv[2],sys.argv[3]
    char=sys.argv[4] if len(sys.argv)>4 else "none"
    generate(name,seed,scene,char)
