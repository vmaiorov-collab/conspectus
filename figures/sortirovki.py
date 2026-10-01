from kit import *

NOTE = "parallel-c/parallel-c-zan2-slozhnost-sortirovki.html"


def merge_sort():
    a = [5, 2, 8, 1, 9, 3, 7, 4]
    f = Fig("o1", 560, title="Сортировка слиянием: делим пополам, затем сливаем",
            sub="Сверху — деление до одного элемента, снизу — слияние отсортированных половинок.")
    cw, gap, y0, dy = 38, 22, 96, 62
    width = lambda parts: sum(len(p) for p in parts) * cw + (len(parts) - 1) * gap
    ox_center = 320

    def draw_row(y, parts, color, tcolor):
        x = ox_center - width(parts) / 2
        boxes = []
        for p in parts:
            x_start = x
            for v in p:
                f.cell(x + 2, y, v, w=cw - 4, h=38, fill=color, stroke=color if color != NODE else GRID, tcolor=tcolor, size=16)
                x += cw
            boxes.append((x_start, x))
            x += gap
        return boxes

    rows = []
    # деление
    split = [[a]]
    while len(split[-1]) < len(a):
        nxt = []
        for p in split[-1]:
            h = (len(p) + 1) // 2
            nxt += [p[:h], p[h:]] if len(p) > 1 else [p]
        split.append(nxt)
    merge = []
    cur = [[v] for v in a]
    while len(cur) > 1:
        cur = [sorted(cur[i] + cur[i + 1]) for i in range(0, len(cur), 2)]
        merge.append(cur)
    all_rows = [(p, NODE, TEXT) for p in split[:-1]] + [(split[-1], YELLOW, BG)] + [(p, GREEN, BG) for p in merge]
    prev = None
    for i, (parts, col, tc) in enumerate(all_rows):
        y = y0 + i * dy
        boxes = draw_row(y, parts, col, tc)
        if prev:
            pboxes, py = prev
            if len(boxes) > len(pboxes):      # деление: родитель → два ребёнка
                for k, (x0, x1) in enumerate(pboxes):
                    for c in (2 * k, 2 * k + 1):
                        cx0, cx1 = boxes[c]
                        f.line((x0 + x1) / 2, py + 40, (cx0 + cx1) / 2, y - 2, stroke=EDGE, sw=1.5, arrow=True)
            else:                              # слияние: два → один
                for k, (x0, x1) in enumerate(boxes):
                    for c in (2 * k, 2 * k + 1):
                        cx0, cx1 = pboxes[c]
                        f.line((cx0 + cx1) / 2, py + 40, (x0 + x1) / 2, y - 2, stroke=GREEN, sw=1.5, arrow=True)
        prev = (boxes, y)
    tx = 600
    f.text(tx, y0 + 1 * dy + 24, "делим", size=16, fill=TEXT, weight=700)
    f.text(tx, y0 + 1 * dy + 46, "log₂ n уровней", size=14, fill=MUTED)
    f.text(tx, y0 + 3 * dy + 24, "по одному —", size=14.5, fill=YELLOW, weight=700)
    f.text(tx, y0 + 3 * dy + 44, "уже отсортированы", size=14, fill=MUTED)
    f.text(tx, y0 + 5 * dy + 4, "сливаем", size=16, fill=GREEN, weight=700)
    f.text(tx, y0 + 5 * dy + 26, "каждый уровень —", size=14, fill=MUTED)
    f.text(tx, y0 + 5 * dy + 46, "O(n) на merge", size=14, fill=MUTED)
    f.note(y0 + 6 * dy + 70, "log n уровней × O(n) работы на уровне = O(n log n).", size=15.5, color=TEXT2, weight=700)
    return f.svg()


FIGS = {
    1: (merge_sort, "Делим до отдельных элементов, затем сливаем отсортированные половинки снизу вверх: $\\log n$ уровней по $O(n)$ — итого $O(n\\log n)$."),
}
