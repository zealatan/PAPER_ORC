#!/usr/bin/env python3
"""voice_timeline.json 대로 클립들을 절대시각에 배치해 전체 음성 트랙 생성."""
import json, os
from pydub import AudioSegment

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, '..')
TTSDIR = os.path.join(ROOT, 'tts')
TL = json.load(open(os.path.join(HERE, 'voice_timeline.json'), encoding='utf-8'))
OUT = os.path.join(ROOT, 'recordings', 'voice_track.wav')
os.makedirs(os.path.dirname(OUT), exist_ok=True)

total_ms = TL['total_ms'] + 500   # 꼬리 여유
track = AudioSegment.silent(duration=total_ms, frame_rate=48000)

placed = 0
for it in TL['items']:
    p = os.path.join(TTSDIR, it['file'])
    if not os.path.exists(p):
        print('  누락:', it['file']); continue
    clip = AudioSegment.from_file(p).set_frame_rate(48000)
    track = track.overlay(clip, position=it['abs_ms'])
    placed += 1

track = track.set_channels(2)
track.export(OUT, format='wav')
print(f"음성 트랙: {OUT}")
print(f"배치 클립: {placed}/{len(TL['items'])}")
print(f"길이: {len(track)/1000:.1f}s")
