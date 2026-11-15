from kit import *

NOTE = "parallel-bp/parallel-bp-zan5-dfs-2.html"


def scc():
    f = Fig("d1", 380, title="Компоненты сильной связности и конденсация",
            sub="В каждой компоненте из любой вершины можно прийти в любую; сжав их, получаем ациклический граф.")
    comp = {"A": ([0, 1, 2], BLUE, (120, 150)), "B": ([3, 4, 5], GREEN, (290, 150)),
            "C": ([6, 7], ORANGE, (450, 150)), "D": ([8], PURPLE, (450, 270))}
    pos = {}
    import math
    for name, (vs, c, (cx, cy)) in comp.items():
        r = 44 if len(vs) > 1 else 0
        for i, v in enumerate(vs):
            a = math.pi / 2 + 2 * math.pi * i / len(vs)
            pos[v] = (cx + r * math.cos(a), cy - r * math.sin(a) + (0 if len(vs) > 1 else 0))
        f.circle(cx, cy, 70 if len(vs) > 1 else 28, fill="none", stroke=c, sw=2, op=.7)
    def e(a, b, c=EDGE, bend=0):
        f.edge(*pos[a], *pos[b], r1=17, r2=17, color=c, sw=2.4, arrow=True, bend=bend)
    for a, b in [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3)]:
        e(a, b, TEXT2)
    e(6, 7, TEXT2, bend=14); e(7, 6, TEXT2, bend=14)
    e(2, 3, YELLOW); e(5, 6, YELLOW)
    for name, (vs, c, _) in comp.items():
        for v in vs:
            f.node(*pos[v], v, color=c, r=17, size=15)
    # конденсация
    f.text(600, 108, "после сжатия", size=14, fill=MUTED, anchor="middle")
    cp = {"A": (560, 160), "B": (640, 160), "C": (700, 215), "D": (560, 260)}
    # вертикально: A -> B -> C, D отдельно
    cp = {"A": (610, 140), "B": (610, 210), "C": (610, 280), "D": (700, 210)}
    f.edge(*cp["A"], *cp["B"], r1=20, r2=20, color=YELLOW, sw=2.4)
    f.edge(*cp["B"], *cp["C"], r1=20, r2=20, color=YELLOW, sw=2.4)
    for n, (x, y) in cp.items():
        f.node(x, y, n, color=comp[n][1], r=20, size=16)
    f.note(364, "Жёлтые рёбра остаются в конденсации; рёбра внутри компонент исчезают.", size=14.5, color=TEXT2)
    return f.svg()


def bridges():
    f = Fig("d2", 450, title="Мосты и точки сочленения по дереву обхода DFS",
            sub="Подписи у вершин: h — глубина, up — наименьшая глубина, достижимая обратным ребром из поддерева.")
    P = {1: (90, 90), 2: (210, 90), 3: (330, 90), 4: (330, 210), 5: (470, 90), 6: (590, 90), 7: (590, 210)}
    h = {1: 0, 2: 1, 3: 2, 4: 3, 5: 2, 6: 3, 7: 4}
    up = {1: "∞", 2: 1, 3: 1, 4: 1, 5: 2, 6: 2, 7: 2}
    pos = {1: (90, 160), 2: (230, 160), 3: (150, 270), 4: (310, 270), 5: (450, 160), 6: (550, 270), 7: (700, 270)}
    tree = [(1, 2, RED), (2, 3, TEXT2), (3, 4, TEXT2), (2, 5, RED), (5, 6, TEXT2), (6, 7, TEXT2)]
    back = [(4, 2), (7, 5)]
    for a, b, c in tree:
        f.line(*pos[a], *pos[b], stroke=c, sw=3.2 if c == RED else 2.6)
    for a, b in back:
        f.line(*pos[a], *pos[b], stroke=GREEN, sw=2.4, dash="6 5")
    cut = {2, 5}
    for v, (x, y) in pos.items():
        f.node(x, y, v, color=YELLOW if v in cut else BLUE, r=19, size=16)
        f.text(x, y + 38 if v in (3, 4, 6, 7) else y - 30, f"h={h[v]}  up={up[v]}", size=12.5, anchor="middle", fill=MUTED)
    f.legend(40, 345, [(RED, "мост: up[v] > h[parent]", "line"), (GREEN, "обратное ребро (пунктир)", "line"), (YELLOW, "точка сочленения: up[child] ≥ h[v]", "dot")], size=14, gap=26)
    f.note(426, "Рёбра 1–2 и 2–5 — мосты; вершины 2 и 5 — точки сочленения.", size=14.5, color=TEXT2)
    return f.svg()


def root():
    f = Fig("d3", 350, title="Корень DFS: точка сочленения, если у него хотя бы два сына",
            sub="Для корня условие up[child] ≥ h[root] выполнено всегда — его нужно заменить на проверку числа сыновей.")
    def tree(cx, cy, title, kids):
        f.text(cx, cy - 68, title, size=15, anchor="middle", fill=TEXT2, weight=700)
        f.node(cx, cy, "корень", color=YELLOW if kids >= 2 else BLUE, r=28, size=12)
        for k in range(kids):
            x = cx + (k - (kids - 1) / 2) * 120
            f.line(cx, cy + 28, x, cy + 90, stroke=EDGE, sw=2.5)
            f.node(x, cy + 90, "", color=BLUE, r=14)
            f.line(x - 24, cy + 150, x, cy + 104, stroke=GRID, sw=1.5); f.line(x + 24, cy + 150, x, cy + 104, stroke=GRID, sw=1.5)
            f.line(x - 24, cy + 150, x + 24, cy + 150, stroke=GRID, sw=1.5)
    tree(200, 170, "один сын — не точка сочленения", 1)
    tree(560, 170, "два сына — точка сочленения", 2)
    return f.svg()


FIGS = {
    1: (scc, "Компоненты сильной связности и сжатый (ациклический) граф."),
    2: (bridges, "Мосты и точки сочленения определяются по глубинам $h$ и значениям $up$."),
    3: (root, "Для корня дерева DFS важно количество сыновей: при удалении корня поддеревья сыновей разъединяются."),
}
