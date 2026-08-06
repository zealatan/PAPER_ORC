#!/usr/bin/env python3
"""만화 백테스트 쇼츠 파이프라인 드라이버.
사용: python build.py --scenario scenario.json [--only N] [--from concat|reframe] [--no-shorts]
"""
import argparse
import json
import os
import sys
import importlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lib import panels, data, render, scene_common  # noqa

# 종목 로고 기본 경로(scenario['assets']로 오버라이드 가능)
DEFAULT_ASSETS = {
    'SEC':   '/home/messi/PAPER_ORC/blog/golden_shorts_accum/assets/sec_logo.png',
    'HYNIX': '/home/messi/PAPER_ORC/blog/golden_shorts_accum/assets/skh_logo.png',
}


def resolve_tokens(params, meta):
    """params 안의 'buy_date'/'asof' 토큰을 실제 날짜로 치환."""
    def rt(v):
        if v == 'buy_date':
            return meta['buy_date']
        if v == 'asof':
            return meta['asof']
        if v == 'inj_date':
            return meta['inj_date']
        return v
    out = {}
    for k, v in (params or {}).items():
        if isinstance(v, list):
            out[k] = [rt(x) for x in v]
        else:
            out[k] = rt(v)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scenario', required=True)
    ap.add_argument('--only', type=int, default=None, help='해당 컷만 재생성')
    ap.add_argument('--start', default='panels', choices=['panels', 'scenes', 'concat', 'reframe'])
    ap.add_argument('--no-shorts', action='store_true')
    ap.add_argument('--outdir', default=None)
    args = ap.parse_args()

    scn = json.load(open(args.scenario, encoding='utf-8'))
    base = os.path.dirname(os.path.abspath(args.scenario))
    out = args.outdir or os.path.join(base, 'out')
    os.makedirs(out, exist_ok=True)
    scenes_dir = os.path.join(out, 'scenes')
    os.makedirs(scenes_dir, exist_ok=True)
    panels_dir = os.path.join(out, 'panels')

    order = ['panels', 'scenes', 'concat', 'reframe']
    run_from = order.index(args.start)

    # ① 패널
    if run_from <= 0:
        print('① 패널 추출')
        cartoon = os.path.join(base, scn['cartoon'])
        panels.extract(cartoon, panels_dir)
    panel_paths = [os.path.join(panels_dir, f'panel_{i}.png') for i in range(1, 9)]

    # ② 데이터 + 에셋
    print('② 데이터 페치')
    income = None
    dca = None
    if 'benchmark' in scn:
        income = data.build_income(scn)
        series, meta = {}, {'buy_date': scn['buy_date'], 'asof': scn['asof'], 'ticker': scn['ticker']}
    elif 'ticker' in scn:
        dca = data.build_dca(scn)
        series, meta = {}, {'buy_date': scn['buy_date'], 'asof': scn['asof'], 'ticker': scn['ticker']}
    else:
        series, meta = data.build_series(scn)
    assets_cfg = {**DEFAULT_ASSETS, **scn.get('assets', {})}
    assets = {k: scene_common.b64(p) for k, p in assets_cfg.items() if os.path.exists(p)}

    # ③④ 씬 빌드+렌더
    durs = scn.get('durations', {})
    scene_mp4s = []
    for pd in scn['panels']:
        n = pd['n']
        mp4 = os.path.join(scenes_dir, f'scene_{n}.mp4')
        scene_mp4s.append(mp4)
        if run_from > 1:
            continue
        if args.only and n != args.only:
            continue
        otype = pd['overlay']
        print(f'③ 씬 {n} · overlay={otype}')
        mod = importlib.import_module(f'lib.overlays.{otype}')
        P = {
            'bg': scene_common.b64(panel_paths[n - 1]),
            'panel_png': panel_paths[n - 1],
            'series': series, 'meta': meta, 'dca': dca, 'income': income,
            'params': resolve_tokens(pd.get('params', {}), meta),
            'assets': assets, 'helpers': scene_common.HELPERS_JS,
        }
        html = mod.build(P)
        html_path = os.path.join(scenes_dir, f'scene_{n}.html')
        open(html_path, 'w', encoding='utf-8').write(html)
        hold = pd.get('hold')
        if hold is not None:
            print(f'④ 렌더 {n} (autohold +{hold}s)')
            render.render_scene(html_path, None, mp4, autohold=float(hold))
        else:
            dur = float(durs.get(str(n), 3.0))
            print(f'④ 렌더 {n} ({dur}s)')
            render.render_scene(html_path, dur, mp4)

    ep = scn.get('id') or os.path.basename(os.path.dirname(os.path.abspath(args.scenario))) or 'ep'
    full = os.path.join(out, f'{ep}_full.mp4')
    if run_from <= 2:
        print('⑤ 통합 concat')
        render.concat(scene_mp4s, full)

    if not args.no_shorts:
        shorts = os.path.join(out, f'{ep}_shorts.mp4')
        sh = scn.get('shorts', {})
        print('⑥ 쇼츠 리프레임')
        render.reframe_shorts(full, shorts, sh.get('inner_width', 1004),
                              sh.get('bg', 'white'), sh.get('valign', 'center'))
        print('완료:', shorts)
    else:
        print('완료:', full)


if __name__ == '__main__':
    main()
