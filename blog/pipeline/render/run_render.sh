#!/bin/bash
# 덱 주입 -> 화면녹화 -> 오디오 믹싱. DUR을 total_ms에서 자동산출, OUT={ticker} 경로화.
# reuses: rec/record_full.sh, rec/mix_audio.sh, keep_fs.py, send_key.py, nav_raise.py
# STATUS: stub (설계 wf_0c9ec72e-2f1)
# usage: run_render.sh <spec.json>
echo "TODO: DUR=\$(deck total_ms); gtk-launch firefox _recload; record_full.sh; mix_audio.sh"; exit 1
