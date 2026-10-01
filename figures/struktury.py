from kit import *

NOTE = "parallel-ap/parallel-ap-zan2-struktury.html"


def bottom_up():
    K = 8
    l0, r0 = 1, 7
    # симулируем get(l, r)
    taken = []
    l, r = l0 + K, r0 + K
    while l < r:
        if l & 1:
            taken.append(l); l += 1
        if r & 1:
            r -= 1; taken.append(r)
        l //= 2; r //= 2
    f = Fig("s1", 470, title=f"Дерево «снизу», 8 элементов: запрос get({l0}, {r0})",
            sub="Вершина v: дети 2v и 2v+1, родитель v / 2. Элемент a[i] лежит в листе 8 + i.")
    levels = [[1], [2, 3], [4, 5, 6, 7], list(range(8, 16))]
    ys = [116, 186, 256, 326]
    x0, x1 = 60, 700
    pos = {}
    for d, row in enumerate(levels):
        w = (x1 - x0) / len(row)
        for j, v in enumerate(row):
            pos[v] = (x0 + w * (j + 0.5), ys[d])
    for v in range(2, 16):
        f.edge(*pos[v // 2], *pos[v], r1=19, r2=19, color=EDGE, arrow=False)
    for v, (x, y) in pos.items():
        if v in taken:
            f.node(x, y, v, color=ORANGE, r=19, fill=ORANGE, tcolor=BG)
            k = taken.index(v) + 1
            f.circle(x + 18, y - 17, 10, fill=YELLOW)
            f.text(x + 18, y - 12.5, str(k), size=12, anchor="middle", weight=700, fill=BG)
        else:
            f.node(x, y, v, color=BLUE if v < 8 else GREEN, r=19)
    # элементы под листьями
    for i in range(K):
        x, y = pos[8 + i]
        inq = l0 <= i < r0
        f.text(x, y + 44, f"a[{i}]", size=14, anchor="middle", fill=TEXT if inq else MUTED, weight=700 if inq else None)
    xa = pos[8 + l0][0] - 30
    xb = pos[8 + r0 - 1][0] + 30
    f.path(f"M{xa},{ys[3] + 58} v8 H{xb} v-8", stroke=ORANGE, sw=2)
    f.text((xa + xb) / 2, ys[3] + 86, f"[{l0}, {r0}) = a[1] + (a[2]+a[3]) + (a[4]+a[5]) + a[6]", size=14.5, anchor="middle", fill=ORANGE, weight=700)
    f.note(450, "l = 9 нечётно → берём 9;  r = 15 нечётно → берём 14.  Поднялись: l = 5, r = 7 → берём 5 и 6.  l = r — стоп.", size=13.5, color=TEXT2)
    return f.svg()


def distinct():
    a = [4, 1, 2, 4, 1, 2]
    n = len(a)
    ql, qr = 1, 4
    f = Fig("s2", 500, title="Число различных на отрезке: сканлайн по r",
            sub="Ставим 1 в последнем на данный момент вхождении каждого значения, остальные — 0.")
    cw, ox, oy = 52, 150, 112
    # массив
    f.text(ox - 16, oy + 26, "a", size=15, fill=MUTED, anchor="end", italic=True)
    for i, v in enumerate(a):
        f.cell(ox + i * cw + 3, oy, v, w=cw - 6, h=38, fill=NODE2, stroke=AXIS)
        f.text(ox + i * cw + cw / 2, oy - 8, str(i), size=13, fill=MUTED, anchor="middle")
    last = {}
    marks = [0] * n
    for r in range(n):
        prev = last.get(a[r])
        if prev is not None:
            marks[prev] = 0
        marks[r] = 1
        last[a[r]] = r
        y = oy + 62 + r * 50
        f.text(ox - 16, y + 25, f"r = {r}", size=14, fill=TEXT2 if r != qr else YELLOW, anchor="end", weight=700 if r == qr else None)
        for i in range(n):
            x = ox + i * cw + 3
            if i > r:
                f.rect(x, y, cw - 6, 38, fill=NODE2, op=0.5, rx=6)
                continue
            if i == r:
                fill, tc = GREEN, BG
            elif i == prev:
                fill, tc = RED, BG
            else:
                fill, tc = NODE, TEXT if marks[i] else MUTED
            f.cell(x, y, marks[i], w=cw - 6, h=38, fill=fill, stroke=GRID if fill == NODE else fill, tcolor=tc)
        if r == qr:
            xa, xb = ox + ql * cw, ox + (qr + 1) * cw
            f.rect(xa - 1, y - 5, xb - xa + 2, 48, fill="none", stroke=YELLOW, sw=2.5, rx=9)
            f.text(xb + 16, y + 18, f"сумма на [{ql}, {qr}] = {sum(marks[ql:qr + 1])}", size=15, fill=YELLOW, weight=700)
            f.text(xb + 16, y + 38, "= |{1, 2, 4}| — три различных", size=13.5, fill=MUTED)
    lx = 32
    f.rect(lx, 466, 16, 16, fill=GREEN, rx=3); f.text(lx + 24, 479, "новое последнее вхождение → 1", size=14, fill=TEXT2)
    f.rect(lx + 300, 466, 16, 16, fill=RED, rx=3); f.text(lx + 324, 479, "прежнее вхождение того же числа → 0", size=14, fill=TEXT2)
    return f.svg()


FIGS = {
    1: (bottom_up, "Запрос идёт снизу вверх: нечётный левый конец и нечётный правый конец забираем в ответ и сдвигаем — на каждом уровне не больше двух вершин."),
    2: (distinct, "При сдвиге $r$ значение $a_r$ «переезжает» в новую позицию. Тогда для отрезка $[l, r]$ сумма единиц равна числу различных."),
}
