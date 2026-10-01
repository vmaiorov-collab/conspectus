from kit import *

NOTE = "parallel-ap/parallel-ap-zan1-kornevye.html"


def blocks():
    n, K, l, r = 20, 4, 2, 17
    f = Fig("k1", 380, title="add(l, r, x) на блоках: n = 20, K = 4, запрос [2, 17]",
            sub="Отрезок распадается на хвост слева, целые блоки и хвост справа.")
    cw, ox, oy = 33, 50, 150
    for b in range(n // K):
        x = ox + b * K * cw
        full = l <= b * K and (b + 1) * K - 1 <= r
        f.rect(x + 2, oy - 34, K * cw - 4, 24, fill=BLUE if full else NODE2, op=0.35 if full else None,
               stroke=BLUE if full else GRID, rx=5)
        f.text(x + K * cw / 2, oy - 17, f"блок {b}", size=13.5, anchor="middle", fill=TEXT if full else MUTED)
    for i in range(n):
        x = ox + i * cw
        if l <= i <= r:
            blk = i // K
            full = l <= blk * K and (blk + 1) * K - 1 <= r
            col = BLUE if full else (GREEN if i < (l // K + 1) * K else ORANGE)
        else:
            col = None
        f.cell(x + 1, oy, "", w=cw - 2, h=36, fill=col if col else NODE, stroke=col if col else GRID)
        if col:
            f.rect(x + 1, oy, cw - 2, 36, fill=col, op=0.45 if col != BLUE else 0.25, rx=6)
        f.text(x + cw / 2, oy + 58, str(i), size=13, anchor="middle", fill=TEXT if col else MUTED)
        if i % K == 0 and i:
            f.line(x, oy - 38, x, oy + 42, stroke=AXIS, sw=1.5, dash="3 4")
    # скобки и действия
    def brace(i0, i1, color, head, body):
        x0, x1 = ox + i0 * cw + 2, ox + (i1 + 1) * cw - 2
        y = oy + 76
        f.path(f"M{x0},{y} v8 H{x1} v-8", stroke=color, sw=2)
        cx = (x0 + x1) / 2
        f.text(cx, y + 32, head, size=15, anchor="middle", fill=color, weight=700)
        for k, line in enumerate(body):
            f.text(cx, y + 54 + k * 20, line, size=14, anchor="middle", fill=TEXT2)
    brace(2, 3, GREEN, "хвост", ["a[i] += x", "по одному"])
    brace(4, 15, BLUE, "3 целых блока", ["add[блок] += x — O(1) на блок,", "элементы не трогаем"])
    brace(16, 17, ORANGE, "хвост", ["a[i] += x", "по одному"])
    f.note(352, "Хвосты — не больше 2K элементов, блоков — не больше n/K. При K ≈ √n запрос стоит O(√n).", size=14.5)
    return f.svg()


def mo_order():
    B = 4
    # запросы (l, r): по полосам l // B; внутри полосы — по r, направление чередуется
    qs = [(1, 3), (3, 6), (0, 9), (2, 13),
          (5, 15), (7, 11), (4, 8), (6, 6),
          (9, 10), (10, 12), (8, 14), (11, 15),
          (12, 15), (14, 14), (13, 13)]
    bands = {}
    for q in qs:
        bands.setdefault(q[0] // B, []).append(q)
    order = []
    for b in sorted(bands):
        order += sorted(bands[b], key=lambda q: q[1], reverse=(b % 2 == 1))
    f = Fig("k2", 470, title="Порядок Мо: полосы по l, внутри полосы — по r",
            sub="Каждая точка — запрос (l, r). Линия показывает, в каком порядке их обработать.")
    ox, oy, s = 70, 420, 19.5
    N = 16
    X = lambda l: ox + (l + 0.5) * s * 1.55
    Y = lambda r: oy - (r + 0.5) * s
    xw = s * 1.55
    for b in range(N // B):
        x0 = ox + b * B * xw
        f.rect(x0, Y(N - 0.5), B * xw, N * s, fill=BLUE if b % 2 == 0 else PURPLE, op=0.07, rx=0)
        f.text(x0 + B * xw / 2, Y(N - 0.5) - 8, f"полоса {b}", size=14, anchor="middle", fill=MUTED)
        if b:
            f.line(x0, Y(N - 0.5), x0, oy, stroke=AXIS, sw=1.5, dash="4 4")
    f.line(ox, oy, ox + N * xw, oy, stroke=AXIS, sw=1.5)
    f.line(ox, oy, ox, Y(N - 0.5), stroke=AXIS, sw=1.5)
    f.text(ox + N * xw, oy + 24, "l →", size=14, fill=MUTED, anchor="end")
    f.text(ox - 10, Y(N - 1) + 4, "r", size=14, fill=MUTED, anchor="end", italic=True)
    f.text(ox - 10, Y(N - 2) + 4, "↑", size=14, fill=MUTED, anchor="end")
    for i in range(0, N, 4):
        f.text(X(i), oy + 22, str(i), size=13, anchor="middle", fill=MUTED)
    pts = [(X(l), Y(r)) for l, r in order]
    f.polyline(pts, stroke=ORANGE, sw=2.5)
    for i, (x, y) in enumerate(pts):
        f.circle(x, y, 10, fill=NODE, stroke=ORANGE, sw=2)
        f.text(x, y + 4.5, str(i + 1), size=12, anchor="middle", weight=700)
    tx = ox + N * xw + 30
    f.text(tx, 130, "Внутри полосы", size=15, weight=700)
    f.text(tx, 152, "r идёт только вверх", size=14, fill=TEXT2)
    f.text(tx, 172, "или только вниз:", size=14, fill=TEXT2)
    f.text(tx, 192, "O(n) на полосу.", size=14, fill=TEXT2)
    f.text(tx, 236, "l прыгает лишь", size=15, weight=700)
    f.text(tx, 258, "внутри полосы:", size=14, fill=TEXT2)
    f.text(tx, 278, "≤ B на запрос.", size=14, fill=TEXT2)
    f.text(tx, 322, "«Змейка»", size=15, weight=700)
    f.text(tx, 344, "чётные полосы — вверх,", size=14, fill=TEXT2)
    f.text(tx, 364, "нечётные — вниз,", size=14, fill=TEXT2)
    f.text(tx, 384, "r не бегает назад.", size=14, fill=TEXT2)
    return f.svg()


def euler_tree():
    pos = {1: (380, 108), 2: (230, 166), 5: (530, 166), 3: (160, 228), 4: (300, 228),
           6: (600, 228), 7: (540, 290), 8: (660, 290)}
    tree = [(1, 2), (2, 3), (2, 4), (1, 5), (5, 6), (6, 7), (6, 8)]
    tour = [1, 2, 3, 2, 4, 2, 1, 5, 6, 7, 6, 8, 6, 5, 1]
    s_, f_ = 3, 8
    a, b = tour.index(s_), tour.index(f_)
    seg = [(tour[i - 1], tour[i]) for i in range(a + 1, b + 1)]
    key = lambda e: tuple(sorted(e))
    cnt = {}
    for e in seg:
        cnt[key(e)] = cnt.get(key(e), 0) + 1
    path = {e for e, c in cnt.items() if c % 2 == 1}

    f = Fig("k3", 520, title="Мо на дереве: путь 3 → 8 из эйлерова обхода",
            sub="Берём кусок обхода от первого входа в 3 до первого входа в 8 и смотрим на рёбра-переходы.")
    for u, v in tree:
        on = key((u, v)) in path
        f.edge(*pos[u], *pos[v], r1=17, r2=17, color=ORANGE if on else EDGE, sw=3.5 if on else 2, arrow=False)
    for v, (x, y) in pos.items():
        col = ORANGE if v in (s_, f_) else (BLUE if any(v in e for e in path) else GRID)
        f.node(x, y, v, color=col, r=17)
    f.text(pos[3][0] - 26, pos[3][1] + 5, "s", size=15, fill=ORANGE, anchor="end", weight=700, italic=True)
    f.text(pos[8][0] + 26, pos[8][1] + 5, "f", size=15, fill=ORANGE, weight=700, italic=True)

    cw, ox, oy = 44, 50, 350
    f.text(ox, oy - 14, "эйлеров обход:", size=14, fill=MUTED)
    for i, v in enumerate(tour):
        inside = a <= i <= b
        f.cell(ox + i * cw + 2, oy, v, w=cw - 4, h=38, fill=YELLOW if i in (a, b) else NODE,
               stroke=YELLOW if inside else GRID, tcolor=BG if i in (a, b) else (TEXT if inside else MUTED))
    # рёбра-переходы под стыками ячеек
    for i in range(a + 1, b + 1):
        e = (tour[i - 1], tour[i])
        odd = key(e) in path
        x = ox + i * cw
        f.text(x, oy + 62, f"{e[0]}–{e[1]}", size=13.5, anchor="middle",
               fill=ORANGE if odd else MUTED, weight=700 if odd else None)
        if not odd:
            f.line(x - 14, oy + 57, x + 14, oy + 57, stroke=MUTED, sw=1.5)
    f.text(ox + a * cw + cw / 2, oy + 88, "↑ первый вход в 3", size=13.5, anchor="start", fill=YELLOW)
    f.text(ox + (b + 1) * cw, oy + 88, "первый вход в 8 ↑", size=13.5, anchor="end", fill=YELLOW)
    f.note(472, "Рёбра 2–4 и 6–7 встретились дважды (туда и обратно) — они сокращаются.", size=14.5)
    f.note(496, "Рёбра, встретившиеся нечётное число раз, — это ровно путь 3 → 2 → 1 → 5 → 6 → 8.", size=14.5, color=ORANGE)
    return f.svg()


FIGS = {
    1: (blocks, "Хвосты обновляем поэлементно, а целые блоки — одной пометкой <code>add</code>; так запрос стоит $O(K + n/K)$."),
    2: (mo_order, "Сортировка по $(\\lfloor l/B\\rfloor, r)$ «змейкой»: $r$ монотонен внутри полосы, $l$ двигается не дальше $B$."),
    3: (euler_tree, "На отрезке обхода между первыми входами в $s$ и $f$ рёбра пути встречаются нечётно, остальные — чётно."),
}
