from kit import *

NOTE = "parallel-c/parallel-c-zan1-vvodnaya.html"


def week_cycle():
    f = Fig("v1", 380, title="Как устроена неделя: тема → контест → разбор через неделю",
            sub="Каждую субботу: разбор прошлого контеста, лекция по новой теме, выдача контеста, дорешка.")
    cols = [(40, 1), (280, 2), (520, 3)]
    cw = 200
    for x, n in cols:
        f.text(x + cw / 2, 106, f"суббота {n}", size=15, anchor="middle", fill=MUTED, weight=700)
        rows = [
            (f"разбор контеста {n - 1}" if n > 1 else "—", GREEN if n > 1 else NODE2, BG if n > 1 else MUTED),
            (f"лекция: тема {n}", BLUE, BG),
            (f"выдан контест {n}", ORANGE, BG),
            ("дорешка, вопросы", NODE, TEXT2),
        ]
        for i, (t, c, tc) in enumerate(rows):
            y = 122 + i * 52
            f.rect(x, y, cw, 40, fill=c, stroke=c if c not in (NODE, NODE2) else GRID, rx=8)
            f.text(x + cw / 2, y + 26, t, size=14.5, anchor="middle", fill=tc, weight=700 if c not in (NODE, NODE2) else None)
    for (x, n), (x2, _n2) in zip(cols, cols[1:]):
        f.path(f"M{x + cw},{122 + 2 * 52 + 20} C{x + cw + 30},{122 + 2 * 52 + 20} {x2 - 30},{122 + 20} {x2},{122 + 20}",
               stroke=ORANGE, sw=2.5, arrow=True, dash="6 4")
    f.note(348, "Посещаемость не учитывается. Контест можно дорешать и после разбора — на те же баллы.", size=14.5, color=TEXT2)
    return f.svg()


def grade():
    f = Fig("v2", 330, title="Оценка за семестр = дедлайны + зачёт + бонусы",
            sub="Дедлайны — до 4 баллов (по одному за сданный), зачёт — нормируется в 0–4, бонусы сверху.")
    ox, y, c = 40, 130, 62

    def block(x, n, fill_n, color, label, sub):
        for k in range(n):
            on = k < fill_n
            f.rect(x + k * c + 2, y, c - 4, 48, fill=color if on else NODE2, stroke=color if on else GRID, rx=6,
                   dash=None if on else "4 4")
            if on:
                f.text(x + k * c + c / 2, y + 31, "1", size=16, anchor="middle", fill=BG, weight=700)
        f.text(x + n * c / 2, y - 12, label, size=15, anchor="middle", fill=color, weight=700)
        f.text(x + n * c / 2, y + 74, sub, size=14, anchor="middle", fill=MUTED)

    block(ox, 4, 3, BLUE, "дедлайны", "сдано 3 из 4 → 3")
    f.text(ox + 4 * c + 16, y + 32, "+", size=24, anchor="middle", fill=MUTED)
    block(ox + 4 * c + 32, 4, 2, GREEN, "зачёт", "5 из 10 задач → 2")
    f.text(ox + 8 * c + 48, y + 32, "+", size=24, anchor="middle", fill=MUTED)
    block(ox + 8 * c + 64, 1, 1, ORANGE, "бонус", "олимпиада, семинар")
    f.text(32, 268, "= 6 баллов в примере из лекции (из 8 без бонусов)", size=17, fill=TEXT, weight=700)
    f.text(32, 294, "По итоговой оценке решают про следующий семестр, автопроход и мерч.", size=14.5, fill=MUTED)
    return f.svg()


def vsosh():
    f = Fig("v3", 370, title="ВсОШ по информатике: четыре этапа",
            sub="Сроки ориентировочные. Региональный и заключительный — два тура по 5 часов и 4 задачи.")
    stages = [("Школьный", "сентябрь–октябрь", "онлайн, Сириус", BLUE),
              ("Муниципальный", "начало декабря", "в школе / на площадке", GREEN),
              ("Региональный", "январь–февраль", "2 тура, Ejudge", ORANGE),
              ("Заключительный", "март–апрель", "2 тура", RED)]
    w, gap, ox, y = 160, 24, 40, 122
    for i, (name, when, fmt, c) in enumerate(stages):
        x = ox + i * (w + gap)
        f.rect(x, y, w, 96, fill=c, op=0.18, stroke=c, sw=2, rx=10)
        f.text(x + w / 2, y + 28, name, size=15.5, anchor="middle", fill=c, weight=700)
        f.text(x + w / 2, y + 54, when, size=14, anchor="middle", fill=TEXT)
        f.text(x + w / 2, y + 76, fmt, size=13.5, anchor="middle", fill=MUTED)
        if i:
            f.line(x - gap + 2, y + 48, x - 4, y + 48, stroke=AXIS, sw=2, arrow=True)
    # пометка про классы
    x2 = ox + 1 * (w + gap) + w
    f.path(f"M{ox},{y + 120} H{x2}", stroke=YELLOW, sw=3)
    f.text(ox, y + 146, "за свой 7–8 класс — только до муниципального", size=14.5, fill=YELLOW, weight=700)
    f.path(f"M{ox},{y + 178} H{ox + 4 * w + 3 * gap}", stroke=GREEN, sw=3)
    f.text(ox, y + 204, "за 9 класс и старше — можно пройти до заключительного", size=14.5, fill=GREEN, weight=700)
    f.text(ox + 2 * (w + gap), y + 236, "с регионального этапа выбирается профиль", size=13.5, fill=MUTED)
    return f.svg()


INSERTS = [
    ("intro-week", "Дорешка", week_cycle,
     "Контест по теме недели разбирают в следующую субботу; дорешивать можно и после разбора."),
    ("intro-grade", "3 + 2 + 1 = 6", grade,
     "Пример из лекции: три дедлайна, зачёт на 2 балла и один бонус — итого 6."),
    ("intro-vsosh", "конец марта – апрель", vsosh,
     "Этапы ВсОШ по информатике. Чтобы пройти дальше муниципального, школьнику 7–8 класса нужно писать за 9-й."),
]
