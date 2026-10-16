from kit import *

NOTE = "parallel-a/parallel-a-zan4-prokachivaem-derevo-otrezkov.html"


def persistent_path():
    f = Fig("sg1", 380, title="Персистентное ДО: при изменении копируется только путь от корня до листа",
            sub="Все вершины вне пути остаются общими для старой и новой версии.")
    # старая версия
    pos = {"R": (230, 120), "A": (130, 210), "B": (330, 210), "L1": (90, 300), "L2": (170, 300), "L3": (290, 300), "L4": (370, 300)}
    for a, b in [("R", "A"), ("R", "B"), ("A", "L1"), ("A", "L2"), ("B", "L3"), ("B", "L4")]:
        f.edge(*pos[a], *pos[b], r1=17, r2=17, color=EDGE, arrow=False)
    new = {"R'": (520, 120), "B'": (600, 210), "L3'": (560, 300)}
    f.edge(*new["R'"], *new["B'"], r1=17, r2=17, color=GREEN, arrow=False, sw=3)
    f.edge(*new["B'"], *new["L3'"], r1=17, r2=17, color=GREEN, arrow=False, sw=3)
    f.edge(*new["R'"], *pos["A"], r1=17, r2=17, color=GREEN, arrow=False, dash="6 5", bend=-18)
    f.edge(*new["B'"], *pos["L4"], r1=17, r2=17, color=GREEN, arrow=False, dash="6 5", bend=22)
    for k, (x, y) in pos.items():
        shared = k in ("A", "L4")
        f.node(x, y, k, color=BLUE if not shared else YELLOW, r=17, size=13)
    for k, (x, y) in new.items():
        f.node(x, y, k, color=GREEN, r=17, size=13)
    f.text(230, 80, "версия 0", size=14, fill=BLUE, anchor="middle", weight=700)
    f.text(520, 80, "версия 1", size=14, fill=GREEN, anchor="middle", weight=700)
    f.text(32, 352, "Жёлтые вершины A и L4 общие: новая версия ссылается на них. Новых вершин — столько, сколько уровней.", size=14, fill=TEXT2)
    return f.svg()


def dcp_time():
    f = Fig("sg2", 400, title="Offline dynamic connectivity: рёбра по дереву времени",
            sub="Ребро на [l, r) попадает в O(log T) вершин; DFS добавляет их в СНМ и откатывает.")
    ox, cw, T = 60, 80, 8
    levels = [(0, 8, 110), (0, 4, 170), (4, 8, 170), (0, 2, 230), (2, 4, 230), (4, 6, 230), (6, 8, 230)]
    for l, r, y in levels:
        f.cell(ox + l * cw + 4, y - 20, "", w=(r - l) * cw - 8, h=36, fill=NODE2, stroke=GRID)
        f.text(ox + (l + r) * cw / 2, y - 24, f"[{l}, {r})", size=12.5, fill=MUTED, anchor="middle")
    for t in range(T):
        f.cell(ox + t * cw + 4, 270, f"t={t}", w=cw - 8, h=34, fill=NODE, size=14)
    # рёбра: e1 [0,8) -> корень; e2 [2,6) -> [2,4), [4,6); e3 [1,3) -> [1,2), [2,3)
    chips = [("a", BLUE, [(0, 8, 110)]), ("b", ORANGE, [(2, 4, 230), (4, 6, 230)]), ("c", GREEN, [(1, 2, 270), (2, 3, 270)])]
    for name, col, spots in chips:
        for l, r, y in spots:
            cx = ox + (l + r) * cw / 2 + (14 if name == "c" else (-14 if name == "b" else 0))
            if y == 270:
                f.circle(cx, 322, 11, fill=col, stroke=col)
                f.text(cx, 327, name, size=13, fill=BG, anchor="middle", weight=700)
            else:
                f.circle(cx, y - 2, 11, fill=col, stroke=col)
                f.text(cx, y + 3, name, size=13, fill=BG, anchor="middle", weight=700)
    f.legend(60, 362, [(BLUE, "ребро a: [0, 8)", "dot")], size=13.5)
    f.legend(280, 362, [(ORANGE, "ребро b: [2, 6)", "dot")], size=13.5)
    f.legend(500, 362, [(GREEN, "ребро c: [1, 3)", "dot")], size=13.5)
    return f.svg()


def lichao_cases():
    f = Fig("sg3", 360, title="Ли Чао: в вершине остаётся прямая, лучшая в середине отрезка",
            sub="Проигравшая прямая может быть лучше только в одной половине — туда она и спускается.")
    x0, x1 = 60, 700
    f.line(x0, 300, x1, 300, stroke=AXIS, sw=2)
    f.line(x0, 90, x0, 300, stroke=AXIS, sw=2)
    # две прямые (экранные y растёт вниз)
    f.line(x0, 250, x1, 130, stroke=BLUE, sw=4)
    f.line(x0, 140, x1, 270, stroke=ORANGE, sw=4)
    xm = (x0 + x1) / 2
    f.line(xm, 90, xm, 300, stroke=MUTED, sw=2, dash="6 5")
    f.text(xm, 320, "x_m (середина)", size=14, fill=MUTED, anchor="middle")
    f.text(x0, 320, "x_l", size=14, fill=MUTED)
    f.text(x1, 320, "x_r", size=14, fill=MUTED, anchor="end")
    f.text(x1 - 10, 122, "старая прямая", size=14, fill=BLUE, anchor="end", weight=700)
    f.text(x1 - 10, 292, "новая прямая", size=14, fill=ORANGE, anchor="end", weight=700)
    f.circle(xm, 205, 7, fill=YELLOW, stroke=YELLOW)
    f.text(xm + 12, 232, "в x_m ниже оранжевая → остаётся в вершине", size=14, fill=YELLOW)
    f.text(120, 215, "слева синяя ниже", size=14, fill=BLUE)
    f.line(300, 170, 150, 175, stroke=BLUE, sw=3, arrow=True)
    f.text(120, 120, "проигравшая (синяя) уходит влево", size=14, fill=BLUE, weight=700)
    return f.svg()


def kinetic():
    f = Fig("sg4", 350, title="Kinetic segment tree: melting point вершины",
            sub="Пока x не дошёл до точки пересечения, победитель в вершине не меняется.")
    f.line(40, 290, 380, 290, stroke=AXIS, sw=2)
    f.line(40, 290, 40, 90, stroke=AXIS, sw=2)
    f.line(40, 250, 380, 110, stroke=GREEN, sw=4)                 # растёт «вверх» (экран: y меньше)
    f.line(40, 150, 380, 230, stroke=BLUE, sw=4)
    cross = 40 + (250 - 150) / ((250 - 150) + (230 - 110) * 0 + 0.0) if False else 190
    f.circle(190, 187, 6, fill=YELLOW, stroke=YELLOW)
    f.line(90, 290, 90, 120, stroke=ORANGE, sw=2, dash="6 5")
    f.text(90, 312, "x", size=14, fill=ORANGE, anchor="middle", weight=700)
    f.text(190, 312, "x*", size=14, fill=YELLOW, anchor="middle", weight=700)
    f.line(92, 275, 188, 275, stroke=YELLOW, sw=3, arrow=True)
    f.text(140, 268, "melt", size=14, fill=YELLOW, anchor="middle", weight=700)
    f.text(52, 274, "сейчас лучшая", size=14, fill=GREEN, weight=700)
    f.text(250, 126, "растёт медленнее — обгонит", size=14, fill=BLUE, weight=700)
    # дерево
    f.node(570, 120, "v", color=BLUE, r=20, size=16)
    f.node(500, 220, "L", color=GREEN, r=18, size=15)
    f.node(640, 220, "R", color=BLUE, r=18, size=15)
    f.edge(570, 120, 500, 220, r1=20, r2=18, arrow=False)
    f.edge(570, 120, 640, 220, r1=20, r2=18, arrow=False)
    f.text(570, 80, "melt(v) = min(melt(L), melt(R), x* − x)", size=13.5, fill=TEXT2, anchor="middle")
    f.text(570, 276, "x += d: если d ≤ melt — просто", size=14, fill=TEXT2, anchor="middle")
    f.text(570, 298, "обновляем val и melt;", size=14, fill=TEXT2, anchor="middle")
    f.text(570, 320, "иначе спускаемся к детям", size=14, fill=TEXT2, anchor="middle")
    return f.svg()


def hist_sum():
    f = Fig("sg5", 330, title="Историческая сумма: S_k = D + A · k",
            sub="Вместо суммы всех версий храним два обычных массива, которые меняются на отрезке.")
    cols = ["после запроса", "A", "D", "S = D + k·A"]
    xs = [40, 220, 400, 540]
    for x, c in zip(xs, cols):
        f.text(x, 108, c, size=14.5, fill=MUTED, weight=700)
    rows = [("k = 0: A = [1, 2, 3]", "[1, 2, 3]", "[0, 0, 0]", "[0, 0, 0]"),
            ("k = 1: +1 на [0, 2)", "[2, 3, 3]", "[0, 0, 0]", "[2, 3, 3]"),
            ("k = 2: +2 на [1, 3)", "[2, 5, 5]", "[0, −2, −2]", "[4, 8, 8]")]
    for i, r in enumerate(rows):
        y = 150 + i * 46
        f.rect(32, y - 26, 696, 38, fill=NODE2, stroke=GRID, rx=8)
        for j, (x, t) in enumerate(zip(xs, r)):
            f.text(x + 4, y, t, size=15, fill=[TEXT, BLUE, ORANGE, GREEN][j], weight=700 if j else None)
    f.text(32, 300, "При A[l..r) += x: A += x, D −= k·x на том же отрезке, потом k++. Проверка: A₁ + A₂ = [2,3,3] + [2,5,5] = [4,8,8].", size=13.5, fill=TEXT2)
    return f.svg()


def beats_second_max():
    f = Fig("sg6", 360, title="Beats: при x > второго максимума chmin меняет только максимумы",
            sub="В вершине храним max, второй max (строго меньше) и количество максимумов.")
    vals = [3, 7, 5, 7, 2, 7, 4]
    ox, cw, base, unit = 80, 70, 280, 24
    x_cut = 6
    for i, v in enumerate(vals):
        col = ORANGE if v == 7 else BLUE
        f.rect(ox + i * cw, base - v * unit, cw - 14, v * unit, fill=col, op=0.85, rx=3)
        if v == 7:
            f.rect(ox + i * cw, base - 7 * unit, cw - 14, (7 - x_cut) * unit, fill=RED, op=0.5, rx=3, dash="5 4")
        f.text(ox + i * cw + (cw - 14) / 2, base + 22, str(v), size=15, fill=TEXT, anchor="middle", weight=700)
    f.line(ox - 20, base - x_cut * unit, ox + len(vals) * cw, base - x_cut * unit, stroke=YELLOW, sw=3, dash="8 5")
    f.text(ox - 24, base - x_cut * unit + 5, "x = 6", size=14, fill=YELLOW, anchor="end", weight=700)
    f.line(ox - 20, base - 5 * unit, ox + len(vals) * cw, base - 5 * unit, stroke=GREEN, sw=2, dash="3 4")
    f.text(ox + len(vals) * cw + 4, base - 5 * unit + 5, "2-й max = 5", size=13.5, fill=GREEN, weight=700)
    f.text(ox + len(vals) * cw + 4, base - 7 * unit + 5, "max = 7 (×3)", size=13.5, fill=ORANGE, weight=700)
    f.text(32, 335, "x = 6 > 5: задеты только три семёрки, sum −= (7 − 6) · 3. Если бы x ≤ 5, пришлось бы спускаться.", size=13.5, fill=TEXT2)
    return f.svg()


def beats_vertices():
    f = Fig("sg7", 360, title="Три вида вершин при оценке работы алгоритма",
            sub="Дополнительные — спуск из-за невыполненного условия; в тупиковых ставим тег.")
    def n(x, y, color, label=""):
        f.node(x, y, label, color=color, r=16, size=13)
    n(380, 110, BLUE, "v")
    f.edge(380, 110, 260, 190, r1=16, r2=16, arrow=False); f.edge(380, 110, 500, 190, r1=16, r2=16, arrow=False)
    n(260, 190, ORANGE); n(500, 190, ORANGE)
    for (px, py, cx_list) in [(260, 190, [(190, 270, ORANGE), (330, 270, GREEN)]), (500, 190, [(430, 270, GREEN), (570, 270, GREEN)])]:
        for cx, cy, col in cx_list:
            f.edge(px, py, cx, cy, r1=16, r2=16, arrow=False)
            n(cx, cy, col)
    for cx in (140, 240):
        f.edge(190, 270, cx, 340 - 8, r1=16, r2=10, arrow=False)
        f.circle(cx, 340 - 8, 10, fill=NODE, stroke=GREEN, sw=2.5)
    f.legend(560, 110, [(BLUE, "обычная", "dot"), (ORANGE, "дополнительная", "dot"), (GREEN, "тупиковая", "dot")], size=14, gap=24)
    return f.svg()


FIGS = {
    1: (persistent_path, "Новая версия создаёт $O(\\log n)$ вершин: путь от корня до изменённого листа; остальное разделяется со старой версией."),
    2: (dcp_time, "Каждое ребро попадает в $O(\\log T)$ вершин дерева отрезков по времени; при обходе его добавляют в СНМ при входе и откатывают при выходе."),
    3: (lichao_cases, "Из двух прямых в вершине остаётся та, что ниже в середине; вторая может быть лучше лишь слева или справа от середины."),
    4: (kinetic, "Melting point вершины — момент, когда в поддереве может сменить победителя какая-то пара прямых."),
    5: (hist_sum, "Массив $S$ восстанавливается по $D$ и $A$ как $S=D+A\\cdot k$; обновление отрезка трогает только $A$ и $D$."),
    7: (beats_second_max, "Если $x$ строго больше второго максимума, то $\\min=x$ затрагивает только максимумы вершины."),
    6: (beats_vertices, "Обычные вершины — $O(\\log n)$ на запрос; каждая дополнительная уменьшает потенциал; тупиковых не больше, чем $2\\cdot(\\text{обычных}+\\text{дополнительных})$."),
}
