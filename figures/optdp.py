from kit import *

NOTE = "parallel-ap/parallel-ap-zan5-optimizacii-dp.html"


def quad():
    f = Fig("od1", 370, title="Неравенство четырёхугольника: пересекающиеся отрезки дешевле вложенных",
            sub="Для a ≤ b ≤ c ≤ d:   w(a,c) + w(b,d)  ≤  w(a,d) + w(b,c).")
    xs = {"a": 120, "b": 260, "c": 480, "d": 640}

    def axis(y):
        f.line(80, y, 680, y, stroke=AXIS, sw=2)
        for k, x in xs.items():
            f.line(x, y - 6, x, y + 6, stroke=AXIS, sw=2)
            f.text(x, y + 26, k, size=15, anchor="middle", fill=TEXT2, weight=700)

    def seg(y, a, b, c, dy=0):
        f.path(f"M{xs[a]},{y - 10 - dy} H{xs[b]}", stroke=c, sw=5)

    y1, y2 = 150, 280
    axis(y1)
    seg(y1, "a", "c", GREEN, 0); seg(y1, "b", "d", GREEN, 22)
    f.text(60, y1 - 46, "пересекающиеся: w(a,c) + w(b,d)", size=15, fill=GREEN, weight=700)
    axis(y2)
    seg(y2, "a", "d", ORANGE, 0); seg(y2, "b", "c", ORANGE, 22)
    f.text(60, y2 - 46, "вложенные: w(a,d) + w(b,c)", size=15, fill=ORANGE, weight=700)
    f.note(352, "Любые два вложенных отрезка выгодно заменить двумя пересекающимися с теми же концами.", size=14.5, color=TEXT2)
    return f.svg()


def opt():
    f = Fig("od2", 340, title="Монотонность оптимума: opt(i−1, j) ≤ opt(i, j) ≤ opt(i, j+1)",
            sub="Таблица ДП: строки — число отрезков i, столбцы — длина префикса j. Стрелки — границы поиска.")
    ox, oy, cw, ch = 110, 100, 92, 54
    f.text(ox + 2 * cw, oy - 16, "j  →", size=14, fill=MUTED, anchor="middle")
    labels = {(0, 1): ("opt(i−1, j)", BLUE), (1, 1): ("opt(i, j)", YELLOW), (1, 2): ("opt(i, j+1)", GREEN)}
    for r in range(3):
        f.text(ox - 18, oy + r * ch + 30, f"i{'−1' if r == 0 else ''}{'+1' if r == 2 else ''}" if r != 1 else "i", size=14, anchor="end", fill=MUTED)
        for c in range(4):
            lab = labels.get((r, c))
            if lab:
                f.rect(ox + c * cw + 4, oy + r * ch + 4, cw - 8, ch - 8, fill=NODE, stroke=lab[1], sw=2.5, rx=8)
                f.text(ox + c * cw + cw / 2, oy + r * ch + 32, lab[0], size=14, anchor="middle", fill=lab[1], weight=700)
            else:
                f.rect(ox + c * cw + 4, oy + r * ch + 4, cw - 8, ch - 8, fill=NODE2, stroke=GRID, rx=8)
    f.text(ox + 4 * cw + 18, oy + 30, "нижняя граница поиска", size=13.5, fill=BLUE)
    f.text(ox + 4 * cw + 18, oy + ch + 30, "искомый оптимум", size=13.5, fill=YELLOW)
    f.text(ox + 4 * cw + 18, oy + ch + 54, "верхняя граница поиска", size=13.5, fill=GREEN)
    f.note(320, "Порядок обхода: i по возрастанию, j по убыванию — тогда обе границы к нужному моменту уже посчитаны.", size=14.5, color=TEXT2)
    return f.svg()


def envelope():
    lines = [(-2.0, 9.0, BLUE), (-0.6, 5.0, GREEN), (0.9, 2.2, ORANGE), (2.3, -3.0, PURPLE)]
    f = Fig("od3", 380, title="Convex Hull Trick: верхняя огибающая прямых",
            sub="Огибающая — выпуклая ломаная; на каждом её звене «побеждает» одна прямая.")
    X0, X1, Y0, Y1 = 60, 620, 90, 330
    xmin, xmax, ymin, ymax = -1, 6, -4, 10

    def tx(x): return X0 + (x - xmin) / (xmax - xmin) * (X1 - X0)
    def ty(y): return Y1 - (y - ymin) / (ymax - ymin) * (Y1 - Y0)
    f.line(X0, ty(0), X1, ty(0), stroke=AXIS, sw=1.5)
    f.line(tx(0), Y0 - 10, tx(0), Y1 + 6, stroke=AXIS, sw=1.5)
    for k, b, c in lines:
        pts = [(tx(x), ty(k * x + b)) for x in (xmin, xmax)]
        pts = [(x, min(max(y, Y0 - 6), Y1 + 6)) for x, y in pts]
        f.polyline(pts, stroke=c, sw=1.6, op=.45)
    # огибающая
    xs = [xmin + i * (xmax - xmin) / 400 for i in range(401)]
    env = [(x, max(k * x + b for k, b, _ in lines)) for x in xs]
    pts = [(tx(x), ty(y)) for x, y in env if ymin <= y <= ymax + 0.5]
    f.polyline(pts, stroke=YELLOW, sw=3.6)
    for i, (k, b, c) in enumerate(lines):
        f.text(X1 + 24, 110 + i * 24, f"y = {k:g}x + {b:g}".replace("-", "−"), size=13, fill=c, weight=700)
    f.note(366, "При добавлении прямой с бо́льшим наклоном она «съедает» хвост огибающей — как в алгоритме выпуклой оболочки.", size=14, color=TEXT2)
    return f.svg()


def lichao():
    f = Fig("od4", 390, title="Дерево Ли Чао: сравниваем в середине, спускаемся в одну половину",
            sub="В вершине хранится прямая; новая прямая f проигрывает или выигрывает — и «лишняя» уходит вниз.")
    X0, X1, Y0, Y1 = 50, 400, 100, 330
    def tx(t): return X0 + t * (X1 - X0)
    def ty(v): return Y1 - v * (Y1 - Y0)
    f.rect(X0, Y0, X1 - X0, Y1 - Y0, fill=NODE2, stroke=GRID, rx=8)
    f.line(tx(.5), Y0, tx(.5), Y1, stroke=AXIS, sw=1.5, dash="5 5")
    f.text(tx(.5), Y1 + 22, "m", size=15, fill=TEXT2, anchor="middle", weight=700)
    f.text(tx(0), Y1 + 22, "x_l", size=14, fill=MUTED, anchor="middle")
    f.text(tx(1), Y1 + 22, "x_r", size=14, fill=MUTED, anchor="middle")
    q = [(0, .78), (1, .22)]    # в вершине (хранится)
    g = [(0, .35), (1, .88)]    # новая прямая
    f.polyline([(tx(a), ty(b)) for a, b in q], stroke=BLUE, sw=3.4)
    f.polyline([(tx(a), ty(b)) for a, b in g], stroke=ORANGE, sw=3.4)
    f.text(tx(.02), ty(.82) - 8, "q — в вершине", size=14, fill=BLUE, weight=700)
    f.text(tx(.55), ty(.82) - 8, "f — новая", size=14, fill=ORANGE, weight=700)
    f.circle(tx(.5), ty(.5), 6, fill=YELLOW)
    steps = ["1. Если f хуже q в середине m —",
             "    меняем f и q местами.",
             "2. Теперь в m побеждает q;",
             "    смотрим на концы отрезка:",
             "    f лучше слева → в левого сына,",
             "    f лучше справа → в правого,",
             "    нигде лучше → выходим.",
             "Один спуск: O(log n)."]
    for i, s_ in enumerate(steps):
        f.text(430, 118 + i * 28, s_, size=14, fill=TEXT2 if i < 7 else YELLOW, weight=700 if i == 7 else None)
    return f.svg()


FIGS = {
    1: (quad, "Неравенство четырёхугольника: пересекающиеся отрезки не дороже вложенных с теми же концами."),
    2: (opt, "Границы поиска оптимума для клетки $(i,j)$ лежат в двух уже посчитанных клетках."),
    3: (envelope, "Верхняя огибающая набора прямых — выпуклая кусочно-линейная функция."),
    4: (lichao, "Шаг добавления прямой в дерево Ли Чао: сравнение в середине, затем спуск в одну половину."),
}
