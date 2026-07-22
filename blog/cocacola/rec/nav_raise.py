#!/usr/bin/env python3
"""실행 중인 firefox 창을 찾아 앞으로 올리고 포커스한다. (창 존재 확인용)"""
import os, sys, time
os.environ.setdefault('DISPLAY', ':1')
os.environ.setdefault('XAUTHORITY', '/run/user/1000/gdm/Xauthority')
from ewmh import EWMH

def find_ff(e):
    for w in e.getClientList():
        try:
            c = w.get_wm_class()
        except Exception:
            c = None
        if c and any('firefox' in (x or '').lower() for x in c):
            return w
    return None

def main():
    e = EWMH()
    ff = find_ff(e)
    if not ff:
        print("NO_FIREFOX")
        return 2
    try:
        e.setWmState(ff, 1, '_NET_WM_STATE_FULLSCREEN')
    except Exception as ex:
        print("fullscreen warn:", ex)
    e.setActiveWindow(ff)
    e.display.flush()
    time.sleep(0.3)
    try:
        nm = e.getWmName(ff)
        if isinstance(nm, bytes): nm = nm.decode('utf8','replace')
    except Exception:
        nm = '?'
    print("RAISED", hex(ff.id), nm)
    return 0

sys.exit(main())
