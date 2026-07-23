#!/usr/bin/env python3
"""지정한 창(win id)을 전체화면+최상단+포커스로 유지한다.
   다른 창이 끼어들어 전체화면이 풀리면 즉시 복구.
   사용: keep_fs.py <winid_hex> <지속초>
"""
import os, sys, time
os.environ.setdefault('DISPLAY', ':1')
os.environ.setdefault('XAUTHORITY', '/run/user/1000/gdm/Xauthority')
from ewmh import EWMH

def main():
    wid = int(sys.argv[1], 16)
    dur = float(sys.argv[2]) if len(sys.argv) > 2 else 800
    e = EWMH()
    # id로 창 객체 확보
    win = None
    for w in e.getClientList():
        if w.id == wid:
            win = w; break
    if win is None:
        # display 통해 직접
        win = e.display.create_resource_object('window', wid)
    heals = 0
    t0 = time.time()
    while time.time() - t0 < dur:
        try:
            st = e.getWmState(win, str=True) or []
            active = e.getActiveWindow()
            need = ('_NET_WM_STATE_FULLSCREEN' not in st) or (active is None) or (active.id != wid)
            if need:
                e.setActiveWindow(win)
                e.setWmState(win, 1, '_NET_WM_STATE_FULLSCREEN')
                e.display.flush()
                heals += 1
        except Exception as ex:
            pass
        time.sleep(0.7)
    print(f"keep_fs done, heals={heals}")

main()
