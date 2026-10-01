import math
from kit import *

NOTE = "parallel-a/parallel-a-zan1-matematika.html"


def growth():
    """Сколько операций при данном n; логарифмические оси; линия ≈ 1 секунда."""
    f = Fig("m1", 430, title="Сколько операций сделает алгоритм при данном n",
            sub="Обе оси логарифмические: каждое деление — ×10. Линия 10⁸ ≈ 1 секунда на C++.")
    x0, x1, y0, y1 = 92, 600, 380, 96          # область графика
    nmax, opmax = 6, 12                         # n до 10⁶, операций до 10¹²
    X = lambda lg: x0 + (x1 - x0) * lg / nmax
    Y = lambda lg: y0 - (y0 - y1) * lg / opmax
    for k in range(0, nmax + 1):
        f.line(X(k), y1, X(k), y0, stroke=GRID, sw=1)
        f.text(X(k), y0 + 22, "1" if k == 0 else ("10" if k == 1 else f"10{''.join('⁰¹²³⁴⁵⁶⁷⁸⁹'[int(c)] for c in str(k))}"), size=14, fill=MUTED, anchor="middle")
    for k in range(0, opmax + 1, 3):
        f.line(x0, Y(k), x1, Y(k), stroke=GRID, sw=1)
        f.text(x0 - 10, Y(k) + 5, "1" if k == 0 else f"10{''.join('⁰¹²³⁴⁵⁶⁷⁸⁹'[int(c)] for c in str(k))}", size=14, fill=MUTED, anchor="end")
    f.line(x0, y0, x1, y0, stroke=AXIS, sw=1.5)
    f.line(x0, y1, x0, y0, stroke=AXIS, sw=1.5)
    # 1 секунда
    f.rect(x0, Y(12), x1 - x0, Y(8) - Y(12), fill=RED, op=0.08, rx=0)
    f.line(x0, Y(8), x1, Y(8), stroke=RED, sw=2, dash="6 5")
    f.text(x0 + 8, Y(8) - 8, "10⁸ ≈ 1 сек", size=14, fill=RED, weight=700)
    f.text(x0 + 8, Y(12) + 20, "не успеет", size=14, fill=RED)
    curves = [
        ("log n", BLUE, lambda n: math.log2(max(n, 2))),
        ("√n", GREEN, lambda n: math.sqrt(n)),
        ("n", YELLOW, lambda n: n),
        ("n log n", ORANGE, lambda n: n * math.log2(max(n, 2))),
        ("n²", RED, lambda n: n * n),
        ("2ⁿ", PURPLE, lambda n: 2.0 ** n),
    ]
    for name, col, fn in curves:
        pts, last = [], None
        for i in range(0, 241):
            lg = nmax * i / 240
            n = 10 ** lg
            v = fn(n)
            if v <= 0:
                continue
            lv = math.log10(v)
            if lv > opmax:
                # обрезаем на верхней границе
                pts.append((X(lg), Y(opmax)))
                last = (X(lg), Y(opmax))
                break
            pts.append((X(lg), Y(max(lv, 0))))
            last = pts[-1]
        f.polyline(pts, stroke=col, sw=3)
    # подписи справа — вычислены по значению при n = 10⁶ (или в точке обрезки)
    labels = [("log n", BLUE, "20"), ("√n", GREEN, "10³"), ("n", YELLOW, "10⁶"),
              ("n log n", ORANGE, "2·10⁷"), ("n²", RED, "10¹²"), ("2ⁿ", PURPLE, "уже при n≈40")]
    ys = {"log n": Y(math.log10(20)), "√n": Y(3), "n": Y(6), "n log n": Y(math.log10(2e7)),
          "n²": Y(12), "2ⁿ": Y(12)}
    # раздвигаем, чтобы не наезжали
    order = sorted(labels, key=lambda t: -ys[t[0]])
    placed = []
    for name, col, val in order:
        y = ys[name]
        if name == "2ⁿ":
            # 2ⁿ упирается в потолок слева — подпишем у точки обрезки
            xx = X(math.log10(40))
            f.text(xx + 8, Y(12) + 40, "2ⁿ", size=16, fill=col, weight=700)
            continue
        while any(abs(y - p) < 20 for p in placed):
            y -= 20
        placed.append(y)
        f.text(x1 + 12, y + 5, name, size=15, fill=col, weight=700)
        f.text(x1 + 12 + (len(name) * 8.5 + 10), y + 5, (val if val.startswith("уже") else f"= {val}"), size=14, fill=MUTED)
    f.text(x1, y0 + 44, "n →", size=14, fill=MUTED, anchor="end")
    return f.svg()


def euclid():
    a, b, s = 30, 18, 12
    f = Fig("m2", 356, title="Алгоритм Евклида для 30 и 18: отрезаем квадраты",
            sub="Из прямоугольника 30 × 18 раз за разом вырезаем самый большой квадрат.")
    ox, oy = 40, 96
    f.rect(ox, oy, a * s, b * s, fill=NODE, stroke=AXIS, sw=1.5, rx=2)
    # 18×18
    f.rect(ox, oy, 18 * s, 18 * s, fill=BLUE, op=0.35, stroke=BLUE, sw=2, rx=2)
    f.text(ox + 9 * s, oy + 9 * s + 6, "18 × 18", size=17, anchor="middle", weight=700)
    # 12×12
    f.rect(ox + 18 * s, oy, 12 * s, 12 * s, fill=GREEN, op=0.35, stroke=GREEN, sw=2, rx=2)
    f.text(ox + 24 * s, oy + 6 * s + 6, "12 × 12", size=16, anchor="middle", weight=700)
    # 6×6 два раза
    for k in range(2):
        f.rect(ox + (18 + 6 * k) * s, oy + 12 * s, 6 * s, 6 * s, fill=ORANGE, op=0.45, stroke=ORANGE, sw=2, rx=2)
        f.text(ox + (21 + 6 * k) * s, oy + 15 * s + 5, "6", size=16, anchor="middle", weight=700)
    f.text(ox + a * s / 2, oy + b * s + 22, "30", size=14, fill=MUTED, anchor="middle")
    f.text(ox - 10, oy + b * s / 2 + 5, "18", size=14, fill=MUTED, anchor="end")
    # шаги справа
    tx = ox + a * s + 36
    steps = [(BLUE, "30 = 1·18 + 12", "один квадрат 18"),
             (GREEN, "18 = 1·12 + 6", "один квадрат 12"),
             (ORANGE, "12 = 2·6 + 0", "два квадрата 6 — остаток 0")]
    for i, (c, eq, why) in enumerate(steps):
        y = oy + 18 + i * 58
        f.rect(tx, y - 15, 14, 14, fill=c, rx=3)
        f.text(tx + 24, y, eq, size=17, weight=700)
        f.text(tx + 24, y + 22, why, size=14, fill=MUTED)
    y = oy + 18 + 3 * 58 + 4
    f.text(tx, y, "gcd(30, 18) = 6", size=18, fill=ORANGE, weight=700)
    f.text(tx, y + 22, "сторона последнего квадрата", size=14, fill=MUTED)
    return f.svg()


def crt():
    f = Fig("m3", 372, title="КТО: x ≡ 1 (mod 3) и x ≡ 2 (mod 5)",
            sub="Отмечаем числа, подходящие под каждое условие. Совпадение — каждые 3·5 = 15.")
    n, cw, ox = 18, 38, 40
    yh, y1, y2 = 104, 154, 204
    for x in range(n):
        cx = ox + x * cw + cw / 2
        both = x % 3 == 1 and x % 5 == 2
        if both:
            f.rect(ox + x * cw + 2, yh - 24, cw - 4, y2 + 26 - yh + 24, fill=YELLOW, op=0.18, stroke=YELLOW, sw=2, rx=8)
        f.text(cx, yh, str(x), size=15, anchor="middle", fill=TEXT if both else MUTED, weight=700 if both else None)
        if x % 3 == 1:
            f.circle(cx, y1, 11, fill=BLUE)
        else:
            f.circle(cx, y1, 3, fill=GRID)
        if x % 5 == 2:
            f.circle(cx, y2, 11, fill=GREEN)
        else:
            f.circle(cx, y2, 3, fill=GRID)
    f.legend(ox, 262, [(BLUE, "x ≡ 1 (mod 3): 1, 4, 7, 10, 13, 16 — шаг 3", "dot"),
                       (GREEN, "x ≡ 2 (mod 5): 2, 7, 12, 17 — шаг 5", "dot")], size=14.5, gap=24)
    f.text(ox, 340, "Ответ: x ≡ 7 (mod 15)", size=17, fill=YELLOW, weight=700)
    f.text(ox + 210, 340, "— то есть 7, 22, 37, …: ровно одно решение на каждые 15 чисел", size=14.5, fill=MUTED)
    return f.svg()


def primitive_root():
    p = 11
    f = Fig("m4", 410, title="Первообразный корень по модулю 11",
            sub="Умножаем на g снова и снова: 1 → g → g² → … Сколько разных остатков встретится?")

    def powers(g):
        seq, x = [], 1
        while True:
            seq.append(x)
            x = x * g % p
            if x == 1:
                return seq

    def ring(cx, cy, R, seq, color):
        pos = []
        for i in range(len(seq)):
            ang = -math.pi / 2 + 2 * math.pi * i / len(seq)
            pos.append((cx + R * math.cos(ang), cy + R * math.sin(ang)))
        for i in range(len(seq)):
            f.edge(*pos[i], *pos[(i + 1) % len(seq)], r1=17, r2=17, color=color, sw=2, bend=-10)
        for i, (x, y) in enumerate(pos):
            f.node(x, y, seq[i], color=color, r=17, size=15)
            # показатель степени снаружи круга
            ang = -math.pi / 2 + 2 * math.pi * i / len(seq)
            f.text(cx + (R + 32) * math.cos(ang), cy + (R + 32) * math.sin(ang) + 5,
                   f"g{''.join('⁰¹²³⁴⁵⁶⁷⁸⁹'[int(c)] for c in str(i))}", size=13, fill=MUTED, anchor="middle")

    s2, s3 = powers(2), powers(3)
    ring(190, 222, 104, s2, GREEN)
    f.text(190, 226, "g = 2", size=17, anchor="middle", weight=700)
    f.text(190, 382, "все 10 остатков ✓  первообразный", size=15, anchor="middle", fill=GREEN, weight=700)

    ring(530, 222, 70, s3, RED)
    f.text(530, 226, "g = 3", size=17, anchor="middle", weight=700)
    missed = [v for v in range(1, p) if v not in s3]
    for i, v in enumerate(missed):
        x = 650 + (i % 2) * 44
        y = 150 + (i // 2) * 44
        f.node(x, y, v, color=GRID, r=16, size=14, tcolor=MUTED)
    f.text(672, 296, "не встретились", size=13, fill=MUTED, anchor="middle")
    f.text(560, 382, "только 5 остатков ✗  не корень", size=15, anchor="middle", fill=RED, weight=700)
    return f.svg()


def pollard():
    p = 17
    seq = [4, 0, 1, 2, 5, 9, 14, 10, 16]
    tail, cyc = seq[:3], seq[3:]
    f = Fig("m5", 360, title="Почему «ρ»: последовательность aᵢ₊₁ = aᵢ² + 1 по модулю p = 17",
            sub="Остатков всего p, поэтому значения обязаны повториться — и дальше идут по кругу.")
    cx, cy, R = 520, 214, 92
    cpos = []
    for i in range(len(cyc)):
        ang = math.pi + 2 * math.pi * i / len(cyc)
        cpos.append((cx + R * math.cos(ang), cy + R * math.sin(ang)))
    tpos = [(cpos[0][0] - 120 * (len(tail) - i), cy + 0) for i in range(len(tail))]
    for i in range(len(tail)):
        a = tpos[i]
        b = tpos[i + 1] if i + 1 < len(tail) else cpos[0]
        f.edge(*a, *b, r1=19, r2=19, color=BLUE, sw=2.5)
    for i in range(len(cyc)):
        f.edge(*cpos[i], *cpos[(i + 1) % len(cyc)], r1=19, r2=19, color=GREEN, sw=2.5, bend=-14)
    for i, (x, y) in enumerate(tpos):
        f.node(x, y, tail[i], color=BLUE, r=19)
        f.text(x, y + 40, f"a{'₀₁₂'[i]}", size=14, anchor="middle", fill=MUTED)
    for i, (x, y) in enumerate(cpos):
        f.node(x, y, cyc[i], color=YELLOW if i == 0 else GREEN, r=19)
    f.text(tpos[0][0] - 2, cy - 40, "хвост", size=15, fill=BLUE, weight=700)
    f.text(cx, cy + 5, "цикл", size=16, fill=GREEN, weight=700, anchor="middle")
    f.text(cx, cy + 25, "длины 6", size=14, fill=MUTED, anchor="middle")
    f.text(cpos[0][0] - 8, cy - 38, "16 → 2: повтор", size=14, fill=YELLOW, anchor="end", weight=700)
    sub = lambda c: f'<tspan baseline-shift="sub" font-size="11">{c}</tspan>'
    f.text(32, 326, f"Хвост и цикл вместе — около √p шагов. Как только a{sub('i')} ≡ a{sub('j')} (mod p), "
           f"число p делит gcd(a{sub('i')} − a{sub('j')}, n).", size=14.5, fill=TEXT2, raw=True)
    return f.svg()


def floor_sum():
    n, a, b, m = 7, 3, 2, 4
    vals = [(a * x + b) // m for x in range(n)]
    f = Fig("m6", 430, title="Floor-сумма = число целых точек под прямой",
            sub=f"S = Σ ⌊(3x + 2) / 4⌋ при x = 0…6: в столбце x ровно ⌊(3x+2)/4⌋ точек с y ≥ 1.")
    s, ox, oy = 46, 80, 352         # шаг сетки и начало координат
    ymax = 5
    for x in range(n + 1):
        f.line(ox + x * s, oy, ox + x * s, oy - ymax * s + 10, stroke=GRID, sw=1)
    for y in range(ymax + 1):
        f.line(ox, oy - y * s, ox + n * s - 10, oy - y * s, stroke=GRID, sw=1)
        if y:
            f.text(ox - 12, oy - y * s + 5, str(y), size=14, fill=MUTED, anchor="end")
    f.line(ox, oy, ox + n * s, oy, stroke=AXIS, sw=1.5)
    f.line(ox, oy, ox, oy - ymax * s, stroke=AXIS, sw=1.5)
    # прямая y = (3x+2)/4
    X = lambda x: ox + x * s
    Y = lambda y: oy - y * s
    f.rect(X(0), Y(ymax), n * s, 0, fill=BG)  # no-op placeholder for layering
    f.path(f"M{X(-0.2):.1f},{Y((3*-0.2+2)/4):.1f} L{X(n - 0.6):.1f},{Y((3*(n-0.6)+2)/4):.1f}", stroke=BLUE, sw=3)
    f.text(X(n - 0.6) + 8, Y((3 * (n - 0.6) + 2) / 4) + 4, "y = (3x + 2) / 4", size=15, fill=BLUE, weight=700)
    for x in range(n):
        for y in range(1, ymax + 1):
            if y <= vals[x]:
                f.circle(X(x), Y(y), 8, fill=YELLOW)
            else:
                f.circle(X(x), Y(y), 3, fill=GRID)
        f.text(X(x), oy + 24, str(x), size=14, fill=MUTED, anchor="middle")
        f.text(X(x), oy + 50 - 4, str(vals[x]), size=15, fill=YELLOW, anchor="middle", weight=700)
    f.text(ox - 12, oy + 24, "x", size=14, fill=MUTED, anchor="end", italic=True)
    f.text(ox - 12, oy + 46, "точек", size=14, fill=MUTED, anchor="end")
    tx = ox + n * s + 40
    f.text(tx, 236, f"S = {sum(vals)}", size=20, fill=YELLOW, weight=700)
    f.text(tx, 262, "жёлтых точек", size=14, fill=MUTED)
    f.text(tx, 300, "Повернём картинку на 90° —", size=14, fill=TEXT2)
    f.text(tx, 320, "та же задача по строкам y,", size=14, fill=TEXT2)
    f.text(tx, 340, "но с меньшими числами.", size=14, fill=TEXT2)
    return f.svg()


FIGS = {
    1: (growth, "Логарифм и корень почти не растут, $n^2$ при $n=10^6$ уже не укладывается в секунду, а $2^n$ упирается в потолок при $n\\approx 40$."),
    2: (euclid, "Алгоритм Евклида — это нарезка прямоугольника $a\\times b$ на квадраты; сторона последнего квадрата и есть $\\gcd(a,b)$."),
    3: (crt, "Китайская теорема об остатках: условия по взаимно простым модулям 3 и 5 совпадают ровно в одном остатке по модулю 15."),
    4: (primitive_root, "Степени первообразного корня перебирают все ненулевые остатки; у остального числа цикл короче $p-1$."),
    5: (pollard, "Последовательность по модулю $p$ неизбежно зацикливается и рисует букву ρ — на этом и основан метод Полларда."),
    6: (floor_sum, "Каждое слагаемое $\\lfloor(ax+b)/m\\rfloor$ — число целых точек в своём столбце, вся сумма — число точек под прямой."),
}
