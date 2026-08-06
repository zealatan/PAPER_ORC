"""② 데이터 페치 — 골든 엔진(fire_engine) 재사용: 배당 재투자·세금 반영.

'일시 추매(lump-sum injection)'는 엔진 네이티브 기능이 아니므로 2개 트랜치로 모델링:
  트랜치A = invest_each @ buy_date, 트랜치B = injection.amount_each @ inj_date.
각 트랜치를 run_fire_backtest(annual_withdrawal=0, reinvest_dividends=True)로 돌려
날짜 정렬 후 합산 → 배당·세금이 반영된 평가액 시계열.
fire_engine 은 공유 엔진이라 read-only import 만 한다(수정 금지).
"""
import sys
import os

_ENGINE_DIR = '/home/messi/PAPER_ORC/global_cup_suite/global_cup'
if _ENGINE_DIR not in sys.path:
    sys.path.insert(0, _ENGINE_DIR)
import fire_engine  # noqa: E402  (read-only 공유 엔진)


def _is_kr(code):
    return code.upper().endswith('.KS') or code.upper().endswith('.KQ')


def _fetch(code, start, end):
    """raw close + dividends (auto_adjust=False → 배당 분리)."""
    import yfinance as yf
    df = yf.Ticker(code).history(start=start, end=end, auto_adjust=False)
    close = df['Close'].dropna()
    div = df['Dividends'] if 'Dividends' in df else None
    if div is not None:
        div = div[div > 0]
    import pandas as pd
    if div is None:
        div = pd.Series(dtype=float)
    return close, div


def _pv_map(close, div, amount, start_date, end_date, tax):
    """단일 트랜치 → {날짜str: 평가액}. 인출0·배당재투자."""
    import datetime as dt
    r = fire_engine.run_fire_backtest(
        close, div, float(amount),
        annual_withdrawal=0.0, strategy='fixed_nominal', frequency='monthly',
        tax_rate_pct=tax, reinvest_dividends=True, reinvest_surplus=True,
        start_date=dt.date.fromisoformat(start_date),
        end_date=dt.date.fromisoformat(end_date),
    )
    if r is None:
        return {}
    tl = r.timeline_df
    out = {}
    for _, row in tl.iterrows():
        d = row['Date']
        ds = (d.strftime('%Y-%m-%d') if hasattr(d, 'strftime') else str(d)[:10])
        out[ds] = round(float(row['Portfolio Value']))
    return out


def build_series(scn):
    tickers = scn['tickers']
    buy = scn['buy_date']
    asof = scn['asof']
    inv_each = scn['invest_each']
    inj = scn.get('injection')
    import datetime as dt
    end = (dt.date.fromisoformat(asof) + dt.timedelta(days=2)).isoformat()

    # 공통 거래일 축(첫 종목 기준)
    first_code = next(iter(tickers.values()))['code']
    base_close, _ = _fetch(first_code, buy, end)
    all_dates = [d.strftime('%Y-%m-%d') for d in base_close.index]
    all_dates = [d for d in all_dates if buy <= d <= asof]

    inj_date = None
    inj_idx = None
    add = 0
    if inj:
        cand = [d for d in all_dates if d <= inj['date']]
        inj_date = cand[-1] if cand else all_dates[0]
        inj_idx = all_dates.index(inj_date)
        add = inj['amount_each']
    INV = inv_each + add

    out = {}
    for key, tk in tickers.items():
        code = tk['code']
        tax = 15.4 if _is_kr(code) else 15.0
        close, div = _fetch(code, buy, end)
        px = [round(float(close.loc[close.index.strftime('%Y-%m-%d') == d].iloc[0]))
              if (close.index.strftime('%Y-%m-%d') == d).any() else None
              for d in all_dates]
        # 결측 전값 채움
        last = next(v for v in px if v)
        px = [v if v else last for v in px] if None in px else px
        filled = []
        cur = None
        for v in px:
            cur = v if v else cur
            filled.append(cur if cur else last)
        px = filled

        # 트랜치A(전체) = 100만 buy→asof, 배당재투자 (windows·단일보유용)
        A = _pv_map(close, div, inv_each, buy, asof, tax)
        # 트랜치B = 추매액 inj→asof
        B = _pv_map(close, div, add, inj_date, asof, tax) if inj else {}

        single = [A.get(d, A.get(all_dates[max(0, i - 1)], inv_each)) for i, d in enumerate(all_dates)]
        value = []
        for i, d in enumerate(all_dates):
            a = A.get(d, single[i])
            b = (B.get(d, 0) if (inj_idx is not None and i > inj_idx) else 0)
            value.append(round(a + b))

        redFrom = len(value)
        if inj_idx is not None:
            k = len(value)
            for i in range(len(value) - 1, inj_idx, -1):
                if value[i] < INV:
                    k = i
                else:
                    break
            redFrom = k

        out[key] = {
            'name': tk['name'], 'color': tk['color'], 'code': code,
            'dates': all_dates, 'price': px, 'value': value, 'single': single,
            'pre': (value[inj_idx] if inj_idx is not None else value[-1]),
            'final': value[-1], 'invested': INV, 'redFrom': redFrom, 'inj_idx': inj_idx,
        }
    meta = {'buy_date': buy, 'asof': asof, 'invest_each': inv_each,
            'inj_date': inj_date, 'inj_idx': inj_idx, 'add': add, 'INV': INV,
            'tickers': tickers}
    return out, meta


def window(series, d0, d1):
    """[d0,d1] 구간을 시작=100만 리베이스. 배당재투자 반영(single 사용)."""
    dates = series['dates']
    i0 = next(i for i, d in enumerate(dates) if d >= d0)
    i1 = max(i for i, d in enumerate(dates) if d <= d1)
    base = series.get('single', series['value'])
    b0 = base[i0] if base[i0] else 1_000_000
    inv = 1_000_000
    return {'dates': dates[i0:i1 + 1],
            'value': [round(inv * base[i] / b0) for i in range(i0, i1 + 1)],
            'invest': inv, 'name': series['name'], 'color': series['color']}


# ── EP2: 일시매수 vs 분할매수(DCA) — fire_engine 트랜치 합산 ──────────────
def _tranche_series(close, div, amount, start_date, asof, tax, reinvest):
    import datetime as dt
    r = fire_engine.run_fire_backtest(
        close, (div if reinvest else div.iloc[0:0]), float(amount),
        annual_withdrawal=0.0, strategy='fixed_nominal', frequency='monthly',
        tax_rate_pct=tax, reinvest_dividends=reinvest, reinvest_surplus=reinvest,
        start_date=dt.date.fromisoformat(start_date), end_date=dt.date.fromisoformat(asof))
    if r is None:
        return {}
    out = {}
    for _, row in r.timeline_df.iterrows():
        d = row['Date']
        out[d.strftime('%Y-%m-%d') if hasattr(d, 'strftime') else str(d)[:10]] = float(row['Portfolio Value'])
    return out


def build_dca(scn):
    """QQQ 일시매수 vs 분할매수(N개월). 두 전략 동일 총액 투입.
    반환: {'dates', 'ticker', 'total', 'lump':{value[],mdd,final_mult,recover_m,loss_m},
           'dca':{...}, 'buy_date','asof'}
    """
    import datetime as dt
    tk = scn['ticker']
    code = tk['code']
    buy = scn['buy_date']
    asof = scn['asof']
    total = scn['invest_total']
    nmon = scn.get('dca_months', 6)
    reinvest = scn.get('reinvest_dividends', True)
    tax = 15.4 if _is_kr(code) else 15.0

    close, div = _fetch(code, buy, (dt.date.fromisoformat(asof) + dt.timedelta(days=3)).isoformat())
    all_dates = [d.strftime('%Y-%m-%d') for d in close.index if buy <= d.strftime('%Y-%m-%d') <= asof]

    def on_after(t):
        return next(d for d in all_dates if d >= t)

    # 기여 스케줄
    lump_sched = [(buy, total)]
    b = dt.date.fromisoformat(buy)
    dca_sched = []
    for i in range(nmon):
        m = (b.replace(day=1) + dt.timedelta(days=32 * i)).replace(day=1).isoformat()
        dca_sched.append((on_after(m), total / nmon))

    def combine(sched):
        maps = [(_tranche_series(close, div, amt, sd, asof, tax, reinvest), sd, amt) for sd, amt in sched]
        value, invested = [], []
        for d in all_dates:
            v = sum(mp.get(d, 0.0) for mp, sd, amt in maps if d >= sd)
            inv = sum(amt for mp, sd, amt in maps if d >= sd)
            value.append(round(v))
            invested.append(round(inv))
        return value, invested

    def stats(value, invested, sched_dates):
        mdd = min((value[i] / invested[i] - 1) for i in range(len(value)) if invested[i] > 0)
        final_mult = value[-1] / invested[-1]
        # 원금회복: 마지막 기여 이후 value>=invested 첫 시점까지 개월
        last_buy = max(sched_dates)
        rec = None
        loss = 0
        below = False
        for i, d in enumerate(all_dates):
            if invested[i] <= 0:
                continue
            if value[i] < invested[i]:
                below = True
            elif below and rec is None and d > last_buy:
                a = dt.date.fromisoformat(buy)
                bb = dt.date.fromisoformat(d)
                rec = (bb.year - a.year) * 12 + (bb.month - a.month)
        # 손실기간(개월): value<invested 인 달 수 근사
        loss_days = sum(1 for i in range(len(value)) if invested[i] > 0 and value[i] < invested[i])
        loss_m = round(loss_days / 21)
        return {'mdd': round(mdd * 100, 1), 'final_mult': round(final_mult, 2),
                'recover_m': rec, 'loss_m': loss_m}

    lv, li = combine(lump_sched)
    dv, di = combine(dca_sched)
    out = {
        'dates': all_dates, 'ticker': tk, 'total': total, 'buy_date': buy, 'asof': asof,
        'dca_months': nmon,
        'lump': {'value': lv, 'invested': li, **stats(lv, li, [s[0] for s in lump_sched])},
        'dca': {'value': dv, 'invested': di, **stats(dv, di, [s[0] for s in dca_sched])},
    }
    return out


def price_line(code, d0, d1, base=100):
    """임의 구간 정규화 가격라인(배당 제외 순수 가격). {dates, value(base=d0)}"""
    close, _ = _fetch(code, d0, d1)
    ds = [d.strftime('%Y-%m-%d') for d in close.index]
    px = [float(v) for v in close.values]
    if not px:
        return {'dates': [], 'value': []}
    p0 = px[0]
    return {'dates': ds, 'value': [round(base * p / p0, 2) for p in px]}


# ── EP3: 고분배 ETF(QYLD) vs 시장(SPY) — 총수익 vs 분배율 ──────────────
def build_income(scn):
    """QYLD(고분배) vs SPY(시장). 총수익(배당재투자)·가격만·분배금누적.
    반환: {dates, buy_date, asof, invest,
      QYLD:{name,color, total[], price[], dist_cum[], total_mult, price_chg, yield_pct, dist_cum_final},
      SPY :{name,color, total[], price[], total_mult, price_chg}}
    """
    import datetime as dt
    tk = scn['ticker']          # QYLD
    bm = scn['benchmark']       # SPY
    buy = scn['buy_date']
    asof = scn['asof']
    invest = scn['invest']
    end = (dt.date.fromisoformat(asof) + dt.timedelta(days=3)).isoformat()

    # 공통 축(QYLD 기준)
    qclose, qdiv = _fetch(tk['code'], buy, end)
    all_dates = [d.strftime('%Y-%m-%d') for d in qclose.index if buy <= d.strftime('%Y-%m-%d') <= asof]

    def total_map(code):
        c, dv = _fetch(code, buy, end)
        return _tranche_series(c, dv, invest, buy, asof, 15.0, True)  # 배당재투자 총수익

    def price_map(code):
        c, dv = _fetch(code, buy, end)
        return _tranche_series(c, dv.iloc[0:0], invest, buy, asof, 15.0, False)  # 가격만

    def align(mp):
        out = []
        last = invest
        for d in all_dates:
            last = mp.get(d, last)
            out.append(round(last))
        return out

    q_total = align(total_map(tk['code']))
    q_price = align(price_map(tk['code']))
    s_total = align(total_map(bm['code']))
    s_price = align(price_map(bm['code']))

    def _mdd(v):
        peak = v[0]
        m = 0.0
        for x in v:
            if x > peak:
                peak = x
            dd = x / peak - 1
            if dd < m:
                m = dd
        return round(m * 100, 1)

    # QYLD 분배금 누적(현금 수령 가정): shares0 * cumsum(dps)
    p0 = float(qclose.iloc[0])
    sh0 = invest / p0
    qdiv2 = qdiv.copy()
    qdiv2.index = [d.strftime('%Y-%m-%d') for d in qdiv2.index]
    dist_cum = []
    acc = 0.0
    for d in all_dates:
        if d in qdiv2.index:
            acc += float(qdiv2.loc[d]) * (1 if not hasattr(qdiv2.loc[d], '__len__') else 0)
        # 안전: 같은 날짜 중복 합산
        dist_cum.append(round(acc * sh0))
    # 최근 12개월 분배율
    import datetime as _dt
    cutoff = (_dt.date.fromisoformat(asof) - _dt.timedelta(days=365)).isoformat()
    y1 = sum(float(v) for k, v in zip(qdiv2.index, qdiv2.values) if k >= cutoff)
    yield_pct = round(y1 / float(qclose.iloc[-1]) * 100, 1)

    out = {
        'dates': all_dates, 'buy_date': buy, 'asof': asof, 'invest': invest,
        'QYLD': {'name': tk['name'], 'color': tk['color'], 'total': q_total, 'price': q_price,
                 'dist_cum': dist_cum, 'total_mult': round(q_total[-1] / invest, 2),
                 'price_chg': round(q_price[-1] / invest * 100 - 100), 'yield_pct': yield_pct,
                 'dist_cum_final': dist_cum[-1], 'mdd': _mdd(q_total),
                 'ret_pct': round(q_total[-1] / invest * 100 - 100)},
        'SPY': {'name': bm['name'], 'color': bm['color'], 'total': s_total, 'price': s_price,
                'total_mult': round(s_total[-1] / invest, 2),
                'price_chg': round(s_price[-1] / invest * 100 - 100), 'mdd': _mdd(s_total),
                'ret_pct': round(s_total[-1] / invest * 100 - 100)},
    }
    return out
