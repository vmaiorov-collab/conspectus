import math
from kit import *

NOTE = "parallel-bp/parallel-bp-zan1-cpp.html"


def vector_growth():
    f = Fig("c1", 400, title="vector::push_back: size, capacity и удвоение",
            sub="data — указатель на буфер из capacity ячеек; заняты первые size из них.")
    cw, ox = 52, 210

    def buf(y, cap, vals, label, sub, new=None, copied=False):
        f.text(ox - 18, y + 18, label, size=15, anchor="end", weight=700)
        f.text(ox - 18, y + 38, sub, size=13.5, anchor="end", fill=MUTED)
        for k in range(cap):
            x = ox + k * cw + 3
            if k < len(vals):
                is_new = new is not None and k == new
                fill = ORANGE if is_new else (BLUE if copied else NODE)
                f.cell(x, y, vals[k], w=cw - 6, h=42, fill=fill, stroke=fill if fill != NODE else AXIS,
                       tcolor=BG if fill != NODE else TEXT)
            else:
                f.rect(x, y, cw - 6, 42, fill=NODE2, stroke=GRID, dash="4 4")
        if len(vals) < cap:
            f.text(ox + len(vals) * cw + cw / 2 - 3, y + 62, "↑ size", size=13.5, fill=TEXT2, anchor="middle")
        f.text(ox + cap * cw + 6, y + 27, f"capacity = {cap}", size=14, fill=MUTED)

    buf(100, 4, [1, 2, 3, 4], "было", "size = 4 = capacity")
    f.text(ox + 4 * cw + 14, 186, "push_back(5): места нет →", size=15, fill=RED, weight=700)
    f.text(ox + 4 * cw + 14, 206, "выделяем 8 ячеек и копируем", size=14, fill=MUTED)
    for k in range(4):
        f.line(ox + k * cw + cw / 2, 150, ox + k * cw + cw / 2, 206, stroke=BLUE, sw=2, arrow=True, dash="5 4")
    buf(212, 8, [1, 2, 3, 4, 5], "стало", "новый буфер ×2", new=4, copied=True)
    f.legend(32, 316, [(BLUE, "скопировано из старого буфера (старый освобождается)", "box"),
                       (ORANGE, "новый элемент — на позицию size", "box")], gap=26)
    f.note(382, "Копирований за n вставок ≤ 1 + 2 + 4 + … < 2n, поэтому push_back — O(1) в среднем.", size=14.5, color=TEXT2)
    return f.svg()


def ring():
    cap = 8
    head, tail = 5, 2
    f = Fig("c2", 384, title="Очередь на циклическом буфере: capacity = 8",
            sub="head — первый элемент, tail — куда положить следующий. Оба идут вперёд по кругу.")
    cw, ox, y = 70, 100, 150
    occ = [(head + k) % cap for k in range((tail - head) % cap)]
    order = {v: i for i, v in enumerate(occ)}
    for k in range(cap):
        on = k in order
        f.cell(ox + k * cw + 4, y, f"x{order[k] + 1}" if on else "", w=cw - 8, h=46,
               fill=BLUE if on else NODE2, stroke=BLUE if on else GRID, tcolor=BG)
        f.text(ox + k * cw + cw / 2, y - 12, str(k), size=13.5, anchor="middle", fill=MUTED)
    hx = ox + head * cw + cw / 2
    tx = ox + tail * cw + cw / 2
    f.line(hx, y + 92, hx, y + 54, stroke=GREEN, sw=2.5, arrow=True)
    f.text(hx, y + 112, "head = 5", size=15, anchor="middle", fill=GREEN, weight=700)
    f.text(hx, y + 132, "pop отсюда", size=13.5, anchor="middle", fill=MUTED)
    f.line(tx, y + 92, tx, y + 54, stroke=ORANGE, sw=2.5, arrow=True)
    f.text(tx, y + 112, "tail = 2", size=15, anchor="middle", fill=ORANGE, weight=700)
    f.text(tx, y + 132, "push сюда", size=13.5, anchor="middle", fill=MUTED)
    # перенос через край
    x7 = ox + 7 * cw + cw / 2
    x0 = ox + 0 * cw + cw / 2
    f.path(f"M{x7 + 30},{y + 23} C{x7 + 70},{y + 23} {x7 + 70},{y - 40} {x7},{y - 40} L{x0},{y - 40} C{x0 - 70},{y - 40} {x0 - 70},{y + 23} {x0 - 34},{y + 23}",
           stroke=BLUE, sw=2, dash="6 5", arrow=True)
    f.text((x0 + x7) / 2, y - 48, "после ячейки 7 — снова 0", size=14, anchor="middle", fill=BLUE)
    f.note(312, "push:  a[tail] = x,  tail = (tail + 1) % cap", size=14.5, color=TEXT2)
    f.note(334, "pop:   head = (head + 1) % cap", size=14.5, color=TEXT2)
    f.note(364, "Очередь сейчас: x1 x2 x3 x4 x5 — она «переехала» через край массива.", size=14.5, color=MUTED)
    return f.svg()


def two_stacks():
    f = Fig("c3", 420, title="Очередь на двух стеках: in для push, out для pop",
            sub="Когда out пуст, перекладываем в него весь in — порядок переворачивается.")

    def stack(x, y, vals, label, color, top_hl=False):
        cw, ch = 64, 38
        for k in range(4):
            yy = y - (k + 1) * ch
            if k < len(vals):
                hl = top_hl and k == len(vals) - 1
                f.cell(x, yy + 2, vals[k], w=cw, h=ch - 4, fill=YELLOW if hl else color,
                       stroke=YELLOW if hl else color, tcolor=BG)
            else:
                f.rect(x, yy + 2, cw, ch - 4, fill=NODE2, stroke=GRID, dash="4 4")
        f.path(f"M{x - 6},{y - 4 * ch - 4} V{y + 4} H{x + cw + 6} V{y - 4 * ch - 4}", stroke=AXIS, sw=2)
        f.text(x + cw / 2, y + 28, label, size=15, anchor="middle", weight=700, fill=color)

    panels = [
        (40, "1. push 1, 2, 3", [1, 2, 3], [], False),
        (290, "2. pop: перекладываем", [], [3, 2, 1], False),
        (540, "3. pop вернул 1 ✓", [], [3, 2, 1], True),
    ]
    for x, title, a, b, hl in panels:
        f.text(x, 108, title, size=15, weight=700)
        stack(x + 6, 300, a, "in", BLUE)
        stack(x + 96, 300, b, "out", GREEN, top_hl=hl)
    f.path("M226,200 C246,200 256,200 276,200", stroke=MUTED, sw=2, arrow=True)
    f.path("M476,200 C496,200 506,200 526,200", stroke=MUTED, sw=2, arrow=True)
    f.note(366, "1 пришёл первым и первым ушёл — это очередь. Каждый элемент перекладывается", size=14.5, color=TEXT2)
    f.note(388, "ровно один раз, поэтому все операции — O(1) амортизированно.", size=14.5, color=TEXT2)
    return f.svg()


def bounds():
    a = [1, 3, 5, 5, 5, 7, 9]
    f = Fig("c4", 400, title="lower_bound и upper_bound в отсортированном массиве",
            sub="lower_bound — первый элемент ≥ x;  upper_bound — первый элемент > x.")
    cw, ox = 62, 130

    def row(y, x, title):
        lb = next((i for i, v in enumerate(a) if v >= x), len(a))
        ub = next((i for i, v in enumerate(a) if v > x), len(a))
        f.text(ox - 20, y + 26, title, size=16, anchor="end", weight=700)
        for i, v in enumerate(a + ["end"]):
            eq = i < len(a) and v == x
            if i == len(a):
                f.rect(ox + i * cw + 4, y, cw - 8, 40, fill=NODE2, stroke=GRID, dash="4 4")
                f.text(ox + i * cw + cw / 2, y + 26, "end", size=13.5, anchor="middle", fill=MUTED)
                continue
            f.cell(ox + i * cw + 4, y, v, w=cw - 8, h=40, fill=YELLOW if eq else NODE,
                   stroke=YELLOW if eq else GRID, tcolor=BG if eq else TEXT)
            f.text(ox + i * cw + cw / 2, y - 8, str(i), size=12.5, anchor="middle", fill=MUTED)
        xl = ox + lb * cw + cw / 2
        xu = ox + ub * cw + cw / 2
        if lb == ub:
            f.line(xl, y + 86, xl, y + 46, stroke=PURPLE, sw=2.5, arrow=True)
            f.text(xl, y + 104, "lower = upper", size=14, anchor="middle", fill=PURPLE, weight=700)
        else:
            f.line(xl, y + 86, xl, y + 46, stroke=BLUE, sw=2.5, arrow=True)
            f.text(xl, y + 104, "lower_bound", size=14, anchor="middle", fill=BLUE, weight=700)
            f.line(xu, y + 86, xu, y + 46, stroke=ORANGE, sw=2.5, arrow=True)
            f.text(xu, y + 104, "upper_bound", size=14, anchor="middle", fill=ORANGE, weight=700)
        return lb, ub

    lb, ub = row(108, 5, "x = 5")
    row(254, 6, "x = 6")
    f.note(384, f"Число пятёрок = upper − lower = {ub} − {lb} = {ub - lb}.  Если x нет, оба указывают на первый элемент > x.", size=14.5, color=TEXT2)
    return f.svg()


FIGS = {
    1: (vector_growth, "Пока <code>size &lt; capacity</code>, вставка — $O(1)$. Когда места нет, буфер удваивается и копируется; в сумме это всё равно $O(1)$ на вставку."),
    2: (ring, "Указатели <code>head</code> и <code>tail</code> идут по кругу по модулю <code>capacity</code>; очередь может «переехать» через край массива."),
    3: (two_stacks, "Перекладывание переворачивает порядок, и стек начинает отдавать элементы в порядке очереди. Каждый элемент перекладывается один раз."),
    4: (bounds, "Обе функции — бинпоиск по отсортированному диапазону за $O(\\log n)$; вместе они дают отрезок элементов, равных $x$."),
}
