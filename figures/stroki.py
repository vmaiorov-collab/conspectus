from kit import *

NOTE = "parallel-b/parallel-b-zan2-stroki.html"


def prefix_function(s):
    p = [0] * len(s)
    for i in range(1, len(s)):
        j = p[i - 1]
        while j and s[j] != s[i]:
            j = p[j - 1]
        if s[j] == s[i]:
            j += 1
        p[i] = j
    return p


def border_chain():
    S = "abacabab"
    pi = prefix_function(S)
    i = 7
    f = Fig("t1", 440, title="Считаем π[7] для S = abacabab: перебор по цепочке бордеров",
            sub="Кандидат j: первые j символов уже совпали с концом. Осталось сравнить S[j] и S[i].")
    cw, ox = 50, 210
    def row(y, label, sub, hl, cmp_ok=None, j=None):
        f.text(ox - 18, y + 20, label, size=15, anchor="end", weight=700)
        if sub:
            f.text(ox - 18, y + 40, sub, size=13, anchor="end", fill=MUTED)
        for k, ch in enumerate(S):
            col = hl.get(k)
            fill = col if col else NODE
            f.cell(ox + k * cw + 3, y, ch, w=cw - 6, h=40, fill=fill, stroke=col or GRID,
                   tcolor=BG if col else TEXT, size=17)
        if j is not None:
            c = GREEN if cmp_ok else RED
            x1, x2 = ox + j * cw + cw / 2, ox + i * cw + cw / 2
            f.path(f"M{x1},{y + 44} C{x1},{y + 70} {x2},{y + 70} {x2},{y + 44}", stroke=c, sw=2.5)
            f.text((x1 + x2) / 2, y + 80, f"S[{j}] = {S[j]}  {'=' if cmp_ok else '≠'}  S[{i}] = {S[i]}  {'✓' if cmp_ok else '✗'}",
                   size=14.5, anchor="middle", fill=c, weight=700)
    # индексы
    for k in range(len(S)):
        f.text(ox + k * cw + cw / 2, 102, str(k), size=13, anchor="middle", fill=YELLOW if k == i else MUTED, weight=700 if k == i else None)
    f.text(ox + i * cw + cw / 2, 86, "i", size=14, anchor="middle", fill=YELLOW, weight=700, italic=True)
    # шаг 1: j = π[6] = 3
    j1 = pi[i - 1]
    hl = {k: BLUE for k in range(j1)}
    hl.update({k: BLUE for k in range(i - j1, i)})
    hl[j1] = RED; hl[i] = RED
    row(112, f"j = π[6] = {j1}", "бордер «aba»", hl, False, j1)
    # шаг 2: j = π[j1-1]
    j2 = pi[j1 - 1]
    hl = {k: GREEN for k in range(j2)}
    hl.update({k: GREEN for k in range(i - j2, i)})
    hl[j2] = YELLOW; hl[i] = YELLOW
    row(240, f"j = π[2] = {j2}", "бордер бордера «a»", hl, True, j2)
    f.text(32, 380, f"Совпало при j = {j2}, значит π[7] = j + 1 = {pi[i]}.", size=16, fill=GREEN, weight=700)
    f.note(406, "Кандидат j = 2 даже не рассматривали: кандидаты — только цепочка бордеров π[i−1], π[π[i−1]−1], … до 0.", size=14)
    return f.svg()


def kmp():
    S, T = "abc", "abxabcab"
    A = S + "#" + T
    pi = prefix_function(A)
    f = Fig("t2", 330, title="Поиск S = abc в T = abxabcab через π строки S#T",
            sub="Там, где π = |S| = 3, в тексте заканчивается вхождение шаблона.")
    cw, ox = 52, 120
    y1, y2 = 120, 190
    f.text(ox - 16, y1 + 25, "S#T", size=15, anchor="end", fill=TEXT2, weight=700)
    f.text(ox - 16, y2 + 25, "π", size=16, anchor="end", fill=TEXT2, weight=700, italic=True)
    hit = [k for k, v in enumerate(pi) if v == len(S)]
    match = set()
    for k in hit:
        match |= set(range(k - len(S) + 1, k + 1))
    for k, ch in enumerate(A):
        x = ox + k * cw + 3
        if k < len(S):
            fill, st, tc = BLUE, BLUE, BG
        elif ch == "#":
            fill, st, tc = NODE2, AXIS, MUTED
        elif k in match:
            fill, st, tc = GREEN, GREEN, BG
        else:
            fill, st, tc = NODE, GRID, TEXT
        f.cell(x, y1, ch, w=cw - 6, h=40, fill=fill, stroke=st, tcolor=tc, size=17)
        on = k in hit
        f.cell(x, y2, pi[k], w=cw - 6, h=40, fill=YELLOW if on else NODE, stroke=YELLOW if on else GRID,
               tcolor=BG if on else TEXT, size=16)
        f.text(ox + k * cw + cw / 2, y1 - 10, str(k), size=12.5, anchor="middle", fill=MUTED)
    k = hit[0]
    f.text(ox + k * cw + cw / 2, y2 + 66, "↑ π = 3", size=15, anchor="middle", fill=YELLOW, weight=700)
    f.note(286, f"Вхождение заканчивается в позиции {k} склейки, то есть начинается в T с индекса {k - 2 * len(S)}.", size=14.5)
    f.note(310, "Разделитель # не даёт π стать больше |S| — совпадение не «перетечёт» через границу.", size=14.5, color=MUTED)
    return f.svg()


def trie():
    words = ["бор", "бот", "борд", "дом"]
    f = Fig("t3", 430, title="Бор для слов: бор, бот, борд, дом",
            sub="Общий префикс «бо» хранится один раз. Зелёные вершины — конец какого-то слова.")
    # узлы: префикс -> координаты
    P = {"": (330, 100), "б": (220, 170), "д": (470, 170), "бо": (220, 240), "до": (470, 240),
         "бор": (150, 310), "бот": (290, 310), "дом": (470, 310), "борд": (150, 380)}
    cnt = {p: sum(w.startswith(p) for w in words) for p in P}
    for p, (x, y) in P.items():
        if p:
            par = P[p[:-1]]
            f.edge(*par, x, y, r1=18, r2=18, color=EDGE, arrow=False)
            mx, my = (par[0] + x) / 2, (par[1] + y) / 2
            dx = -16 if x <= par[0] else 16
            if x == par[0]:
                dx = -16
            f.text(mx + dx, my + 6, p[-1], size=17, anchor="middle", fill=BLUE, weight=700)
    for p, (x, y) in P.items():
        term = p in words
        f.node(x, y, cnt[p], color=GREEN if term else (AXIS if not p else BLUE), r=18, size=14,
               fill=GREEN if term else NODE, tcolor=BG if term else TEXT)
        if term:
            f.text(x + (28 if p != "бор" else -28), y + 5, f"«{p}»", size=14.5, fill=GREEN, weight=700,
                   anchor="start" if p != "бор" else "end")
    f.text(330 - 30, 100 + 5, "корень", size=13.5, fill=MUTED, anchor="end")
    tx = 560
    f.text(tx, 120, "Буква — на ребре.", size=14, fill=TEXT2)
    f.text(tx, 150, "Число в вершине —", size=14, fill=TEXT2)
    f.text(tx, 170, "cnt: сколько слов", size=14, fill=TEXT2)
    f.text(tx, 190, "начинается с этого", size=14, fill=TEXT2)
    f.text(tx, 210, "префикса.", size=14, fill=TEXT2)
    f.text(tx, 250, "Поиск «бот»:", size=14, fill=TEXT2, weight=700)
    f.text(tx, 270, "б → о → т, вершина", size=14, fill=TEXT2)
    f.text(tx, 290, "зелёная — слово есть.", size=14, fill=TEXT2)
    return f.svg()


def binary_trie():
    nums = {3: "011", 2: "010", 7: "111"}
    x, xb = 4, "100"
    f = Fig("t4", 450, title="Бинарный бор: max(x XOR y) для x = 4 = 100₂",
            sub="Числа 3 = 011, 2 = 010, 7 = 111. Идём от старшего бита и стараемся взять бит, противоположный биту x.")
    # строим узлы
    P = {"": (300, 110)}
    xs = {"0": 180, "1": 420, "01": 180, "11": 420, "010": 120, "011": 240, "111": 420}
    ys = {1: 190, 2: 270, 3: 350}
    for b in nums.values():
        for k in range(1, 4):
            p = b[:k]
            P[p] = (xs[p], ys[k])
    best = ""
    for k in range(3):
        want = "1" if xb[k] == "0" else "0"
        best += want if (best + want) in P else xb[k]
    path = {best[:k] for k in range(4)}
    for p, (x_, y) in P.items():
        if p:
            par = P[p[:-1]]
            on = p in path
            f.edge(*par, x_, y, r1=17, r2=17, color=ORANGE if on else EDGE, sw=3.5 if on else 2, arrow=False)
            mx, my = (par[0] + x_) / 2, (par[1] + y) / 2
            f.text(mx + (-14 if x_ <= par[0] else 14), my + 5, p[-1], size=16, anchor="middle",
                   fill=ORANGE if on else BLUE, weight=700)
    for p, (x_, y) in P.items():
        on = p in path
        f.circle(x_, y, 17, fill=ORANGE if on else NODE, stroke=ORANGE if on else BLUE, sw=2.5)
        if len(p) == 3:
            val = int(p, 2)
            f.text(x_, y + 5, str(val), size=14, anchor="middle", weight=700, fill=BG if on else TEXT)
            f.text(x_, y + 38, p, size=13.5, anchor="middle", fill=MUTED)
    tx = 520
    for k in range(3):
        want = "1" if xb[k] == "0" else "0"
        got = best[k]
        ok = got == want
        y = 150 + k * 66
        f.text(tx, y, f"бит {2 - k}: у x {xb[k]}, хотим {want}", size=14.5, fill=TEXT2)
        f.text(tx, y + 22, "есть → идём" + f" в {got}" if ok else f"нет → идём в {got}", size=14.5,
               fill=GREEN if ok else RED, weight=700)
    f.note(420, f"Нашли y = {best}₂ = {int(best, 2)}:  4 XOR 3 = 100 XOR 011 = 111₂ = 7 — максимум.", size=15, color=ORANGE, weight=700)
    return f.svg()


FIGS = {
    1: (border_chain, "Если очередной кандидат не продолжается символом $S[i]$, переходим к бордеру этого бордера: $j \\leftarrow \\pi[j-1]$."),
    2: (kmp, "Склейка $S\\#T$: значение $\\pi = |S|$ отмечает конец вхождения шаблона в тексте."),
    3: (trie, "Слова с общим началом делят путь от корня; <code>cnt</code> в вершине — сколько слов начинаются с этого префикса."),
    4: (binary_trie, "Жадный спуск по битам от старшего: где можно, идём в бит, противоположный биту $x$, — так XOR получается максимальным."),
}
