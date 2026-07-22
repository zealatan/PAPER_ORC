# -*- coding: utf-8 -*-
"""cocacola 현재 33씬 덱 → 스토리보드 + 대본 생성 (PNG 썸네일 삽입)."""
import json, sys, html, base64, pathlib, math
THUMBS = pathlib.Path("thumbs_sm")
def thumb_uri(i):
    p = THUMBS/f"s{i+1:02d}.jpg"
    if p.exists(): return "data:image/jpeg;base64,"+base64.b64encode(p.read_bytes()).decode()
    return None

DECK = sys.argv[1] if len(sys.argv)>1 else "cocacola_cur33.json"
d = json.load(open(DECK, encoding="utf-8"))
S = d["scenes"]

RATE = 5.0        # 자/s (공백 제외)
BUF  = 1.3        # 씬당 호흡 버퍼(s)

# (대본, 배경, 요소[], fx[], 자료) — 33씬 현재 덱 순서
SB = [
 ("", "다크 그라디언트", ["유의사항 카드"], ["페이드인"], "대사 없음 — 인트로 고지"),
 ("같은 주식에 투자했는데, 한 사람은 파산했고, 다른 한 사람은 자산이 오히려 늘어났습니다. 같은 날 은퇴한 두 사람이 있었습니다. 둘 다 같은 종목에 투자했습니다. 하지만 은퇴 후의 선택은 달랐습니다. A는 넉넉한 은퇴 자금 덕분에 은퇴 전과 다르지 않은 생활을 이어갔습니다. 반면 B는 생활비를 크게 줄였습니다. 그리고 26년 뒤. 두 사람의 운명은 완전히 달라졌습니다.", "AI 실사 영상(훅)", ["와인 축배→주가 폭락→몰락→컵라면","해변 $4.5M 대비","AI 제작 표기"], ["풀블리드"], "AI 생성 영상 · clip/full_clip.mp4"),
 ("먼저 A입니다. A의 은퇴 자금은 60만 달러였습니다. 충분히 넉넉한 금액이었죠. 그래서 은퇴 전과 비슷한 생활을 이어갔습니다. 매달 3천 달러를 생활비로 사용했습니다. 배당금으로 부족한 금액은 보유한 주식을 조금씩 매도하며 충당했습니다.", "트레이더 배경", ["A 인물카드","현금다발","스탯"], ["슬라이드인"], None),
 ("이번에는 B입니다. B의 은퇴 자금은 40만 달러였습니다. A보다 20만 달러나 적은 금액이었죠. 그래서 생활 방식을 바꾸기로 했습니다. 매달 생활비를 1천 달러로 줄였고, 받은 배당금은 한 푼도 쓰지 않았습니다. 모든 배당금을 다시 같은 종목에 재투자했습니다.", "새싹 배경", ["B 인물카드","머니트리","스탯"], ["슬라이드인"], None),
 ("26년이 지난 지금, 두 사람은 과연 어떻게 살고 있을까요?", "얼음/소다 실사", ["전환 스크림"], ["디졸브"], None),
 ("본론에 들어가기 전에, 먼저 이 종목부터 살펴보겠습니다. 전 세계에서 하루에만 22억 잔이 팔리는 회사입니다.", "자판기 실사", ["대형 숫자","라벨"], ["카운트업"], None),
 ("200개가 넘는 브랜드를 보유하고, 워런 버핏이 평생 팔지 않은 종목. 바로 코카콜라입니다. 오늘은 코카콜라 25년 백테스트를 통해, 두 사람의 운명이 왜 달라졌는지 확인해 보겠습니다. 그리고 이 결과를 바탕으로, 사회초년생에게는 어떤 투자 전략이 더 유리한지도 함께 살펴보겠습니다.", "콜라 따르는 실사", ["타이틀","코크 로고","칩(주가·증배·시총)"], ["로고팝"], None),
 ("이제 2000년으로 돌아가 보겠습니다. 은퇴자금 20만 달러 전액을 코카콜라에 투자했다고 가정했습니다. 그래프의 가로축은 시간, 세로축은 남아 있는 자산입니다. 생활비는 배당금으로 먼저 충당하고, 부족한 금액만큼 주식을 매도했습니다. 또한 생활비는 미국 물가상승률을 반영해 매년 증가하도록 설정했습니다. 결과는 생각보다 가혹했습니다. 매달 3천 달러를 사용한 경우에는 불과 5년 만인 2005년에 파산했습니다. 매달 2천 달러를 사용해도 2007년에 자산이 모두 소진됐습니다. 가장 적은 월 1천 달러를 사용한 경우조차 2015년을 버티지 못했습니다. 결국 은퇴자금 20만 달러로는 생활비를 아무리 줄여도 26년의 은퇴 생활을 버티기 어려웠습니다.", "종이 배경", ["라인차트","인출액 표","기준선","범례"], ["드로우인"], "야후 파이낸스 · FIRE 엔진 · 물가 US CPI 연동 · 세율 15%"),
 ("그렇다면 은퇴 자금이 두 배라면 어떨까요? 이번에는 40만 달러입니다. 확실히 결과는 달라졌습니다. 매달 1천 달러를 사용한 경우에는 26년이 지난 지금까지도 자산이 모두 소진되지 않았습니다. 하지만 매달 2천 달러와 3천 달러를 사용한 경우에는 결국 파산을 피하지 못했습니다.", "종이 배경", ["라인차트","인출액 표"], ["드로우인"], "야후 파이낸스 · FIRE 엔진 · 물가 반영"),
 ("이번에는 60만 달러로 시작해 보겠습니다. 놀랍게도 매달 1천 달러를 사용한 경우는 물론, 2천 달러를 사용한 경우에도 26년 동안 살아남았습니다. 하지만 매달 3천 달러를 사용한 경우에는 결국 자산이 모두 소진됐습니다. 같은 종목에 투자했는데도 은퇴 자금과 소비 습관에 따라 결과는 이렇게 크게 달라졌습니다.", "종이 배경", ["라인차트","인출액 표"], ["드로우인","강조팝"], "야후 파이낸스 · FIRE 엔진 · 물가 반영"),
 ("그런데 여기에는 중요한 조건이 하나 있습니다. 지금까지의 백테스트는 2000년을 시작점으로 삼았습니다. 바로 닷컴버블이 정점에 달했던 시기입니다. 당시에는 거의 모든 자산의 가격이 비정상적으로 높았습니다. 그리고 버블이 무너지면서 S&P500은 고점 대비 절반 가까이 하락했고, 나스닥은 무려 78퍼센트나 폭락했습니다. 시스코와 야후 같은 대표 기술주들은 90퍼센트 이상 무너지기도 했습니다. 즉, 지금까지의 결과는 은퇴 직후 대폭락을 맞는 상당히 보수적인 조건에서 나온 결과입니다.", "닷컴 크래시 실사", ["S&P500 라인","나스닥 라인","테크주 낙폭 표"], ["라인 드로우인"], "야후 파이낸스 · S&P500 −49% · 나스닥 −78% · 시스코 −89% · 야후 −97% · 노텔 −99%"),
 ("그렇다면 은퇴 시점을 닷컴버블이 무너진 뒤인 2002년으로 바꾸면 어떨까요? 투자 종목도 같고, 은퇴 자금도 같은 20만 달러입니다. 생활비 역시 물가를 반영해 똑같은 방식으로 인출했습니다. 2000년에 은퇴했을 때는 월 1천 달러를 사용해도 2015년에 자산이 소진됐습니다. 하지만 2002년에 시작하자 같은 돈으로 무려 10년을 더 버텼습니다. 결국 파산을 피하지는 못했지만, 단지 은퇴 시점이 2년 달라졌을 뿐인데 자산의 수명은 크게 늘어났습니다.", "종이 배경", ["라인차트","인출액 표"], ["드로우인"], "야후 파이낸스 · FIRE 엔진 · 2002 시작 · 물가 반영"),
 ("은퇴 자금이 40만 달러라면 차이는 더욱 커집니다. 매달 3천 달러를 사용한 경우에는 2013년에 자산이 소진됐습니다. 매달 2천 달러를 사용한 경우에도 2025년에는 결국 바닥을 드러냈습니다. 하지만 매달 1천 달러만 사용했다면 26년이 지난 뒤에도 살아남았습니다. 남은 자산은 약 127만 달러. 2000년에 같은 조건으로 시작했을 때의 약 72만 달러보다 훨씬 많습니다. 같은 종목과 같은 생활비라도 언제 은퇴했는지에 따라 마지막 자산은 거의 두 배 가까이 달라졌습니다.", "종이 배경", ["라인차트"], ["드로우인"], "야후 파이낸스 · FIRE 엔진 · 2002 시작"),
 ("이번에는 은퇴 자금 60만 달러입니다. 2000년에 은퇴했을 때는 매달 2천 달러를 사용한 경우에도 원금이 크게 줄어든 채 간신히 버티는 모습이었습니다. 하지만 2002년에 시작하자 결과는 완전히 달라졌습니다. 매달 1천 달러는 물론, 2천 달러를 사용한 경우에도 26년 동안 자산이 살아남았습니다. 다만 매달 3천 달러를 사용한 경우에는 시작 시점이 좋아졌어도 결국 파산을 피하지 못했습니다. 결국 은퇴의 결과를 결정한 것은 종목 하나만이 아니었습니다. 얼마를 가지고 시작했는지, 매달 얼마를 사용했는지, 그리고 언제 은퇴했는지가 모두 함께 작용했습니다. 똑같은 생활비인데도, 언제 시작했느냐가 이렇게 운명을 갈랐습니다.", "종이 배경", ["라인차트"], ["드로우인"], "야후 파이낸스 · FIRE 엔진 · 2002 시작"),
 ("지금까지의 결과를 한눈에 정리해 보겠습니다. 초록색은 26년 뒤에도 자산이 남은 경우, 붉은색은 그전에 자산이 소진된 경우입니다. 히트맵에서 가장 먼저 보이는 것은 매달 사용하는 생활비가 적을수록 은퇴 자산이 오래 살아남았다는 점입니다. 하지만 생활비만큼이나 중요한 변수가 하나 더 있었습니다. 바로 은퇴를 시작한 시점입니다. 같은 자산으로, 같은 코카콜라에 투자하고, 매달 같은 생활비를 사용했어도 닷컴버블 정점인 2000년에 은퇴했는지, 버블이 무너진 뒤인 2002년에 은퇴했는지에 따라 결과는 크게 달라졌습니다. 결국 안정적인 은퇴를 결정하는 것은 얼마나 많이 모았느냐만이 아닙니다. 은퇴 후 얼마를 쓰는지, 그리고 어떤 시장에서 은퇴를 시작하는지가 자산의 수명을 함께 결정합니다.", "종이 배경", ["3×3 생존 히트맵 ×2","범례"], ["셀 페이드"], "야후 파이낸스 · FIRE 엔진 요약 · 물가 반영"),
 ("여기서 이런 생각이 들 수 있습니다. \"그래서 코카콜라는 지금 사도 괜찮은 걸까?\" 25년 전에는 좋은 투자였을지 몰라도, 지금도 같은 결과를 기대할 수 있을까요? 이제 과거가 아니라, 현재의 코카콜라를 살펴보겠습니다.", "자판기 실사", ["전환 스크림"], ["디졸브"], None),
 ("먼저 코카콜라는 미국에만 의존하는 회사가 아닙니다. 전체 매출의 약 65퍼센트가 북미 밖에서 발생합니다. 유럽과 중남미, 아시아를 포함한 200여 개 국가에서 제품을 판매하고 있습니다. 특정 국가의 소비가 둔화되더라도 다른 지역이 이를 보완할 수 있는 구조입니다. 다만 해외 매출 비중이 높은 만큼 달러 강세와 환율 변동에는 영향을 받을 수 있습니다.", "보틀링 실사", ["세계지도","지역 핀"], ["핀팝"], "지역별 순매출 비중(개략)"),
 ("코카콜라의 가장 큰 장점 중 하나는 배당의 꾸준함입니다. 1963년 이후 무려 64년 연속으로 배당금을 인상했습니다. 오일쇼크와 닷컴버블, 글로벌 금융위기와 코로나까지 겪었지만 단 한 번도 배당을 줄이지 않았습니다. 배당주 투자자들이 코카콜라를 대표적인 배당 성장주로 평가하는 이유입니다.", "다크 배경", ["연도별 막대","증가곡선"], ["드로우인"], "1963~2026 분할조정 주당배당"),
 ("하지만 배당을 오래 줬다는 사실만으로는 충분하지 않습니다. 중요한 것은 앞으로도 계속 지급할 수 있느냐입니다. 현재 코카콜라는 벌어들인 조정 이익의 약 67퍼센트를 배당으로 지급하고 있습니다. 이익 전부를 배당하는 것이 아니라 약 3분의 1은 회사에 남기고 있는 셈입니다. 배당성향이 아주 낮지는 않지만, 코카콜라처럼 실적 변동이 크지 않은 기업에는 비교적 안정적인 수준입니다.", "레몬 소다 실사", ["게이지","컵"], ["채움 애니"], "조정 EPS 대비 배당성향 · 2025 배당 88억$"),
 ("최근 실적도 나쁘지 않습니다. 2026년 1분기 순매출은 125억 달러로 전년보다 12퍼센트 증가했습니다. 환율과 인수 효과 등을 제외한 유기적 매출 성장률도 10퍼센트를 기록했습니다. 글로벌 판매량은 3퍼센트 증가했고, 영업이익률도 35퍼센트까지 높아졌습니다. 단순히 가격만 올린 것이 아니라 판매량과 수익성이 함께 개선되고 있습니다. 성장이 매우 빠른 기업은 아니지만, 지금도 꾸준히 이익을 늘리고 있는 회사입니다.", "트레이더 배경", ["KPI 타일 4"], ["팝인"], "코카콜라 실적발표(IR) · 2026년 1분기"),
 ("그리고 코카콜라는 콜라만 판매하는 회사도 아닙니다. 코카콜라와 스프라이트 같은 탄산음료뿐 아니라, 생수와 스포츠음료, 주스와 유제품, 커피와 차까지 판매하고 있습니다. 전체 브랜드는 약 200개, 이 가운데 30개는 연간 매출 10억 달러가 넘는 메가브랜드입니다. 소비자의 취향이 바뀌어 탄산음료 시장이 흔들리더라도 다른 음료 사업이 이를 보완할 수 있습니다. 코카콜라의 진짜 경쟁력은 콜라 한 제품이 아니라, 전 세계 음료 시장을 장악한 브랜드와 유통망에 있습니다.", "소다 실사", ["4분할 그리드","제품 이미지"], ["순차 등장"], None),
 ("", "블루 소다 실사", ["전환 스크림"], ["디졸브"], "대사 없음 — 챕터 전환"),
 ("그렇다면 코카콜라에 투자한다면 어떻게 사는 것이 가장 좋을까요? 한 번에 목돈을 투자하는 것이 좋을까요? 아니면 매달 꾸준히 분할 매수하는 것이 좋을까요? 혹은 주가가 크게 하락할 때만 추가 매수하는 전략이 더 유리할까요? 이번에는 세 가지 투자 전략을 동일한 조건에서 직접 비교해 보겠습니다.", "콜라캔 실사", ["전환 스크림"], ["디졸브"], None),
 ("", "레몬 소다 실사", ["전환 스크림"], ["디졸브"], "대사 없음 — 챕터 전환"),
 ("첫 번째 투자자는 완벽한 매수 타이밍을 기다렸습니다. 주가가 크게 하락하면 그때 싸게 사겠다는 전략입니다. 평소에는 현금을 들고 있다가, 이전 고점 대비 30퍼센트 이상 하락했을 때만 투자를 시작합니다. 좋은 회사를 더 싸게 사는 것이 더 좋은 투자일까요?", "트레이더 배경", ["A 인물카드","현금 대기"], ["슬라이드인"], None),
 ("두 번째 투자자는 조금 달랐습니다. 시장 타이밍을 예측하지 않았습니다. 매달 같은 금액을 꾸준히 투자했습니다. 배당금도 모두 재투자하며 25년 동안 한 번도 원칙을 바꾸지 않았습니다. 과연 기다림이 더 좋은 결과를 만들었을까요? 아니면 꾸준함이 더 강했을까요?", "새싹 배경", ["B 인물카드","적립"], ["슬라이드인"], None),
 ("먼저 확인해 보겠습니다. 25년 동안 코카콜라가 30퍼센트 이상 하락한 순간은 과연 몇 번이나 있었을까요? 놀랍게도 단 5번뿐이었습니다. 폭락은 자주 오지 않았습니다. 즉, 이 전략은 대부분의 시간을 현금으로 기다리는 전략이었습니다.", "종이 배경", ["주가 라인","폭락 별표","트리거선"], ["드로우인"], "야후 파이낸스 · global_cup 엔진 · KO 일봉"),
 ("그 결과는 어땠을까요? 25년 동안 실제로 투자한 돈은 27만 4천 달러. 전체 준비한 현금보다 훨씬 적었습니다. 하지만 배당까지 모두 재투자했다면 최종 자산은 약 118만 달러. 배당을 재투자하지 않아도 84만 달러를 넘었습니다. 폭락을 기다리는 전략도 충분히 좋은 성과를 만들었습니다.", "종이 배경", ["라인차트","주식평가액 선","투입 계단"], ["드로우인"], "야후 파이낸스 · ko_smart 엔진 · 세율 15.4%"),
 ("이번에는 매달 1천 달러씩 꾸준히 투자해 보겠습니다. 총 투자금은 31만 9천 달러. 폭락 매수보다 조금 더 많은 돈을 투자했습니다. 배당을 모두 재투자했다면 최종 자산은 약 117만 달러. 배당을 쓰면서 투자해도 95만 달러를 만들었습니다. 시장 타이밍을 맞히지 않아도 시간은 충분히 강력했습니다.", "종이 배경", ["라인차트","원금 점선"], ["드로우인"], "야후 파이낸스 · ko_smart 엔진 · 월말 매수"),
 ("결과를 비교해 보겠습니다. 폭락만 기다린 전략은 118만 달러. 매달 꾸준히 투자한 전략은 117만 달러. 생각보다 차이는 거의 없었습니다. 오히려 꾸준히 투자한 전략은 언제 폭락이 올지 고민할 필요가 없었습니다. 결국 완벽한 타이밍을 기다리는 것보다 좋은 기업을 오랫동안 보유하는 것이 더 중요한 전략일 수도 있습니다.", "다크 배경", ["좌우 가로막대","비교"], ["드로우인"], "둘 다 원금 $319,000 동일"),
 ("그렇다면 코카콜라를 지금 포트폴리오에 담아도 될까요? 제 결론은 이렇습니다. 첫째, 배당의 안정성은 여전히 최고 수준입니다. 둘째, 성장은 빠르지 않지만 꾸준한 성장이 기대됩니다. 셋째, 현재 밸류에이션은 역사적으로 다소 높은 편입니다. 따라서 무리하게 한 번에 매수하기보다는 분할 매수가 조금 더 유리해 보입니다. 그리고 마지막. 코카콜라는 단기간에 큰 수익을 노리는 종목이 아니라, 배당을 재투자하며 오랫동안 복리를 쌓아가는 투자자에게 더 잘 어울리는 기업입니다.", "다크 배경", ["체크리스트 4","코크 로고","판정"], ["팝인"], None),
 ("오늘 백테스트의 결론은 워런 버핏의 이 한 문장으로 정리할 수 있을 것 같습니다. \"위대한 기업을 적정한 가격에 사서 아주 오래 보유하라.\" 결국 중요한 것은 완벽한 타이밍이 아니라, 좋은 기업을 오랫동안 함께하는 것이었습니다.", "건배 실사", ["대형 인용문","버핏 사진"], ["페이드"], None),
 ("이번 영상에서는 코카콜라를 25년 동안 직접 백테스트해 봤습니다. 다음에는 또 다른 배당주로 같은 방식의 백테스트를 진행해 보겠습니다. 보고 싶은 종목이 있다면 댓글로 남겨주세요. 영상이 도움이 되셨다면 구독과 좋아요도 부탁드립니다. 시청해 주셔서 감사합니다.", "건배 실사", ["CTA 타이틀","이모지 칩"], ["로고팝"], None),
]
assert len(SB)==len(S), f"{len(SB)} vs {len(S)}"

# 삭제할 씬 (0-indexed): 원본 22·24페이지(챕터 전환 카드)
DROP = {21, 23}
ORIG = [i for i in range(len(S)) if i not in DROP]   # 썸네일용 원본 인덱스
S  = [S[i]  for i in ORIG]
SB = [SB[i] for i in ORIG]

newdurs=[]
for i,s in enumerate(S):
    orig=s.get("dur",5000); script=SB[i][0]
    if script:
        chars=len(script.replace(" ",""))
        nd=max(orig, int(math.ceil((chars/RATE+BUF)))*1000)
    else:
        nd=orig
    newdurs.append(nd); S[i]["dur"]=nd

def fmt(ms):
    s=ms//1000; return f"00:{s//60:02d}:{s%60:02d}"
durs=newdurs; total=sum(durs); maxd=max(durs)
starts=[]; acc=0
for x in durs: starts.append(acc); acc+=x

def esc(t): return html.escape(t)
cards=[]
for i,(s,(script,bg,els,fxs,src)) in enumerate(zip(S,SB)):
    dur=durs[i]; start=starts[i]
    chars=len(script.replace(" ","")); rate=chars/(dur/1000) if script else 0
    hot=" hot" if rate>=6.5 else ""; quiet=" quiet" if not script else ""
    dat=s.get("data",{})
    title=(dat.get('title') or dat.get('main') or dat.get('eyebrow') or dat.get('num') or dat.get('kick') or dat.get('quote') or '')
    if isinstance(title,str) and title.startswith('data:'): title=''
    title=title.replace('{{coke}}','').replace('|',' · ').strip(' —')
    turi=thumb_uri(ORIG[i])
    if turi:
        thumb=f'<div class="thumb"><img loading="lazy" alt="씬 {i+1:02d}" src="{turi}"><span class="thnum">{i+1:02d}</span></div>'
    else:
        thumb=f'<div class="thumb ph"><div class="phnum">{i+1:02d}</div><div class="phttl">{esc(title) if title else "전환/인터루드"}</div><div class="phtpl">{s["tpl"]}</div></div>'
    header=(f'<header><span class="num">{i+1:02d}</span>'
            f'<span class="tc">{fmt(start)} <em>&rarr;</em> {fmt(start+dur)}</span>'
            f'<span class="dur">{dur/1000:.1f}s</span>'
            + (f'<span class="rate{hot}" title="발화 속도(공백 제외)">{rate:.1f}자/s</span>' if script else '')
            + f'<span class="durbar"><i style="width:{dur/maxd*100:.1f}%"></i></span></header>')
    sc=(f'<p class="script">{esc(script)}</p>' if script else f'<p class="script mute">{esc(src or "대사 없음")}</p>')
    tags='<div class="tags"><span class="chip bg" title="배경">'+esc(bg)+'</span>'
    for e in els: tags+=f'<span class="chip el" title="요소">{esc(e)}</span>'
    for f in fxs: tags+=f'<span class="chip fx" title="액션">{esc(f)}</span>'
    tags+='</div>'
    srcl=f'<p class="srcline"><b>자료</b> {esc(src)}</p>' if (src and script) else ''
    cards.append(f'<article class="card{quiet}" id="s{i+1}">{thumb}<div class="info">{header}{sc}{tags}{srcl}</div></article>')

CSS = """:root{--bg:#16181d;--panel:#1e2127;--line:#2b2f37;--ink:#e6e8ec;--mute:#8b919c;--amber:#e8a33d;--amber-dim:#8a6526;--coke:#e61a27}
html{background:var(--bg);scroll-behavior:smooth}
body{font-family:"Pretendard Variable",Pretendard,"Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR",sans-serif;color:var(--ink);line-height:1.7;margin:0;padding:0 20px 80px}
.wrap{max-width:960px;margin:0 auto}
.masthead{padding:56px 0 28px}
.eyebrow{font-family:ui-monospace,"SF Mono",Consolas,monospace;font-size:12px;letter-spacing:.18em;color:var(--coke);text-transform:uppercase}
h1{font-size:clamp(24px,4vw,34px);font-weight:800;letter-spacing:-.02em;margin:10px 0 6px;text-wrap:balance}
.sub{color:var(--mute);font-size:14.5px;margin:0}.sub b{color:var(--ink);font-weight:600}
.meta{display:flex;gap:28px;margin-top:22px;flex-wrap:wrap}
.meta div{display:flex;flex-direction:column;gap:2px}
.meta dt{font-size:11.5px;color:var(--mute);letter-spacing:.08em}
.meta dd{margin:0;font-size:20px;font-weight:700;font-variant-numeric:tabular-nums;font-family:ui-monospace,Consolas,monospace}
.kbdhint{color:#565c66;font-size:11px;margin-top:8px;font-family:ui-monospace,Consolas,monospace;letter-spacing:.06em}
.tlbox{position:sticky;top:0;z-index:5;background:linear-gradient(var(--bg) 78%,transparent);padding:14px 0 18px}
.tllabel{font-size:11px;color:var(--mute);letter-spacing:.12em;margin-bottom:6px;font-family:ui-monospace,Consolas,monospace;display:flex;justify-content:space-between}
.timeline{display:flex;gap:2px;height:26px;border-radius:4px;overflow:hidden;align-items:flex-end}
.seg{flex-basis:0;flex-grow:var(--g,1);min-width:3px;background:var(--panel);position:relative;height:100%}
.seg span{position:absolute;inset:auto 0 0 0;background:var(--amber-dim)}
.seg:hover,.seg:focus-visible{background:#2a2e36;outline:none}
.seg:hover span,.seg:focus-visible span{background:var(--amber)}
.list{display:flex;flex-direction:column;gap:14px;margin-top:26px}
.card{display:grid;grid-template-columns:300px 1fr;gap:0;background:var(--panel);border:1px solid var(--line);border-radius:6px;overflow:hidden;scroll-margin-top:78px}
.thumb{background:#000;aspect-ratio:16/9;position:relative}
.thumb img{width:100%;height:100%;object-fit:cover;display:block}
.thnum{position:absolute;left:8px;top:7px;font-family:ui-monospace,Consolas,monospace;font-size:12px;font-weight:700;color:#fff;background:rgba(0,0,0,.55);padding:1px 7px;border-radius:3px;font-variant-numeric:tabular-nums}
.thumb.ph{display:flex;flex-direction:column;justify-content:center;padding:14px 16px;background:radial-gradient(120% 120% at 0 0,#242832,#15171c)}
.phnum{font-family:ui-monospace,Consolas,monospace;font-size:13px;color:var(--coke);font-weight:700}
.phttl{font-size:14px;font-weight:700;margin-top:4px;line-height:1.35}
.phtpl{margin-top:auto;font-family:ui-monospace,Consolas,monospace;font-size:10.5px;color:var(--mute);letter-spacing:.08em;text-transform:uppercase}
.info{padding:16px 22px 18px;min-width:0}
.info header{display:flex;align-items:center;gap:14px;margin-bottom:8px;flex-wrap:wrap}
.num{font-family:ui-monospace,Consolas,monospace;font-size:22px;font-weight:700;color:var(--coke);font-variant-numeric:tabular-nums}
.tc{font-family:ui-monospace,Consolas,monospace;font-size:13px;color:var(--mute);font-variant-numeric:tabular-nums}
.tc em{font-style:normal;color:#565c66}
.dur{font-family:ui-monospace,Consolas,monospace;font-size:13px;color:var(--ink);font-variant-numeric:tabular-nums}
.durbar{flex:1;min-width:60px;height:3px;background:var(--line);border-radius:2px;overflow:hidden}
.durbar i{display:block;height:100%;background:var(--amber-dim)}
.rate{font-family:ui-monospace,Consolas,monospace;font-size:11.5px;color:var(--mute);border:1px solid var(--line);border-radius:3px;padding:1px 7px;font-variant-numeric:tabular-nums;white-space:nowrap}
.rate.hot{color:var(--amber);border-color:var(--amber-dim)}
.script{margin:0;font-size:14.5px;max-width:66ch;color:#c9cdd4}
.script.mute{color:#565c66;font-style:italic}
.card.quiet{opacity:.6}.card.quiet:hover{opacity:.9}
.card.kfocus{border-color:var(--coke);box-shadow:0 0 0 1px var(--amber-dim)}
.tags{display:flex;flex-wrap:wrap;gap:5px;margin-top:10px}
.chip{font-size:11px;line-height:1;padding:4px 9px;border-radius:11px;border:1px solid var(--line);color:var(--mute);white-space:nowrap}
.chip.bg{color:#8fa8c8;border-color:#31405a;background:rgba(63,101,158,.08)}
.chip.fx{color:var(--amber);border-color:var(--amber-dim);background:rgba(232,163,61,.07)}
.chip.fx::before{content:"\\25B6 ";font-size:8px;vertical-align:1px}
.srcline{margin-top:8px;font-size:12px;line-height:1.55;color:#79a8d9;border-left:2px solid #2c4258;padding-left:9px}
.srcline b{color:#9fc3e8;font-weight:600}
@media(max-width:720px){.card{grid-template-columns:1fr}}"""

segbar="".join(f'<a class="seg" style="--g:{durs[i]}" href="#s{i+1}" title="{i+1:02d}"><span style="height:{min(100,20+durs[i]/maxd*80):.0f}%"></span></a>' for i in range(len(S)))
JS = """<script>const cards=[...document.querySelectorAll('.card')];let ci=-1;
function focus(n){if(ci>=0)cards[ci].classList.remove('kfocus');ci=Math.max(0,Math.min(cards.length-1,n));cards[ci].classList.add('kfocus');cards[ci].scrollIntoView({behavior:'smooth',block:'center'});}
addEventListener('keydown',e=>{if(e.key==='ArrowRight'){e.preventDefault();focus(ci+1)}if(e.key==='ArrowLeft'){e.preventDefault();focus(ci-1)}});</script>"""
avg=total/len(S)/1000
OUT=f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>코카콜라, 시간이 만든 복리 — 스토리보드 — {len(S)}씬</title><style>{CSS}</style></head><body>
<div class="wrap"><header class="masthead">
<div class="eyebrow">Storyboard · cocacola · KO 25년 배당 백테스트</div>
<h1>코카콜라, 시간이 만든 복리 — 워런 버핏의 영원한 종목</h1>
<p class="sub">배투실 · <b>{len(S)}씬</b> 페이지별 대본 + 컷 구성 · 친근한 설명형</p>
<dl class="meta"><div><dt>총 길이</dt><dd>{fmt(total)[3:]}</dd></div><div><dt>씬</dt><dd>{len(S)}</dd></div>
<div><dt>평균 씬 길이</dt><dd>{avg:.1f}s</dd></div><div><dt>종목</dt><dd>KO</dd></div></dl>
<p class="kbdhint">&larr;/&rarr; 키로 이전·다음 씬 이동</p></header>
<nav class="tlbox" aria-label="씬 타임라인"><div class="tllabel"><span>TIMELINE — 폭은 씬 길이 비례 · 클릭하면 이동</span><span>00:00 &rarr; {fmt(total)[3:]}</span></div>
<div class="timeline">{segbar}</div></nav>
<main class="list">{''.join(cards)}</main></div>{JS}</body></html>"""
open("cocacola-storyboard-sb.html","w",encoding="utf-8").write(OUT)
print(f"→ 스토리보드 {len(S)}씬 · 총 {fmt(total)[3:]} · 평균 {avg:.1f}s → cocacola-storyboard-sb.html")
