from kit import *

NOTE = "parallel-c/parallel-c-zan4-bazovye-struktury.html"


def containers():
    f = Fig("bs1", 392, title="Стек, очередь и дек",
            sub="Где можно добавлять и удалять элементы — то и определяет контейнер.")
    # --- стек: вертикальная «ваза» ---
    sx, sw, ch = 70, 100, 44
    base = 340
    f.text(sx - 8, 90, "стек (LIFO)", size=16, weight=700)
    f.path(f"M{sx - 8},{base - 3 * ch - 24} V{base + 8} H{sx + sw + 8} V{base - 3 * ch - 24}", stroke=AXIS, sw=2.5)
    for k, v in enumerate((10, 20, 30)):
        y = base - (k + 1) * ch
        top = k == 2
        f.cell(sx, y, v, w=sw, h=ch - 4, fill=YELLOW if top else NODE, stroke=YELLOW if top else GRID,
               tcolor=BG if top else TEXT)
    f.line(sx + 28, 108, sx + 28, 180, stroke=GREEN, sw=2.5, arrow=True)
    f.text(sx + 18, 134, "push(x)", size=14.5, fill=GREEN, anchor="end", weight=700)
    f.line(sx + 72, 180, sx + 72, 108, stroke=RED, sw=2.5, arrow=True)
    f.text(sx + 82, 134, "pop()", size=14.5, fill=RED, weight=700)
    f.text(sx - 6, base + 30, "top() = 30 — только верхний", size=14, fill=MUTED)

    # --- очередь и дек: горизонтальные «трубы» ---
    def pipe(y, title, deque):
        x0, cw = 360, 70
        f.text(x0, y - 22, title, size=16, weight=700)
        f.path(f"M{x0 - 8},{y - 4} H{x0 + 3 * cw + 8} M{x0 - 8},{y + 44} H{x0 + 3 * cw + 8}", stroke=AXIS, sw=2.5)
        for k, v in enumerate((10, 20, 30)):
            f.cell(x0 + k * cw + 3, y, v, w=cw - 6, h=40, fill=NODE)
        f.cell(x0 + 3, y, 10, w=cw - 6, h=40, fill=BLUE, stroke=BLUE, tcolor=BG)
        f.cell(x0 + 2 * cw + 3, y, 30, w=cw - 6, h=40, fill=PURPLE, stroke=PURPLE, tcolor=BG)
        # левый конец
        if deque:
            f.line(x0 - 70, y + 20, x0 - 12, y + 20, stroke=GREEN, sw=2.5, arrow=True)
            f.text(x0 - 150, y + 14, "push_front", size=14, fill=GREEN, weight=700)
            f.text(x0 - 150, y + 34, "pop_front", size=14, fill=RED, weight=700)
        else:
            f.line(x0 - 12, y + 20, x0 - 70, y + 20, stroke=RED, sw=2.5, arrow=True)
            f.text(x0 - 128, y + 25, "pop()", size=14, fill=RED, weight=700)
        # правый конец
        xe = x0 + 3 * cw
        f.line(xe + 70, y + 20, xe + 12, y + 20, stroke=GREEN, sw=2.5, arrow=True)
        f.text(xe + 78, y + 14 if deque else y + 25, "push_back" if deque else "push(x)", size=14, fill=GREEN, weight=700)
        if deque:
            f.text(xe + 78, y + 34, "pop_back", size=14, fill=RED, weight=700)
        f.text(x0 + cw / 2, y + 66, "front()", size=14, fill=BLUE, anchor="middle", weight=700)
        f.text(x0 + 2.5 * cw, y + 66, "back()", size=14, fill=PURPLE, anchor="middle", weight=700)
    pipe(140, "очередь (FIFO)", False)
    pipe(274, "дек (двусторонняя очередь)", True)
    return f.svg()


def _bars(f, ox, base, unit, hu, vals, first_idx=0, fills=None, hide=()):
    for k, v in enumerate(vals):
        x = ox + k * unit
        idx = first_idx + k
        f.text(x + unit / 2, base + 22, str(idx), size=14, fill=MUTED, anchor="middle")
        if v == 0:
            continue
        fill, stroke, tc = (fills or {}).get(idx, (NODE, BLUE, TEXT))
        f.rect(x + 4, base - v * hu, unit - 8, v * hu, fill=fill, stroke=stroke, sw=2, rx=5)
        f.text(x + unit / 2, base - v * hu + 22, str(v), size=15.5, fill=tc, anchor="middle", weight=700)


def histogram():
    a = [2, 1, 5, 6, 2, 3]
    f = Fig("bs2", 330, title="Гистограмма: самый большой прямоугольник",
            sub="Высоты 2, 1, 5, 6, 2, 3; ширина каждого столбика — 1.")
    ox, unit, hu, base = 70, 74, 30, 276
    f.line(ox - 10, base, ox + 6 * unit + 10, base, stroke=AXIS, sw=2)
    _bars(f, ox, base, unit, hu, a)
    # лучший прямоугольник: столбики 2..3, высота 5
    f.rect(ox + 2 * unit + 2, base - 5 * hu, 2 * unit - 4, 5 * hu, fill="none", stroke=ORANGE, sw=3.5, rx=6)
    # сравнение: высота 2 на столбиках 2..5
    f.rect(ox + 2 * unit + 6, base - 2 * hu + 4, 4 * unit - 12, 2 * hu - 8, fill="none", stroke=GREEN, sw=2.5, rx=6, dash="7 5")
    f.legend(ox + 6 * unit + 30, 120, [(ORANGE, "лучший: 5 × 2 = 10", "line"), (GREEN, "для сравнения: 2 × 4 = 8", "line")], size=14)
    return f.svg()


def bounds():
    a = [0, 2, 1, 5, 6, 2, 3, 0]          # индексы -1 .. 6
    f = Fig("bs3", 330, title="Идея: прямоугольник, у которого «потолком» служит столбик i",
            sub="Для i = 4 (высота 2): ближайший меньший слева — индекс 1, справа — «нулевой» столбик с индексом 6.")
    ox, unit, hu, base = 60, 80, 30, 276
    f.line(ox - 10, base, ox + 8 * unit + 10, base, stroke=AXIS, sw=2)
    fills = {4: (YELLOW, YELLOW, BG), 1: (RED, RED, BG)}
    vals = a
    for k, v in enumerate(vals):
        idx = k - 1
        x = ox + k * unit
        f.text(x + unit / 2, base + 22, str(idx), size=14, fill=MUTED, anchor="middle")
        if idx in (-1, 6):
            f.rect(x + 4, base - 22, unit - 8, 22, fill="none", stroke=AXIS, sw=1.5, rx=5, dash="5 4")
            f.text(x + unit / 2, base - 6, "0", size=14, fill=MUTED, anchor="middle")
            continue
        fill, stroke, tc = fills.get(idx, (NODE, BLUE, TEXT))
        f.rect(x + 4, base - v * hu, unit - 8, v * hu, fill=fill, stroke=stroke, sw=2, rx=5)
        f.text(x + unit / 2, base - v * hu + 22, str(v), size=15.5, fill=tc, anchor="middle", weight=700)
    # прямоугольник между L[i] и R[i]
    xl, xr = ox + 3 * unit, ox + 7 * unit - 0
    f.rect(xl + 2, base - 2 * hu, xr - xl - 4, 2 * hu, fill="none", stroke=ORANGE, sw=3.5, rx=6)
    f.text(ox + 5 * unit + 14, 128, "l = L[i]+1 = 2, r = R[i]−1 = 5", size=14.5, fill=ORANGE, weight=700)
    f.text(ox + 5 * unit + 14, 150, "S = (r − l + 1) · a[i] = 4 · 2 = 8", size=14.5, fill=ORANGE, weight=700)
    f.text(ox + 2 * unit + unit / 2, 100, "L[i]", size=15, fill=RED, anchor="middle", weight=700)
    f.line(ox + 2 * unit + unit / 2, 108, ox + 2 * unit + unit / 2, base - 1 * hu - 14, stroke=RED, sw=2, arrow=True)
    f.text(ox + 7 * unit + 40, 100, "R[i]", size=15, fill=RED, anchor="middle", weight=700)
    f.line(ox + 7 * unit + 40, 108, ox + 7 * unit + 40, base - 40, stroke=RED, sw=2, arrow=True)
    return f.svg()


def stack_table():
    f = Fig("bs4", 410, title="Ближайший меньший слева: стек индексов, a = [2, 1, 5, 6, 2, 3]",
            sub="Пока вершина не ниже a[i] — снимаем её. Что осталось на вершине — это L[i]. Затем кладём i.")
    cols = [32, 86, 176, 482, 548]
    heads = ["i", "a[i]", "что делаем со стеком", "L[i]", "стек после"]
    y = f.top + 16
    for x, t in zip(cols, heads):
        f.text(x, y, t, size=14, fill=MUTED, weight=700)
    f.line(32, y + 10, 728, y + 10, stroke=GRID, sw=1.5)
    rows = [
        (0, 2, "стек пуст → ближайшего нет", "−1", "[0]"),
        (1, 1, "снимаем 0 (a=2 ≥ 1); стек пуст", "−1", "[1]"),
        (2, 5, "вершина 1 (a=1 < 5) — остаёмся", "1", "[1, 2]"),
        (3, 6, "вершина 2 (a=5 < 6) — остаёмся", "2", "[1, 2, 3]"),
        (4, 2, "снимаем 3 (6 ≥ 2), 2 (5 ≥ 2); вершина 1", "1", "[1, 4]"),
        (5, 3, "вершина 4 (a=2 < 3) — остаёмся", "4", "[1, 4, 5]"),
    ]
    for k, (i, v, what, L, st) in enumerate(rows):
        yy = y + 38 + k * 38
        pops = "снимаем" in what
        if k % 2 == 0:
            f.rect(26, yy - 22, 708, 34, fill=NODE2, rx=6)
        f.text(cols[0], yy, str(i), size=15.5, weight=700)
        f.text(cols[1], yy, str(v), size=15.5, weight=700)
        f.text(cols[2], yy, what, size=14.5, fill=RED if pops else TEXT2)
        f.text(cols[3], yy, L, size=15.5, fill=YELLOW, weight=700)
        f.text(cols[4], yy, st, size=15, fill=GREEN)
    f.note(f.top + 16 + 38 + 6 * 38 + 18, "Аналогично справа налево: R = [1, 6, 4, 4, 6, 6]. Площади (R−L−1)·a: 2, 6, 10, 6, 8, 3 → ответ 10.", size=14.5, color=TEXT2)
    return f.svg()


def matrix():
    A = [[1, 0, 1, 0, 0],
         [0, 0, 1, 0, 0],
         [0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0]]
    H = []
    for i, r in enumerate(A):
        H.append([0 if v else (H[i - 1][j] + 1 if i else 1) for j, v in enumerate(r)])
    f = Fig("bs5", 362, title="Матрица из нулей и единиц → гистограммы",
            sub="h[i][j] — длина столбика из нулей, который заканчивается в клетке (i, j) и растёт вверх.")
    cw = 44
    ox1, ox2, oy = 60, 420, 130
    f.text(ox1, oy - 14, "матрица a", size=15, fill=TEXT2, weight=700)
    f.text(ox2, oy - 14, "высоты h (гистограмма в каждой строке)", size=15, fill=TEXT2, weight=700)
    for i in range(4):
        f.text(ox1 - 14, oy + i * cw + 28, str(i), size=14, fill=MUTED, anchor="end")
        for j in range(5):
            v = A[i][j]
            f.cell(ox1 + j * cw, oy + i * cw, v, w=cw - 4, h=cw - 4, fill=RED if v else NODE,
                   stroke=RED if v else GRID, tcolor=BG if v else TEXT)
            hv = H[i][j]
            f.cell(ox2 + j * cw, oy + i * cw, hv, w=cw - 4, h=cw - 4, fill=NODE if hv else NODE2,
                   stroke=BLUE if hv else GRID, tcolor=TEXT if hv else MUTED)
    # лучший прямоугольник: строки 2..3, столбцы 1..3
    f.rect(ox1 + 1 * cw - 3, oy + 2 * cw - 3, 3 * cw + 2, 2 * cw + 2, fill="none", stroke=YELLOW, sw=3.5, rx=7)
    f.rect(ox2 + 1 * cw - 3, oy + 3 * cw - 3, 3 * cw + 2, cw + 2, fill="none", stroke=YELLOW, sw=3.5, rx=7)
    f.line(ox1 + 5 * cw + 14, oy + 2 * cw, ox2 - 22, oy + 2 * cw, stroke=AXIS, sw=2, arrow=True)
    f.text((ox1 + 5 * cw + ox2) / 2 - 4, oy + 2 * cw - 10, "h[i][j] = 0, если a=1,", size=13.5, fill=MUTED, anchor="middle")
    f.text((ox1 + 5 * cw + ox2) / 2 - 4, oy + 2 * cw + 20, "иначе h[i−1][j] + 1", size=13.5, fill=MUTED, anchor="middle")
    f.note(oy + 4 * cw + 26, "Строка 3: высоты 0, 4, 2, 4, 1 → лучший прямоугольник — столбики 1–3 на высоте 2: площадь 3·2 = 6.", size=14.5, color=YELLOW)
    return f.svg()


def segments():
    segs = [(1, 4), (3, 6), (8, 11), (9, 12), (10, 14), (16, 18)]
    cols = [BLUE, BLUE, ORANGE, ORANGE, ORANGE, PURPLE]
    f = Fig("bs6", 360, title="Объединение отрезков",
            sub="Сортируем по левой границе; пока следующий отрезок начинается не правее R — продлеваем R.")
    ox, u = 52, 34
    y0 = f.top + 14
    for x in range(0, 20):
        f.line(ox + x * u, y0 - 6, ox + x * u, y0 + 6 * 26 + 6, stroke=GRID, sw=1, op=0.5)
        f.text(ox + x * u, y0 + 6 * 26 + 24, str(x), size=13, fill=MUTED, anchor="middle")
    for k, ((l, r), c) in enumerate(zip(segs, cols)):
        y = y0 + k * 26
        f.rect(ox + l * u, y, (r - l) * u, 18, fill=c, rx=4)
        f.text(ox + l * u - 8, y + 14, f"[{l}, {r}]", size=13, fill=TEXT2, anchor="end")
    yr = y0 + 6 * 26 + 44
    for (l, r) in ((1, 6), (8, 14), (16, 18)):
        f.rect(ox + l * u, yr, (r - l) * u, 20, fill=GREEN, rx=4)
        f.text(ox + (l + r) / 2 * u, yr + 15, f"[{l}, {r}]", size=13.5, fill=BG, anchor="middle", weight=700)
    f.text(ox, yr + 44, "результат: три непересекающихся отрезка", size=14.5, fill=GREEN, weight=700)
    return f.svg()


def four_pointers():
    v = [[1, 3, 5, 7], [4, 6], [11, 12], [2, 4, 6]]
    names = "ABCD"
    # шаги, на которых указатель стоял в клетке
    steps = {
        (0, 0): "1", (0, 1): "2–3", (0, 2): "4–6", (0, 3): "7",
        (1, 0): "1–4", (1, 1): "5–7",
        (2, 0): "1–7", (2, 1): "",
        (3, 0): "1–2", (3, 1): "3–5", (3, 2): "6–7",
    }
    final = {(0, 3), (1, 1), (2, 0), (3, 2)}
    f = Fig("bs7", 372, title="Четыре указателя: двигаем тот, что на минимуме",
            sub="A = 1 3 5 7, B = 4 6, C = 11 12, D = 2 4 6. Под клеткой — номера шагов, когда указатель стоял в ней.")
    ox, cw = 110, 62
    y = f.top + 22
    for t in range(4):
        yy = y + t * 66
        f.text(ox - 30, yy + 26, names[t], size=17, weight=700, anchor="middle", fill=TEXT2)
        for k, val in enumerate(v[t]):
            on = (t, k) in final
            f.cell(ox + k * cw, yy, val, w=cw - 6, h=40, fill=GREEN if on else NODE, stroke=GREEN if on else GRID,
                   tcolor=BG if on else TEXT)
            f.text(ox + k * cw + (cw - 6) / 2, yy + 58, steps.get((t, k), ""), size=13, fill=MUTED, anchor="middle")
    f.text(ox + 4 * cw + 50, y + 22, "оценка = max − min", size=14, fill=TEXT2, weight=700)
    table = [(1, "1 4 11 2", 10), (2, "3 4 11 2", 9), (3, "3 4 11 4", 8), (4, "5 4 11 4", 7),
             (5, "5 6 11 4", 7), (6, "5 6 11 6", 6), (7, "7 6 11 6", 5)]
    for k, (s, st, sc) in enumerate(table):
        yy = y + 48 + k * 24
        f.text(ox + 4 * cw + 50, yy, f"{s}.  {st}", size=13.5, fill=TEXT2)
        f.text(ox + 4 * cw + 210, yy, f"→ {sc}", size=13.5, fill=GREEN if s == 7 else MUTED, weight=700 if s == 7 else None)
    return f.svg()


def inversions():
    L, R = [2, 4, 7, 9], [3, 5, 8]
    f = Fig("bs8", 360, title="Инверсии между половинами при слиянии",
            sub="Обе половины уже отсортированы. Для каждого a[r] справа считаем элементы левой половины, строго большие его.")
    cw = 56
    ox, oy = 70, f.top + 30
    f.text(32, oy + 26, "левая", size=14, fill=MUTED)
    f.text(32, oy + 96, "правая", size=14, fill=MUTED)
    for k, val in enumerate(L):
        f.cell(ox + 60 + k * cw, oy, val, w=cw - 6, h=40)
    for k, val in enumerate(R):
        f.cell(ox + 60 + k * cw, oy + 70, val, w=cw - 6, h=40, fill=NODE2)
    # l-указатели для каждого r
    ls = [1, 2, 3]
    cols = [YELLOW, ORANGE, PURPLE]
    for k, (l, c) in enumerate(zip(ls, cols)):
        xr = ox + 60 + k * cw + (cw - 6) / 2
        xl = ox + 60 + l * cw + (cw - 6) / 2
        f.line(xr, oy + 66, xl, oy + 46, stroke=c, sw=2.5, arrow=True)
    tx = ox + 60 + 4 * cw + 40
    f.text(tx, oy + 14, "a[r]", size=14, fill=MUTED, weight=700)
    f.text(tx + 70, oy + 14, "l останавливается на", size=14, fill=MUTED, weight=700)
    f.text(tx + 280, oy + 14, "вклад", size=14, fill=MUTED, weight=700)
    for k, (r, l, c) in enumerate(zip(R, ls, cols)):
        yy = oy + 44 + k * 28
        f.text(tx, yy, str(r), size=15, fill=c, weight=700)
        f.text(tx + 70, yy, f"a[{l}] = {L[l]}  (первый > {r})", size=14.5, fill=TEXT2)
        f.text(tx + 280, yy, f"4 − {l} = {4 - l}", size=14.5, fill=c, weight=700)
    f.note(oy + 150, "Пары: (4,3) (7,3) (9,3) (7,5) (9,5) (9,8) — всего 3 + 2 + 1 = 6 инверсий между половинами.", size=14.5, color=TEXT2)
    f.note(oy + 178, "Указатель l только растёт, поэтому слияние со счётом — по-прежнему O(размер блока).", size=14.5, color=GREEN)
    return f.svg()


def puzzles():
    A = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
    contrib = [[0, 2, 4], [1, 3, 5], [2, 4, 6]]
    f = Fig("bs9", 362, title="Головоломки: сколько чужих значений меньше каждого",
            sub="Под каждым временем — число элементов в остальных строках, строго меньших его. Сумма по строке — ответ.")
    cw = 78
    ox, oy = 150, f.top + 26
    for i in range(3):
        yy = oy + i * 74
        f.text(ox - 24, yy + 28, f"строка {i + 1}", size=15, fill=TEXT2, anchor="end", weight=700)
        for j in range(3):
            f.cell(ox + j * cw, yy, A[i][j], w=cw - 8, h=42)
            f.text(ox + j * cw + (cw - 8) / 2, yy + 62, f"+{contrib[i][j]}", size=15, fill=YELLOW, anchor="middle", weight=700)
        f.text(ox + 3 * cw + 24, yy + 28, "=", size=17, fill=MUTED)
        f.text(ox + 3 * cw + 52, yy + 28, str(sum(contrib[i])), size=19, fill=GREEN, weight=700)
    f.note(oy + 3 * 74 + 8, "Для 9 «живых» элементов за один шаг: убираем максимум x из строки k и добавляем alive − cntRow[k].", size=14.5, color=TEXT2)
    return f.svg()


FIGS = {
    1: (containers, "Стек добавляет и снимает только сверху, очередь добавляет в конец и снимает с начала, дек умеет и то и другое с обоих концов."),
    2: (histogram, "Из всех прямоугольников, поместившихся под ломаной, самый большой — высоты 5 и ширины 2."),
    3: (bounds, "Если прямоугольник «упирается» в столбик $i$ сверху, то его влево и вправо ограничивают ближайшие более низкие столбики."),
    4: (stack_table, "Каждый индекс один раз кладётся в стек и не более одного раза снимается — отсюда $O(n)$ на весь проход."),
    5: (matrix, "Каждая строка матрицы даёт свою гистограмму из «растущих вверх» столбиков из нулей."),
    6: (four_pointers, "Минимум на каждом шаге двигаем вправо: любая четвёрка с этим минимальным элементом хуже текущей. Лучшая оценка — 5."),
    7: (segments, "Три цвета — три группы пересекающихся отрезков; зелёным показано объединение."),
    8: (inversions, "Для каждого $a[r]$ из правой половины указатель $l$ ищет первый больший элемент слева; все элементы правее образуют инверсии."),
    9: (puzzles, "Третья строка: $2+4+6=12$; вторая — $1+3+5=9$; первая — $0+2+4=6$."),
}
