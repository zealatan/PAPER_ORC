#!/usr/bin/env python3
"""blog 루트 정적 서빙 + 편집 저장 API (파이프라인 편집 UI 동기화용).
   기존 `python3 -m http.server`를 대체 — 읽기 + 소스 파일 되쓰기(저장) 가능.

   사용: python3 pipeline/edit_server.py [port]        (기본 8090)

   POST /api/save-deck     {stock, scenes, ov, cp}
        → <stock>/spec/deck_ov.json 갱신(+ 무손실 스냅샷) → build_deck.py 자동 재실행
   POST /api/rebuild       {stock}   → build_deck.py 실행
   POST /api/save-pipeline {stock, items}
        → <stock>/spec/deck_plan.json 저장 (2단계: 실제 덱 씬 재정렬/생성에 사용)
"""
import json, sys, subprocess
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # blog/
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8090


def sdir(stock):
    """<blog>/<stock> 이 build_deck.py를 가진 정상 종목 폴더면 반환(경로 탈출 방지)."""
    if not stock or "/" in stock or ".." in stock:
        return None
    d = (ROOT / stock).resolve()
    if d.is_dir() and ROOT in d.parents and (d / "deck" / "build_deck.py").exists():
        return d
    return None


def rebuild(stock):
    d = sdir(stock)
    if not d:
        return {"ok": False, "err": "build_deck 없음: " + str(stock)}
    p = subprocess.run([sys.executable, "deck/build_deck.py"], cwd=str(d),
                       capture_output=True, text=True, timeout=300)
    return {"ok": p.returncode == 0, "log": (p.stdout + p.stderr)[-900:]}


def save_deck(data):
    stock = data.get("stock", "MCD")
    d = sdir(stock)
    if not d:
        return {"ok": False, "err": "잘못된 종목: " + str(stock)}
    spec = d / "spec"; spec.mkdir(exist_ok=True)
    written = []
    ov = data.get("ov")
    if isinstance(ov, dict):                    # 라벨 위치·텍스트·anno 숨김 등 → 재굽기에도 유지되는 소스
        (spec / "deck_ov.json").write_text(
            json.dumps(ov, ensure_ascii=False, indent=1), encoding="utf-8")
        written.append("deck_ov.json")
    scenes = data.get("scenes")
    if isinstance(scenes, list):                # 무손실 스냅샷(자막 등 OV 밖 편집도 보존)
        (spec / "deck_edited_scenes.json").write_text(
            json.dumps(scenes, ensure_ascii=False, indent=1), encoding="utf-8")
        written.append("deck_edited_scenes.json")
    rb = rebuild(stock)                         # 자동 재굽기 → mcd_v1.html 최신화
    return {"ok": rb["ok"], "written": written, "rebuild": rb}


def save_pipeline(data):
    stock = data.get("stock", "MCD")
    d = sdir(stock)
    if not d:
        return {"ok": False, "err": "잘못된 종목: " + str(stock)}
    (d / "spec" / "deck_plan.json").write_text(
        json.dumps(data.get("items", []), ensure_ascii=False, indent=1), encoding="utf-8")
    rb = rebuild(stock)                          # build_deck: deck_plan 적용 → mcd_deck.json·mcd_v1.html
    gen = subprocess.run([sys.executable, "deck/tools/gen_dec_edit.py"], cwd=str(d),
                         capture_output=True, text=True, timeout=120)   # 파이프라인·편집페이지 재생성
    return {"ok": rb["ok"] and gen.returncode == 0, "written": ["deck_plan.json"],
            "rebuild": rb, "regen": (gen.stdout + gen.stderr)[-400:]}


def save_subs(data):
    """편집화면 자막 패널에서 수정한 문장 → narration_final.json[scene] 저장 → gen_story→build_deck→gen_dec_edit."""
    stock = data.get("stock", "PG")
    d = sdir(stock)
    if not d:
        return {"ok": False, "err": "잘못된 종목: " + str(stock)}
    scene = data.get("scene")
    if not isinstance(scene, int):
        return {"ok": False, "err": "scene 인덱스(정수) 필요"}
    lines = [str(x) for x in (data.get("lines") or [])]
    nf = d / "spec" / "narration_final.json"
    obj = json.loads(nf.read_text(encoding="utf-8")) if nf.exists() else {}
    obj[str(scene)] = lines
    nf.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
    for script in ("spec/gen_story.py", "deck/build_deck.py", "deck/tools/gen_dec_edit.py"):
        p = subprocess.run([sys.executable, script], cwd=str(d), capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            return {"ok": False, "err": script + " 실패", "log": (p.stdout + p.stderr)[-500:]}
    return {"ok": True, "written": ["narration_final.json"], "scene": scene, "lines": lines}


class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT), **k)

    def log_message(self, *a):
        pass

    def end_headers(self):
        # 브라우저가 옛 pg_v1.html(12MB) 등을 캐시해 '안 바뀜'으로 보이던 문제 → 항상 최신 받도록 no-store
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        super().end_headers()

    def _j(self, code, obj):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0) or 0)
        try:
            data = json.loads(self.rfile.read(n) or b"{}")
        except Exception as e:
            return self._j(400, {"ok": False, "err": "bad json: " + str(e)})
        route = self.path.split("?")[0]
        try:
            if route == "/api/save-deck":
                return self._j(200, save_deck(data))
            if route == "/api/rebuild":
                return self._j(200, rebuild(data.get("stock", "MCD")))
            if route == "/api/save-pipeline":
                return self._j(200, save_pipeline(data))
            if route == "/api/save-subs":
                return self._j(200, save_subs(data))
            return self._j(404, {"ok": False, "err": "unknown route " + route})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return self._j(500, {"ok": False, "err": str(e)})


if __name__ == "__main__":
    print(f"편집 서버 http://0.0.0.0:{PORT}  (root={ROOT})")
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
