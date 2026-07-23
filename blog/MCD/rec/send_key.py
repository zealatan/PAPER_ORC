#!/usr/bin/env python3
"""firefox 창을 포커스하고 키를 보낸다. XTEST fake input.
   사용: send_key.py <key>[,<mod>...]   예) send_key.py F5   / send_key.py r,ctrl,shift / send_key.py F11
"""
import os, sys, time
os.environ.setdefault('DISPLAY', ':1')
os.environ.setdefault('XAUTHORITY', '/run/user/1000/gdm/Xauthority')
from Xlib import X, XK
from Xlib.display import Display
from Xlib.ext import xtest
from ewmh import EWMH

KEYSYMS = {
    'F5': XK.XK_F5, 'F11': XK.XK_F11, 'r': XK.XK_r, 'Return': XK.XK_Return,
    'space': XK.XK_space, 'Escape': XK.XK_Escape, 'Home': XK.XK_Home,
}
MODS = {'ctrl': XK.XK_Control_L, 'shift': XK.XK_Shift_L, 'alt': XK.XK_Alt_L}

def main():
    spec = sys.argv[1] if len(sys.argv) > 1 else 'F5'
    parts = spec.split(',')
    key = parts[0]
    mods = parts[1:]

    e = EWMH()
    ff = None
    for w in e.getClientList():
        try:
            c = w.get_wm_class()
        except Exception:
            c = None
        if c and any('firefox' in (x or '').lower() for x in c):
            ff = w
    if not ff:
        print("NO_FIREFOX"); return 2
    e.setActiveWindow(ff)
    e.display.flush()
    time.sleep(0.4)

    d = Display()
    def kc(sym): return d.keysym_to_keycode(sym)
    mod_codes = [kc(MODS[m]) for m in mods]
    key_code = kc(KEYSYMS.get(key))
    for mc in mod_codes:
        xtest.fake_input(d, X.KeyPress, mc)
    xtest.fake_input(d, X.KeyPress, key_code)
    d.sync(); time.sleep(0.05)
    xtest.fake_input(d, X.KeyRelease, key_code)
    for mc in reversed(mod_codes):
        xtest.fake_input(d, X.KeyRelease, mc)
    d.sync()
    print(f"SENT {spec}")
    return 0

sys.exit(main())
