import math

from kit import *

NOTE = "parallel-bp/parallel-bp-zan4-grafy-dfs.html"


def _graph(f, pos, edges, color=EDGE, sw=2.5, r=18, arrow=False, dash=None, bend=None):
    for k, (a, b) in enumerate(edges):
        bd = (bend or {}).get((a, b), 0)
        f.edge(*pos[a], *pos[b], r1=r, r2=r, color=color, sw=sw, arrow=arrow, dash=dash, bend=bd)


def storage():
    f = Fig("dg1", 530, title="Три способа хранить граф",
            sub="Граф: 5 вершин, рёбра 1–2, 1–3, 2–3, 3–4, 4–5.")
    E = [(1, 2), (1, 3), (2, 3), (3, 4), (4, 5)]
    pos = {1: (90, 150), 2: (90, 250), 3: (190, 200), 4: (290, 200), 5: (380, 200)}
    pos = {1: (80, 140), 2: (80, 240), 3: (170, 190), 4: (260, 190), 5: (330, 190)}
    pos = {1: (70, 140), 2: (70, 240), 3: (160, 190), 4: (250, 190), 5: (330, 190)}
    _graph(f, pos, E)
    for v, (x, y) in pos.items():
        f.node(x, y, v, color=BLUE)
    f.text(70, 115, "граф", size=14, fill=MUTED)
    # матрица смежности
    ox, oy, cw = 420, 118, 34
    f.text(ox, oy - 14, "матрица смежности g[i][j]", size=14.5, fill=TEXT2, weight=700)
    adj = {(a, b) for a, b in E} | {(b, a) for a, b in E}
    for j in range(5):
        f.text(ox + 46 + j * cw + cw / 2 - 2, oy + 12, str(j + 1), size=13, fill=MUTED, anchor="middle")
    for i in range(5):
        f.text(ox + 8, oy + 40 + i * cw, str(i + 1), size=13, fill=MUTED)
        for j in range(5):
            on = (i + 1, j + 1) in adj
            f.cell(ox + 30 + j * cw + 14, oy + 20 + i * cw, 1 if on else 0, w=cw - 4, h=cw - 4,
                   fill=GREEN if on else NODE, stroke=GREEN if on else GRID, tcolor=BG if on else MUTED, size=14)
    f.text(ox, oy + 20 + 5 * cw + 26, "память O(n²) даже для пустого графа", size=14, fill=MUTED)
    # список смежности
    lx, ly = 32, 316
    f.text(lx, ly, "список смежности g[v]", size=14.5, fill=TEXT2, weight=700)
    lists = {1: [2, 3], 2: [1, 3], 3: [1, 2, 4], 4: [3, 5], 5: [4]}
    for k, (v, ns) in enumerate(lists.items()):
        yy = ly + 24 + k * 28
        f.text(lx, yy + 17, f"{v}:", size=14.5, fill=TEXT2, weight=700)
        for j, u in enumerate(ns):
            f.cell(lx + 34 + j * 36, yy, u, w=32, h=24, fill=NODE, stroke=BLUE, size=14)
    f.text(lx + 34, ly + 24 + 5 * 28 + 12, "память O(n + m)", size=14, fill=MUTED)
    # список рёбер
    ex, ey = 420, 380
    f.text(ex, ey, "список рёбер", size=14.5, fill=TEXT2, weight=700)
    for k, (a, b) in enumerate(E):
        f.cell(ex + (k % 3) * 100, ey + 18 + (k // 3) * 34, f"({a}, {b})", w=92, h=26, fill=NODE, stroke=ORANGE, size=14)
    f.text(ex, ey + 18 + 2 * 34 + 18, "память O(m)", size=14, fill=MUTED)
    return f.svg()


def special():
    f = Fig("dg2", 300, title="Смешные графы", sub="Отдельные виды графов, которые встречаются постоянно.")
    cells = [32, 222, 412, 602]
    ty = 270
    # пустой
    cx = cells[0] + 70
    pts = [(cx - 40, 120), (cx + 40, 120), (cx, 160), (cx - 40, 200), (cx + 40, 200)]
    for x, y in pts:
        f.node(x, y, "", color=AXIS, r=12)
    f.text(cx, ty, "пустой: m = 0", size=14, fill=TEXT2, anchor="middle")
    # полный
    cx = cells[1] + 70
    pts = [(cx + 50 * math.cos(math.radians(a)), 160 + 50 * math.sin(math.radians(a))) for a in (-90, -18, 54, 126, 198)]
    for i in range(5):
        for j in range(i + 1, 5):
            f.line(*pts[i], *pts[j], stroke=BLUE, sw=1.8, op=0.8)
    for x, y in pts:
        f.node(x, y, "", color=BLUE, r=11)
    f.text(cx, ty, "полный: m = n(n−1)/2", size=14, fill=TEXT2, anchor="middle")
    # двудольный
    cx = cells[2] + 70
    L = [(cx - 44, 125), (cx - 44, 195)]
    R = [(cx + 44, 105), (cx + 44, 160), (cx + 44, 215)]
    for a in L:
        for b in R:
            f.line(*a, *b, stroke=GREEN, sw=2)
    for x, y in L:
        f.node(x, y, "", color=ORANGE, r=12)
    for x, y in R:
        f.node(x, y, "", color=BLUE, r=12)
    f.text(cx, ty, "двудольный", size=14, fill=TEXT2, anchor="middle")
    # дерево
    cx = cells[3] + 70
    tp = {0: (cx, 105), 1: (cx - 40, 160), 2: (cx + 40, 160), 3: (cx - 62, 215), 4: (cx - 18, 215), 5: (cx + 40, 215)}
    for a, b in [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5)]:
        f.line(*tp[a], *tp[b], stroke=PURPLE, sw=2)
    for x, y in tp.values():
        f.node(x, y, "", color=PURPLE, r=12)
    f.text(cx, ty, "дерево", size=14, fill=TEXT2, anchor="middle")
    return f.svg()


def tree_defs():
    f = Fig("dg3", 330, title="Четыре определения дерева эквивалентны",
            sub="Доказываем по кругу: 1 ⇒ 2 ⇒ 3 ⇒ 4 ⇒ 1.")
    boxes = {
        1: (36, 90, "связный граф без циклов"),
        2: (456, 90, "связный, m = n − 1"),
        3: (456, 220, "без циклов, m = n − 1"),
        4: (36, 220, "между любыми двумя вершинами ровно один путь"),
    }
    w, h = 268, 54
    for k, (x, y, t) in boxes.items():
        f.rect(x, y, w, h, fill=NODE, stroke=BLUE if k in (1, 2) else ORANGE, sw=2, rx=10)
        f.circle(x + 22, y + h / 2, 13, fill=YELLOW)
        f.text(x + 22, y + h / 2 + 5, str(k), size=15, anchor="middle", weight=700, fill=BG)
        if k == 4:
            f.text(x + 44, y + 23, "между любыми двумя вершинами", size=13.5, fill=TEXT)
            f.text(x + 44, y + 43, "ровно один путь", size=13.5, fill=TEXT)
        else:
            f.text(x + 46, y + h / 2 + 5, t, size=15, fill=TEXT)
    f.line(36 + w + 8, 117, 456 - 8, 117, stroke=GREEN, sw=2.5, arrow=True)
    f.line(590, 90 + h + 6, 590, 220 - 8, stroke=GREEN, sw=2.5, arrow=True)
    f.line(456 - 8, 247, 36 + w + 8, 247, stroke=GREEN, sw=2.5, arrow=True)
    f.line(170, 220 - 6, 170, 90 + h + 8, stroke=GREEN, sw=2.5, arrow=True)
    f.text(380, 104, "по индукции", size=13.5, fill=MUTED, anchor="middle")
    f.text(602, 188, "цикл съел бы ребро", size=13.5, fill=MUTED)
    f.text(380, 270, "компоненты", size=13.5, fill=MUTED, anchor="middle")
    f.text(182, 188, "путь и связность", size=13.5, fill=MUTED)
    return f.svg()


def _dfs_order(adj, root):
    order, tree, seen = [], [], set()
    def go(v):
        seen.add(v)
        order.append(v)
        for u in sorted(adj[v]):
            if u not in seen:
                tree.append((v, u))
                go(u)
    go(root)
    return order, tree


def dfs_walk():
    f = Fig("dg4", 392, title="Обход в глубину: идём вглубь, пока есть непокрашенные соседи",
            sub="Цифра у вершины — порядок, в котором DFS в неё входит; пунктир — рёбра в уже покрашенные вершины.")
    E = [(1, 2), (2, 3), (2, 4), (4, 5), (5, 6), (1, 7), (7, 8), (6, 2), (8, 1)]
    adj = {v: set() for v in range(1, 9)}
    for a, b in E:
        adj[a].add(b); adj[b].add(a)
    order, tree = _dfs_order(adj, 1)
    pos = {1: (380, 110), 2: (230, 180), 3: (150, 260), 4: (260, 270), 5: (330, 330), 6: (200, 340), 7: (530, 180), 8: (600, 270)}
    tset = {tuple(sorted(e)) for e in tree}
    for a, b in E:
        if tuple(sorted((a, b))) not in tset:
            f.edge(*pos[a], *pos[b], r1=18, r2=18, color=MUTED, sw=2, arrow=False, dash="6 5", bend=0)
    for a, b in tree:
        f.edge(*pos[a], *pos[b], r1=18, r2=18, color=BLUE, sw=3.5, arrow=True)
    num = {v: i + 1 for i, v in enumerate(order)}
    for v, (x, y) in pos.items():
        f.node(x, y, v, color=BLUE, r=19)
        f.circle(x + 20, y - 20, 11, fill=YELLOW)
        f.text(x + 20, y - 15.5, str(num[v]), size=12.5, anchor="middle", weight=700, fill=BG)
    f.legend(420, 352, [(BLUE, "древесные рёбра (по ним прошли)", "line"), (MUTED, "рёбра в покрашенные вершины", "line")], size=13.5, gap=22)
    return f.svg()


def bipartite():
    f = Fig("dg5", 330, title="Двудольность = раскраска в два цвета",
            sub="Слева граф раскрашивается, справа в нём нечётный цикл — конфликт на ребре.")
    # слева
    L = {1: (90, 130), 2: (90, 230), 3: (210, 130), 4: (210, 230), 5: (150, 180)}
    left = {1: BLUE, 2: BLUE, 5: ORANGE, 3: ORANGE, 4: ORANGE}
    posl = {1: (70, 120), 2: (70, 250), 3: (250, 120), 4: (250, 250), 5: (70, 185)}
    colr = {1: BLUE, 2: BLUE, 5: BLUE, 3: ORANGE, 4: ORANGE}
    El = [(1, 3), (1, 4), (2, 3), (2, 4), (5, 3), (5, 4)]
    for a, b in El:
        f.edge(*posl[a], *posl[b], r1=18, r2=18, color=GREEN, sw=2.5, arrow=False)
    for v, (x, y) in posl.items():
        f.node(x, y, v, color=colr[v], fill=colr[v], tcolor=BG, r=18)
    f.text(160, 300, "доли: {1, 2, 5} и {3, 4}", size=14.5, fill=GREEN, anchor="middle", weight=700)
    # справа
    posr = {1: (470, 120), 2: (590, 120), 3: (530, 210), 4: (650, 210), 5: (650, 120)}
    cr = {1: BLUE, 2: ORANGE, 3: BLUE, 4: ORANGE, 5: BLUE}
    Er = [(1, 2), (2, 3), (3, 1), (3, 4), (2, 5)]
    for a, b in Er:
        bad = (a, b) == (3, 1)
        f.edge(*posr[a], *posr[b], r1=18, r2=18, color=RED if bad else GREEN, sw=3.5 if bad else 2.5, arrow=False)
    for v, (x, y) in posr.items():
        f.node(x, y, v, color=cr[v], fill=cr[v], tcolor=BG, r=18)
    f.text(560, 270, "цикл 1–2–3 нечётной длины:", size=14.5, fill=RED, anchor="middle", weight=700)
    f.text(560, 292, "ребро 1–3 соединяет одноцветные", size=14.5, fill=RED, anchor="middle")
    return f.svg()


def edge_types():
    f = Fig("dg6", 452, title="Типы рёбер при обходе в глубину (ориентированный граф)",
            sub="Дерево обхода нарисовано сверху вниз, поддеревья идут слева направо.")
    pos = {"r": (380, 120), "a": (230, 210), "b": (540, 210), "c": (150, 310), "d": (310, 310), "e": (540, 310)}
    tree = [("r", "a"), ("a", "c"), ("a", "d"), ("r", "b"), ("b", "e")]
    for a, b in tree:
        f.edge(*pos[a], *pos[b], r1=19, r2=19, color=TEXT2, sw=3.5, arrow=True)
    f.edge(*pos["d"], *pos["r"], r1=19, r2=19, color=RED, sw=3, arrow=True, bend=-46)
    f.edge(*pos["r"], *pos["d"], r1=19, r2=19, color=GREEN, sw=3, arrow=True, bend=-30)
    f.edge(*pos["e"], *pos["c"], r1=19, r2=19, color=PURPLE, sw=3, arrow=True, dash="8 5", bend=-30)
    for v, (x, y) in pos.items():
        f.node(x, y, v, color=BLUE, r=19)
    f.legend(32, 372, [(TEXT2, "древесное — по нему вошли в вершину", "line"), (RED, "обратное — в предка (цикл!)", "line")], size=13.5, gap=22)
    f.legend(400, 372, [(GREEN, "прямое — в потомка, не по дереву", "line"), (PURPLE, "перекрёстное — в уже обойдённое поддерево", "line")], size=13.5, gap=22)
    f.note(426, "Перекрёстное ребро всегда ведёт справа налево: слева направо DFS сам бы пошёл по нему.", size=13.5, color=MUTED, x=32)
    return f.svg()


def cycle_restore():
    f = Fig("dg7", 300, title="Восстановление цикла по предкам",
            sub="Стоим в v = 5, видим ребро в уже посещённую вершину u = 2. Поднимаемся по предкам от v до u.")
    xs = [90, 220, 350, 480, 610]
    y = 150
    for i in range(4):
        cyc = i >= 1
        f.edge(xs[i], y, xs[i + 1], y, r1=20, r2=20, color=GREEN if cyc else EDGE, sw=3.5, arrow=True)
    f.edge(xs[4], y, xs[1], y, r1=20, r2=20, color=RED, sw=3.5, arrow=True, bend=70)
    for i, x in enumerate(xs):
        cyc = i >= 1
        f.node(x, y, i + 1, color=GREEN if cyc else BLUE, fill=NODE, r=20)
    f.text(xs[4] + 4, y + 52, "v", size=15, fill=YELLOW, anchor="middle", weight=700)
    f.text(xs[1], y + 52, "u", size=15, fill=YELLOW, anchor="middle", weight=700)
    f.text(350, 88, "обратное ребро v → u", size=14.5, fill=RED, anchor="middle", weight=700)
    f.note(250, "getCycle(v, u): 5, 4, 3, затем u = 2 — вершины цикла; вершина 1 в него не входит.", size=14.5, color=TEXT2)
    f.note(272, "Работает за длину цикла — по предкам поднимаемся ровно столько раз.", size=14, color=MUTED)
    return f.svg()


def toposort():
    f = Fig("dg8", 360, title="Топологическая сортировка: вершины в порядке, обратном выходу из DFS",
            sub="Для каждого ребра v → u вершина u выходит из DFS раньше v, поэтому в обратном порядке v стоит левее u.")
    E = [(1, 2), (1, 3), (2, 4), (3, 4), (4, 5), (3, 5)]
    adj = {v: [] for v in range(1, 6)}
    for a, b in E:
        adj[a].append(b)
    out, seen = [], set()
    def go(v):
        seen.add(v)
        for u in adj[v]:
            if u not in seen:
                go(u)
        out.append(v)
    go(1)
    order = out[::-1]
    xs = {v: 90 + i * 135 for i, v in enumerate(order)}
    y = 250
    for a, b in E:
        xa, xb = xs[a], xs[b]
        mx = (xa + xb) / 2
        h = 34 + 20 * (abs(order.index(a) - order.index(b)) - 1)
        f.path(f"M{xa + 16},{y - 20} Q{mx},{y - 20 - h * 1.6} {xb - 16},{y - 20}", stroke=BLUE, sw=2.5, arrow=True)
    for v in order:
        f.node(xs[v], y, v, color=GREEN, r=20)
        f.text(xs[v], y + 46, f"вышли {out.index(v) + 1}-й", size=13.5, fill=MUTED, anchor="middle")
    f.text(32, 130, "порядок выхода из DFS: " + ", ".join(map(str, out)), size=14.5, fill=TEXT2)
    f.text(32, 156, "после разворота: " + ", ".join(map(str, order)) + " — все рёбра ведут слева направо", size=14.5, fill=GREEN, weight=700)
    return f.svg()


def diameter():
    f = Fig("dg9", 380, title="Диаметр дерева: два обхода в глубину",
            sub="Из любой вершины s находим самую глубокую u; из u — самую глубокую v. Путь u…v — диаметр.")
    pos = {"s": (380, 110), "a": (250, 190), "b": (520, 190), "c": (160, 270), "d": (300, 270), "e": (440, 270), "g": (590, 270), "u": (110, 340), "v": (640, 340)}
    edges = [("s", "a"), ("s", "b"), ("a", "c"), ("a", "d"), ("b", "e"), ("b", "g"), ("c", "u"), ("g", "v")]
    path = {("a", "c"), ("c", "u"), ("s", "a"), ("s", "b"), ("b", "g"), ("g", "v")}
    for a, b in edges:
        on = (a, b) in path
        f.edge(*pos[a], *pos[b], r1=17, r2=17, color=YELLOW if on else EDGE, sw=4 if on else 2.5, arrow=False)
    for k, (x, y) in pos.items():
        col = BLUE
        fill = NODE
        if k == "s":
            col, fill = GREEN, GREEN
        if k in ("u", "v"):
            col, fill = ORANGE, ORANGE
        f.node(x, y, k, color=col, fill=fill, tcolor=BG if fill != NODE else TEXT, r=17)
    f.legend(32, 130, [(GREEN, "s — старт первого обхода", "dot"), (ORANGE, "u — самая глубокая от s; v — от u", "dot"), (YELLOW, "диаметр: u … v", "line")], size=13.5, gap=22)
    return f.svg()


def votes():
    a = [2, 3, 5, 7, 8]
    M = 7
    f = Fig("dg10", 390, title="Подкуп партии: бинпоиск по итоговому числу голосов M",
            sub="Зелёная партия (2 голоса) должна получить M = 7; у остальных должно остаться не больше M − 1 = 6.")
    ox, unit, hu, base = 70, 90, 28, 296
    f.line(ox - 10, base, ox + 5 * unit, base, stroke=AXIS, sw=2)
    yl = base - (M - 1) * hu
    f.line(ox - 10, yl, ox + 5 * unit, yl, stroke=YELLOW, sw=2, dash="7 5")
    f.text(ox + 5 * unit + 4, yl + 5, "M − 1", size=14, fill=YELLOW, weight=700)
    for i, v in enumerate(a):
        x = ox + i * unit
        keep = min(v, M - 1) if i else v
        col = GREEN if i == 0 else BLUE
        f.rect(x + 8, base - keep * hu, unit - 16, keep * hu, fill=NODE, stroke=col, sw=2, rx=5)
        if i and v > M - 1:
            f.rect(x + 8, base - v * hu, unit - 16, (v - keep) * hu, fill=RED, stroke=RED, sw=2, rx=5, op=0.75)
        if i == 0:
            f.rect(x + 8, base - M * hu, unit - 16, (M - v) * hu, fill=GREEN, stroke=GREEN, sw=2, rx=5, op=0.85)
        f.text(x + unit / 2, base + 22, f"a={v}", size=14, fill=MUTED, anchor="middle")
    f.note(362, "Красное — голоса, которые нужно отобрать (1 + 2 = 3); зелёное — докупаем M − a = 5. Хватает: 3 ≤ 5.", size=14, color=TEXT2)
    return f.svg()


def parabolas():
    f = Fig("dg11", 360, title="Точка, лежащая внутри всех парабол",
            sub="Синие «смотрят вверх» (внутри — выше), оранжевые «вниз» (внутри — ниже).")
    ups = [(1.0, 0.0, -3.0), (0.6, 0.2, -1.0)]
    downs = [(-0.8, 0.0, 6.0), (-0.5, -0.4, 4.0)]
    ox, oy, sx, sy = 380, 285, 52, 22
    def P(x, y):
        return ox + x * sx, oy - y * sy
    f.line(60, oy, 700, oy, stroke=AXIS, sw=1.5)
    def seg(fn, col, sw, xs):
        pts = [P(x, fn(x)) for x in xs]
        pts = [(px, py) for px, py in pts if 100 <= py <= 300]
        return pts
    xs = [i / 20 for i in range(-120, 121)]
    for (A, B, C) in ups:
        pts = [P(x, A * x * x + B * x + C) for x in xs]
        pts = [(px, py) for px, py in pts if 80 <= py <= 300 and 60 <= px <= 700]
        f.polyline(pts, stroke=BLUE, sw=1.6, op=0.6)
    for (A, B, C) in downs:
        pts = [P(x, A * x * x + B * x + C) for x in xs]
        pts = [(px, py) for px, py in pts if 80 <= py <= 300 and 60 <= px <= 700]
        f.polyline(pts, stroke=ORANGE, sw=1.6, op=0.6)
    up_env = lambda x: max(A * x * x + B * x + C for A, B, C in ups)
    dn_env = lambda x: min(A * x * x + B * x + C for A, B, C in downs)
    feas = [x for x in xs if up_env(x) <= dn_env(x)]
    upts = [P(x, up_env(x)) for x in xs]
    upts = [(px, py) for px, py in upts if 80 <= py <= 300 and 60 <= px <= 700]
    dpts = [P(x, dn_env(x)) for x in xs]
    dpts = [(px, py) for px, py in dpts if 80 <= py <= 300 and 60 <= px <= 700]
    f.polyline(upts, stroke=BLUE, sw=4)
    f.polyline(dpts, stroke=ORANGE, sw=4)
    if feas:
        x0, x1 = min(feas), max(feas)
        px0, px1 = P(x0, 0)[0], P(x1, 0)[0]
        f.rect(px0, oy + 6, px1 - px0, 8, fill=GREEN, rx=3)
        f.text((px0 + px1) / 2, oy + 34, "здесь есть общая точка", size=14.5, fill=GREEN, anchor="middle", weight=700)
    f.text(60, 345, "g(x) = (верхняя огибающая) − (нижняя) выпукла, поэтому её минимум ищем тернарным поиском.", size=14, fill=TEXT2)
    return f.svg()


FIGS = {
    1: (storage, "Матрица занимает $O(n^2)$ даже для пустого графа, список смежности — $O(n+m)$, список рёбер — $O(m)$."),
    2: (special, "Пустой граф, полный граф ($m=\\frac{n(n-1)}{2}$), двудольный граф и дерево."),
    3: (tree_defs, "Достаточно доказать четыре импликации по кругу — тогда любое из определений можно взять за основное."),
    4: (dfs_walk, "DFS запускается из вершины 1: идёт вглубь по первому непокрашенному соседу, возвращается, когда идти некуда. Пример составлен для конспекта."),
    5: (bipartite, "Граф двудольный, если его вершины можно покрасить в два цвета так, чтобы каждое ребро соединяло разные цвета."),
    6: (cycle_restore, "Цикл — это путь вверх по предкам от $v$ до $u$ плюс найденное обратное ребро."),
    7: (edge_types, "Четыре типа рёбер при DFS: древесные, обратные, прямые и перекрёстные."),
    8: (toposort, "Рёбра ведут слева направо: любое ребро $v\\to u$ даёт $u$ раньше $v$ при выходе из DFS."),
    9: (diameter, "Из любой вершины самая далёкая — конец некоторого диаметра; из неё самая далёкая — другой конец."),
    10: (votes, "Для фиксированного $M$ нужно отобрать у остальных все голоса сверх $M-1$ и проверить, что столько можно докупить."),
    11: (parabolas, "Если верхняя огибающая «смотрящих вверх» парабол не выше нижней огибающей «смотрящих вниз» — в этом $x$ есть общая точка."),
}
