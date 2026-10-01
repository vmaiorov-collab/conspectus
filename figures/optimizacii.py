import math
import random
from kit import *

NOTE = "parallel-a/parallel-a-zan2-optimizacii-dp.html"


def small_to_large():
    f = Fig("d1", 400, title="Переливайка: множество тяжёлого сына забираем, остальные вливаем",
            sub="Пример: множества цветов. У вершины v три сына, их множества размеров 7, 3 и 1.")
    kids = [(40, 7, BLUE, "сын 1 — тяжёлый"), (360, 3, GREEN, "сын 2"), (560, 1, PURPLE, "сын 3")]
    yk = 112
    for x, n, c, t in kids:
        w = 26 * n + 18
        f.text(x, yk - 10, f"{t}: {n}", size=14.5, fill=c, weight=700)
        f.rect(x, yk, w, 40, fill=NODE2, stroke=c, sw=2, rx=8)
        for k in range(n):
            f.circle(x + 22 + k * 26, yk + 20, 9, fill=c)
    bx, by = 40, 262
    f.text(bx, by - 10, "множество v", size=14.5, fill=ORANGE, weight=700)
    f.rect(bx, by, 26 * 11 + 18, 44, fill=NODE2, stroke=ORANGE, sw=2, rx=8)
    for k in range(11):
        c = BLUE if k < 7 else (GREEN if k < 10 else PURPLE)
        f.circle(bx + 22 + k * 26, by + 22, 9, fill=c)
    f.line(130, yk + 46, 130, by - 26, stroke=BLUE, sw=4, arrow=True)
    f.text(146, 184, "swap: забрали", size=14.5, fill=BLUE, weight=700)
    f.text(146, 204, "целиком, O(1)", size=14.5, fill=BLUE, weight=700)
    f.path(f"M{360 + 45},{yk + 46} C{405},200 {300},214 {262 + 6},{by - 22}", stroke=GREEN, sw=2.5, dash="6 5", arrow=True)
    f.path(f"M{560 + 22},{yk + 46} C{582},210 {350},226 {326},{by - 22}", stroke=PURPLE, sw=2.5, dash="6 5", arrow=True)
    f.text(470, 262, "вливаем", size=14.5, fill=GREEN, weight=700)
    f.text(470, 282, "по одному элементу", size=14.5, fill=GREEN, weight=700)
    f.note(350, "Элемент переезжает только в множество, которое хотя бы вдвое больше его прежнего,", size=14.5, color=TEXT2)
    f.note(374, "поэтому переездов не больше log₂ n. Итого O(n log n).", size=14.5, color=TEXT2)
    return f.svg()


def tree_knapsack():
    f = Fig("d2", 420, title="Рюкзак на дереве: слияние детей стоит x · y",
            sub="Сливая ДП двух поддеревьев размеров x и y, перебираем все пары (a, b) — по вершине из каждого.")
    v = (200, 110)
    L = [(110, 190), (70, 270), (150, 270)]
    R = [(290, 190), (250, 270), (330, 270), (290, 340)]
    f.edge(*v, *L[0], r1=18, r2=15, arrow=False); f.edge(*L[0], *L[1], r1=15, r2=15, arrow=False); f.edge(*L[0], *L[2], r1=15, r2=15, arrow=False)
    f.edge(*v, *R[0], r1=18, r2=15, arrow=False); f.edge(*R[0], *R[1], r1=15, r2=15, arrow=False); f.edge(*R[0], *R[2], r1=15, r2=15, arrow=False); f.edge(*R[2], *R[3], r1=15, r2=15, arrow=False)
    f.node(*v, "v", color=ORANGE, r=18, size=15)
    for i, p in enumerate(L):
        f.node(*p, f"a{'₁₂₃'[i]}", color=BLUE, r=15, size=12.5)
    for i, p in enumerate(R):
        f.node(*p, f"b{'₁₂₃₄'[i]}", color=GREEN, r=15, size=12.5)
    f.text(110, 316, "x = 3", size=15, anchor="middle", fill=BLUE, weight=700)
    f.text(372, 344, "y = 4", size=15, fill=GREEN, weight=700)
    ox, oy, c = 440, 120, 44
    for i in range(3):
        f.text(ox - 12, oy + i * c + 28, f"a{'₁₂₃'[i]}", size=14, anchor="end", fill=BLUE, weight=700)
        for j in range(4):
            if i == 0:
                f.text(ox + j * c + c / 2, oy - 10, f"b{'₁₂₃₄'[j]}", size=14, anchor="middle", fill=GREEN, weight=700)
            f.rect(ox + j * c + 2, oy + i * c + 2, c - 4, c - 4, fill=ORANGE, op=0.35, stroke=ORANGE, rx=5)
    f.text(ox + 2 * c, oy + 3 * c + 30, "3 × 4 = 12 пар", size=15, anchor="middle", fill=ORANGE, weight=700)
    f.text(ox + 2 * c, oy + 3 * c + 52, "у каждой LCA = v", size=14, anchor="middle", fill=MUTED)
    f.note(398, "Каждая пара вершин перебирается один раз — в своём LCA. Пар всего ≤ n²/2 ⟹ весь рюкзак O(n²).", size=14.5, color=TEXT2)
    return f.svg()


def cht():
    lines = [(2.0, -2.25), (1.2, 2.15), (0.9, 2.6), (0.6, 4.25), (0.1, 5.0)]
    f = Fig("d3", 430, title="Convex Hull Trick: максимум из прямых k·x + b",
            sub="Верхняя огибающая — ломаная из прямых. Прямые, которые нигде не максимальны, выкидываем.")
    ox, oy, W, H = 70, 370, 500, 260
    x0, x1, y0, y1 = 0, 8, 0, 14
    X = lambda x: ox + W * (x - x0) / (x1 - x0)
    Y = lambda y: oy - H * (y - y0) / (y1 - y0)
    xs = [x0 + (x1 - x0) * i / 400 for i in range(401)]
    best = [max(range(len(lines)), key=lambda j: lines[j][0] * x + lines[j][1]) for x in xs]
    used = sorted(set(best))
    cols = [BLUE, GREEN, PURPLE, YELLOW, ORANGE]
    f.line(ox, oy, ox + W, oy, stroke=AXIS, sw=1.5)
    f.line(ox, oy, ox, oy - H, stroke=AXIS, sw=1.5)
    for j, (k, b) in enumerate(lines):
        on = j in used
        xa = max(x0, (y0 - b) / k if b < 0 else x0)
        xb = min(x1, (y1 - b) / k if k > 0 else x1)
        f.line(X(xa), Y(k * xa + b), X(xb), Y(k * xb + b), stroke=cols[j] if on else MUTED, sw=1.5, dash=None if on else "5 5", op=0.55 if on else 0.8)
    # огибающая
    pts = [(X(x), Y(lines[best[i]][0] * x + lines[best[i]][1])) for i, x in enumerate(xs) if lines[best[i]][0] * x + lines[best[i]][1] <= y1]
    f.polyline(pts, stroke=ORANGE, sw=4)
    # точки пересечения соседних на огибающей
    seq = []
    for b_ in best:
        if not seq or seq[-1] != b_:
            seq.append(b_)
    seq = seq[::-1]
    cross = []
    order = sorted(used, key=lambda j: -lines[j][1])
    env = []
    for i in range(len(xs) - 1):
        if best[i] != best[i + 1]:
            a, c = lines[best[i]], lines[best[i + 1]]
            xc = (c[1] - a[1]) / (a[0] - c[0])
            cross.append(xc)
    for xc in cross:
        j = best[min(range(len(xs)), key=lambda i: abs(xs[i] - xc))]
        yc = lines[j][0] * xc + lines[j][1]
        f.circle(X(xc), Y(yc), 6, fill=YELLOW)
        f.line(X(xc), Y(yc), X(xc), oy, stroke=YELLOW, sw=1, dash="3 4")
        f.text(X(xc), oy + 20, f"{xc:.1f}", size=13, anchor="middle", fill=YELLOW)
    q = 4.6
    jq = max(range(len(lines)), key=lambda j: lines[j][0] * q + lines[j][1])
    yq = lines[jq][0] * q + lines[jq][1]
    f.line(X(q), oy, X(q), Y(yq), stroke=RED, sw=2, dash="6 4")
    f.circle(X(q), Y(yq), 7, fill=RED)
    f.text(X(q) + 10, Y(yq) + 26, "запрос x = yᵢ", size=14, fill=RED, weight=700)
    tx = ox + W + 20
    f.text(tx, 120, "огибающая", size=15, fill=ORANGE, weight=700)
    f.text(tx, 142, "= ответ", size=14, fill=MUTED)
    f.text(tx, 186, "пунктир —", size=14, fill=MUTED)
    f.text(tx, 206, "лишняя прямая,", size=14, fill=MUTED)
    f.text(tx, 226, "удалили из стека", size=14, fill=MUTED)
    f.text(tx, 270, "жёлтые точки:", size=14, fill=YELLOW, weight=700)
    f.text(tx, 290, "по ним бинпоиск", size=14, fill=MUTED)
    f.text(tx, 310, "ищет прямую", size=14, fill=MUTED)
    f.text(ox + W, oy + 40, "x →", size=14, fill=MUTED, anchor="end")
    return f.svg()


def aliens():
    fk = [None, 64, 36, 25, 19, 15.5, 13.5, 12.3, 11.6]
    f = Fig("d4", 430, title="Лямбда-оптимизация: штраф λ за каждый отрезок",
            sub="f(k) — ответ ровно с k отрезками, выпуклая. Минимум f(k) + λk — точка касания прямой наклона −λ.")
    ox, oy, W, H = 80, 370, 470, 270
    X = lambda k: ox + W * (k - 0.5) / 8
    Y = lambda v: oy - H * v / 70
    f.line(ox, oy, ox + W, oy, stroke=AXIS, sw=1.5)
    f.line(ox, oy, ox, oy - H, stroke=AXIS, sw=1.5)
    for k in range(1, 9):
        f.text(X(k), oy + 22, str(k), size=13.5, anchor="middle", fill=MUTED)
    f.text(ox + W, oy + 44, "k — число отрезков", size=14, anchor="end", fill=MUTED)
    f.polyline([(X(k), Y(fk[k])) for k in range(1, 9)], stroke=BLUE, sw=2.5)
    lab = []
    for lam, col in [(10.0, ORANGE), (3.0, GREEN)]:
        kb = min(range(1, 9), key=lambda k: fk[k] + lam * k)
        c = fk[kb] + lam * kb
        xa = max(0.6, (c - 68) / lam)
        xb = min(8.4, c / lam - 0.4)
        f.line(X(xa), Y(c - lam * xa), X(xb), Y(c - lam * xb), stroke=col, sw=2.5)
        f.circle(X(kb), Y(fk[kb]), 9, fill=col)
        lab.append((col, f"λ = {lam:g} → k* = {kb}"))
    for k in range(1, 9):
        f.circle(X(k), Y(fk[k]), 5, fill=BLUE)
    f.text(X(1) + 14, Y(fk[1]) + 5, "f(k)", size=15, fill=BLUE, weight=700)
    tx = 590
    for i, (col, t) in enumerate(lab):
        f.line(tx, 352 + i * 24 - 5, tx + 18, 352 + i * 24 - 5, stroke=col, sw=3)
        f.text(tx + 26, 352 + i * 24, t, size=13.5, fill=col, weight=700)
    f.text(tx, 130, "Больше λ —", size=15, weight=700)
    f.text(tx, 152, "отрезки дороже,", size=14, fill=TEXT2)
    f.text(tx, 172, "их меньше.", size=14, fill=TEXT2)
    f.text(tx, 216, "Бинпоиск по λ,", size=15, weight=700)
    f.text(tx, 238, "пока k* ≠ нужного k.", size=14, fill=TEXT2)
    f.text(tx, 282, "Ответ:", size=15, weight=700)
    f.text(tx, 304, "f(k) = cost − λk", size=14.5, fill=TEXT2)
    return f.svg()


def knuth_table():
    a = [3, 1, 4, 1, 5, 9, 2, 6]
    n, K = len(a), 4
    pre = [0]
    for v in a:
        pre.append(pre[-1] + v)
    INF = float("inf")
    dp = [[INF] * (K + 1) for _ in range(n + 1)]
    opt = [[0] * (K + 1) for _ in range(n + 1)]
    dp[0][0] = 0
    for j in range(1, K + 1):
        for i in range(j, n + 1):
            for k in range(j - 1, i):
                v = dp[k][j - 1] + (pre[i] - pre[k]) ** 2
                if v < dp[i][j]:
                    dp[i][j], opt[i][j] = v, k
    f = Fig("d5", 470, title="Оптимизация Кнута: opt[i][j] монотонен по обоим индексам",
            sub="Массив 3 1 4 1 5 9 2 6, разбиение на j отрезков. В клетке — где выгоднее всего последний разрез.")
    ox, oy, cw, ch = 150, 128, 64, 36
    ti, tj = 6, 2
    for j in range(1, K + 1):
        f.text(ox + (j - 1) * cw + cw / 2, oy - 10, f"j = {j}", size=14, anchor="middle", fill=MUTED)
    for i in range(1, n + 1):
        f.text(ox - 12, oy + (i - 1) * ch + 24, f"i = {i}", size=14, anchor="end", fill=MUTED)
        for j in range(1, K + 1):
            x, y = ox + (j - 1) * cw, oy + (i - 1) * ch
            if i < j:
                f.rect(x + 2, y + 2, cw - 4, ch - 4, fill=NODE2, op=0.5, rx=5)
                continue
            role = (i, j) == (ti, tj) and "me" or ((i, j) == (ti - 1, tj) and "lo") or ((i, j) == (ti, tj + 1) and "hi")
            fill = {"me": ORANGE, "lo": BLUE, "hi": GREEN}.get(role, NODE)
            f.cell(x + 2, y + 2, opt[i][j], w=cw - 4, h=ch - 4, fill=fill, stroke=fill if role else GRID,
                   tcolor=BG if role else TEXT, size=15)
    tx = ox + K * cw + 36
    lo, hi = opt[ti - 1][tj], opt[ti][tj + 1]
    f.text(tx, 170, f"Ищем opt[{ti}][{tj}] (оранжевая).", size=15, weight=700)
    f.text(tx, 200, f"Снизу ограничивает", size=14, fill=TEXT2)
    f.text(tx, 220, f"opt[{ti - 1}][{tj}] = {lo} (синяя),", size=14.5, fill=BLUE, weight=700)
    f.text(tx, 250, f"сверху — opt[{ti}][{tj + 1}] = {hi}", size=14.5, fill=GREEN, weight=700)
    f.text(tx, 270, "(зелёная).", size=14, fill=TEXT2)
    f.text(tx, 310, f"Перебираем k только", size=14, fill=TEXT2)
    f.text(tx, 330, f"в [{lo}, {hi}], а не все 1…{ti - 1}.", size=14.5, fill=ORANGE, weight=700)
    f.text(tx, 374, "Сумма длин таких отрезков", size=14, fill=MUTED)
    f.text(tx, 394, "по диагонали — O(n),", size=14, fill=MUTED)
    f.text(tx, 414, "итого O(n²).", size=14, fill=MUTED)
    return f.svg()


def dnc():
    n = 16
    opt = [0, 0, 1, 1, 2, 3, 3, 4, 6, 6, 7, 8, 9, 9, 11, 12]
    f = Fig("d6", 440, title="Разделяй и властвуй: оптимумы монотонны",
            sub="solve(l, r, optL, optR): считаем середину m перебором, потом делим и задачу, и диапазон оптимумов.")
    ox, oy, s = 90, 380, 17
    X = lambda i: ox + i * s * 1.6
    Y = lambda k: oy - k * s
    f.line(ox - 6, oy + 6, X(n), oy + 6, stroke=AXIS, sw=1.5)
    f.line(ox - 6, oy + 6, ox - 6, Y(15), stroke=AXIS, sw=1.5)
    f.text(X(n), oy + 28, "i →", size=14, anchor="end", fill=MUTED)
    f.text(ox - 14, Y(15) + 4, "opt", size=14, anchor="end", fill=MUTED)
    m = n // 2 - 1
    # шаг 1: весь прямоугольник, перебор в середине
    f.rect(X(0) - 6, Y(13) - 6, X(n - 1) - X(0) + 12, Y(0) - Y(13) + 12, fill=MUTED, op=0.06, stroke=AXIS, dash="4 4", rx=4)
    f.rect(X(m) - 8, Y(13) - 6, 16, Y(0) - Y(13) + 12, fill=YELLOW, op=0.25, rx=4)
    # шаг 2: две половины
    f.rect(X(0) - 5, Y(opt[m]) - 5, X(m - 1) - X(0) + 10, Y(0) - Y(opt[m]) + 10, fill=BLUE, op=0.16, stroke=BLUE, rx=4)
    f.rect(X(m + 1) - 5, Y(13) - 5, X(n - 1) - X(m + 1) + 10, Y(opt[m]) - Y(13) + 10, fill=GREEN, op=0.16, stroke=GREEN, rx=4)
    for i, k in enumerate(opt):
        f.circle(X(i), Y(k), 6.5 if i == m else 5, fill=YELLOW if i == m else TEXT2)
    f.text(X(m), Y(13) - 14, "m: перебор всех opt", size=14, anchor="middle", fill=YELLOW, weight=700)
    f.text(X(2), Y(opt[m]) - 12, "левая половина: opt ≤ opt[m]", size=14, fill=BLUE, weight=700)
    f.text(X(m + 1), Y(13) + 20, "правая: opt ≥ opt[m]", size=14, fill=GREEN, weight=700)
    tx = X(n) + 14
    f.text(tx, 160, "Каждый уровень", size=15, weight=700)
    f.text(tx, 182, "рекурсии суммарно", size=14, fill=TEXT2)
    f.text(tx, 202, "перебирает O(n)", size=14, fill=TEXT2)
    f.text(tx, 222, "кандидатов.", size=14, fill=TEXT2)
    f.text(tx, 262, "Уровней log n ⟹", size=14, fill=TEXT2)
    f.text(tx, 284, "O(n log n) на слой.", size=15, fill=ORANGE, weight=700)
    return f.svg()


def connectivity():
    nv = 5
    edges = [(0, 1), (2, 3), (1, 2), (3, 4), (0, 2), (1, 3), (2, 4), (0, 4), (1, 4)]
    m = len(edges)

    def connected(l, r):
        p = list(range(nv))
        def find(x):
            while p[x] != x:
                p[x] = p[p[x]]; x = p[x]
            return x
        for a, b in edges[l:r + 1]:
            p[find(a)] = find(b)
        return len({find(x) for x in range(nv)}) == 1
    f = Fig("d7", 470, title="Связность на отрезке рёбер: граница монотонна",
            sub=f"Граф на {nv} вершинах, рёбра пронумерованы 0…{m - 1}. Клетка (l, r) — связен ли граф из рёбер l…r.")
    ox, oy, c = 120, 110, 34
    border = []
    for l in range(m):
        f.text(ox - 10, oy + l * c + 22, f"l = {l}", size=13.5, anchor="end", fill=MUTED)
        first = None
        for r in range(m):
            if l == 0:
                f.text(ox + r * c + c / 2, oy - 8, str(r), size=13, anchor="middle", fill=MUTED)
            if r < l:
                continue
            ok = connected(l, r)
            if ok and first is None:
                first = r
            f.rect(ox + r * c + 2, oy + l * c + 2, c - 4, c - 4, fill=GREEN if ok else RED, op=0.55 if ok else 0.3, rx=4)
        border.append(first)
    f.text(ox + m * c / 2, oy - 28, "r →", size=14, anchor="middle", fill=MUTED)
    # ступенька
    pts = []
    for l, b in enumerate(border):
        if b is None:
            break
        pts += [(ox + b * c, oy + l * c), (ox + b * c, oy + (l + 1) * c)]
    f.polyline(pts, stroke=ORANGE, sw=3.5)
    tx = ox + m * c + 30
    f.rect(tx, 140, 16, 16, fill=GREEN, op=0.55, rx=3); f.text(tx + 24, 153, "связен", size=14, fill=TEXT2)
    f.rect(tx, 166, 16, 16, fill=RED, op=0.3, rx=3); f.text(tx + 24, 179, "не связен", size=14, fill=TEXT2)
    f.text(tx, 224, "Оранжевая граница:", size=15, fill=ORANGE, weight=700)
    f.text(tx, 246, "первое r, с которого", size=14, fill=TEXT2)
    f.text(tx, 266, "граф связен.", size=14, fill=TEXT2)
    f.text(tx, 306, "С ростом l она", size=14, fill=TEXT2)
    f.text(tx, 326, "только сдвигается", size=14, fill=TEXT2)
    f.text(tx, 346, "вправо ⟹ разделяйка", size=14, fill=TEXT2)
    f.text(tx, 366, "+ ДСУ с откатами.", size=14, fill=TEXT2)
    return f.svg()


def matrix_paths():
    E = [(0, 1), (1, 2), (0, 2), (2, 0), (1, 0)]
    n = 3
    A = [[0] * n for _ in range(n)]
    for u, v in E:
        A[u][v] = 1
    A2 = [[sum(A[i][k] * A[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    f = Fig("d8", 360, title="Aᵏ[i][j] — число путей длины k из i в j",
            sub="A — матрица смежности. Возводя её в квадрат, считаем пути из двух рёбер.")
    P = {0: (110, 150), 1: (230, 230), 2: (90, 290)}
    for u, v in E:
        bend = 18 if (v, u) in E else 0
        f.edge(*P[u], *P[v], r1=20, r2=20, color=EDGE, sw=2, bend=bend)
    for v, (x, y) in P.items():
        f.node(x, y, v + 1, color=BLUE, r=20)

    def mat(x, y, M, title, hl=None):
        c = 40
        f.text(x + 1.5 * c, y - 14, title, size=16, anchor="middle", weight=700)
        f.path(f"M{x - 4},{y} h-6 v{3 * c} h6", stroke=AXIS, sw=2)
        f.path(f"M{x + 3 * c + 4},{y} h6 v{3 * c} h-6", stroke=AXIS, sw=2)
        for i in range(n):
            for j in range(n):
                on = hl == (i, j)
                f.cell(x + j * c + 3, y + i * c + 3, M[i][j], w=c - 6, h=c - 6, fill=ORANGE if on else NODE,
                       stroke=ORANGE if on else GRID, tcolor=BG if on else (TEXT if M[i][j] else MUTED), size=15)
    mat(330, 110, A, "A")
    f.text(475, 176, "→", size=24, anchor="middle", fill=MUTED)
    mat(510, 110, A2, "A²", hl=(0, 0))
    f.text(32 + 300, 290, f"(A²)₁₁ = {A2[0][0]}: пути 1 → 2 → 1 и 1 → 3 → 1", size=15, fill=ORANGE, weight=700)
    f.text(32 + 300, 314, "Aᵏ — бинарным возведением за O(n³ log k)", size=14, fill=MUTED)
    return f.svg()


def shuffle_band():
    f = Fig("d9", 420, title="Random shuffle: храним только полосу вокруг среднего",
            sub="Состояние — (позиция k, сколько покеболов уже потрачено). После перемешивания их около k · A / n.")
    ox, oy, W, H = 90, 360, 440, 250
    n, A = 40, 20
    X = lambda k: ox + W * k / n
    Y = lambda a: oy - H * a / A
    band = 4
    for k in range(0, n + 1, 2):
        for a in range(0, A + 1, 1):
            if a > k:
                continue
            inside = abs(a - k * A / n) <= band * math.sqrt(k / n + 0.05)
            f.circle(X(k), Y(a), 3.2 if inside else 2, fill=GREEN if inside else GRID)
    pts_hi = [(X(k), Y(min(A, k * A / n + band * math.sqrt(k / n + 0.05)))) for k in range(0, n + 1)]
    pts_lo = [(X(k), Y(max(0, k * A / n - band * math.sqrt(k / n + 0.05)))) for k in range(0, n + 1)]
    f.polyline(pts_hi, stroke=GREEN, sw=2)
    f.polyline(pts_lo, stroke=GREEN, sw=2)
    f.line(X(0), Y(0), X(n), Y(A), stroke=ORANGE, sw=2.5, dash="7 5")
    f.text(X(n) + 8, Y(A) + 5, "k · A / n", size=15, fill=ORANGE, weight=700)
    f.line(ox, oy, ox + W, oy, stroke=AXIS, sw=1.5)
    f.line(ox, oy, ox, oy - H, stroke=AXIS, sw=1.5)
    f.text(ox + W, oy + 24, "позиция k →", size=14, anchor="end", fill=MUTED)
    f.text(ox - 10, oy - H + 4, "a", size=15, anchor="end", fill=MUTED, italic=True)
    tx = ox + W + 30
    f.text(tx, 200, "Зелёная полоса", size=15, fill=GREEN, weight=700)
    f.text(tx, 222, "шириной ~ c√n —", size=14, fill=TEXT2)
    f.text(tx, 242, "храним только её.", size=14, fill=TEXT2)
    f.text(tx, 286, "Серые состояния", size=14, fill=MUTED)
    f.text(tx, 306, "почти невероятны —", size=14, fill=MUTED)
    f.text(tx, 326, "отбрасываем.", size=14, fill=MUTED)
    return f.svg()


INSERTS = [
    ("dp-small-to-large", "переезжает» из множества", small_to_large,
     "Множество тяжёлого сына забираем без копирования, остальные вливаем поэлементно. Каждый элемент переезжает не больше $\\log_2 n$ раз."),
    ("dp-tree-knapsack", "Каждая пара вершин", tree_knapsack,
     "Пара вершин $(a, b)$ перебирается ровно один раз — при слиянии в их LCA. Поэтому суммарная работа $O(n^2)$."),
    ("dp-cht", "Внутренний максимум — это максимум прямых", cht,
     "Ответ для $y_i$ — значение верхней огибающей в этой точке; нужная прямая ищется бинпоиском по точкам пересечения."),
    ("dp-aliens", "нижняя огибающая семейства", aliens,
     "Чем больше штраф $\\lambda$, тем меньше отрезков в оптимуме. Бинпоиском подбираем $\\lambda$, при котором их ровно $k$."),
    ("dp-knuth", "Поэтому, считая ДП в правильном порядке", knuth_table,
     "Настоящая таблица $opt$ для массива 3 1 4 1 5 9 2 6: перебор для каждой клетки зажат соседними клетками."),
    ("dp-dnc", "void solve(int l, int r", dnc,
     "Оптимум середины делит диапазон кандидатов: левой половине достаются меньшие, правой — большие."),
    ("dp-connectivity", "Зафиксировав левую границу", connectivity,
     "Граница «с какого $r$ граф связен» не убывает с ростом $l$ — та же монотонность, что нужна разделяйке."),
    ("dp-matrix-paths", "(A^k)_{ij}$ = число путей", matrix_paths,
     "Элемент $(A^2)_{ij}$ — сумма $\\sum_k A_{ik}A_{kj}$, то есть число путей $i \\to k \\to j$."),
    ("dp-shuffle", "Состояний $O(n \\cdot", shuffle_band,
     "После случайного перемешивания число потраченных покеболов редко отходит от среднего больше чем на $O(\\sqrt n)$."),
]
