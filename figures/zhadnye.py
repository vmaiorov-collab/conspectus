from kit import *

NOTE = "parallel-c/parallel-c-zan5-zhadnye.html"


def knapsack():
    f = Fig("zh1", 372, title="Непрерывный рюкзак: M = 10",
            sub="Слитки (масса, стоимость): A = (10, 60), B = (5, 50), C = (5, 50). Удельная стоимость: 6, 10, 10.")
    ox, unit = 60, 56   # 1 кг = 56 / 5 ≈ 11 px; рюкзак на 10 кг = 560 px
    w = 10.4 * 10

    def bag(y, title, parts, total, color):
        f.text(ox, y - 14, title, size=15.5, weight=700, fill=color)
        f.rect(ox, y, unit * 10, 44, fill=NODE2, stroke=AXIS, sw=2, rx=6)
        x = ox
        for m, name, c in parts:
            f.rect(x + 2, y + 2, m * unit - 4, 40, fill=c, stroke=c, rx=5)
            f.text(x + m * unit / 2, y + 28, name, size=15, anchor="middle", fill=BG, weight=700)
            x += m * unit
        f.text(ox + unit * 10 + 14, y + 28, total, size=16, fill=color, weight=700)

    bag(108, "самый дорогой слиток первым", [(10, "A: 60", RED)], "= 60", RED)
    bag(208, "по удельной стоимости (10, 10, 6)", [(5, "B: 50", GREEN), (5, "C: 50", GREEN)], "= 100", GREEN)
    f.note(318, "Жадность по цене слитка ломается; жадность по цене за единицу массы — работает.", size=15, color=TEXT2)
    f.note(344, "Рюкзак разрешено заполнять дробными частями — поэтому последний слиток можно взять «наполовину».", size=14, color=MUTED)
    return f.svg()


def intervals():
    iv = [(1, 3), (0, 18), (6, 18), (12, 15), (2, 7), (9, 11), (10, 17), (17, 20), (5, 10), (13, 23)]
    iv.sort(key=lambda p: (p[1], p[0]))
    taken, R = set(), -1
    for k, (s, e) in enumerate(iv):
        if s >= R:
            taken.add(k); R = e
    f = Fig("zh2", 460, title="Расписание: сортируем по концу и берём всё, что не мешает",
            sub="Полуинтервалы [s, f). Жёлтая вертикаль — граница R после очередного выбора.")
    ox, oy, ux, rh = 56, 96, 28, 28

    for t in range(0, 25, 3):
        f.line(ox + t * ux, oy - 6, ox + t * ux, oy + len(iv) * rh, stroke=GRID, sw=1)
        f.text(ox + t * ux, oy + len(iv) * rh + 20, str(t), size=13.5, fill=MUTED, anchor="middle")
    for k, (s, e) in enumerate(iv):
        y = oy + k * rh
        ok = k in taken
        f.rect(ox + s * ux, y + 3, (e - s) * ux, rh - 8, fill=GREEN if ok else NODE,
               stroke=GREEN if ok else EDGE, rx=5, op=1)
        f.text(ox + (s + e) / 2 * ux, y + rh - 10, f"{s}–{e}", size=13, anchor="middle",
               fill=BG if ok else MUTED, weight=700)
        f.text(ox - 12, y + rh - 10, "берём" if ok else "", size=12, fill=GREEN, anchor="end")
    # границы R
    for k in sorted(taken):
        e = iv[k][1]
        f.line(ox + e * ux, oy - 6, ox + e * ux, oy + len(iv) * rh, stroke=YELLOW, sw=1.6, dash="4 4", op=.7)
    f.note(432, "Берём 1–3, 5–10, 12–15, 17–20: всего 4 лекции. Остальные начинаются раньше текущей границы R.", size=14.5, color=TEXT2)
    return f.svg()


def two_stacks():
    f = Fig("zh3", 340, title="Очередь на двух стеках: перекладываем, только когда out пуст",
            sub="Стек in принимает push, стек out отдаёт front/pop.")
    cw, ch = 86, 40

    def stack(x, base, vals, label, colors):
        f.text(x + cw / 2, 82, label, size=16, weight=700, anchor="middle")
        f.path(f"M{x - 8},{base - 3 * ch - 10} V{base + 6} H{x + cw + 8} V{base - 3 * ch - 10}", stroke=AXIS, sw=2.5)
        for k, (v, c) in enumerate(zip(vals, colors)):
            y = base - (k + 1) * ch
            f.cell(x, y, v, w=cw, h=ch - 4, fill=c, stroke=c if c != NODE else GRID,
                   tcolor=BG if c != NODE else TEXT)

    # до: in = 10 20 30, out пуст
    f.text(48, 106, "до prepare()", size=14.5, fill=MUTED)
    stack(48, 270, [10, 20, 30], "in", [BLUE, NODE, PURPLE])
    stack(210, 270, [], "out", [])
    f.line(150, 170, 200, 170, stroke=GREEN, sw=2.5, arrow=True)
    f.text(175, 156, "переложить", size=13.5, fill=GREEN, anchor="middle", weight=700)
    # после
    f.text(430, 106, "после", size=14.5, fill=MUTED)
    stack(430, 270, [], "in", [])
    stack(592, 270, [30, 20, 10], "out", [PURPLE, NODE, YELLOW])
    f.text(592 + cw / 2, 300, "top = 10 = front", size=14, fill=YELLOW, anchor="middle", weight=700)
    f.note(328, "Порядок «развернулся»: первым пришедший (10) оказался сверху out.", size=14.5, color=TEXT2)
    return f.svg()


def ring():
    f = Fig("zh4", 450, title="Циклический буфер: cap = 4",
            sub="head — первый элемент очереди, tail — первая свободная ячейка; оба двигаются только вправо по кругу.")
    cw = 84

    def row(y, cells, head, tail, title, cnt):
        f.text(40, y - 40, title, size=15.5, weight=700)
        for k in range(4):
            v = cells[k]
            f.cell(100 + k * cw, y, v if v is not None else "", w=cw - 8, h=46,
                   fill=NODE if v is not None else NODE2, stroke=GRID, tcolor=TEXT)
            f.text(100 + k * cw + (cw - 8) / 2, y - 6, str(k), size=13, anchor="middle", fill=MUTED)
        def mark(i, name, c, dy):
            x = 100 + i * cw + (cw - 8) / 2
            f.line(x, y + 78 + dy, x, y + 52, stroke=c, sw=2.5, arrow=True)
            f.text(x, y + 98 + dy, name, size=15, fill=c, anchor="middle", weight=700)
        if head == tail:
            x = 100 + head * cw + (cw - 8) / 2
            f.line(x - 14, y + 78, x - 14, y + 52, stroke=GREEN, sw=2.5, arrow=True)
            f.line(x + 14, y + 78, x + 14, y + 52, stroke=ORANGE, sw=2.5, arrow=True)
            f.text(x, y + 98, "head = tail", size=14.5, fill=TEXT2, anchor="middle", weight=700)
        else:
            mark(head, "head", GREEN, 0)
            mark(tail, "tail", ORANGE, 0)
        f.text(100 + 4 * cw + 12, y + 30, f"cnt = {cnt}", size=15, fill=TEXT2)

    row(146, [10, 20, 30, None], 0, 3, "очередь 10, 20, 30", 3)
    row(322, [50, 60, 30, 40], 2, 2, "после push 40, pop ×2 (10 и 20), push 50, 60 — очередь 30, 40, 50, 60 полна", 4)
    return f.svg()


FIGS = {
    1: (knapsack, "Если брать слитки по убыванию цены, рюкзак забьёт один тяжёлый слиток; по убыванию цены за единицу массы получается оптимум."),
    2: (intervals, "Сортировка по концу: берём лекцию, если она начинается не раньше последнего выбранного конца $R$."),
    3: (two_stacks, "Один перенос из <code>in</code> в <code>out</code> разворачивает порядок; каждый элемент переносится не более одного раза."),
    4: (ring, "Указатели движутся по кругу: после последней ячейки следующая — нулевая. Пустую и полную очередь различаем по счётчику <code>cnt</code>."),
}
