from kit import *

NOTE = "parallel-b/parallel-b-zan5-matematika1.html"


def exgcd_trace():
    rows = []
    a, b = 18, 30

    def rec(a, b):
        if a == 0:
            rows.append([a, b, None, b, 0, 1]); return b, 0, 1
        g, xp, yp = rec(b % a, a)
        x = yp - (b // a) * xp; y = xp
        rows.append([a, b, b // a, g, x, y])
        return g, x, y
    rec(a, b)
    rows = rows[::-1]
    f = Fig("m1", 80 + 52 + 46 * len(rows) + 60, title="Расширенный Евклид для a = 18, b = 30",
            sub="Спускаемся вниз по (a, b) → (b mod a, a), в основании x = 0, y = 1, затем поднимаемся наверх.")
    cols = [("a", 60), ("b", 150), ("b div a", 270), ("НОД", 390), ("x", 490), ("y", 580)]
    y0 = 104
    for name, x in cols:
        f.text(x, y0, name, size=14, fill=MUTED, anchor="middle", weight=700)
    for i, r in enumerate(rows):
        y = y0 + 24 + i * 46
        last = r[2] is None
        for (name, x), v in zip(cols, r):
            txt = "—" if v is None else str(v)
            f.rect(x - 38, y - 4, 76, 38, fill=NODE, stroke=GREEN if (name in "xy" and last) else GRID, rx=6)
            f.text(x, y + 22, txt, size=16, anchor="middle", fill=YELLOW if (name in ("x", "y") and i == 0) else TEXT, weight=700)
    f.text(650, y0 + 24 + 22, "↓ спуск", size=13.5, fill=MUTED)
    f.text(650, y0 + 24 + 46 * (len(rows) - 1) + 22, "↑ подъём", size=13.5, fill=MUTED)
    f.note(y0 + 24 + 46 * len(rows) + 20, "x = y' − ⌊b/a⌋·x',  y = x'.   Итог в верхней строке: 18·2 + 30·(−1) = 6 = НОД.", size=13.5, color=TEXT2)
    return f.svg()


def sieve():
    N = 30
    d = list(range(N + 1))
    for i in range(2, 6):
        if d[i] == i:
            for j in range(i * i, N + 1, i):
                if d[j] == j:
                    d[j] = i
    f = Fig("m2", 360, title="Решето Эратосфена: вычёркиваем кратные простым",
            sub="Цвет — минимальный простой делитель; зелёные — простые. Для 28: 28 → 14 → 7.")
    cw, ch, ox, oy = 64, 46, 50, 96
    colors = {2: BLUE, 3: ORANGE, 5: PURPLE}
    for n in range(2, N + 1):
        k = n - 2
        r, c = divmod(k, 10)
        x, y = ox + c * cw, oy + r * (ch + 8)
        if d[n] == n:
            f.rect(x, y, cw - 8, ch, fill=NODE, stroke=GREEN, sw=2.5, rx=7)
            f.text(x + (cw - 8) / 2, y + 29, str(n), size=17, anchor="middle", fill=GREEN, weight=700)
        else:
            col = colors[d[n]]
            f.rect(x, y, cw - 8, ch, fill=NODE2, stroke=col, sw=1.5, rx=7, op=.9)
            f.text(x + (cw - 8) / 2, y + 22, str(n), size=16, anchor="middle", fill=MUTED, weight=700)
            f.text(x + (cw - 8) / 2, y + 40, f"d={d[n]}", size=12, anchor="middle", fill=col)
    f.legend(ox, 290, [(BLUE, "делится на 2", "box"), (ORANGE, "на 3 (но не на 2)", "box"), (PURPLE, "на 5 (но не на 2, 3)", "box")], size=13, gap=22)
    f.text(ox + 300, 290, "простые не вычёркиваются: d[p] = p", size=14, fill=GREEN)
    return f.svg()


def pascal():
    from math import comb
    f = Fig("m3", 400, title="Треугольник Паскаля и «хоккейная клюшка»",
            sub="C(3,3) + C(4,3) + C(5,3) + C(6,3) = 1 + 4 + 10 + 20 = 35 = C(7,4).")
    cw, ch = 74, 38
    cx = 380
    for n in range(8):
        for k in range(n + 1):
            x = cx + (k - n / 2) * cw
            y = 100 + n * 30
            hi = k == 3 and 3 <= n <= 6
            res = (n, k) == (7, 4)
            f.rect(x - 26, y - 14, 52, 26, fill=YELLOW if res else (NODE if not hi else GREEN), stroke=YELLOW if res else (GRID if not hi else GREEN), rx=6)
            f.text(x, y + 5, str(comb(n, k)), size=14.5, anchor="middle", fill=BG if (hi or res) else TEXT, weight=700)
    f.text(60, 384, "зелёные — клюшка (k = 3 вдоль диагонали); жёлтая — их сумма в «развороте» на следующей строке.", size=13.5, fill=TEXT2)
    return f.svg()


def stars():
    f = Fig("m4", 300, title="Шарики и перегородки: 6 предметов в 6 групп (5 перегородок)",
            sub="Разбиение 0 + 3 + 0 + 0 + 3 + 0 соответствует последовательности из 6 шариков и 5 перегородок.")
    seq = "|●●●|||●●●|"
    cw = 56
    ox = 380 - len(seq) * cw / 2
    for i, ch in enumerate(seq):
        bar = ch == "|"
        f.rect(ox + i * cw + 3, 128, cw - 6, 52, fill=NODE, stroke=ORANGE if bar else BLUE, sw=2, rx=8)
        f.text(ox + i * cw + cw / 2, 164, "│" if bar else "●", size=24, anchor="middle", fill=ORANGE if bar else BLUE, weight=700)
    f.text(380, 214, "всего 11 мест; выбираем 5 из них под перегородки:", size=15, anchor="middle", fill=TEXT2)
    f.text(380, 246, "C(11, 5) = C(n + k − 1, k − 1) способов, n = 6 предметов, k = 6 групп", size=15, anchor="middle", fill=YELLOW, weight=700)
    return f.svg()


FIGS = {
    1: (exgcd_trace, "Таблица расширенного Евклида: сначала спуск по рекурсии, затем подъём с пересчётом $x,y$."),
    2: (sieve, "Решето Эратосфена для $N=30$; в массиве минимальных делителей $d[n]$ хранится наименьший простой делитель числа."),
    3: (pascal, "Диагональ треугольника Паскаля суммируется в число на следующей строке (тождество «хоккейной клюшки»)."),
    4: (stars, "Расстановка перегородок «между шариками» с повторениями сводится к выбору мест среди $n+k-1$ позиций."),
}
