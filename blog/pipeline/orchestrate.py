"""최상위 러너. spec.json 하나로 data->backtest->fundamentals->story->scenes->deck->dub->render->assets.
단계별 --from/--to 재개. usage: python orchestrate.py --spec spec/KO.json [--from backtest --to deck]

STATUS: stub — 설계 wf_0c9ec72e-2f1. 구현 대기.
"""
from __future__ import annotations

def run_all(spec, _from=None, _to=None):
    """-> outputs"""
    raise NotImplementedError
