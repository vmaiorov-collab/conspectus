import math

from kit import *

NOTE = "parallel-ap/parallel-ap-zan4-struktury-2.html"


def _row(f, x, y, vals, cw=44, h=36, fills=None, labels=None, size=15):
    for k, v in enumerate(vals):
        fill, stroke, tc = (fills or {}).get(k, (NODE, GRID, TEXT))
        f.cell(x + k * cw, y, v, w=cw - 4, h=h, fill=fill, stroke=stroke, tcolor=tc, size=size)
        if labels is not None:
            f.text(x + k * cw + (cw - 4) / 2, y + h + 16, str(labels[k]), size=12.5, fill=MUTED, anchor="middle")


def sparse_cover():
    f = Fig("sd1", 330, title="Sparse table: запрос покрывается двумя отрезками длины 2^k",
            sub="Берём k = ⌊log₂(R − L)⌋ и два полуинтервала длины 2^k: от L и до R.")
    n = 12
    a = [5, 2, 7, 3, 8, 1, 6, 4, 9, 2, 5, 3]
    ox, cw = 60, 54
    L, R = 1, 9
    k = 2                                                  # R-L = 8 -> k = 3? используем 2^k = 4 для наглядности: R-L = 7 → k = 2
    L, R = 1, 8
    fills = {i: (NODE2, GRID, MUTED) for i in range(n)}
    for i in range(L, R):
        fills[i] = (NODE, BLUE, TEXT)
    _row(f, ox, 118, a, cw=cw, fills=fills, labels=list(range(n)))
    y1, y2 = 182, 226
    f.rect(ox + L * cw - 2, y1, 4 * cw - 2, 30, fill=ORANGE, rx=6, op=0.85)
    f.text(ox + L * cw + 2 * cw - 4, y1 + 21, "[L, L + 2^k)", size=14, fill=BG, anchor="middle", weight=700)
    f.rect(ox + (R - 4) * cw - 2, y2, 4 * cw - 2, 30, fill=GREEN, rx=6, op=0.85)
    f.text(ox + (R - 2) * cw - 4, y2 + 21, "[R − 2^k, R)", size=14, fill=BG, anchor="middle", weight=700)
    f.text(ox + 6 * cw + 20, 214, "2^k ≤ R − L < 2^(k+1)", size=14.5, fill=TEXT2)
    f.note(298, "Пример: L = 1, R = 8, k = 2: ответ = min(dp[2][1], dp[2][4]). Общая часть [4, 5) учтена дважды — для min это нормально.", size=13.5, color=TEXT2)
    return f.svg()


def stack_back():
    f = Fig("sd2", 320, title="Стек с минимумом: sparse table «назад»",
            sub="dp[i][j] — минимум на 2^i элементах, заканчивающихся в позиции j.")
    ox, cw = 70, 52
    vals = [4, 7, 2, 9, 5, 3]
    n = len(vals)
    _row(f, ox, 120, vals + ["", ""], cw=cw, fills={5: (YELLOW, YELLOW, BG), 6: (NODE2, GRID, MUTED), 7: (NODE2, GRID, MUTED)},
         labels=list(range(n + 2)))
    for h, col in ((1, BLUE), (2, GREEN), (3, ORANGE)):
        L = 1 << h
        x0 = ox + (5 - L + 1) * cw
        if 5 - L + 1 < 0:
            continue
        f.path(f"M{x0},{196 + (h - 1) * 22} h{L * cw - 4}", stroke=col, sw=5)
        f.text(x0 + L * cw + 6, 202 + (h - 1) * 22, f"dp[{h}][5]: 2^{h} = {L} элем.", size=13.5, fill=col, weight=700)
    f.text(32, 276, "push(x) считает dp[0..log][j] за O(log n): значения в старых позициях не меняются.", size=14.5, fill=TEXT2)
    f.text(32, 300, "pop() — просто уменьшаем размер стека, перестраивать ничего не нужно.", size=14.5, fill=TEXT2)
    return f.svg()


def dst():
    f = Fig("sd3", 380, title="Disjoint sparse table: суффиксы слева от середины, префиксы справа",
            sub="Запрос [l, r] режется там, где l и r разошлись по разным половинам блока.")
    ox, cw = 40, 62
    n = 8
    vals = list(range(1, n + 1))
    # три уровня блоков
    levels = [(8, 120), (4, 180), (2, 240)]
    for size, y in levels:
        for s in range(0, n, size):
            f.rect(ox + s * cw - 2, y, size * cw - 4, 40, fill="none", stroke=AXIS, sw=1.5, rx=6)
            mid = s + size // 2
            f.line(ox + mid * cw - 2, y - 3, ox + mid * cw - 2, y + 43, stroke=YELLOW, sw=2)
    l, r = 1, 6
    # корень: суффикс [1,3] и префикс [4,6]
    f.rect(ox + l * cw, 126, 3 * cw - 8, 28, fill=ORANGE, rx=6, op=0.85)
    f.text(ox + (l + 1.5) * cw - 4, 146, "суффикс 1..3", size=14, fill=BG, anchor="middle", weight=700)
    f.rect(ox + 4 * cw, 126, 3 * cw - 8, 28, fill=GREEN, rx=6, op=0.85)
    f.text(ox + 5.5 * cw - 4, 146, "префикс 4..6", size=14, fill=BG, anchor="middle", weight=700)
    for k in range(n):
        f.cell(ox + k * cw, 300, vals[k], w=cw - 6, h=36, fill=YELLOW if l <= k <= r else NODE,
               stroke=YELLOW if l <= k <= r else GRID, tcolor=BG if l <= k <= r else TEXT)
        f.text(ox + k * cw + (cw - 6) / 2, 354, str(k), size=12.5, fill=MUTED, anchor="middle")
    f.text(ox, 106, "уровень 2 (блок 8)", size=13.5, fill=MUTED)
    f.text(ox, 172, "уровень 1 (блоки по 4)", size=13.5, fill=MUTED)
    f.text(ox, 232, "уровень 0 (блоки по 2)", size=13.5, fill=MUTED)
    f.text(ox + 8 * cw + 12, 150, "l = 1, r = 6", size=14, fill=TEXT2)
    f.text(ox + 8 * cw + 12, 172, "1 xor 6 = 111₂", size=14, fill=TEXT2)
    f.text(ox + 8 * cw + 12, 194, "старший бит → ур. 2", size=14, fill=TEXT2)
    f.text(ox + 8 * cw + 12, 220, "ответ = суф(1) ∘ преф(6)", size=14, fill=GREEN, weight=700)
    return f.svg()


def majority():
    f = Fig("sd4", 330, title="Кандидат в мажоранты: пары разных элементов и непарные",
            sub="Пара (x, cnt): кандидат x и число его «непарных» копий.")
    seq = ["x", "x", "y", "z", "x", "y", "x", "x"]
    cols = {"x": BLUE, "y": ORANGE, "z": PURPLE}
    ox, cw = 80, 60
    for k, c in enumerate(seq):
        f.circle(ox + k * cw + 20, 130, 19, fill=NODE, stroke=cols[c], sw=3)
        f.text(ox + k * cw + 20, 136, c, size=17, anchor="middle", weight=700, fill=cols[c])
    # пары (y,x),(z,x),(y,x)… нарисуем дуги между 2-3, 3-4, 5-... упрощённо: пары (x1,y1) (x2,z) (x4,y2)
    pairs = [(1, 2), (3, 4), (5, 6)]
    for a, b in pairs:
        xa, xb = ox + a * cw + 20, ox + b * cw + 20
        f.path(f"M{xa},{152} Q{(xa + xb) / 2},{200} {xb},{152}", stroke=RED, sw=2.5)
    f.text(ox + 4 * cw + 20, 214, "пары разных — гасят друг друга", size=14, fill=RED, anchor="middle")
    f.text(32, 256, "Остались непарные: x (позиции 0, 7) — у них нет различающейся пары.", size=14.5, fill=TEXT2)
    f.text(32, 282, "Мажоранта (>половины) не может целиком уйти в пары — значит, она среди непарных: кандидат x, cnt = 2.", size=14.5, fill=TEXT2)
    f.text(32, 308, "Слияние (x, c₁) и (y, c₂): если x = y — складываем; иначе остаётся тот, у кого больше, с разностью.", size=14.5, fill=GREEN, weight=700)
    return f.svg()


def rect_cover():
    f = Fig("sd5", 360, title="2D sparse table: прямоугольник покрывается четырьмя блоками 2^a × 2^b",
            sub="Степени двойки по строкам и столбцам независимы, поэтому блоки могут быть вытянутыми.")
    ox, oy, W, H = 90, 112, 460, 210
    f.rect(ox, oy, W, H, fill="none", stroke=AXIS, sw=1.5, rx=4)
    qx, qy, qw, qh = 130, 140, 340, 150
    f.rect(ox + qx - 90 + 0, oy + qy - 112 + 0, 0.1, 0.1, fill="none")
    f.rect(ox + 40, oy + 28, qw, qh, fill="none", stroke=YELLOW, sw=3, rx=4)
    bw, bh = 250, 100
    f.rect(ox + 40, oy + 28, bw, bh, fill=BLUE, stroke=BLUE, rx=0, op=0.35)
    f.rect(ox + 40 + qw - bw, oy + 28, bw, bh, fill=GREEN, stroke=GREEN, rx=0, op=0.35)
    f.rect(ox + 40, oy + 28 + qh - bh, bw, bh, fill=ORANGE, stroke=ORANGE, rx=0, op=0.35)
    f.rect(ox + 40 + qw - bw, oy + 28 + qh - bh, bw, bh, fill=PURPLE, stroke=PURPLE, rx=0, op=0.35)
    f.text(ox + 40 + qw / 2, oy + 28 + qh / 2 + 5, "запрос [r₁, r₂) × [c₁, c₂)", size=14.5, fill=YELLOW, anchor="middle", weight=700)
    f.text(ox + W + 14, oy + 40, "a = ⌊log₂(r₂ − r₁)⌋", size=14, fill=TEXT2)
    f.text(ox + W + 14, oy + 64, "b = ⌊log₂(c₂ − c₁)⌋", size=14, fill=TEXT2)
    f.text(ox + W + 14, oy + 96, "min из 4 значений", size=14, fill=GREEN, weight=700)
    f.text(ox + W + 14, oy + 118, "t[a][b] в четырёх углах", size=14, fill=GREEN, weight=700)
    f.text(32, 346, "Память и предподсчёт: O(nm·log n·log m); запрос — O(1).", size=14, fill=MUTED)
    return f.svg()


def treap():
    f = Fig("sd6", 380, title="Декартово дерево: бинарное дерево поиска по x и куча по y",
            sub="В каждой вершине (x, y): ключи слева меньше x, справа больше; приоритет у корня — наибольший в поддереве.")
    nodes = {1: (380, 110, 5, 90), 2: (230, 190, 2, 70), 3: (540, 190, 8, 60), 4: (150, 270, 1, 40), 5: (300, 270, 4, 55),
             6: (470, 270, 7, 30), 7: (610, 270, 9, 20)}
    edges = [(1, 2), (1, 3), (2, 4), (2, 5), (3, 6), (3, 7)]
    for a, b in edges:
        f.line(nodes[a][0], nodes[a][1], nodes[b][0], nodes[b][1], stroke=EDGE, sw=2.5)
    for k, (x, y, key, pr) in nodes.items():
        f.circle(x, y, 26, fill=NODE, stroke=BLUE if k != 1 else GREEN, sw=2.5)
        f.text(x, y - 2, str(key), size=17, anchor="middle", weight=700)
        f.text(x, y + 16, f"y={pr}", size=12.5, anchor="middle", fill=ORANGE, weight=700)
    f.note(340, "Ключи в порядке обхода: 1 2 4 5 7 8 9 — это BST; приоритеты убывают сверху вниз — это куча.", size=14.5, color=TEXT2)
    f.note(362, "Если приоритеты случайны, ожидаемая глубина — O(log n): P(u — предок v) = 1/(число вершин между u и v).", size=14.5, color=GREEN)
    return f.svg()


def split_merge():
    f = Fig("sd7", 330, title="split и merge — две операции, на которых держится декартово дерево",
            sub="split режет по ключу (или по размеру) на два дерева; merge склеивает их обратно.")
    # split
    def tri(x, y, w, h, col, label):
        f.path(f"M{x},{y} L{x - w / 2},{y + h} L{x + w / 2},{y + h} Z", stroke=col, sw=2.5, fill="none")
        f.text(x, y + h * 0.72, label, size=14.5, anchor="middle", fill=col, weight=700)
    f.text(180, 108, "split(T, k)", size=16, anchor="middle", weight=700)
    tri(180, 130, 120, 90, BLUE, "T")
    f.line(250, 175, 336, 175, stroke=TEXT2, sw=2.5, arrow=True)
    tri(420, 130, 100, 90, GREEN, "ключи ≤ k")
    tri(560, 130, 100, 90, ORANGE, "ключи > k")
    f.text(180, 262, "режем вдоль пути поиска k:", size=14, anchor="middle", fill=MUTED)
    f.text(180, 284, "каждая вершина пути уходит в левое или правое дерево", size=14, anchor="middle", fill=MUTED)
    f.text(490, 262, "обе половины остаются", size=14, anchor="middle", fill=MUTED)
    f.text(490, 284, "декартовыми деревьями", size=14, anchor="middle", fill=MUTED)
    return f.svg()


def impl_treap():
    f = Fig("sd8", 380, title="Неявное декартово дерево: порядок обхода — это массив",
            sub="Индекс вершины: размер её левого поддерева плюс вклады при подъёме к корню.")
    nodes = {1: (380, 110, "E"), 2: (240, 190, "C"), 3: (520, 190, "G"), 4: (160, 270, "B"), 5: (320, 270, "D"), 6: (440, 270, "F"), 7: (600, 270, "H")}
    sizes = {1: 7, 2: 3, 3: 3, 4: 1, 5: 1, 6: 1, 7: 1}
    edges = [(1, 2), (1, 3), (2, 4), (2, 5), (3, 6), (3, 7)]
    for a, b in edges:
        f.line(nodes[a][0], nodes[a][1], nodes[b][0], nodes[b][1], stroke=EDGE, sw=2.5)
    for k, (x, y, c) in nodes.items():
        f.circle(x, y, 24, fill=NODE, stroke=BLUE if k != 1 else GREEN, sw=2.5)
        f.text(x, y + 6, c, size=18, anchor="middle", weight=700)
        f.text(x + 30, y - 18, f"sz={sizes[k]}", size=12.5, fill=MUTED)
    f.text(32, 332, "Обход «левое — вершина — правое»:  B  C  D  E  F  G  H   →  массив  [B, C, D, E, F, G, H],  индексы 0 … 6.", size=14.5, fill=TEXT2)
    f.text(32, 358, "Для D: левое поддерево пусто; из правого сына C поднимаемся: + (sz[B] + 1) = 2; из левого сына E — ничего → индекс 2.", size=13.5, fill=GREEN)
    return f.svg()


def merge_sort_tree():
    f = Fig("sd9", 330, title="Merge sort tree: в каждой вершине — отсортированный отрезок",
            sub="Массив 1 3 2 4 1 6 8 7. Дерево отрезков строится слиянием, как в сортировке слиянием: всего O(n log n) чисел.")
    def box(cx, y, vals, w, col):
        f.rect(cx - w / 2, y, w, 34, fill=NODE, stroke=col, sw=2, rx=6)
        f.text(cx, y + 23, " ".join(map(str, vals)), size=15, anchor="middle", weight=700)
    box(380, 100, [1, 1, 2, 3, 4, 6, 7, 8], 280, GREEN)
    box(220, 170, [1, 2, 3, 4], 150, BLUE); box(540, 170, [1, 6, 7, 8], 150, BLUE)
    for cx, vals in ((130, [1, 3]), (310, [2, 4]), (450, [1, 6]), (630, [7, 8])):
        box(cx, 240, vals, 90, PURPLE)
    for a, b in [((380, 134), (220, 170)), ((380, 134), (540, 170)), ((220, 204), (130, 240)), ((220, 204), (310, 240)), ((540, 204), (450, 240)), ((540, 204), (630, 240))]:
        f.line(*a, *b, stroke=EDGE, sw=2)
    return f.svg()


def hist_versions():
    a = [3, 1, 4, 2]
    n = len(a)
    f = Fig("sd10", 400, title="Историческая сумма: S — сумма всех версий массива M",
            sub="M[i] = min(a[i..r]); при r++ на части M присваивается a[r], затем M прибавляется к S.")
    M = []
    st = []
    for r in range(n):
        while st and a[st[-1]] >= a[r]:
            st.pop()
        left = st[-1] + 1 if st else 0
        st.append(r)
        prev = M[-1] if M else [0] * n
        cur = [prev[i] if not (left <= i <= r) else a[r] for i in range(n)]
        M.append(cur)
    ox, cw = 150, 70
    f.text(32, 120, f"a = {a}", size=15, fill=TEXT2, weight=700)
    for c in range(n):
        f.text(ox + c * cw + 28, 120, f"i={c}", size=13, fill=MUTED, anchor="middle")
    S = [0] * n
    for r in range(n):
        yy = 136 + r * 54
        f.text(32, yy + 26, f"r = {r}: M", size=14.5, fill=BLUE, weight=700)
        for c in range(n):
            changed = M[r][c] != (M[r - 1][c] if r else 0)
            f.cell(ox + c * cw, yy, M[r][c], w=cw - 8, h=36, fill=ORANGE if changed else NODE, stroke=ORANGE if changed else GRID,
                   tcolor=BG if changed else TEXT)
            S[c] += M[r][c]
        f.text(ox + n * cw + 16, yy + 26, "S =", size=14, fill=GREEN, weight=700)
        for c in range(n):
            f.text(ox + n * cw + 56 + c * 40, yy + 26, str(S[c]), size=15, fill=GREEN, weight=700)
    f.note(366, "Оранжевое — присвоено при добавлении a[r]. Последняя строка S[i] — сумма минимумов отрезков с началом в i.", size=13.5, color=TEXT2)
    return f.svg()


def set_iters():
    f = Fig("sd11", 330, title="Итераторы std::set: begin, end, prev(end)",
            sub="Итератор — указатель на элемент; операции ++ / -- и разыменование. end() указывает за последний элемент.")
    vals = [2, 5, 7, 11, 14, 20]
    ox, cw = 110, 78
    for k, v in enumerate(vals):
        f.cell(ox + k * cw, 140, v, w=cw - 8, h=40, fill=NODE)
    f.cell(ox + len(vals) * cw, 140, "end", w=cw - 8, h=40, fill=NODE2, stroke=GRID, tcolor=MUTED, size=14)
    def arrow(k, text, col, dy=0, anchor="middle", dx=0):
        x = ox + k * cw + (cw - 8) / 2
        f.line(x, 232 + dy, x, 190, stroke=col, sw=3, arrow=True)
        f.text(x + dx, 254 + dy, text, size=14, fill=col, anchor=anchor, weight=700)
    arrow(0, "begin() — минимум", GREEN)
    arrow(len(vals) - 1, "prev(end()) — максимум", ORANGE, anchor="end", dx=14)
    arrow(len(vals), "end()", MUTED, anchor="start", dx=-14)
    arrow(3, "lower_bound(10)", YELLOW)
    f.text(32, 288, "k-й минимум при фиксированном k: держим итератор и сдвигаем его на ±1 при добавлении/удалении;", size=13.5, fill=TEXT2)
    f.text(32, 308, "если удаляется сам элемент под итератором — сначала сдвигаем итератор, потом удаляем.", size=13.5, fill=TEXT2)
    return f.svg()


def tangent_path():
    f = Fig("sd12", 360, title="Кратчайший путь в обход круга: касательные и дуга",
            sub="Если отрезок AB пересекает круг, путь = касательная из A + дуга окружности + касательная к B.")
    cx, cy, r = 380, 200, 70
    f.circle(cx, cy, r, fill=NODE, stroke=BLUE, sw=2.5)
    A = (140, 235)
    B = (620, 170)
    def tangent_point(P, sign):
        dx, dy = P[0] - cx, P[1] - cy
        d = math.hypot(dx, dy)
        ang = math.atan2(dy, dx)
        off = math.acos(r / d)
        t = ang + sign * off
        return (cx + r * math.cos(t), cy + r * math.sin(t))
    ta = tangent_point(A, -1)
    tb = tangent_point(B, 1)
    f.line(*A, *ta, stroke=GREEN, sw=3)
    f.line(*B, *tb, stroke=GREEN, sw=3)
    a1 = math.atan2(ta[1] - cy, ta[0] - cx)
    a2 = math.atan2(tb[1] - cy, tb[0] - cx)
    # дуга по часовой/против — выбираем меньшую
    da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
    steps = 40
    pts = [(cx + r * math.cos(a1 + da * k / steps), cy + r * math.sin(a1 + da * k / steps)) for k in range(steps + 1)]
    f.polyline(pts, stroke=YELLOW, sw=4)
    f.line(*A, *B, stroke=RED, sw=2, dash="7 5")
    f.node(*A, "A", color=ORANGE, r=15, size=14)
    f.node(*B, "B", color=ORANGE, r=15, size=14)
    f.text(cx, cy + 5, "круг", size=15, anchor="middle", fill=MUTED)
    f.text(250, 335, "отрезок AB идти нельзя: он пересекает круг", size=14, fill=RED)
    f.legend(560, 70 + 20, [(GREEN, "касательные", "line"), (YELLOW, "дуга: угол · R", "line"), (RED, "прямой путь — запрещён", "line")], size=13.5, gap=22)
    return f.svg()


FIGS = {
    1: (sparse_cover, "Для отрезка длины $R-L$ берём $k=\\lfloor\\log_2(R-L)\\rfloor$: два блока длины $2^k$ покрывают его целиком и перекрываются."),
    2: (stack_back, "Блоки «смотрят назад» от позиции $j$, поэтому добавление нового элемента меняет только его собственный столбец."),
    3: (dst, "На каждом уровне блок делится пополам; слева от середины считаем суффиксы, справа — префиксы."),
    4: (majority, "Разные элементы гасят друг друга; всё, что осталось без пары, — одинаковые элементы, среди них и мажоранта."),
    5: (rect_cover, "Четыре перекрывающихся блока $2^a\\times2^b$ покрывают запрос; для $\\min$ перекрытия не мешают."),
    6: (treap, "По ключам дерево поиска, по приоритетам — куча; при случайных приоритетах глубина логарифмическая."),
    7: (split_merge, "Split разрезает дерево по ключу на два, merge склеивает два дерева, если ключи одного меньше ключей другого."),
    8: (impl_treap, "В неявном декартовом дереве ключ — позиция в массиве, которую можно получить, поднимаясь к корню."),
    9: (merge_sort_tree, "Merge sort tree хранит в каждой вершине отсортированный список значений её отрезка."),
    10: (hist_versions, "Массив $M$ меняется присваиванием на отрезке, а $S$ накапливает сумму его версий."),
    11: (set_iters, "Итераторы $\\texttt{set}$ двигаются на $\\pm1$ за $O(\\log n)$; $\\texttt{end()}$ — это «после последнего»."),
    12: (tangent_path, "Если прямой отрезок пересекает круг, кратчайший обход — две касательные и дуга между точками касания."),
}
