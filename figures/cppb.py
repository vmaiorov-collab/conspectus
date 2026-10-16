from kit import *

NOTE = "parallel-b/parallel-b-zan4-cpp.html"


def io_buffer():
    f = Fig("cb1", 330, title="Буфер вывода: почему cin.tie(nullptr) и '\\n' ускоряют программу",
            sub="Сбросить буфер в систему — дорогая операция. Нужно делать её как можно реже.")
    # блоки
    f.rect(40, 130, 150, 70, fill=NODE, stroke=BLUE, sw=2, rx=10)
    f.text(115, 160, "программа", size=16, anchor="middle", weight=700)
    f.text(115, 184, "cout << x", size=14, anchor="middle", fill=MUTED)
    f.rect(300, 130, 170, 70, fill=NODE, stroke=GREEN, sw=2, rx=10)
    f.text(385, 160, "буфер", size=16, anchor="middle", weight=700)
    f.text(385, 184, "накапливает вывод", size=14, anchor="middle", fill=MUTED)
    f.rect(580, 130, 150, 70, fill=NODE, stroke=ORANGE, sw=2, rx=10)
    f.text(655, 160, "система", size=16, anchor="middle", weight=700)
    f.text(655, 184, "экран / файл", size=14, anchor="middle", fill=MUTED)
    f.line(192, 165, 296, 165, stroke=GREEN, sw=3, arrow=True)
    f.text(244, 152, "быстро", size=14, anchor="middle", fill=GREEN, weight=700)
    f.line(472, 165, 576, 165, stroke=RED, sw=3, arrow=True)
    f.text(524, 152, "flush: медленно", size=14, anchor="middle", fill=RED, weight=700)
    f.text(32, 252, "'\\n' — только перевод строки (в буфер).", size=15, fill=TEXT2)
    f.text(32, 276, "endl = '\\n' + flush — сбрасывает буфер при каждом выводе.", size=15, fill=TEXT2)
    f.text(32, 300, "cin >> x при привязке cin к cout сначала вызывает cout.flush() — отвязываем: cin.tie(nullptr).", size=15, fill=TEXT2)
    return f.svg()


def unique_fig():
    f = Fig("cb2", 340, title="sort + unique + erase: сжатие координат",
            sub="unique сдвигает уникальные значения в начало и возвращает итератор на конец уникальной части.")
    a = [1, 2, 2, 3, 4, 4]
    after = [1, 2, 3, 4, 4, 4]
    ox, cw = 150, 70
    f.text(32, 118, "после sort", size=14.5, fill=MUTED)
    for k, v in enumerate(a):
        f.cell(ox + k * cw, 96, v, w=cw - 8, h=40, fill=NODE)
    f.text(32, 208, "после unique", size=14.5, fill=MUTED)
    for k, v in enumerate(after):
        keep = k < 4
        f.cell(ox + k * cw, 186, v, w=cw - 8, h=40, fill=GREEN if keep else NODE2, stroke=GREEN if keep else GRID,
               tcolor=BG if keep else MUTED)
    xe = ox + 4 * cw - 4
    f.line(xe, 252, xe, 232, stroke=YELLOW, sw=3, arrow=True)
    f.text(xe, 274, "new_end", size=15, fill=YELLOW, anchor="middle", weight=700)
    f.text(xe + 120, 274, "хвост — «мусор»", size=14, fill=MUTED)
    f.note(318, "v.erase(unique(v.begin(), v.end()), v.end());  — отбрасываем хвост, остаются 1 2 3 4", size=14.5, color=TEXT2)
    return f.svg()


def stress_flow():
    f = Fig("cb3", 340, title="Стресс-тестирование: три программы по кругу",
            sub="gen — генератор, solution — ваше решение, stupid — медленное, но верное.")
    def box(x, y, w, h, t, col):
        f.rect(x, y, w, h, fill=NODE, stroke=col, sw=2, rx=10)
        f.text(x + w / 2, y + h / 2 + 5, t, size=15, anchor="middle", weight=700)
    box(40, 150, 100, 50, "gen", PURPLE)
    box(200, 150, 110, 50, "in.txt", AXIS)
    box(380, 100, 130, 50, "solution", BLUE)
    box(380, 200, 130, 50, "stupid", ORANGE)
    box(570, 100, 120, 50, "out.txt", AXIS)
    box(570, 200, 120, 50, "ans.txt", AXIS)
    f.line(142, 175, 198, 175, stroke=TEXT2, sw=2.5, arrow=True)
    f.line(312, 165, 378, 128, stroke=TEXT2, sw=2.5, arrow=True)
    f.line(312, 185, 378, 224, stroke=TEXT2, sw=2.5, arrow=True)
    f.line(512, 125, 568, 125, stroke=TEXT2, sw=2.5, arrow=True)
    f.line(512, 225, 568, 225, stroke=TEXT2, sw=2.5, arrow=True)
    f.line(630, 152, 630, 198, stroke=YELLOW, sw=3, dash="6 5")
    f.text(640, 180, "diff", size=15, fill=YELLOW, weight=700)
    f.text(32, 286, "код возврата != 0 → «решение упало»;  diff != 0 → «найден тест, где ответы отличаются»;  иначе — следующий тест.", size=14, fill=TEXT2)
    f.text(32, 312, "Генератору передаём номер теста как seed: любой тест можно воспроизвести.", size=14, fill=MUTED)
    return f.svg()


def z_to_pi():
    s = "abacaba"
    n = len(s)
    z = [0, 0, 1, 0, 3, 0, 1]
    pi = [0, 0, 1, 0, 1, 2, 3]
    f = Fig("cb4", 330, title="Z-функция → префикс-функция на примере abacaba",
            sub="На конце каждого Z-блока [i, i+z[i]) префикс-функция не меньше z[i]; дальше идём справа налево: p[i−1] ≥ p[i] − 1.")
    ox, cw = 150, 70
    labels = ["i", "s", "z", "π"]
    rows = [list(range(n)), list(s), z, pi]
    for r, (lab, vals) in enumerate(zip(labels, rows)):
        yy = 112 + r * 48
        f.text(90, yy + 26, lab, size=16, fill=MUTED, anchor="middle", weight=700)
        for k, v in enumerate(vals):
            col = NODE
            stroke = GRID
            tc = TEXT
            if r == 3 and k in (4, 5, 6):
                col, stroke, tc = GREEN, GREEN, BG
            if r == 3 and k == 2:
                col, stroke, tc = GREEN, GREEN, BG
            if r == 2 and k in (2, 4):
                col, stroke, tc = ORANGE, ORANGE, BG
            f.cell(ox + k * cw, yy, v, w=cw - 8, h=40, fill=col, stroke=stroke, tcolor=tc)
    # Z-блок [4,7)
    f.path(f"M{ox + 4 * cw},{108} v-8 H{ox + 7 * cw - 8} v8", stroke=ORANGE, sw=2.5)
    f.text(ox + 5.5 * cw - 4, 92, "блок z[4] = 3", size=14, fill=ORANGE, anchor="middle", weight=700)
    f.note(318, "π[6] = 3 (конец блока z[4]); справа налево: π[5] ≥ 2, π[4] ≥ 1. Блок z[2] = 1 даёт π[2] = 1.", size=14.5, color=TEXT2)
    return f.svg()


def radix():
    f = Fig("cb5", 330, title="Поразрядная (LSD) сортировка: сначала младший разряд, затем старший",
            sub="Каждый проход — устойчивая сортировка подсчётом; относительный порядок равных цифр сохраняется.")
    rows = [("исходный массив", [52, 31, 54, 12, 33], None),
            ("после сортировки по единицам", [31, 52, 12, 33, 54], 1),
            ("после сортировки по десяткам", [12, 31, 33, 52, 54], 0)]
    ox, cw = 330, 78
    for r, (lab, vals, dig) in enumerate(rows):
        yy = 110 + r * 70
        f.text(32, yy + 26, lab, size=14.5, fill=TEXT2)
        for k, v in enumerate(vals):
            f.cell(ox + k * cw, yy, "", w=cw - 8, h=42, fill=NODE)
            tens, ones = str(v)[0], str(v)[1]
            tcol = lambda on: YELLOW if on else TEXT
            f.text(ox + k * cw + 18, yy + 28, tens, size=18, weight=700, fill=tcol(dig == 0))
            f.text(ox + k * cw + 38, yy + 28, ones, size=18, weight=700, fill=tcol(dig == 1))
    f.note(318, "52 и 12 равны по единицам: после первого прохода 52 стоит раньше 12 — как в исходном массиве.", size=14.5, color=MUTED)
    return f.svg()


def tree_brackets():
    f = Fig("cb6", 330, title="Корневое дерево как скобочная последовательность",
            sub="Для вершины: «(» + отсортированные последовательности детей + «)». Листу соответствует «()».")
    pos = {"r": (190, 110), "a": (80, 190), "b": (190, 190), "c": (300, 190), "d": (150, 270), "e": (230, 270)}
    for u, v in [("r", "a"), ("r", "b"), ("r", "c"), ("b", "d"), ("b", "e")]:
        f.line(*pos[u], *pos[v], stroke=EDGE, sw=2.5)
    for k, (x, y) in pos.items():
        f.node(x, y, k, color=BLUE if k != "r" else GREEN, r=17, size=14)
    f.text(400, 130, "лист:", size=14.5, fill=MUTED)
    f.text(450, 130, "()", size=16, fill=TEXT, weight=700)
    f.text(400, 170, "вершина b:", size=14.5, fill=MUTED)
    f.text(500, 170, "(()())", size=16, fill=TEXT, weight=700)
    f.text(400, 210, "корень r:  (", size=14.5, fill=MUTED)
    f.text(485, 210, "(()())", size=16, fill=GREEN, weight=700)
    f.text(562, 210, "()", size=16, fill=TEXT, weight=700)
    f.text(590, 210, "()", size=16, fill=TEXT, weight=700)
    f.text(618, 210, ")", size=14.5, fill=MUTED)
    f.text(400, 250, "Дети отсортированы лексикографически, поэтому", size=14, fill=TEXT2)
    f.text(400, 272, "изоморфные деревья дают одну и ту же строку.", size=14, fill=TEXT2)
    return f.svg()


def hash2d():
    f = Fig("cb7", 360, title="Хэш подматрицы из двумерных префиксных хэшей",
            sub="Как с префиксными суммами: берём большую область, вычитаем две полосы, возвращаем угол.")
    ox, oy, W, H = 60, 100, 340, 230
    f.rect(ox, oy, W, H, fill="none", stroke=AXIS, sw=2, rx=4)
    r1, c1, r2, c2 = 90, 110, 190, 290          # внутренний прямоугольник в локальных координатах
    f.rect(ox, oy, c2, r1, fill=RED, stroke=RED, rx=0, op=0.35)                      # верхняя полоса H[r1][c2]
    f.rect(ox, oy, c1, r2, fill=BLUE, stroke=BLUE, rx=0, op=0.35)                    # левая полоса H[r2][c1]
    f.rect(ox, oy, c1, r1, fill=PURPLE, stroke=PURPLE, rx=0, op=0.5)                 # угол H[r1][c1]
    f.rect(ox + c1, oy + r1, c2 - c1, r2 - r1, fill="none", stroke=YELLOW, sw=3.5, rx=4)
    f.text(ox + (c1 + c2) / 2, oy + (r1 + r2) / 2 + 5, "нужный", size=15, fill=YELLOW, anchor="middle", weight=700)
    f.text(ox + 8, oy + H - 10, "H[r2][c2] — вся область от угла (0,0)", size=13.5, fill=MUTED)
    f.text(430, 130, "hash = H[r2][c2]", size=15, fill=TEXT)
    f.text(430, 160, "− H[r1][c2]·P^h", size=15, fill=RED, weight=700)
    f.text(430, 190, "− H[r2][c1]·Q^w", size=15, fill=BLUE, weight=700)
    f.text(430, 220, "+ H[r1][c1]·P^h·Q^w", size=15, fill=PURPLE, weight=700)
    f.text(430, 262, "h, w — высота и ширина подматрицы;", size=14, fill=TEXT2)
    f.text(430, 284, "P, Q — основания по строкам и столбцам.", size=14, fill=TEXT2)
    return f.svg()


def substr_hash():
    f = Fig("cb8", 300, title="Хэш подстроки: H[r] − H[l]·P^(r−l)",
            sub="h[i+1] = h[i]·P + s[i]: префикс до l в хэше до r сдвинут на r − l разрядов — его и вычитаем.")
    ox, cw = 80, 56
    chars = "abcabbca"
    for k, c in enumerate(chars):
        inside = 2 <= k < 6
        f.cell(ox + k * cw, 120, c, w=cw - 6, h=40, fill=YELLOW if inside else NODE, stroke=YELLOW if inside else GRID,
               tcolor=BG if inside else TEXT)
        f.text(ox + k * cw + (cw - 6) / 2, 182, str(k), size=13, fill=MUTED, anchor="middle")
    f.line(ox + 2 * cw - 3, 110, ox + 2 * cw - 3, 196, stroke=RED, sw=2.5)
    f.line(ox + 6 * cw - 3, 110, ox + 6 * cw - 3, 196, stroke=GREEN, sw=2.5)
    f.text(ox + 2 * cw - 3, 214, "l", size=16, fill=RED, anchor="middle", weight=700)
    f.text(ox + 6 * cw - 3, 214, "r", size=16, fill=GREEN, anchor="middle", weight=700)
    f.path(f"M{ox},104 H{ox + 2 * cw - 6}", stroke=RED, sw=3)
    f.text(ox + cw, 92, "H[l]", size=15, fill=RED, anchor="middle", weight=700)
    f.path(f"M{ox},238 H{ox + 6 * cw - 6}", stroke=GREEN, sw=3)
    f.text(ox + 3 * cw, 258, "H[r] — включает и префикс до l, и подстроку", size=14.5, fill=GREEN, anchor="middle", weight=700)
    f.text(ox + 4 * cw - 3, 92, "подстрока [l, r)", size=15, fill=YELLOW, anchor="middle", weight=700)
    f.note(284, "H[l]·P^(r−l) стоит в H[r] ровно в тех же разрядах, что и префикс до l, — разность оставляет только подстроку.", size=14, color=TEXT2)
    return f.svg()


FIGS = {
    1: (io_buffer, "Вывод сначала копится в буфере (быстро), а сброс буфера в систему — дорогая операция."),
    2: (unique_fig, "После <code>sort</code> и <code>unique</code> уникальные значения идут в начале, <code>erase</code> удаляет хвост."),
    3: (stress_flow, "Генератор, решение и «тупое» решение запускаются по кругу; проверка — по кодам возврата и <code>diff</code>."),
    4: (z_to_pi, "Конец Z-блока даёт опорное значение префикс-функции, остальные позиции блока заполняются справа налево."),
    5: (substr_hash, "Хэш подстроки через префиксные хэши: умножаем $H[l]$ на $P^{r-l}$ и вычитаем из $H[r]$."),
    6: (radix, "Две устойчивые сортировки подсчётом подряд — по младшему и по старшему разряду — сортируют массив чисел."),
    7: (tree_brackets, "Изоморфные корневые деревья дают одну и ту же скобочную последовательность или хэш от неё."),
    8: (hash2d, "Хэш подматрицы выражается через четыре значения двумерных префиксных хэшей."),
}
