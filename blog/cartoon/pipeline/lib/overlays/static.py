"""static — 만화 원본 그대로(모션 없음)."""
from lib.scene_common import html_skeleton


def build(P):
    js = P['helpers'] + "window.__renderAt=function(t){};"
    return html_skeleton(P['bg'], "", "", js)
