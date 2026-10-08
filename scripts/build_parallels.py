#!/usr/bin/env python3
"""Собирает страницы параллелей parallel-*/index.html для conspectus.

Данные о занятиях берутся из самих лекций (заголовок, описание, длительность),
оформление (шапка, стили, тема) — из index.html. Запуск из корня репозитория:
    python3 scripts/build_parallels.py
"""
import glob
import html
import os
import re

BASE = 'https://vmaiorov-collab.github.io/conspectus/'
PARALLELS = [  # ключ, название, бейдж, цвет, плейлист
    ('a', 'Параллель A', 'A', '#2f5bd3', 'https://www.youtube.com/playlist?list=PLPEbYG2GETx8'),
    ('ap', "Параллель A'", "A'", '#7a4bc4', 'https://www.youtube.com/playlist?list=PLVEPlEFLCYes'),
    ('b', 'Параллель B', 'B', '#1f8a5b', 'https://www.youtube.com/playlist?list=PLfU-HktHP470'),
    ('bp', "Параллель B'", "B'", '#b7791f', 'https://www.youtube.com/playlist?list=PLP5aGLvQB07Y'),
    ('c', 'Параллель C', 'C', '#c2412d', 'https://www.youtube.com/playlist?list=PLNeWOJRrsoEA'),
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
        title = h1.split('—', 1)[-1].strip()
        sub = re.search(r'<div class="sub">(.*?)</div>', s, re.S)
        sub = html.unescape(sub.group(1)).strip() if sub else ''
        sub = re.sub(r'^Яндекс Кружок · направление «[^»]*»\.\s*', '', sub)
        chips = [html.unescape(c) for c in re.findall(r'<span class="chip">([^<]*)</span>', s)]
        dur = next((c.replace('Длительность ', '') for c in chips if '≈' in c), '')
        out.append(dict(n=n, title=title, sub=sub, dur=dur, href=os.path.basename(f)))
    return sorted(out, key=lambda x: x['n'])


idx = open('index.html', encoding='utf-8').read()
head_tpl = idx[:idx.index('</head>')]
# относительные пути к иконкам; заголовок и og-теги подставим свои
head_tpl = head_tpl.replace('href="favicon-v2.png"', 'href="../favicon-v2.png"').replace('href="apple-touch-icon.png"', 'href="../apple-touch-icon.png"')
head_tpl = re.sub(r'<title>.*?</title>', '<title>@@T@@</title>', head_tpl, flags=re.S)
head_tpl = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="@@D@@">', head_tpl)
head_tpl = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="@@T@@">', head_tpl)
head_tpl = re.sub(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="@@D@@">', head_tpl)
head_tpl = re.sub(r'<meta name="twitter:title" content="[^"]*">', '<meta name="twitter:title" content="@@T@@">', head_tpl)
head_tpl = re.sub(r'<meta name="twitter:description" content="[^"]*">', '<meta name="twitter:description" content="@@D@@">', head_tpl)
head_tpl = re.sub(r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="@@U@@">', head_tpl)

CSS = '''<style>
.ptitle{display:flex;align-items:center;gap:14px;margin:6px 0 4px}
.pbadge{font-family:var(--mono);font-weight:800;font-size:1.25rem;color:var(--ink);background:none;border:1.5px solid var(--rule-hard,var(--line));padding:5px 11px;border-radius:10px;line-height:1.1}
.plist{display:grid;gap:12px;margin:26px 0 0}
.row{display:block;padding:18px 20px;border:1px solid var(--line);border-radius:14px;background:var(--paper,var(--bg));color:var(--ink)!important;text-decoration:none!important;transition:border-color .15s,transform .15s}
.row:hover{border-color:var(--ink);transform:translateY(-2px)}
.row .rn{font-family:var(--mono);font-size:.74rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.row .rt{display:block;font-family:var(--serif);font-weight:700;font-size:1.25rem;line-height:1.25;margin:4px 0 6px}
.row .rs{display:block;color:var(--muted);font-size:.95rem;line-height:1.55}
.row .rd{display:block;margin-top:8px;font-family:var(--mono);font-size:.74rem;color:var(--muted)}
.pbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-top:16px;font-family:var(--mono);font-size:.8rem;color:var(--muted)}
.pbar a{color:var(--accent)}
.pnav{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:44px}
.pnav a{display:flex;flex-direction:column;gap:2px;padding:14px 16px;border:1px solid var(--line);border-radius:12px;color:var(--ink)!important;text-decoration:none!important}
.pnav a:hover{border-color:var(--accent)}.pnav small{font-family:var(--mono);font-size:.72rem;color:var(--muted)}
.pnav a:last-child:nth-child(2){text-align:right}.pnav .ph0{visibility:hidden}
.pfoot{margin-top:48px;padding-top:18px;border-top:1px solid var(--line);display:flex;gap:8px 24px;justify-content:space-between;flex-wrap:wrap;font-family:var(--mono);font-size:.78rem}
.pfoot a{color:var(--muted)}.pfoot a:hover{color:var(--ink)}
.top .sitelink[data-up]{margin-right:0}
</style>
'''
THEME_JS = '''<script>(function(){var root=document.documentElement,btn=document.getElementById("theme-toggle");
function label(){btn.textContent=root.getAttribute("data-theme")==="dark"?"светлая тема":"тёмная тема"}label();
btn.addEventListener("click",function(){var next=root.getAttribute("data-theme")==="dark"?"light":"dark";root.classList.add("theme-anim");setTimeout(function(){root.classList.remove("theme-anim")},350);root.setAttribute("data-theme",next);label();try{localStorage.setItem("conspectusTheme",next)}catch(e){}});
var b=document.querySelector("[data-up]");
if(b)b.addEventListener("click",function(e){var home=new URL("../",location.href).href,r=document.referrer;if(history.length>1&&r&&r.indexOf(home)===0&&r.indexOf("/parallel-")<0){e.preventDefault();history.back()}});
})();</script>
<script data-goatcounter="https://vmaiorov.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
'''

for i, (key, name, badge, color, playlist) in enumerate(PARALLELS):
    ls = lessons_of(key)
    desc = f'{name}: ' + ', '.join(l['title'] for l in ls) + '. Конспекты лекций Яндекс Кружка.'
    rows = ''.join(
        f'<a class="row" href="{l["href"]}"><span class="rn">Занятие {l["n"]}</span><span class="rt">{esc(l["title"])}</span>'
        + (f'<span class="rs">{esc(l["sub"])}</span>' if l['sub'] else '')
        + (f'<span class="rd">{esc(l["dur"])}</span>' if l['dur'] else '') + '</a>' for l in ls)
    pv, nx = PARALLELS[i - 1] if i else None, PARALLELS[i + 1] if i < len(PARALLELS) - 1 else None
    prev = f'<a href="../parallel-{pv[0]}/index.html"><small>← предыдущая</small><b>{esc(pv[1])}</b></a>' if pv else '<a class="ph0"></a>'
    nxt = f'<a href="../parallel-{nx[0]}/index.html"><small>следующая →</small><b>{esc(nx[1])}</b></a>' if nx else ''
    head = (head_tpl.replace('@@T@@', esc(f'{name} — Конспекты лекций')).replace('@@D@@', esc(desc))
            .replace('@@U@@', f'{BASE}parallel-{key}/'))
    page = f'''{head}
{CSS}</head>
<body>
<div class="wrap">

<div class="top"><a class="sitelink" data-up href="../index.html">← Все параллели</a>
  <span>conspectus</span>
  <span><button type="button" id="theme-toggle" class="theme-toggle">тёмная тема</button></span>
</div>

<section class="intro">
  <p class="kicker">Яндекс Кружок · олимпиадное программирование</p>
  <div class="ptitle"><span class="pbadge">{esc(badge)}</span><h1 style="margin:0">{esc(name)}</h1></div>
  <div class="pbar"><span>{word(len(ls))}</span><span>·</span><a href="{playlist}" target="_blank" rel="noopener">плейлист на YouTube</a></div>
</section>

<div class="plist">{rows}</div>

<nav class="pnav">{prev}{nxt}</nav>

<div class="pfoot"><a href="https://yandex.ru/yaintern/olympiads/kruzhok">yandex.ru/yaintern/olympiads/kruzhok</a>
<a href="https://t.me/conspectus_csbot" target="_blank" rel="noopener">идея или ошибка → бот</a>
<a href="https://vmaiorov-collab.github.io/">все проекты</a></div>

</div>
{THEME_JS}</body>
</html>
'''
    open(f'parallel-{key}/index.html', 'w', encoding='utf-8').write(page)
    print(key, word(len(ls)))
