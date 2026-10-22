import math
from kit import *

NOTE = "parallel-a/parallel-a-zan5-nevzveshennye-grafy.html"


def twosat():
    f = Fig("nv1", 400, title="2-SAT: граф импликаций для (x ∨ y)(¬x ∨ z)(¬y ∨ ¬z)",
            sub="Скобка (a ∨ b) даёт рёбра ¬a → b и ¬b → a — рёбра идут парами.")
    pos = {"¬x": (140, 150), "y": (300, 150), "¬z": (220, 280),
           "x": (480, 150), "z": (640, 150), "¬y": (560, 280)}
    for a, b, c in [("¬x", "y", ORANGE), ("y", "¬z", ORANGE), ("¬z", "¬x", ORANGE),
                    ("¬y", "x", BLUE), ("x", "z", BLUE), ("z", "¬y", BLUE)]:
        f.edge(*pos[a], *pos[b], color=c, sw=2.6, arrow=True)
    for n, (x, y) in pos.items():
        c = ORANGE if n in ("¬x", "y", "¬z") else BLUE
        f.node(x, y, n, color=c, r=24, size=17)
    f.text(220, 118, "КСС 1", size=15, fill=ORANGE, anchor="middle", weight=700)
    f.text(560, 118, "КСС 2", size=15, fill=BLUE, anchor="middle", weight=700)
    f.note(350, "x и ¬x в разных КСС — формула выполнима.", size=14.5, color=TEXT2)
    f.note(374, "Компоненты несравнимы, годятся оба выбора (КСС 1 или КСС 2 истинной).", size=14, color=MUTED)
    return f.svg()


def konig():
    L = ["a1", "a2", "a3", "a4", "a5"]
    R = ["b1", "b2", "b3", "b4", "b5"]
    E = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 2), (3, 2), (3, 3), (4, 3)]
    nl, nr = len(L), len(R)
    adj = [[] for _ in range(nl)]
    for a, b in E:
        adj[a].append(b)
    mt = [-1] * nr
    ml = [-1] * nl

    def tr(v, seen):
        for t in adj[v]:
            if mt[t] < 0 or (mt[t] not in seen and (seen.add(mt[t]) or tr(mt[t], seen))):
                mt[t] = v; ml[v] = t
                return True
        return False
    for v in range(nl):
        tr(v, {v})
    vis_l, vis_r = set(), set()

    def walk(v):
        vis_l.add(v)
        for t in adj[v]:
            if mt[t] >= 0 and ml[v] != t and mt[t] not in vis_l:
                vis_r.add(t); walk(mt[t])
    for v in range(nl):
        if ml[v] < 0:
            walk(v)
    for v in list(vis_l):
        for t in adj[v]:
            if mt[t] >= 0 and ml[v] != t:
                vis_r.add(t)
    f = Fig("nv2", 430, title="Теорема Кёнига: покрытие и независимое множество из паросочетания",
            sub="От свободных левых вершин идём по рёбрам не из паросочетания вправо и по рёбрам паросочетания влево.")
    xl, xr, y0, dy = 190, 570, 112, 56
    for a, b in E:
        m = ml[a] == b
        f.line(xl, y0 + a * dy, xr, y0 + b * dy, stroke=YELLOW if m else EDGE, sw=4 if m else 2)
    for i, n in enumerate(L):
        plus = i in vis_l
        f.node(xl, y0 + i * dy, n, color=GREEN if plus else RED, r=20, size=15, fill=NODE)
        f.text(xl - 38, y0 + i * dy + 6, "L+" if plus else "L−", size=15, anchor="end", fill=GREEN if plus else RED, weight=700)
    for i, n in enumerate(R):
        plus = i in vis_r
        f.node(xr, y0 + i * dy, n, color=GREEN if plus else RED, r=20, size=15, fill=NODE)
        f.text(xr + 38, y0 + i * dy + 6, "R+" if plus else "R−", size=15, fill=GREEN if plus else RED, weight=700)
    f.text(380, 392, "покрытие = R+ ∪ L−   (красные слева, зелёные справа)", size=15, fill=TEXT2, anchor="middle", weight=700)
    f.text(380, 416, "независимое = L+ ∪ R−   (зелёные слева, красные справа); жёлтое — паросочетание", size=14.5, fill=MUTED, anchor="middle")
    return f.svg()


def blocks():
    f = Fig("nv3", 330, title="Блоки (вершинная двусвязность): рёбра делятся, вершины — нет",
            sub="Точки сочленения 3, 5, 6 принадлежат сразу нескольким блокам; мост — блок из одного ребра.")
    P = {1: (90, 120), 2: (90, 240), 3: (200, 180), 4: (320, 120), 5: (320, 240),
         6: (470, 180), 7: (600, 120), 8: (600, 240)}
    E = [(1, 2, RED), (2, 3, RED), (1, 3, RED), (3, 4, GREEN), (4, 5, GREEN), (3, 5, GREEN),
         (5, 6, PURPLE), (6, 7, BLUE), (7, 8, BLUE), (6, 8, BLUE)]
    for a, b, c in E:
        f.line(*P[a], *P[b], stroke=c, sw=4)
    for k, (x, y) in P.items():
        cut = k in (3, 5, 6)
        f.node(x, y, k, color=YELLOW if cut else GRID, r=20, size=16)
    f.legend(40, 292, [(RED, "блок 1", "box"), (GREEN, "блок 2", "box"), (PURPLE, "блок 3 (мост)", "box"), (BLUE, "блок 4", "box")], size=13) if False else None
    for i, (c, t) in enumerate([(RED, "блок 1"), (GREEN, "блок 2"), (PURPLE, "блок 3 — мост"), (BLUE, "блок 4")]):
        f.rect(70 + i * 170, 292, 18, 12, fill=c, rx=3)
        f.text(94 + i * 170, 303, t, size=14, fill=TEXT2)
    return f.svg()


def dag_cover():
    f = Fig("nv4", 380, title="Покрытие DAG непересекающимися путями = n − (максимальное паросочетание)",
            sub="Каждую вершину v раздваиваем: v_out (слева) и v_in (справа); ребро u → v даёт ребро u_out — v_in.")
    # исходный DAG
    D = {"a": (90, 130), "b": (200, 90), "c": (200, 210), "d": (310, 150)}
    for u, v in [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")]:
        f.edge(*D[u], *D[v], r1=18, r2=18, color=EDGE, sw=2.5)
    for n, (x, y) in D.items():
        f.node(x, y, n, color=BLUE, r=18)
    f.text(200, 264, "DAG", size=15, fill=MUTED, anchor="middle")
    # двудольный
    xl, xr = 480, 690
    ys = {"a": 100, "b": 160, "c": 220, "d": 280}
    for u, v, m in [("a", "b", 1), ("a", "c", 0), ("b", "d", 1), ("c", "d", 0)]:
        f.line(xl, ys[u], xr, ys[v], stroke=YELLOW if m else EDGE, sw=4 if m else 2)
    for n, y in ys.items():
        f.node(xl, y, n + "ₒ", color=GREEN, r=18, size=14)
        f.node(xr, y, n + "ᵢ", color=ORANGE, r=18, size=14)
    f.text(xl, 72, "out", size=14, fill=GREEN, anchor="middle", weight=700)
    f.text(xr, 72, "in", size=14, fill=ORANGE, anchor="middle", weight=700)
    f.note(334, "Паросочетание {a→b, b→d} склеивает вершины в путь a → b → d; c остаётся одна: путей 4 − 2 = 2.", size=14.5, color=TEXT2)
    f.note(358, "Каждая вершина получает не более одного следующего и не более одного предыдущего.", size=14, color=MUTED)
    return f.svg()


FIGS = {
    1: (twosat, "Граф импликаций; формула невыполнима тогда и только тогда, когда $x$ и $\\neg x$ лежат в одной КСС."),
    2: (konig, "Обход от свободных левых вершин делит вершины на $L^+,L^-,R^+,R^-$; из них собираются минимальное покрытие и максимальное независимое множество."),
    3: (blocks, "Компоненты вершинной двусвязности — классы рёбер; вершины-сочленения лежат сразу в нескольких блоках."),
    4: (dag_cover, "Раздвоение вершин: паросочетание из $k$ рёбер даёт покрытие DAG путями из $n-k$ штук."),
}
