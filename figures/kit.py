"""Мини-библиотека для схем конспектов.

Цвета — палитра 3Blue1Brown; scripts/paper-style.py перекрашивает их под светлую
и тёмную темы, поэтому здесь используем только константы ниже.
Ширина схемы — 760 единиц; на телефоне она ужимается примерно вдвое, поэтому
подписи не мельче 14.
"""
from html import escape

BG = "#141a24"      # фон / тёмный текст на цветной заливке
NODE = "#1e2836"    # заливка вершин и клеток
NODE2 = "#151f30"   # вторичная заливка
TEXT = "#dfe7f1"
TEXT2 = "#c2cdde"
MUTED = "#9aa4b2"
AXIS = "#7c8aa0"
EDGE = "#3b4a63"
GRID = "#33415a"
BLUE = "#58c4dd"
GREEN = "#83c167"
ORANGE = "#ff8c1a"
YELLOW = "#ffff00"
RED = "#fc6255"
PURPLE = "#c78bff"

W = 760


def _a(**kw):
    out = []
    for k, v in kw.items():
        if v is None:
            continue
        k = k.rstrip("_").replace("_", "-")
        out.append(f'{k}="{v}"')
    return " ".join(out)


class Fig:
    def __init__(self, fid, h, w=W, title=None, sub=None):
        self.fid, self.w, self.h = fid, w, h
        self.parts = []
        self.markers = {}
        self.parts.append(f'<rect x="0" y="0" width="{w}" height="{h}" rx="14" fill="{BG}"/>')
        y = 36
        if title:
            self.text(32, y, title, size=18, weight=700)
            y += 26
        if sub:
            self.text(32, y, sub, size=14.5, fill=MUTED)
        self.top = y + 14 if (title or sub) else 24

    # --- примитивы ---
    def raw(self, s):
        self.parts.append(s)

    def rect(self, x, y, w, h, fill=NODE, stroke=None, sw=1.5, rx=6, op=None, dash=None):
        self.parts.append(f'<rect {_a(x=x, y=y, width=w, height=h, rx=rx, fill=fill, stroke=stroke, stroke_width=sw if stroke else None, opacity=op, stroke_dasharray=dash)}/>')

    def circle(self, cx, cy, r, fill=NODE, stroke=None, sw=2, op=None):
        self.parts.append(f'<circle {_a(cx=cx, cy=cy, r=r, fill=fill, stroke=stroke, stroke_width=sw if stroke else None, opacity=op)}/>')

    def text(self, x, y, s, size=15, fill=TEXT, anchor="start", weight=None, italic=False, raw=False):
        body = s if raw else escape(s)
        self.parts.append(f'<text {_a(x=x, y=y, fill=fill, font_size=size, font_weight=weight, text_anchor=anchor, font_style="italic" if italic else None)}>{body}</text>')

    def _marker(self, color):
        if color not in self.markers:
            mid = f"{self.fid}-ar{len(self.markers)}"
            self.markers[color] = mid
        return self.markers[color]

    def line(self, x1, y1, x2, y2, stroke=EDGE, sw=2, dash=None, arrow=False, op=None):
        m = f'url(#{self._marker(stroke)})' if arrow else None
        self.parts.append(f'<line {_a(x1=x1, y1=y1, x2=x2, y2=y2, stroke=stroke, stroke_width=sw, stroke_dasharray=dash, marker_end=m, opacity=op, stroke_linecap="round")}/>')

    def path(self, d, stroke=EDGE, sw=2, fill="none", dash=None, arrow=False, op=None):
        m = f'url(#{self._marker(stroke)})' if arrow else None
        self.parts.append(f'<path {_a(d=d, stroke=stroke, stroke_width=sw, fill=fill, stroke_dasharray=dash, marker_end=m, opacity=op, stroke_linecap="round", stroke_linejoin="round")}/>')

    def polyline(self, pts, stroke=BLUE, sw=3, fill="none", op=None):
        p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.parts.append(f'<polyline {_a(points=p, stroke=stroke, stroke_width=sw, fill=fill, opacity=op, stroke_linejoin="round", stroke_linecap="round")}/>')

    # --- составные элементы ---
    def node(self, x, y, label, color=BLUE, r=18, size=15, fill=NODE, tcolor=TEXT):
        self.circle(x, y, r, fill=fill, stroke=color, sw=2.5)
        self.text(x, y + size * 0.35, str(label), size=size, anchor="middle", weight=700, fill=tcolor)

    def cell(self, x, y, label, w=40, h=40, fill=NODE, stroke=GRID, tcolor=TEXT, size=16, weight=700):
        self.rect(x, y, w, h, fill=fill, stroke=stroke, rx=6)
        if label != "":
            self.text(x + w / 2, y + h / 2 + size * 0.36, str(label), size=size, anchor="middle", fill=tcolor, weight=weight)

    def edge(self, x1, y1, x2, y2, r1=18, r2=18, color=EDGE, sw=2, arrow=True, dash=None, bend=0):
        """Ребро между центрами двух вершин с отступом на радиусы."""
        import math
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy) or 1
        ux, uy = dx / d, dy / d
        sx, sy = x1 + ux * r1, y1 + uy * r1
        ex, ey = x2 - ux * (r2 + (4 if arrow else 0)), y2 - uy * (r2 + (4 if arrow else 0))
        if bend:
            mx, my = (sx + ex) / 2 - uy * bend, (sy + ey) / 2 + ux * bend
            self.path(f"M{sx:.1f},{sy:.1f} Q{mx:.1f},{my:.1f} {ex:.1f},{ey:.1f}", stroke=color, sw=sw, arrow=arrow, dash=dash)
        else:
            self.line(round(sx, 1), round(sy, 1), round(ex, 1), round(ey, 1), stroke=color, sw=sw, arrow=arrow, dash=dash)

    def legend(self, x, y, items, size=14, gap=22):
        """items: [(color, текст, 'dot'|'line'|'box')] — вертикальный список."""
        for i, (c, t, kind) in enumerate(items):
            yy = y + i * gap
            if kind == "line":
                self.line(x, yy - 5, x + 22, yy - 5, stroke=c, sw=3)
            elif kind == "box":
                self.rect(x, yy - 13, 18, 14, fill=c, rx=3)
            else:
                self.circle(x + 8, yy - 5, 6, fill=c)
            self.text(x + 30, yy, t, size=size, fill=TEXT2)

    def note(self, y, s, color=TEXT2, size=15, x=32, weight=None):
        self.text(x, y, s, size=size, fill=color, weight=weight)

    def svg(self):
        defs = ""
        if self.markers:
            ms = "".join(
                f'<marker id="{mid}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                f'<path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
                for c, mid in self.markers.items()
            )
            defs = f"<defs>{ms}</defs>"
        return (f'<svg viewBox="0 0 {self.w} {self.h}" role="img" xmlns="http://www.w3.org/2000/svg">'
                + defs + "".join(self.parts) + "</svg>")
