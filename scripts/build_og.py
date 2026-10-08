#!/usr/bin/env python3
"""Рисует картинки для превью ссылок (1200×630): og-image.png для главной и og-parallel-<ключ>.png для каждой параллели.

Данные берутся из index.html (DATA), рендер — через headless Chrome. Запуск из корня репозитория:
    python3 scripts/build_og.py
Chrome ищется в стандартном месте macOS или берётся из переменной CHROME. Шрифт Onest подгружается
из Google Fonts, поэтому нужен интернет.
"""
import html
import json
import os
import re
import subprocess
import tempfile

CHROME = os.environ.get('CHROME', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
PASTEL = {'a': '#b9e6c9', 'ap': '#ffd3b0', 'b': '#cfe3ff', 'bp': '#e4d6ff', 'c': '#d4f56a'}
URL = 'vmaiorov-collab.github.io/conspectus'
esc = html.escape

idx = open('index.html', encoding='utf-8').read()
data_js = re.search(r'const DATA = \[(.*?)\n\];', idx, re.S).group(1)
PAR = []
for m in re.finditer(r'\{ name: "([^"]+)", badge: "([^"]+)", url: "[^"]*", lessons: \[(.*?)\n  \]\}', data_js, re.S):
    titles = re.findall(r'title: "([^"]+)"', m.group(3))
    key = re.search(r'href: "parallel-(\w+)/', m.group(3)).group(1)
    PAR.append((key, m.group(1), m.group(2), titles))
TOTAL = sum(len(p[3]) for p in PAR)

BASE = '''<!doctype html><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Onest:wght@400..800&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box}html,body{margin:0}
body{width:1200px;height:630px;background:#fff;font-family:"Onest",Helvetica,Arial,sans-serif;color:#000;padding:28px}
.panel{position:relative;width:100%;height:100%;border-radius:44px;padding:52px 60px;overflow:hidden}
.chip{display:inline-block;padding:9px 20px;border-radius:12px;background:rgba(255,255,255,.75);font-size:25px;font-weight:500}
h1{margin:26px 0 0;font-weight:800;letter-spacing:-.045em;line-height:.98}
.foot{position:absolute;left:60px;right:60px;bottom:44px;display:flex;justify-content:space-between;align-items:baseline;font-size:26px}
.foot b{font-family:"JetBrains Mono",monospace;font-weight:500;font-size:24px}
.foot span{color:#6c6d69}
.hi{background:linear-gradient(transparent 62%,#d4f56a 62%,#d4f56a 94%,transparent 94%);padding:0 .05em}
</style>
'''


def home():
    circles = ''.join(
        f'<i style="background:{PASTEL[k]}">{esc(b)}</i>' for k, _n, b, _t in PAR)
    return BASE + f'''<style>
.panel{{background:#f3f4f1}}
h1{{font-size:118px;white-space:nowrap}}
.lead{{margin:28px 0 0;font-size:36px;line-height:1.35;color:#6c6d69;max-width:640px}}
.row{{position:absolute;right:60px;bottom:112px;display:flex;gap:14px}}
.row i{{display:flex;align-items:center;justify-content:center;width:92px;height:92px;border-radius:50%;font-style:normal;font-weight:800;font-size:38px}}
</style>
<div class="panel"><span class="chip">Яндекс Кружок · олимпиадное программирование</span>
<h1>Конспекты <span class="hi">лекций</span></h1>
<p class="lead">Формулы, код и разборы задач. Читаются офлайн.</p>
<div class="row">{circles}</div>
<div class="foot"><b>{URL}</b><span>{TOTAL} занятий · {len(PAR)} параллелей</span></div></div>'''


def parallel(key, name, badge, titles):
    items = ''.join(f'<li><em>{i + 1}</em>{esc(t)}</li>' for i, t in enumerate(titles))
    return BASE + f'''<style>
.panel{{background:{PASTEL[key]}}}
h1{{font-size:112px;white-space:nowrap}}
ul{{list-style:none;margin:32px 0 0;padding:0;display:grid;gap:12px;max-width:820px}}
li{{display:flex;gap:18px;align-items:center;font-size:38px;font-weight:600;letter-spacing:-.02em}}
li em{{display:flex;align-items:center;justify-content:center;flex:none;width:46px;height:46px;border-radius:12px;background:#000;color:#fff;font-style:normal;font-size:24px;font-weight:700}}
.big{{position:absolute;right:60px;top:60px;display:flex;align-items:center;justify-content:center;width:230px;height:230px;border-radius:50%;background:rgba(255,255,255,.6);font-weight:800;font-size:128px;letter-spacing:-.04em}}
</style>
<div class="panel"><span class="chip">Яндекс Кружок · конспекты лекций</span>
<h1>{esc(name)}</h1>
<ul>{items}</ul>
<div class="big">{esc(badge)}</div>
<div class="foot"><b>{URL}</b><span>{len(titles)} занятия</span></div></div>'''


def render(markup, out):
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(markup)
        path = f.name
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--virtual-time-budget=9000',
                    '--window-size=1200,630', f'--screenshot={out}', f'file://{path}'],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    os.unlink(path)
    print('готово:', out)


render(home(), 'og-image.png')
for key, name, badge, titles in PAR:
    render(parallel(key, name, badge, titles), f'og-parallel-{key}.png')
