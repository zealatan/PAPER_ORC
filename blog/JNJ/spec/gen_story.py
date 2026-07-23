# -*- coding: utf-8 -*-
"""C단계 대본/스토리(개정판) → spec.story + narration_draft.json + SCRIPT.md.
   개정 요지(코카콜라 diff + 흐름 진단 반영):
   - 반전을 앞으로(씬4 차트로 즉시 공개) → 회사소개가 '이유'로 연결
   - 최신뉴스 씬 신설 · survheat 생존지도 · divbars 배당히스토리 복원
   - 파산 차트 물가반영(real) 중심 · 나레이션 숫자 자연스러운 반올림(만 단위)
   철칙: 숫자·연도는 backtest 인용만. 지어내기 금지.
"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "spec"))
import spec as S

spec = S.load_spec(str(ROOT / "spec" / "JNJ.json"))
SC = {s["id"]: s for s in spec["backtest"]["fire"]["scenarios"]}
STR = spec["backtest"]["strategy_compare"]["strategies"]
BIZ = spec["data"]["business"]


def man(x): return f"{round(x/10000)}만 달러"          # 490052 → "49만 달러"
def yr(dep): return dep.split("-")[0] if dep else None
g = lambda i, mo: SC[f"nominal_{i}_{mo}"]
r = lambda i, mo: SC[f"real_{i}_{mo}"]
r2 = lambda i, mo: SC[f"real2002_{i}_{mo}"]           # 2002년(닷컴버블 저점) 은퇴

# 인용 값
A = g(400000, 3000); B = g(400000, 1000)            # 후킹: 명목(달러 그대로)
assert not A["survived"] and B["survived"]
A_yr = yr(A["depletion"]); A_years = int(A_yr) - 2000
SM = spec["backtest"]["strategy_compare"]["smart"]   # 폭락 매수
SD = spec["backtest"]["strategy_compare"]["steady"]  # 매달 적립
gap = round((SM["final_on"] / SD["final_on"] - 1) * 100)
trig_years = sorted({t["date"][:4] for t in spec["backtest"]["strategy_compare"]["deck_triggers"]})

narration = [
 # ═══════ 1부 후킹 (videohook 제거 — 사용자 편집 반영) ═══════
 # 1페이지(유의사항): 더빙 없음 — 효과음(beep)만, 자막 없음 (사용자 요청)
 {"scene": 0, "sec": "hook", "tpl": "notice", "lines": []},
 {"scene": 2, "sec": "hook", "tpl": "solostory", "lines": [
   "같은 날 존슨앤드존슨으로 은퇴한 두 사람이 있습니다. 먼저 A입니다.",
   "40만 달러로 은퇴해, 매달 3천 달러씩 넉넉히 썼습니다.",
   "배당으로 모자란 돈은 주식을 팔아 메웠죠."]},
 {"scene": 3, "sec": "hook", "tpl": "solostory", "lines": [
   "B도 똑같이 40만 달러.",
   "하지만 매달 쓴 돈은 천 달러, A의 3분의 1이었습니다.",
   "남는 배당은 다시 주식을 샀습니다."]},
 {"scene": 4, "sec": "hook", "tpl": "enginechart", "chart": "reveal", "lines": [
   "26년이 지난 지금, 결과를 볼까요?",
   f"넉넉히 쓴 A는 {A_yr}년, {A_years}년 만에 잔고가 바닥났습니다.",
   f"반면 아껴 쓴 B는 {man(B['final'])}.",
   "차이는 단 하나, 매달 얼마를 쓰느냐였습니다."]},
 # ═══════ 종목 소개 + 최신뉴스 ═══════
 {"scene": 5, "sec": "intro", "tpl": "herostat", "lines": [
   "이 극과 극의 차이, 종목 특성과 관련이 깊습니다.",
   f"존슨앤드존슨은 {BIZ['dividend_king_years']}년 연속 배당을 늘려온 배당왕이자,",
   "한 해도 거르지 않은 방어주죠."]},
 {"scene": 6, "sec": "intro", "tpl": "kpirow", "lines": [
   "제약이 매출의 약 3분의 2, 의료기기가 나머지.",
   f"2025년 총매출은 942억 달러로 {int(BIZ['fy2025_yoy_pct'])}퍼센트 늘었고,",
   f"주당 배당은 {BIZ['annual_dividend_ps']}달러입니다."]},
 {"scene": 7, "sec": "intro", "tpl": "checks", "lines": [
   "요즘 근황도 짚어볼까요?",
   "최근 매출은 사상 처음 1,000억 달러를 바라보고,",
   "수술로봇 오타바가 FDA 승인을 받았습니다.",
   "다만 오래 발목을 잡아온 탈크 소송은 여전히 진행 중입니다."]},
 # ═══════ 2부 파산 시나리오 (물가반영, 2000년 은퇴) ═══════
 {"scene": 8, "sec": "part2", "tpl": "interlude", "lines": [
   "자, 그럼 본격적으로 파고들어 볼까요?",
   "얼마가 있으면, 매달 얼마까지 써도 버틸까?",
   "물가상승까지 반영한, 진짜 냉혹한 그림입니다."]},
 {"scene": 9, "sec": "part2", "tpl": "enginechart", "chart": "fire_200k", "lines": [
   "먼저 20만 달러로 은퇴한 경우.",
   "물가를 반영하면 매달 천 달러조차 겨우 버티고,",
   f"2천 달러는 {yr(r(200000,2000)['depletion'])}년, 3천 달러는 {yr(r(200000,3000)['depletion'])}년에 파산합니다."]},
 {"scene": 10, "sec": "part2", "tpl": "enginechart", "chart": "fire_400k", "lines": [
   "40만 달러라면 조금 낫습니다.",
   f"천 달러는 {man(r(400000,1000)['final'])}까지 불어나지만,",
   f"3천 달러는 {yr(r(400000,3000)['depletion'])}년에 무너집니다."]},
 {"scene": 11, "sec": "part2", "tpl": "enginechart", "chart": "fire_600k", "lines": [
   "60만 달러면 물가를 반영해도 셋 다 살아남습니다.",
   f"매달 3천 달러를 써도 {man(r(600000,3000)['final'])}가 남죠.",
   "결국 원금과 지출이 생사를 가릅니다."]},
 # ═══════ 3부 매수 방법 (코카콜라와 동일 2전략 구조) ═══════
 {"scene": 13, "sec": "part3", "tpl": "interlude", "lines": [
   "이번엔 반대로, 이제부터 모으는 입장입니다.",
   "매달 천 달러씩 25년, 어떻게 사야 가장 크게 불릴까요?",
   "두 투자자가 있습니다."]},
 {"scene": 14, "sec": "part3", "tpl": "solostory", "lines": [
   "첫 번째, 타이밍을 노리는 투자자.",
   "평소엔 현금으로 기다리다,",
   "폭락, 30퍼센트 하락 때 싸게 몰아 삽니다."]},
 {"scene": 15, "sec": "part3", "tpl": "solostory", "lines": [
   "두 번째, 매달 꾸준히 사는 투자자.",
   "매달 꼬박꼬박 사 모으고,",
   "배당은 전액 재투자합니다."]},
 {"scene": 16, "sec": "part3", "tpl": "enginechart", "chart": "price_trigger", "lines": [
   "먼저 JNJ 주가와 폭락 신호부터.",
   f"25년간 30퍼센트 폭락은 {trig_years[0]}년과 {trig_years[1]}년, 딱 두 번뿐이었습니다.",
   "방어주라 싸게 살 기회 자체가 거의 없었죠."]},
 {"scene": 17, "sec": "part3", "tpl": "enginechart", "chart": "smart_result", "lines": [
   "타이밍을 노린 쪽의 결과입니다.",
   f"폭락만 노려 재투자해도 {man(SM['final_on'])}.",
   "하지만 현금 대부분이 놀았습니다 — 실제 투입은 원금의 일부뿐."]},
 {"scene": 18, "sec": "part3", "tpl": "enginechart", "chart": "steady_result", "lines": [
   "이번엔 매달 적립한 쪽입니다.",
   f"매달 사서 배당까지 재투자하면 {man(SD['final_on'])}.",
   "쉬지 않고 복리가 굴러갑니다."]},
 {"scene": 19, "sec": "part3", "tpl": "hbars2", "lines": [
   "나란히 놓고 볼까요?",
   f"완벽한 폭락 타이밍은 {man(SM['final_on'])}, 그냥 적립은 {man(SD['final_on'])}.",
   f"폭락 매수는 현금 3분의 1이 놀았는데도, 적립이 {abs(gap)}퍼센트 앞섰죠.",
   "금액도, 수익률도 — 기다리는 사이 시간이 이겼습니다."]},
 # ═══════ 마무리 ═══════
 {"scene": 20, "sec": "outro", "tpl": "divbars", "lines": [
   "이 모든 걸 가능하게 한 건 결국 배당입니다.",
   f"존슨앤드존슨은 {BIZ['dividend_king_years']}년 동안 단 한 해도 거르지 않고 배당을 늘려왔습니다."]},
 {"scene": 21, "sec": "outro", "tpl": "quotebig", "lines": [
   "결론은 단순합니다.",
   "타이밍을 맞히려 애쓰지 말고,",
   "쓰는 돈을 지키고, 꾸준히 모아 재투자할 것."]},
 {"scene": 22, "sec": "outro", "tpl": "card", "lines": [
   "배당으로 은퇴하는 이야기, 다음 종목도 이어집니다.",
   "구독하고 함께 지켜봐 주세요."]},
]

# ── spec.story ──
spec["story"]["hook"] = {
  "a": {"init": 400000, "monthly": 3000, "outcome": "파산", "year": int(A_yr)},
  "b": {"init": 400000, "monthly": 1000, "outcome": "생존", "final": B["final"]},
  "question": "같은 40만 달러·같은 JNJ·같은 26년, 매달 쓰는 돈만 달랐다.",
}
from collections import OrderedDict
# 씬 삽입/재배치로 번호가 밀리므로 리스트 순서대로 자동 재번호
for i, n in enumerate(narration):
    n["scene"] = i
SEC_TITLES = {"hook": "1부 후킹 — 같은 돈, 다른 운명", "intro": "종목 소개 + 최신 근황",
              "part2": "2부 파산 시나리오 — 물가 반영 생존지도",
              "part3": "3부 매수 방법 — 폭락 타이밍 vs 매달 적립", "outro": "마무리 — 배당왕의 꾸준함"}
grp = OrderedDict()
for n in narration:
    grp.setdefault(n["sec"], []).append(n["scene"])
spec["story"]["sections"] = [{"id": k, "title": SEC_TITLES[k], "scenes": v} for k, v in grp.items()]
S.save_spec(spec, str(ROOT / "spec" / "JNJ.json"))
json.dump(narration, open(ROOT / "spec" / "narration_draft.json", "w"), ensure_ascii=False, indent=1)

md = ["# JNJ 대본 (개정판) — 반전 앞으로 + 뉴스 + 물가반영 + survheat/divbars 복원\n"]
cur = None
for n in narration:
    if n["sec"] != cur:
        cur = n["sec"]
        md.append(f"\n## {next(s['title'] for s in spec['story']['sections'] if s['id']==cur)}\n")
    ch = f" · chart={n['chart']}" if n.get("chart") else ""
    md.append(f"**[{n['scene']}] {n['tpl']}{ch}**")
    md += [f"- {l}" for l in n["lines"]] + [""]
(ROOT / "spec" / "SCRIPT.md").write_text("\n".join(md), encoding="utf-8")

chars = sum(len(l.replace(" ", "")) for n in narration for l in n["lines"])
print(f"씬 {len(narration)}개 · {chars}자 · 낭독 ≈ {chars/5/1.18/60+len(narration)*1.3/60:.1f}분")
print(f"인용: A파산{A_yr} / B {man(B['final'])} / real400_1k {man(r(400000,1000)['final'])} / 폭락gap {gap}%")
print("→ spec/JNJ.json(story) · narration_draft.json · SCRIPT.md")
