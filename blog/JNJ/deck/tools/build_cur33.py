# -*- coding: utf-8 -*-
"""디스크 36덱 → 회원님 현재 33씬 덱 재구성 (videohook 삽입 + 4씬 제거 + OV 부착)."""
import json

d = json.load(open("cocacola_final36.json", encoding="utf-8"))
S = d["scenes"]

def title(s):
    dt = s.get("data", {})
    t = (dt.get("title") or dt.get("main") or dt.get("eyebrow") or dt.get("num") or dt.get("kick") or dt.get("quote") or "")
    return t if isinstance(t, str) else ""

# 제거할 4씬 (제목 부분일치)
DROP = ["일시불", "$100,000이", "가만히 있어도", "2020년부터"]
kept = [s for s in S if not any(k in title(s) for k in DROP)]
assert len(kept) == 32, f"kept={len(kept)} (expected 32)"

# videohook 를 notice(0) 다음(1번)에 삽입
videohook = {"tpl": "videohook", "dur": 36000, "cam": {"s": 1, "x": 50, "y": 50},
             "data": {"src": "clip/full_clip.mp4"}, "bgid": None}
scenes = [kept[0], videohook] + kept[1:]
assert len(scenes) == 33, len(scenes)

# accum 인터루드 3개 연속화: soda_lemon 인터루드를 첫 accum solostory 앞으로 이동
lemon = next(i for i, s in enumerate(scenes) if s["tpl"] == "interlude" and s.get("bgid") == "soda_lemon")
first_accum = next(i for i, s in enumerate(scenes) if s["tpl"] == "solostory" and "두 사람" in (s.get("data", {}).get("kick") or "") and "두 사람" == (s.get("data", {}).get("kick") or "").replace("2000년, ", "").strip())
sc = scenes.pop(lemon)
scenes.insert(first_accum if lemon > first_accum else first_accum - 1, sc)
assert len(scenes) == 33

# _ver 존재 확인 (FIRE 마이그레이션 재실행 방지)
assert any(s.get("data", {}).get("_ver") == "v8-hook" for s in scenes), "no v8-hook flag!"

# 회원님 OV/CP (붙여주신 localStorage 상태) — 33씬 인덱스 기준
OV = {
  "6:brand": {"c": "#fdfcf9", "bc": "#fdfcf9"},
  "20:grid": {"x": -0.16, "y": 1.79}, "20:grid.c3": {}, "20:sub": {}, "20:grid.c0": {},
  "5:eyebrow": {"hide": True}, "5:sub": {"hide": True}, "5:brand": {}, "5:label": {},
  "6:chips": {"hide": True}, "6:sub": {"hide": True},
  "6:main": {"x": 0.81, "y": 5.12, "s": 0.4},
  "6:eyebrow": {"hide": True, "x": -12.34, "y": -20.93},
  "6:copy.mrn4k8lc3y6": {"x": 41.92, "y": 9.69, "s": 2.2},
  "29:anno": {"hide": True}, "29:chart": {"x": 0.41, "y": 3.33}, "29:left.head": {}, "29:right.head": {}, "29:sub": {"hide": True},
  "27:title": {}, "28:title": {}, "29:title": {},
  "17:sub": {"hide": True}, "17:chart": {"x": -1.7, "y": 0.25}, "17:anno": {"x": 2.27, "y": -16.39},
  "2:tag": {"hide": True}, "2:row.2": {"hide": True}, "2:row.0": {}, "2:row.1": {},
  "2:accent": {"x": 44.32, "y": -21.19}, "2:kick": {"txt": "2000년, 은퇴한 두 사람"},
  "3:row.2": {"hide": True}, "3:tag": {"hide": True}, "3:accent": {"x": 44.4, "y": -26.14},
  "3:kick": {"txt": "2000년, 은퇴한 두 사람"},
  "7:anno": {"hide": True}, "7:chart": {}, "8:anno": {"hide": True}, "9:anno": {"hide": True},
  "10:anno": {"hide": True}, "11:anno": {"hide": True}, "12:anno": {"hide": True}, "13:anno": {"hide": True},
}
CP = {"6": [{"id": "mrn4k8lc3y6", "html": "<h1 class=\"cmain\" data-ek=\"main\" data-tx=\"main\" contenteditable=\"plaintext-only\" style=\"color: rgb(244, 247, 251);\">{{coke}}</h1>"}]}

out = {"scenes": scenes, "ov": OV, "cp": CP, "theme": "paper", "paper": "photo"}
json.dump(out, open("cocacola_cur33.json", "w", encoding="utf-8"), ensure_ascii=False)

print("33씬 덱 생성 완료 → cocacola_cur33.json")
for i, s in enumerate(scenes):
    print(f'{i:2d} {s["tpl"]:12s} {title(s).replace("{{coke}}","")[:36]}')
