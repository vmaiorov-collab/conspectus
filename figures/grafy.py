from kit import *

NOTE = "parallel-b/parallel-b-zan1-grafy.html"


def tin_tout():
    children = {"A": ["B", "C"], "B": ["D", "E"], "C": [], "D": [], "E": []}
    tin, tout, t = {}, {}, [0]

    def dfs(v):
        tin[v] = t[0]; t[0] += 1
        for u in children[v]:
            dfs(u)
        tout[v] = t[0]; t[0] += 1
    dfs("A")
    col = {"A": BLUE, "B": GREEN, "C": PURPLE, "D": YELLOW, "E": ORANGE}
    depth = {"A": 0, "B": 1, "C": 1, "D": 2, "E": 2}
    f = Fig("g1", 410, title="Времена входа и выхода DFS: отрезки вложены или не пересекаются",
            sub="Таймер +1 при каждом входе и выходе. Отрезок [tin, tout] — пока вершина в стеке вызовов.")
    pos = {"A": (150, 130), "B": (90, 212), "C": (220, 212), "D": (50, 294), "E": (140, 294)}
    for v, cs in children.items():
        for u in cs:
            f.edge(*pos[v], *pos[u], r1=19, r2=19, arrow=False)
    for v, (x, y) in pos.items():
        f.node(x, y, v, color=col[v], r=19)
        f.text(x, y + 38, f"[{tin[v]}, {tout[v]}]", size=14, anchor="middle", fill=TEXT2)
    # временная шкала
    ox, s = 300, 42
    ya = 330
    for k in range(10):
        f.text(ox + k * s, ya + 26, str(k), size=13.5, anchor="middle", fill=MUTED)
        f.line(ox + k * s, 110, ox + k * s, ya, stroke=GRID, sw=1)
    f.line(ox - 10, ya, ox + 9 * s + 10, ya, stroke=AXIS, sw=1.5)
    f.text(ox + 9 * s + 14, ya + 26, "время", size=13.5, fill=MUTED)
    for v in "ABCDE":
        y = 120 + depth[v] * 66
        x0, x1 = ox + tin[v] * s, ox + tout[v] * s
        f.rect(x0 - 8, y, x1 - x0 + 16, 32, fill=col[v], op=0.85, rx=8)
        f.text(x0 + 4, y + 22, v, size=15, weight=700, fill=BG)
    f.note(398, "D и E внутри отрезка B — они потомки B. Отрезки B и C не пересекаются — ни один не предок другого.", size=14)
    return f.svg()


def condensation():
    f = Fig("g2", 360, title="Конденсация: каждую КСС сжимаем в одну вершину",
            sub="Слева исходный граф, компоненты обведены. Справа — что остаётся после сжатия.")
    P = {1: (90, 140), 2: (190, 140), 3: (140, 220), 4: (110, 300), 5: (210, 300), 6: (320, 220)}
    # обводки КСС
    f.rect(54, 106, 172, 146, fill=BLUE, op=0.12, stroke=BLUE, sw=1.5, rx=22, dash="5 4")
    f.rect(74, 270, 172, 62, fill=GREEN, op=0.12, stroke=GREEN, sw=1.5, rx=22, dash="5 4")
    f.rect(284, 188, 72, 64, fill=PURPLE, op=0.12, stroke=PURPLE, sw=1.5, rx=22, dash="5 4")
    inner = [(1, 2, 0), (2, 3, 0), (3, 1, 0), (4, 5, 12), (5, 4, 12)]
    for u, v, b in inner:
        f.edge(*P[u], *P[v], r1=18, r2=18, color=EDGE, sw=2, bend=b)
    cross = [(3, 4), (2, 6), (5, 6)]
    for u, v in cross:
        f.edge(*P[u], *P[v], r1=18, r2=18, color=ORANGE, sw=2.5)
    cc = {1: BLUE, 2: BLUE, 3: BLUE, 4: GREEN, 5: GREEN, 6: PURPLE}
    for v, (x, y) in P.items():
        f.node(x, y, v, color=cc[v], r=18)
    f.text(395, 226, "⟹", size=34, anchor="middle", fill=MUTED)
    M = {"{1,2,3}": (560, 140, BLUE), "{4,5}": (500, 290, GREEN), "{6}": (660, 260, PURPLE)}
    for (a, b) in [("{1,2,3}", "{4,5}"), ("{1,2,3}", "{6}"), ("{4,5}", "{6}")]:
        f.edge(M[a][0], M[a][1], M[b][0], M[b][1], r1=34, r2=34, color=ORANGE, sw=2.5)
    for name, (x, y, c) in M.items():
        f.circle(x, y, 34, fill=c, op=0.25)
        f.circle(x, y, 34, fill="none", stroke=c, sw=2.5)
        f.text(x, y + 5, name, size=14.5, anchor="middle", weight=700)
    f.note(350, "Оранжевые рёбра идут между компонентами и сохраняются. Циклов в сжатом графе нет — это DAG.", size=14)
    return f.svg()


def nine():
    f = Fig("g3", 420, title="Пример на 9 вершинах: три КСС и две перемычки",
            sub="Рёбра 1→2→3→1, 4→5→4, 8→7→9→6→8, перемычки 4→3 и 2→8.")
    P = {4: (90, 170), 5: (90, 280),
         1: (290, 150), 2: (370, 230), 3: (260, 290),
         8: (520, 160), 7: (650, 160), 9: (650, 290), 6: (520, 290)}
    groups = [((50, 120, 84, 210), GREEN, "№0"), ((214, 106, 204, 228), BLUE, "№1"), ((476, 116, 220, 220), PURPLE, "№2")]
    for (x, y, w, h), c, lab in groups:
        f.rect(x, y, w, h, fill=c, op=0.1, stroke=c, sw=1.5, rx=24, dash="5 4")
        f.text(x + w / 2, y + h + 24, f"КСС {lab}", size=15, anchor="middle", fill=c, weight=700)
    inner = [(1, 2), (2, 3), (3, 1), (8, 7), (7, 9), (9, 6), (6, 8)]
    for u, v in inner:
        f.edge(*P[u], *P[v], r1=19, r2=19, color=EDGE, sw=2)
    f.edge(*P[4], *P[5], r1=19, r2=19, color=EDGE, sw=2, bend=16)
    f.edge(*P[5], *P[4], r1=19, r2=19, color=EDGE, sw=2, bend=16)
    for u, v in [(4, 3), (2, 8)]:
        f.edge(*P[u], *P[v], r1=19, r2=19, color=ORANGE, sw=3)
    cc = {4: GREEN, 5: GREEN, 1: BLUE, 2: BLUE, 3: BLUE, 6: PURPLE, 7: PURPLE, 8: PURPLE, 9: PURPLE}
    for v, (x, y) in P.items():
        f.node(x, y, v, color=cc[v], r=19)
    f.note(396, "Конденсация: №0 → №1 → №2 — номера из алгоритма Косарайю идут в порядке топсорта.", size=14)
    return f.svg()


def diameter():
    f = Fig("g4", 420, title="Диаметр через вершину v: склеиваем два самых длинных спуска",
            sub="down[u] — длина самого длинного пути из u вниз. Берём два наибольших: x и y.")
    v = (380, 110)
    branches = [("u₁", 200, 2, YELLOW), ("u₂", 380, 1, MUTED), ("u₃", 560, 3, YELLOW)]
    best = sorted(branches, key=lambda b: -b[2])[:2]
    for name, x, down, c in branches:
        chosen = (name, x, down, c) in best
        col = ORANGE if chosen else EDGE
        prev = v
        for k in range(down + 1):
            pt = (x, 186 + k * 62)
            f.edge(*prev, *pt, r1=17, r2=15, color=col, sw=3.5 if chosen else 2, arrow=False)
            prev = pt
        for k in range(down + 1):
            pt = (x, 186 + k * 62)
            if k == 0:
                f.node(*pt, name, color=ORANGE if chosen else BLUE, r=17, size=14)
            else:
                f.circle(*pt, 9, fill=ORANGE if chosen else GRID)
        f.text(x + 30, 192, f"down = {down}", size=15, fill=ORANGE if chosen else MUTED, weight=700 if chosen else None)
    f.node(*v, "v", color=ORANGE, r=20, size=16)
    f.note(394, "x = 3 (через u₃), y = 2 (через u₁)  ⟹  путь через v: x + y + 2 = 7 рёбер (оранжевый).", size=14.5)
    return f.svg()


def depth_sums():
    f = Fig("g5", 470, title="Запрос (v = 2, d = 2): сумма потомков на глубине 3",
            sub="Вершины одной глубины, выписанные по tin, — поддерево v занимает в них сплошной отрезок.")
    P = {1: (300, 108), 2: (170, 176), 3: (440, 176),
         4: (110, 244), 5: (240, 244), 6: (390, 244), 7: (510, 244),
         8: (70, 312), 9: (150, 312), 10: (240, 312), 11: (390, 312), 12: (470, 312), 13: (560, 312)}
    par = {2: 1, 3: 1, 4: 2, 5: 2, 6: 3, 7: 3, 8: 4, 9: 4, 10: 5, 11: 6, 12: 7, 13: 7}
    a = {8: 5, 9: 2, 10: 4, 11: 1, 12: 3, 13: 6}
    sub = {2, 4, 5, 8, 9, 10}
    f.rect(36, 150, 240, 190, fill=BLUE, op=0.08, stroke=BLUE, sw=1.5, rx=20, dash="5 4")
    for u, p in par.items():
        f.edge(*P[p], *P[u], r1=17, r2=17, arrow=False, color=BLUE if u in sub else EDGE)
    for u, (x, y) in P.items():
        if u in a:
            on = u in sub
            f.node(x, y, u, color=YELLOW if on else GREEN, r=17, size=14)
            f.text(x, y + 36, f"a={a[u]}", size=13, anchor="middle", fill=YELLOW if on else MUTED)
        else:
            f.node(x, y, u, color=ORANGE if u == 2 else (BLUE if u in sub else GRID), r=17, size=14)
    for d, y in enumerate([108, 176, 244, 312]):
        f.text(640, y + 5, f"глубина {d}", size=13.5, fill=MUTED)
    # массив глубины 3 и префиксы
    order = [8, 9, 10, 11, 12, 13]
    cw, ox, y0 = 64, 150, 386
    f.text(ox - 14, y0 + 25, "глубина 3:", size=14, fill=TEXT2, anchor="end")
    f.text(ox - 14, y0 + 70, "префиксы:", size=14, fill=TEXT2, anchor="end")
    pref = [0]
    for u in order:
        pref.append(pref[-1] + a[u])
    for i, u in enumerate(order):
        on = u in sub
        f.cell(ox + i * cw + 3, y0, f"{u}", w=cw - 6, h=38, fill=YELLOW if on else NODE, stroke=YELLOW if on else GRID, tcolor=BG if on else TEXT)
    for i, p in enumerate(pref):
        f.text(ox + i * cw, y0 + 70, str(p), size=15, anchor="middle", fill=TEXT2, weight=700 if i in (0, 3) else None)
    f.text(ox + 6 * cw + 30, y0 + 25, "по tin →", size=13.5, fill=MUTED)
    f.text(ox + 6 * cw + 30, y0 + 70, "11 − 0 = 11", size=16, fill=YELLOW, weight=700)
    return f.svg()


def potentials():
    f = Fig("g6", 480, title="Условия на суммы → граф на префиксных суммах",
            sub="Вершины — индексы P₀…P₄. Условие «a[l] + … + a[r−1] = x» — ребро l → r с весом x.")
    ox, s, y = 110, 140, 250
    X = lambda i: ox + i * s
    P = {0: 0, 2: 5, 4: 8, 1: 2, 3: 0}
    cons = [(0, 2, 5, 70), (2, 4, 3, 70), (1, 4, 6, -1), (0, 4, 8, 150)]
    for l, r, x, h in cons:
        if h > 0:
            x0, x1 = X(l) + 6, X(r) - 6
            f.path(f"M{x0},{y - 20} C{x0},{y - 20 - h} {x1},{y - 20 - h} {x1},{y - 24}", stroke=BLUE if (l, r) != (0, 4) else GREEN, sw=2.5, arrow=True)
            f.text((x0 + x1) / 2, y - 20 - h * 0.75 - 6, f"+{x}", size=16, anchor="middle", fill=BLUE if (l, r) != (0, 4) else GREEN, weight=700)
        else:
            x0, x1 = X(l) + 6, X(r) - 6
            f.path(f"M{x0},{y + 20} C{x0},{y + 95} {x1},{y + 95} {x1},{y + 24}", stroke=BLUE, sw=2.5, arrow=True)
            f.text((x0 + x1) / 2, y + 92, f"+{x}", size=16, anchor="middle", fill=BLUE, weight=700)
    for i in range(5):
        iso = i == 3
        f.node(X(i), y, f"P{'₀₁₂₃₄'[i]}", color=GRID if iso else ORANGE, r=21, size=14)
    for i in range(5):
        f.text(X(i), y + 120, f"= {P[i]}", size=16, anchor="middle", fill=ORANGE if i != 3 else MUTED, weight=700)
    f.text(ox - 40, y + 120, "P", size=15, anchor="end", fill=MUTED, italic=True)
    f.text(X(3), y + 142, "не связана — любое", size=13, anchor="middle", fill=MUTED)
    f.note(428, "Обход из P₀ = 0: P₂ = 5, P₄ = 5 + 3 = 8, P₁ = 8 − 6 = 2.", size=14.5)
    f.note(452, "Зелёное ребро 0 → 4 (+8) ведёт в уже посещённую P₄: 0 + 8 = 8 — сходится, противоречия нет.", size=14.5, color=GREEN)
    return f.svg()


FIGS = {
    1: (tin_tout, "Вход и выход задают отрезок времени. Из-за стека вызовов любые два отрезка либо вложены (предок и потомок), либо не пересекаются."),
    2: (condensation, "Внутри КСС все вершины взаимно достижимы, поэтому её можно заменить одной вершиной. Рёбра между компонентами остаются, и получается DAG."),
    3: (nine, "Граф из разбора: три КСС (зелёная, синяя, фиолетовая) и две перемычки. Конденсация — путь №0 → №1 → №2."),
    4: (diameter, "Диаметр через $v$ — два самых длинных спуска из разных детей плюс два ребра: $x + y + 2$."),
    5: (depth_sums, "Внутри одной глубины вершины поддерева идут подряд по $\\mathrm{tin}$, поэтому ответ — разность двух префиксных сумм."),
    6: (potentials, "Каждое условие $P_r - P_l = x$ — ребро с весом. Обходим граф из $P_0 = 0$ и раздаём значения; ребро, ведущее в уже посещённую вершину, проверяет согласованность."),
}
