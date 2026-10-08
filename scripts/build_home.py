#!/usr/bin/env python3
"""Собирает главную (index.html) и страницы параллелей (parallel-*/index.html).

Занятия берутся из самих лекций (заголовок, описание, длительность), оформление —
в assets/site.css. Блок «ask» (бот идей и плагин) и индекс разделов SECTIONS
для поиска переносятся из текущего index.html, поэтому scripts/paper-style.py,
который обновляет SECTIONS, продолжает работать. Формат литерала DATA
({ n: "Занятие 1", title: "...", href: "..." }) тоже оставлен прежним —
по нему paper-style.py строит порядок занятий.

Запуск из корня репозитория: python3 scripts/build_home.py
"""
import glob
import html
import json
import os
import re

BASE = 'https://vmaiorov-collab.github.io/conspectus/'
PARALLELS = [  # ключ, название, бейдж, плейлист
    ('a', 'Параллель A', 'A', 'https://www.youtube.com/playlist?list=PLPEbYG2GETx8'),
    ('ap', "Параллель A'", "A'", 'https://www.youtube.com/playlist?list=PLVEPlEFLCYes'),
    ('b', 'Параллель B', 'B', 'https://www.youtube.com/playlist?list=PLfU-HktHP470'),
    ('bp', "Параллель B'", "B'", 'https://www.youtube.com/playlist?list=PLP5aGLvQB07Y'),
    ('c', 'Параллель C', 'C', 'https://www.youtube.com/playlist?list=PLNeWOJRrsoEA'),
]
esc = lambda x: html.escape(x, quote=True)


def word(n):
    if n % 10 == 1 and n % 100 != 11:
        return f'{n} занятие'
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return f'{n} занятия'
    return f'{n} занятий'


def lessons_of(key):
    out = []
    for f in sorted(glob.glob(f'parallel-{key}/parallel-{key}-zan*.html')):
        s = open(f, encoding='utf-8').read()
        n = int(re.search(r'-zan(\d+)-', f).group(1))
        h1 = html.unescape(re.search(r'<h1>(.*?)</h1>', s, re.S).group(1))
        sub = re.search(r'<div class="sub">(.*?)</div>', s, re.S)
        sub = html.unescape(sub.group(1)).strip() if sub else ''
        sub = re.sub(r'^Яндекс Кружок · направление «[^»]*»\.\s*', '', sub)
        chips = [html.unescape(c) for c in re.findall(r'<span class="chip">([^<]*)</span>', s)]
        dur = next((c.replace('Длительность ', '') for c in chips if '≈' in c), '')
        out.append(dict(n=n, title=h1.split('—', 1)[-1].strip(), sub=sub, dur=dur,
                        href=f'parallel-{key}/{os.path.basename(f)}', file=os.path.basename(f)))
    return sorted(out, key=lambda x: x['n'])


old = open('index.html', encoding='utf-8').read()
ASK = re.search(r'<section class="ask">.*?</section>', old, re.S).group(0)
SECTIONS = re.search(r'/\*SECTIONS\*/const SECTIONS = (.*?);/\*/SECTIONS\*/', old, re.S).group(1)
LESSONS = {k: lessons_of(k) for k, *_ in PARALLELS}
TOTAL = sum(len(v) for v in LESSONS.values())

THEME_INIT = ('<script>(function(){try{var t=localStorage.getItem("conspectusTheme");'
              'document.documentElement.setAttribute("data-theme",t||"light")}catch(e){document.documentElement.setAttribute("data-theme","light")}})();</script>')
TRACK = ('<script data-goatcounter="https://vmaiorov.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>\n'
         '<script defer src=\'https://static.cloudflareinsights.com/beacon.min.js\' '
         'data-cf-beacon=\'{"token": "82e3760401a547558cc1d22198113255"}\'></script>')
TOGGLE = '<button type="button" id="theme-toggle" class="theme-toggle" aria-label="Переключить тему">тёмная тема</button>'
THEME_JS = '''(function(){var root=document.documentElement,btn=document.getElementById("theme-toggle");
function label(){btn.textContent=root.getAttribute("data-theme")==="dark"?"светлая тема":"тёмная тема"}label();
btn.addEventListener("click",function(){var next=root.getAttribute("data-theme")==="dark"?"light":"dark";root.setAttribute("data-theme",next);label();try{localStorage.setItem("conspectusTheme",next)}catch(e){}});})();'''
FOOT = ('<footer class="foot"><a href="https://yandex.ru/yaintern/olympiads/kruzhok">yandex.ru/yaintern/olympiads/kruzhok</a>'
        '<a href="https://t.me/conspectus_csbot" target="_blank" rel="noopener">идея или ошибка → бот</a>'
        '<a href="https://vmaiorov-collab.github.io/">все проекты</a>'
        '<a href="https://vmaiorov.goatcounter.com/" target="_blank" rel="noopener">статистика посещений</a></footer>')
ICON_PATH = lambda p: p  # префикс пути


def head(title, desc, url, pre, og_title=None):
    og = esc(og_title or title)
    return f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#fc3f1d">
<link rel="icon" type="image/png" href="{pre}favicon-v2.png">
<link rel="apple-touch-icon" href="{pre}apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Конспекты лекций">
<meta property="og:title" content="{og}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{BASE}og-image-v2.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="ru_RU">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{og}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{BASE}og-image-v2.png">
{THEME_INIT}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Onest:wght@400..800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{pre}assets/site.css">
{TRACK}
</head>
'''


# ── DATA в прежнем формате (его читает scripts/paper-style.py) ──
data_js = 'const DATA = [\n' + ',\n'.join(
    f'  {{ name: {json.dumps(name, ensure_ascii=False)}, badge: {json.dumps(badge, ensure_ascii=False)}, '
    f'url: {json.dumps(pl)}, lessons: [\n' + ',\n'.join(
        f'    {{ n: "Занятие {l["n"]}", title: {json.dumps(l["title"], ensure_ascii=False)}, href: "{l["href"]}" }}'
        for l in LESSONS[key]) + '\n  ]}'
    for key, name, badge, pl in PARALLELS) + '\n];'


ART = """<svg viewBox="0 0 600 520" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
<circle cx="506" cy="98" r="40" fill="none" stroke="#ee8cf0" stroke-width="26"/>
<circle cx="96" cy="86" r="30" fill="none" stroke="#a99bf5" stroke-width="20"/>
<circle cx="42" cy="440" r="44" fill="none" stroke="#ee8cf0" stroke-width="24"/>
<rect x="58" y="244" width="136" height="136" rx="10" fill="#6fe090"/>
<rect x="404" y="318" width="96" height="96" rx="8" fill="#6fe090"/>
<g stroke="#a99bf5" stroke-width="22" stroke-linecap="square"><path d="M156 112l54 54M210 112l-54 54"/><path d="M360 392l44 44M404 392l-44 44"/></g>
<path d="M298 52h38v38h38v38h-38v38h-38v-38h-38V90h38z" fill="#fff"/>
<polygon points="86,196 140,196 86,250" fill="#fff"/><polygon points="452,236 520,236 520,304" fill="#fff"/>
<g><rect x="230" y="318" width="260" height="70" rx="8" fill="#cdb437"/><rect x="262" y="262" width="228" height="66" rx="8" fill="#d9c24a"/>
<rect x="298" y="206" width="192" height="66" rx="8" fill="#e4d15f"/><rect x="334" y="150" width="156" height="66" rx="8" fill="#efdf7c"/>
<rect x="230" y="318" width="260" height="14" rx="6" fill="#b89f26"/></g>
<g fill="#000"><rect x="250" y="430" width="22" height="22"/><rect x="272" y="452" width="22" height="22"/><rect x="294" y="430" width="22" height="22"/></g>
</svg>"""

NAV = ('<header class="nav"><div style="display:flex;align-items:center;gap:4px"><a class="mark" href="{home}" aria-label="Конспекты лекций">К</a>'
       '<nav class="links"><a href="{up}">Параллели</a><a href="https://vmaiorov-collab.github.io/">Проекты</a></nav></div>'
       '<div class="navr">{toggle}<a class="pill-black" href="https://t.me/conspectus_csbot" target="_blank" rel="noopener">Написать в бот</a></div></header>')

SEARCH_ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">'
               '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>')

cards = ''
for key, name, badge, _pl in PARALLELS:
    ls = LESSONS[key]
    cards += (f'<a class="row" href="parallel-{key}/index.html"><span class="idx">{esc(badge)}</span>'
              f'<span class="rb"><b class="rn">{esc(name)}</b><span class="rt">{esc(" · ".join(l["title"] for l in ls))}</span></span>'
              f'<span class="rc">{word(len(ls))}<i>→</i></span></a>')
noscript = '<noscript><ul>' + ''.join(
    f'<li>{esc(name)} — ' + ', '.join(f'<a href="{l["href"]}">Занятие {l["n"]}. {esc(l["title"])}</a>' for l in LESSONS[key]) + '</li>'
    for key, name, _b, _p in PARALLELS) + '</ul></noscript>'

SEARCH_JS = r'''
const pick = document.getElementById("pick"), res = document.getElementById("res"), q = document.getElementById("q"), nores = document.getElementById("nores");
const esc = (x) => x.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
function mark(text, t) {
  const i = text.toLowerCase().indexOf(t);
  return i < 0 ? esc(text) : esc(text.slice(0, i)) + "<mark>" + esc(text.slice(i, i + t.length)) + "</mark>" + esc(text.slice(i + t.length));
}
// формулы $...$ в заголовках: KaTeX подгружается лениво, пока его нет (или нет сети) — читаемый текст
let katexState = 0; // 0 — не грузили, 1 — грузится, 2 — готов, -1 — не вышло
function loadKatex() {
  if (katexState !== 0) return;
  katexState = 1;
  const css = document.createElement("link");
  css.rel = "stylesheet";
  css.href = "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css";
  document.head.appendChild(css);
  const js = document.createElement("script");
  js.src = "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js";
  js.onload = () => { katexState = 2; q.dispatchEvent(new Event("input")); };
  js.onerror = () => { katexState = -1; };
  document.head.appendChild(js);
}
const texPlain = (m) => m.replace(/\\(sqrt)\s*/g, "√").replace(/\\(le|leq)\b/g, "≤").replace(/\\(ge|geq)\b/g, "≥")
  .replace(/\\cdot/g, "·").replace(/\\(?:text|mathrm|operatorname)\{([^}]*)\}/g, "$1").replace(/\\([a-zA-Z]+)/g, "$1").replace(/[{}]/g, "");
function renderTitle(title, t) {
  if (title.indexOf("$") < 0) return mark(title, t);
  loadKatex();
  let marked = false;
  return title.split(/(\$[^$]+\$)/).map((part) => {
    if (part.length > 2 && part[0] === "$" && part[part.length - 1] === "$") {
      const m = part.slice(1, -1);
      if (katexState === 2) { try { return katex.renderToString(m, { throwOnError: false }); } catch (e) {} }
      return esc(texPlain(m));
    }
    if (!marked && part.toLowerCase().includes(t)) { marked = true; return mark(part, t); }
    return esc(part);
  }).join("");
}
q.addEventListener("input", () => {
  const t = q.value.trim().toLowerCase();
  pick.hidden = !!t;
  res.hidden = !t;
  if (!t) { res.innerHTML = ""; nores.hidden = true; return; }
  let out = "", n = 0;
  DATA.forEach((p) => p.lessons.forEach((l) => {
    const found = t.length < 2 ? [] : (SECTIONS[l.href] || []).filter(([, title]) => title.toLowerCase().includes(t));
    if (!(p.name.toLowerCase().includes(t) || l.title.toLowerCase().includes(t) || found.length)) return;
    n++;
    const seen = new Set();
    const hits = found.filter(([id, title]) => !seen.has(title) && seen.add(title)).slice(0, 6)
      .map(([id, title]) => `<a href="${l.href}#${id}">${renderTitle(title, t)}</a>`).join("");
    out += `<div class="rl"><div class="rp">${p.name} · ${l.n}</div><a class="rt" href="${l.href}">${esc(l.title)}</a>${hits ? `<div class="rh">${hits}</div>` : ""}</div>`;
  }));
  res.innerHTML = out;
  nores.hidden = n > 0;
});
'''

index = head('Конспекты лекций — Олимпиадное программирование',
             'Подробные автономные конспекты лекций по олимпиадному программированию (Яндекс Кружок): ДП, графы, строки, сортировки, структуры данных. Читаются офлайн в браузере.',
             BASE, '', 'Конспекты лекций — Олимпиадное программирование') + f'''<body>
<div class="page">

<header class="bar"><a class="word" href="index.html">конспекты<i>/</i></a><nav><a href="#pick">параллели</a><a href="https://vmaiorov-collab.github.io/">проекты</a><a href="https://t.me/conspectus_csbot" target="_blank" rel="noopener">бот</a>{TOGGLE}</nav></header>

<section class="hero">
  <p class="kicker">Яндекс Кружок · олимпиадное программирование</p>
  <h1>Конспекты <span class="mk">лекций</span></h1>
  <p class="lead">Формулы, код и разборы задач. Чтобы найти одну идею, не нужно пересматривать четырёхчасовую запись.</p>
  <div class="cmd"><span class="pr">&gt;</span><input id="q" type="search" placeholder="найти тему: хэши, LCA, бор…" autocomplete="off" aria-label="Поиск по лекциям"><kbd>/</kbd></div>
</section>

<div class="strip"><div><b>{TOTAL}</b>занятий с формулами и кодом</div><div><b>{len(PARALLELS)}</b>параллелей разной сложности</div><div><b>1 файл</b>на лекцию, читается офлайн</div></div>

<div id="res" class="res" hidden></div>
<div class="nores" id="nores" hidden>Ничего не найдено.</div>

<section id="pick">
<h2 class="sec">Параллели</h2>
<nav class="rows">{cards}</nav>
</section>
{noscript}

{ASK}

{FOOT}

</div>
<script>
{data_js}

/*SECTIONS*/const SECTIONS = {SECTIONS};/*/SECTIONS*/
{SEARCH_JS}
{THEME_JS}
addEventListener("keydown", (e) => {{ if (e.key === "/" && document.activeElement !== q && !e.metaKey && !e.ctrlKey) {{ e.preventDefault(); q.focus(); }} }});
</script>
</body>
</html>
'''
open('index.html', 'w', encoding='utf-8').write(index)

# ── страницы параллелей ──
for i, (key, name, badge, playlist) in enumerate(PARALLELS):
    ls = LESSONS[key]
    desc = f'{name}: ' + ', '.join(l['title'] for l in ls) + '. Конспекты лекций Яндекс Кружка.'
    rows = ''.join(
        f'<a class="lr" href="{l["file"]}"><span class="ln">{l["n"]:02d}</span><span class="lb"><b>{esc(l["title"])}</b>'
        + (f'<span>{esc(l["sub"])}</span>' if l['sub'] else '') + '</span>'
        + (f'<span class="ld">{esc(l["dur"])}</span>' if l['dur'] else '<span></span>') + '</a>' for l in ls)
    pv = PARALLELS[i - 1] if i else None
    nx = PARALLELS[i + 1] if i < len(PARALLELS) - 1 else None
    prev = f'<a href="../parallel-{pv[0]}/index.html"><small>← предыдущая</small><b>{esc(pv[1])}</b></a>' if pv else '<a class="ph0"></a>'
    nxt = f'<a href="../parallel-{nx[0]}/index.html"><small>следующая →</small><b>{esc(nx[1])}</b></a>' if nx else ''
    page = head(f'{name} — Конспекты лекций', desc, f'{BASE}parallel-{key}/', '../') + f'''<body>
<div class="page">

<header class="bar"><a class="word" href="../index.html" data-up>← конспекты<i>/</i></a><nav><a href="../index.html#pick" data-up>параллели</a><a href="https://vmaiorov-collab.github.io/">проекты</a><a href="https://t.me/conspectus_csbot" target="_blank" rel="noopener">бот</a>{TOGGLE}</nav></header>

<section class="pp">
  <aside class="pside">
    <p class="kicker">Яндекс Кружок</p>
    <div class="bigl">{esc(badge)}</div>
    <h1>{esc(name)}</h1>
    <div class="pmeta"><span>{word(len(ls))}</span><a href="{playlist}" target="_blank" rel="noopener">плейлист на YouTube ↗</a></div>
  </aside>
  <div>
    <nav class="lrows">{rows}</nav>
    <nav class="pnav">{prev}{nxt}</nav>
  </div>
</section>

{FOOT}

</div>
<script>
{THEME_JS}
(function(){{var b=document.querySelector("[data-up]");if(!b)return;document.querySelectorAll("[data-up]").forEach(function(b){{b.addEventListener("click",function(e){{var home=new URL("../",location.href).href,r=document.referrer;if(history.length>1&&r&&r.indexOf(home)===0&&r.indexOf("/parallel-")<0){{e.preventDefault();history.back()}}}})}});}})();
</script>
</body>
</html>
'''
    open(f'parallel-{key}/index.html', 'w', encoding='utf-8').write(page)
print('ok:', TOTAL, 'занятий,', len(PARALLELS), 'параллелей')
