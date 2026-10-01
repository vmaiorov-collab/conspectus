import math
from kit import *

NOTE = "parallel-bp/parallel-bp-zan2-poiski.html"


def lr_meaning():
    a = [1, 2, 2, 2, 5, 7]
    f = Fig("p1", 380, title="Инвариант a[L] ≤ x < a[R]: где окажутся L и R",
            sub="Считаем, что a[−1] = −∞ и a[n] = +∞, поэтому начинаем с L = −1, R = n.")
    cw, ox = 72, 130

    def row(y, x):
        L = max([i for i, v in enumerate(a) if v <= x], default=-1)
        R = L + 1
        f.text(ox - 26, y + 26, f"x = {x}", size=16, anchor="end", weight=700)
        for k, v in enumerate(["−∞"] + a + ["+∞"]):
            i = k - 1
            ghost = i in (-1, len(a))
            eq = not ghost and a[i] == x
            if ghost:
                f.rect(ox + k * cw + 4, y, cw - 8, 40, fill=NODE2, stroke=GRID, dash="4 4")
                f.text(ox + k * cw + cw / 2, y + 26, v, size=14, anchor="middle", fill=MUTED)
            else:
                f.cell(ox + k * cw + 4, y, v, w=cw - 8, h=40, fill=YELLOW if eq else NODE,
                       stroke=YELLOW if eq else GRID, tcolor=BG if eq else TEXT)
            f.text(ox + k * cw + cw / 2, y - 8, str(i), size=12.5, anchor="middle", fill=MUTED)
        for idx, name, c in [(L, "L", GREEN), (R, "R", ORANGE)]:
            xx = ox + (idx + 1) * cw + cw / 2
            f.line(xx, y + 82, xx, y + 46, stroke=c, sw=2.5, arrow=True)
            f.text(xx, y + 100, f"{name} = {idx}", size=15, anchor="middle", fill=c, weight=700)
        return L, R

    row(102, 2)
    row(236, 4)
    f.note(362, "x есть: L — последнее вхождение x, R — сразу за ним.  x нет: L — последний < x, R — первый > x.", size=14, color=TEXT2)
    return f.svg()


def answer_split():
    f = Fig("p2", 330, title="Бинпоиск по ответу: ищем границу «не подходит | подходит»",
            sub="Если чекер подходит для D, то подходит и для любого большего D (монотонность).")
    n, cw, ox, y = 14, 48, 44, 128
    border = 6
    for k in range(n):
        ok = k >= border
        f.cell(ox + k * cw + 3, y, k, w=cw - 6, h=42, fill=GREEN if ok else RED,
               stroke=GREEN if ok else RED, tcolor=BG, size=15)
    f.text(ox + border * cw / 2, y - 14, "чекер = false", size=15, anchor="middle", fill=RED, weight=700)
    f.text(ox + (border + n) * cw / 2, y - 14, "чекер = true", size=15, anchor="middle", fill=GREEN, weight=700)
    for idx, name, c in [(border - 1, "L", RED), (border, "R", GREEN)]:
        xx = ox + idx * cw + cw / 2
        f.line(xx, y + 86, xx, y + 48, stroke=c, sw=2.5, arrow=True)
        f.text(xx, y + 104, name, size=16, anchor="middle", fill=c, weight=700)
    f.text(ox + border * cw, y + 134, "ответ — R: минимальное подходящее", size=15, anchor="middle", fill=GREEN, weight=700)
    f.note(298, "Шаг: mid = (L + R) / 2;  чекер(mid) ? R = mid : L = mid.  Пока R − L > 1.", size=15, color=TEXT2)
    return f.svg()


def cows():
    stalls = [1, 2, 4, 8, 9]
    m = 3
    f = Fig("p3", 400, title="Коровы в стойлах: жадный чекер для m = 3",
            sub="Ставим корову в первое стойло, дальше — в каждое, до которого от последней коровы ≥ D.")
    ox, s = 100, 56

    def row(y, D):
        f.text(ox - 26, y + 6, f"D = {D}", size=16, anchor="end", weight=700)
        f.line(ox - 10, y, ox + 9 * s + 10, y, stroke=AXIS, sw=1.5)
        for c in range(10):
            f.line(ox + c * s, y - 5, ox + c * s, y + 5, stroke=AXIS, sw=1)
            f.text(ox + c * s, y + 24, str(c), size=12.5, anchor="middle", fill=MUTED)
        placed, last = [], None
        for a in stalls:
            if last is None or a - last >= D:
                placed.append(a); last = a
        for a in stalls:
            on = a in placed
            f.rect(ox + a * s - 15, y - 34, 30, 26, fill=GREEN if on else NODE2, stroke=GREEN if on else GRID, rx=5)
            f.text(ox + a * s, y - 15, "К" if on else "·", size=14, anchor="middle",
                   fill=BG if on else MUTED, weight=700)
        for p, q in zip(placed, placed[1:]):
            f.path(f"M{ox + p * s},{y - 40} C{ox + p * s},{y - 64} {ox + q * s},{y - 64} {ox + q * s},{y - 40}", stroke=BLUE, sw=2)
            f.text(ox + (p + q) * s / 2, y - 62, f"{q - p}", size=14, anchor="middle", fill=BLUE, weight=700)
        ok = len(placed) >= m
        f.text(ox + 9 * s + 30, y - 10, f"{len(placed)} коровы", size=15, fill=GREEN if ok else RED, weight=700)
        f.text(ox + 9 * s + 30, y + 12, "✓ подходит" if ok else "✗ мало", size=15, fill=GREEN if ok else RED, weight=700)

    row(180, 3)
    row(320, 4)
    f.note(384, "Стойла 1, 2, 4, 8, 9. «К» — поставили корову, синие дуги — расстояния между соседними.", size=14, color=MUTED)
    return f.svg()


def ieee():
    f = Fig("p4", 340, title="double по стандарту IEEE 754: 64 бита",
            sub="Значение = (−1)ˢ × 1.мантисса₂ × 2^(порядок − 1023). Длина блоков — в масштабе.")
    ox, W, y = 40, 680, 112
    unit = W / 64
    parts = [(1, "знак", RED, "s"), (11, "порядок", BLUE, "11 бит"), (52, "мантисса", GREEN, "52 бита ≈ 15–16 цифр")]
    x = ox
    for bits, name, c, note in parts:
        w = bits * unit
        f.rect(x, y, w, 44, fill=c, op=0.85, rx=4)
        if bits > 1:
            for k in range(1, bits):
                f.line(x + k * unit, y + 30, x + k * unit, y + 44, stroke=BG, sw=0.6, op=0.5)
            f.text(x + w / 2, y + 24, name, size=15, anchor="middle", fill=BG, weight=700)
        f.text(x + (w / 2 if bits > 1 else 0), y + 68, f"{bits} бит" if bits == 1 else note, size=13.5,
               anchor="middle" if bits > 1 else "start", fill=c, weight=700)
        x += w
    f.text(ox, y + 90, "знак", size=13, fill=RED)
    f.text(32, 236, "0.5 = 0.1₂ — представимо точно ✓", size=15, fill=GREEN, weight=700)
    f.text(32, 266, "0.1 = 0.0001100110011…₂ — бесконечная дробь, хвост обрезан ✗", size=15, fill=RED, weight=700)
    f.text(32, 290, "поэтому 0.1 + 0.2 == 0.3 — false; сравнивайте с точностью eps", size=14, fill=MUTED)
    f.text(32, 318, "float — 32 бита (~7 цифр), long double — 80 бит (~18 цифр)", size=14, fill=MUTED)
    return f.svg()


def ternary():
    f = Fig("p5", 400, title="Тернарный поиск максимума: сравниваем f(m₁) и f(m₂)",
            sub="Функция растёт, потом убывает. Если f(m₁) < f(m₂), максимум точно правее m₁.")
    ox, oy, W, H = 70, 330, 600, 200
    L, R = 0.0, 9.0
    fn = lambda x: 4.2 - 0.22 * (x - 6.1) ** 2 + 0.6 * math.sin(x * 0.6)
    X = lambda x: ox + W * (x - L) / (R - L)
    vals = [fn(L + (R - L) * i / 200) for i in range(201)]
    lo, hi = min(vals) - 0.3, max(vals) + 0.4
    Y = lambda v: oy - H * (v - lo) / (hi - lo)
    m1, m2 = L + (R - L) / 3, R - (R - L) / 3
    f.rect(X(L), oy - H - 10, X(m1) - X(L), H + 10, fill=RED, op=0.12, rx=0)
    f.text((X(L) + X(m1)) / 2, oy - H + 10, "отбрасываем", size=14, anchor="middle", fill=RED, weight=700)
    f.line(ox - 10, oy, ox + W + 10, oy, stroke=AXIS, sw=1.5)
    pts = [(X(L + (R - L) * i / 200), Y(v)) for i, v in enumerate(vals)]
    f.polyline(pts, stroke=BLUE, sw=3)
    for x, name, c in [(L, "L", MUTED), (m1, "m₁", YELLOW), (m2, "m₂", ORANGE), (R, "R", MUTED)]:
        f.line(X(x), oy, X(x), Y(fn(x)), stroke=c if c != MUTED else AXIS, sw=2, dash="5 4")
        f.text(X(x), oy + 24, name, size=16, anchor="middle", fill=c if c != MUTED else TEXT2, weight=700)
        if c != MUTED:
            f.circle(X(x), Y(fn(x)), 7, fill=c)
            left = name == "m₁"
            f.text(X(x) + (-12 if left else 12), Y(fn(x)) - 10, f"f({name})", size=14, fill=c, weight=700,
                   anchor="end" if left else "start")
    f.note(382, "f(m₁) < f(m₂) ⟹ L = m₁.  Иначе R = m₂.  За шаг остаётся 2/3 отрезка.", size=15, color=TEXT2)
    return f.svg()


FIGS = {
    1: (lr_meaning, "С инвариантом $a[L] \\le x &lt; a[R]$ граница $L$ встаёт на последний элемент $\\le x$, а $R$ — на первый $&gt; x$."),
    2: (answer_split, "Ответы делятся на «не подходит» и «подходит». Бинпоиск сохраняет $L$ слева и $R$ справа от границы и сужает отрезок до соседних чисел."),
    3: (cows, "Чекер для бинпоиска по ответу: жадно ставим коров слева направо. При $D=3$ помещаются три, при $D=4$ — только две."),
    4: (ieee, "<code>double</code> хранит около 15–16 значащих цифр. Дроби со «знаменателем» не из степеней двойки, например $0.1$, хранятся приближённо."),
    5: (ternary, "На каждом шаге выкидываем треть отрезка, где максимума точно нет; итераций $\\approx \\log_{3/2}\\frac{R-L}{\\varepsilon}$."),
}
