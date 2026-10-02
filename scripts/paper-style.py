#!/usr/bin/env python3
"""Приводит конспекты к оформлению главной страницы («бумажный» стиль).

Добавляет в конец <head> блок <style id="paper"> и переносит переключатель темы
в верхнюю строку рядом со ссылкой «← Все конспекты». Скрипт идемпотентен:
повторный запуск заменяет блок стилей на актуальный.

    python3 scripts/paper-style.py            # все конспекты
    python3 scripts/paper-style.py file.html  # отдельные файлы
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEARCH = {}

CSS = r"""
@view-transition{navigation:auto}
::view-transition-old(root),::view-transition-new(root){animation-duration:.22s}
html[data-theme]{
  --bg:#f7f5f0; --card:#fffdf8; --ink:#1c1b19; --muted:#6f6a61; --faint:#a19b90;
  --accent:#1f4fd1; --accent-soft:#eef0f6; --line:#e3ded3;
  --tag:#ece7dc; --tag-ink:#3a362f; --warn:#faf1e1; --warn-ink:#94560c; --green:#ebf3ea; --green-ink:#2a6038;
  --code-bg:#1d1c1a; --code-ink:#ebe7df;
  --shadow-sm:none; --shadow-md:none; --shadow-lg:none;
  --serif:"PT Serif",Georgia,"Times New Roman",serif;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --mono:ui-monospace,"SF Mono","PT Mono",Menlo,Consolas,monospace;
  scroll-behavior:smooth;
}
html[data-theme="dark"]{
  --bg:#141413; --card:#1b1b19; --ink:#e9e6df; --muted:#a29d93; --faint:#6f6b64;
  --accent:#8fb0ff; --accent-soft:#1c1f27; --line:#2e2d2a;
  --tag:#26251f; --tag-ink:#d9d4c9; --warn:#272116; --warn-ink:#e3b46a; --green:#17221a; --green-ink:#93cfa2;
  --code-bg:#0e0e0d; --code-ink:#ebe7df;
  color-scheme:dark;
}
html[data-theme] body{background:var(--bg); color:var(--ink); font-family:var(--sans); font-size:16px; line-height:1.7; -webkit-font-smoothing:antialiased}
html[data-theme] .wrap{max-width:820px; padding:28px 24px 80px}

/* верхняя строка */
html[data-theme] .top{display:flex; justify-content:space-between; align-items:center; gap:12px; font-family:var(--mono); font-size:.8rem}
html[data-theme] .back{display:inline; margin:0; padding:0; border:0; background:none; color:var(--muted); font:inherit}
html[data-theme] .back:hover{color:var(--ink); text-decoration:none}
html[data-theme] .theme-toggle{position:static; width:auto; height:auto; font:inherit; font-size:.8rem; color:var(--muted); background:none; border:1px solid var(--line); border-radius:6px; padding:4px 10px; box-shadow:none; cursor:pointer; transform:none}
html[data-theme] .theme-toggle:hover{color:var(--ink); border-color:var(--muted); transform:none}

/* шапка */
html[data-theme] header.hero{background:none; color:var(--ink); border-radius:0; box-shadow:none; padding:52px 0 26px; margin:0 0 8px; border-bottom:1px solid var(--line); overflow:visible}
html[data-theme] header.hero::after{display:none}
html[data-theme] header.hero h1{font-family:var(--serif); font-weight:700; font-size:clamp(1.9rem,5vw,2.6rem); line-height:1.12; letter-spacing:-.01em; margin:0 0 14px}
html[data-theme] header.hero .sub{font-family:var(--serif); font-size:1.12rem; line-height:1.55; opacity:1; max-width:38em}
html[data-theme] header.hero .meta{gap:0; margin-top:16px}
html[data-theme] .chip{background:none; backdrop-filter:none; border:0; border-radius:0; padding:0; font-family:var(--mono); font-size:.78rem; color:var(--muted)}
html[data-theme] .chip + .chip::before{content:"·"; margin:0 .7em; color:var(--faint)}

/* оглавление */
html[data-theme] .toc{background:none; border:0; border-radius:0; box-shadow:none; padding:20px 0 24px; margin:0 0 12px; border-bottom:1px solid var(--line)}
html[data-theme] .toc h2{font-family:var(--mono); font-size:.78rem; font-weight:500; color:var(--muted); letter-spacing:.04em; text-transform:uppercase; margin:0 0 6px; padding:0; border:0}
html[data-theme] .toc ol{columns:2 280px; column-gap:32px; padding-left:1.5em; margin:0}
html[data-theme] .toc li{font-family:var(--serif); break-inside:avoid; margin:0 0 .4em; color:var(--muted)}
html[data-theme] .toc a{color:var(--ink)}
html[data-theme] .toc a:hover{color:var(--accent); text-decoration:underline; text-underline-offset:3px}

/* текст */
html[data-theme] h2{font-family:var(--serif); font-size:1.7rem; font-weight:700; line-height:1.25; letter-spacing:-.005em; margin:2.4em 0 .6em; padding:0; border:0; scroll-margin-top:20px}
html[data-theme] h3{font-family:var(--serif); font-size:1.25rem; font-weight:700; color:var(--ink); margin:1.8em 0 .5em; scroll-margin-top:20px}
html[data-theme] .wrap > p, html[data-theme] .wrap > ul, html[data-theme] .wrap > ol, html[data-theme] .card p,
html[data-theme] .card li{font-family:var(--serif); font-size:1.08rem; line-height:1.68}
html[data-theme] .note, html[data-theme] .warn, html[data-theme] .good{font-family:var(--serif); font-size:1.04rem}
html[data-theme] a{color:var(--accent)}
html[data-theme] a:hover{text-decoration:underline; text-underline-offset:3px}
html[data-theme] a.ts{display:inline-block; vertical-align:.2em; margin:0 0 0 .5em; padding:2px 7px; border-radius:4px; background:var(--tag); color:var(--tag-ink); font-family:var(--mono); font-size:.72rem; font-weight:500; letter-spacing:0; transition:background-color .15s, color .15s}
html[data-theme] a.ts::before{content:"▶\00a0"; font-size:.85em}
html[data-theme] a.ts:hover{background:var(--ink); color:var(--bg); text-decoration:none; filter:none; transform:none}
html[data-theme] p > a.ts:first-child{margin:0 .4em 0 0; vertical-align:.1em}

/* блоки */
html[data-theme] .card{background:var(--card); border:1px solid var(--line); border-radius:6px; box-shadow:none; transform:none}
html[data-theme] .card:hover{transform:none; box-shadow:none; border-color:var(--line)}
html[data-theme] .note, html[data-theme] .warn, html[data-theme] .good{border-radius:0; border-left-width:2px; padding:12px 18px}
html[data-theme] .note{border-left-color:var(--accent); background:var(--accent-soft)}
html[data-theme] .warn{border-left-color:var(--warn-ink); background:var(--warn)}
html[data-theme] .good{border-left-color:var(--green-ink); background:var(--green)}
html[data-theme] .note .lbl, html[data-theme] .warn .lbl, html[data-theme] .good .lbl{font-family:var(--mono); font-size:.74rem; font-weight:600; letter-spacing:.04em; text-transform:uppercase}
html[data-theme] table{background:none; border-radius:0; box-shadow:none; font-size:.92rem}
html[data-theme] th, html[data-theme] td{border:0; border-bottom:1px solid var(--line); padding:9px 12px}
html[data-theme] th{background:none; color:var(--muted); font-weight:600; font-size:.82rem; border-bottom:1px solid var(--ink)}
html[data-theme] tr:nth-child(even) td{background:none}
html[data-theme] code{background:var(--tag); color:var(--ink); border-radius:3px; font-family:var(--mono)}
html[data-theme] pre{background:var(--code-bg); color:var(--code-ink); border-radius:6px; box-shadow:none; font-family:var(--mono)}
html[data-theme] pre code{background:none; color:inherit}
html[data-theme] .formula, html[data-theme] .ascii{background:var(--card); border:1px solid var(--line); border-radius:6px}
html[data-theme] .viz svg{border-radius:6px; box-shadow:none}
html[data-theme] .viz figcaption, html[data-theme] .algocap{font-size:.85rem; color:var(--muted)}
html[data-theme] .algo{border-radius:6px; box-shadow:none}
html[data-theme] .timeline{border-left:1px solid var(--line)}
html[data-theme] .timeline .step::before{width:9px; height:9px; left:-29px; top:8px; border:0; background:var(--ink)}

html[data-theme] footer{font-size:.82rem; color:var(--muted); border-top:1px solid var(--line); margin-top:56px; padding-top:16px}
html[data-theme] .toplink{background:var(--ink); color:var(--bg); border:0; border-radius:6px; box-shadow:none; padding:8px 14px; font-family:var(--sans); font-size:.82rem; cursor:pointer; transform:translateY(8px); transition:opacity .2s, transform .2s}
html[data-theme] .toplink.show{transform:none}

/* схемы: палитра 3B1B → цвета темы (CSS перекрывает атрибуты fill/stroke) */
html[data-theme]{
  --f-bg:var(--card); --f-node:#f1ece2; --f-node2:#ebe5d9; --f-node3:#dde7ef; --f-edge:#c9c1b2; --f-axis:#8f887c;
  --f-text:var(--ink); --f-text2:#4a463e; --f-muted:var(--muted); --f-on:#1c1b19;
  --f-blue:#1b7aa0; --f-blue-bg:#a8d4e6; --f-green:#3b8530; --f-green-bg:#bfdfae;
  --f-orange:#c0610a; --f-orange-bg:#f1bf88; --f-yellow:#a07f00; --f-yellow-bg:#ecd568;
  --f-red:#bf3a2b; --f-red-bg:#ecb0a6; --f-purple:#7a4cc6; --f-purple-bg:#d0bdf0;
}
html[data-theme="dark"]{
  --f-bg:var(--card); --f-node:#262521; --f-node2:#22211e; --f-node3:#23384d; --f-edge:#46433d; --f-axis:#8a857b;
  --f-text:var(--ink); --f-text2:#cfcac0; --f-muted:var(--muted); --f-on:#141413;
  --f-blue:#58c4dd; --f-blue-bg:#58c4dd; --f-green:#83c167; --f-green-bg:#83c167;
  --f-orange:#ff8c1a; --f-orange-bg:#ff8c1a; --f-yellow:#f2e04a; --f-yellow-bg:#f2e04a;
  --f-red:#fc6255; --f-red-bg:#fc6255; --f-purple:#c78bff; --f-purple-bg:#c78bff;
}
html[data-theme] svg :not(text)[fill="#141A24"]{fill:var(--f-bg)}
html[data-theme] svg text[fill="#141A24"]{fill:var(--f-on)}
html[data-theme] svg [stroke="#141A24"]{stroke:var(--f-bg)}
html[data-theme] svg :not(text)[fill="#141a24"]{fill:var(--f-bg)}
html[data-theme] svg text[fill="#141a24"]{fill:var(--f-on)}
html[data-theme] svg [stroke="#141a24"]{stroke:var(--f-bg)}
html[data-theme] svg :not(text)[fill="#1E2836"]{fill:var(--f-node)}
html[data-theme] svg text[fill="#1E2836"]{fill:var(--f-text)}
html[data-theme] svg [stroke="#1E2836"]{stroke:var(--f-node)}
html[data-theme] svg :not(text)[fill="#1e2836"]{fill:var(--f-node)}
html[data-theme] svg text[fill="#1e2836"]{fill:var(--f-text)}
html[data-theme] svg [stroke="#1e2836"]{stroke:var(--f-node)}
html[data-theme] svg :not(text)[fill="#151F30"]{fill:var(--f-node2)}
html[data-theme] svg text[fill="#151F30"]{fill:var(--f-text)}
html[data-theme] svg [stroke="#151F30"]{stroke:var(--f-node2)}
html[data-theme] svg :not(text)[fill="#151f30"]{fill:var(--f-node2)}
html[data-theme] svg text[fill="#151f30"]{fill:var(--f-text)}
html[data-theme] svg [stroke="#151f30"]{stroke:var(--f-node2)}
html[data-theme] svg :not(text)[fill="#24405C"]{fill:var(--f-node3)}
html[data-theme] svg text[fill="#24405C"]{fill:var(--f-text)}
html[data-theme] svg [stroke="#24405C"]{stroke:var(--f-node3)}
html[data-theme] svg :not(text)[fill="#24405c"]{fill:var(--f-node3)}
html[data-theme] svg text[fill="#24405c"]{fill:var(--f-text)}
html[data-theme] svg [stroke="#24405c"]{stroke:var(--f-node3)}
html[data-theme] svg :not(text)[fill="#DFE7F1"]{fill:var(--f-text)}
html[data-theme] svg text[fill="#DFE7F1"]{fill:var(--f-text)}
html[data-theme] svg [stroke="#DFE7F1"]{stroke:var(--f-text)}
html[data-theme] svg :not(text)[fill="#dfe7f1"]{fill:var(--f-text)}
html[data-theme] svg text[fill="#dfe7f1"]{fill:var(--f-text)}
html[data-theme] svg [stroke="#dfe7f1"]{stroke:var(--f-text)}
html[data-theme] svg :not(text)[fill="#C2CDDE"]{fill:var(--f-text2)}
html[data-theme] svg text[fill="#C2CDDE"]{fill:var(--f-text2)}
html[data-theme] svg [stroke="#C2CDDE"]{stroke:var(--f-text2)}
html[data-theme] svg :not(text)[fill="#c2cdde"]{fill:var(--f-text2)}
html[data-theme] svg text[fill="#c2cdde"]{fill:var(--f-text2)}
html[data-theme] svg [stroke="#c2cdde"]{stroke:var(--f-text2)}
html[data-theme] svg :not(text)[fill="#9AA4B2"]{fill:var(--f-muted)}
html[data-theme] svg text[fill="#9AA4B2"]{fill:var(--f-muted)}
html[data-theme] svg [stroke="#9AA4B2"]{stroke:var(--f-axis)}
html[data-theme] svg :not(text)[fill="#9aa4b2"]{fill:var(--f-muted)}
html[data-theme] svg text[fill="#9aa4b2"]{fill:var(--f-muted)}
html[data-theme] svg [stroke="#9aa4b2"]{stroke:var(--f-axis)}
html[data-theme] svg :not(text)[fill="#7C8AA0"]{fill:var(--f-axis)}
html[data-theme] svg text[fill="#7C8AA0"]{fill:var(--f-muted)}
html[data-theme] svg [stroke="#7C8AA0"]{stroke:var(--f-axis)}
html[data-theme] svg :not(text)[fill="#7c8aa0"]{fill:var(--f-axis)}
html[data-theme] svg text[fill="#7c8aa0"]{fill:var(--f-muted)}
html[data-theme] svg [stroke="#7c8aa0"]{stroke:var(--f-axis)}
html[data-theme] svg :not(text)[fill="#33415A"]{fill:var(--f-edge)}
html[data-theme] svg text[fill="#33415A"]{fill:var(--f-muted)}
html[data-theme] svg [stroke="#33415A"]{stroke:var(--f-edge)}
html[data-theme] svg :not(text)[fill="#33415a"]{fill:var(--f-edge)}
html[data-theme] svg text[fill="#33415a"]{fill:var(--f-muted)}
html[data-theme] svg [stroke="#33415a"]{stroke:var(--f-edge)}
html[data-theme] svg :not(text)[fill="#3B4A63"]{fill:var(--f-edge)}
html[data-theme] svg text[fill="#3B4A63"]{fill:var(--f-muted)}
html[data-theme] svg [stroke="#3B4A63"]{stroke:var(--f-edge)}
html[data-theme] svg :not(text)[fill="#3b4a63"]{fill:var(--f-edge)}
html[data-theme] svg text[fill="#3b4a63"]{fill:var(--f-muted)}
html[data-theme] svg [stroke="#3b4a63"]{stroke:var(--f-edge)}
html[data-theme] svg :not(text)[fill="#58C4DD"]{fill:var(--f-blue-bg)}
html[data-theme] svg text[fill="#58C4DD"]{fill:var(--f-blue)}
html[data-theme] svg [stroke="#58C4DD"]{stroke:var(--f-blue)}
html[data-theme] svg :not(text)[fill="#58c4dd"]{fill:var(--f-blue-bg)}
html[data-theme] svg text[fill="#58c4dd"]{fill:var(--f-blue)}
html[data-theme] svg [stroke="#58c4dd"]{stroke:var(--f-blue)}
html[data-theme] svg :not(text)[fill="#83C167"]{fill:var(--f-green-bg)}
html[data-theme] svg text[fill="#83C167"]{fill:var(--f-green)}
html[data-theme] svg [stroke="#83C167"]{stroke:var(--f-green)}
html[data-theme] svg :not(text)[fill="#83c167"]{fill:var(--f-green-bg)}
html[data-theme] svg text[fill="#83c167"]{fill:var(--f-green)}
html[data-theme] svg [stroke="#83c167"]{stroke:var(--f-green)}
html[data-theme] svg :not(text)[fill="#FF8C1A"]{fill:var(--f-orange-bg)}
html[data-theme] svg text[fill="#FF8C1A"]{fill:var(--f-orange)}
html[data-theme] svg [stroke="#FF8C1A"]{stroke:var(--f-orange)}
html[data-theme] svg :not(text)[fill="#ff8c1a"]{fill:var(--f-orange-bg)}
html[data-theme] svg text[fill="#ff8c1a"]{fill:var(--f-orange)}
html[data-theme] svg [stroke="#ff8c1a"]{stroke:var(--f-orange)}
html[data-theme] svg :not(text)[fill="#FFFF00"]{fill:var(--f-yellow-bg)}
html[data-theme] svg text[fill="#FFFF00"]{fill:var(--f-yellow)}
html[data-theme] svg [stroke="#FFFF00"]{stroke:var(--f-yellow)}
html[data-theme] svg :not(text)[fill="#ffff00"]{fill:var(--f-yellow-bg)}
html[data-theme] svg text[fill="#ffff00"]{fill:var(--f-yellow)}
html[data-theme] svg [stroke="#ffff00"]{stroke:var(--f-yellow)}
html[data-theme] svg :not(text)[fill="#FC6255"]{fill:var(--f-red-bg)}
html[data-theme] svg text[fill="#FC6255"]{fill:var(--f-red)}
html[data-theme] svg [stroke="#FC6255"]{stroke:var(--f-red)}
html[data-theme] svg :not(text)[fill="#fc6255"]{fill:var(--f-red-bg)}
html[data-theme] svg text[fill="#fc6255"]{fill:var(--f-red)}
html[data-theme] svg [stroke="#fc6255"]{stroke:var(--f-red)}
html[data-theme] svg :not(text)[fill="#C78BFF"]{fill:var(--f-purple-bg)}
html[data-theme] svg text[fill="#C78BFF"]{fill:var(--f-purple)}
html[data-theme] svg [stroke="#C78BFF"]{stroke:var(--f-purple)}
html[data-theme] svg :not(text)[fill="#c78bff"]{fill:var(--f-purple-bg)}
html[data-theme] svg text[fill="#c78bff"]{fill:var(--f-purple)}
html[data-theme] svg [stroke="#c78bff"]{stroke:var(--f-purple)}
/* наконечники стрелок — насыщенным цветом */
html[data-theme] svg marker [fill="#58c4dd"]{fill:var(--f-blue)}
html[data-theme] svg marker [fill="#83c167"]{fill:var(--f-green)}
html[data-theme] svg marker [fill="#ff8c1a"]{fill:var(--f-orange)}
html[data-theme] svg marker [fill="#ffff00"]{fill:var(--f-yellow)}
html[data-theme] svg marker [fill="#fc6255"]{fill:var(--f-red)}
html[data-theme] svg marker [fill="#c78bff"]{fill:var(--f-purple)}
html[data-theme] svg marker [fill="#3b4a63"]{fill:var(--f-axis)}
html[data-theme] svg marker [fill="#33415a"]{fill:var(--f-axis)}
html[data-theme] svg marker [fill="#7c8aa0"]{fill:var(--f-axis)}
html[data-theme] svg marker [fill="#9aa4b2"]{fill:var(--f-muted)}
html[data-theme] svg marker [fill="#dfe7f1"]{fill:var(--f-text)}
html[data-theme] svg marker [fill="#c2cdde"]{fill:var(--f-text2)}
html[data-theme] svg text{font-family:var(--sans)}
html[data-theme] .viz{margin:26px 0}
html[data-theme] .viz svg{border:1px solid var(--line); border-radius:6px; box-shadow:none; background:var(--card)}
html[data-theme] .viz figcaption{font-family:var(--serif); font-size:.95rem; color:var(--muted); text-align:left; margin-top:10px}

/* пошаговые плееры */
html[data-theme] .algo{background:var(--card); border:1px solid var(--line); border-radius:6px; box-shadow:none}
html[data-theme] .algo .bar{background:var(--f-edge)}
html[data-theme] .algo .bar .v{color:var(--f-muted)}
html[data-theme] .algo .bar.cmp{background:var(--f-yellow-bg)} html[data-theme] .algo .bar.cmp .v{color:var(--f-yellow)}
html[data-theme] .algo .bar.swap{background:var(--f-red-bg)} html[data-theme] .algo .bar.swap .v{color:var(--f-red)}
html[data-theme] .algo .bar.done{background:var(--f-green-bg)} html[data-theme] .algo .bar.done .v{color:var(--f-green)}
html[data-theme] .algo .ctl input[type=range]{accent-color:var(--ink)}
html[data-theme] .algo .ctl button{background:none; color:var(--ink); border:1px solid var(--line); border-radius:6px}
html[data-theme] .algo .ctl button:hover{background:var(--hover,var(--tag))}
html[data-theme] .algo .lbl, html[data-theme] .algo .bslbl{color:var(--muted)}
html[data-theme] .algo .bscell{background:var(--f-node); border-color:var(--f-edge); color:var(--ink)}
html[data-theme] .algo .bscell.L, html[data-theme] .algo .bscell.found{background:var(--f-green-bg); color:var(--f-on)}
html[data-theme] .algo .bscell.R{background:var(--f-orange-bg); color:var(--f-on)}
html[data-theme] .algo .bscell.mid{background:var(--f-yellow-bg); color:var(--f-on)}
html[data-theme] .algo .bscell.found{box-shadow:0 0 0 3px color-mix(in srgb,var(--f-green) 40%,transparent)}

/* блоки кода */
html[data-theme]{
  --code-paper:#f4f0e7; --code-head:#ebe5d8; --code-line:#e0d9ca; --code-text:#2b2925;
  --hl-c:#8d877b; --hl-k:#1f4fd1; --hl-t:#7a3fb8; --hl-s:#2e7d32; --hl-n:#b4540a; --hl-f:#8a5a00; --hl-p:#b8372a;
}
html[data-theme="dark"]{
  --code-paper:#1c1b19; --code-head:#232220; --code-line:#2e2d2a; --code-text:#e6e2d9;
  --hl-c:#7f7a70; --hl-k:#8fb0ff; --hl-t:#c9a6ff; --hl-s:#a5d68f; --hl-n:#f2a96a; --hl-f:#e9d18e; --hl-p:#f08c7c;
}
html[data-theme] .code{margin:18px 0; border:1px solid var(--code-line); border-radius:8px; background:var(--code-paper); overflow:hidden}
html[data-theme] .code-head{display:flex; align-items:center; justify-content:space-between; gap:12px; padding:6px 8px 6px 14px; background:var(--code-head); border-bottom:1px solid var(--code-line); font-family:var(--mono); font-size:.72rem; color:var(--muted); letter-spacing:.03em}
html[data-theme] .code-head .copy{font:inherit; color:var(--muted); background:none; border:1px solid transparent; border-radius:5px; padding:3px 9px; cursor:pointer; transition:color .15s, border-color .15s, background-color .15s}
html[data-theme] .code-head .copy:hover{color:var(--ink); border-color:var(--code-line); background:var(--code-paper)}
html[data-theme] .code pre{margin:0; border:0; border-radius:0; background:none; color:var(--code-text); padding:14px 16px; font-size:.84rem; line-height:1.6; tab-size:4; overflow-x:auto}
html[data-theme] .code pre code{font-family:var(--mono); background:none; color:inherit; padding:0}
html[data-theme] .hl .c{color:var(--hl-c); font-style:italic}
html[data-theme] .hl .k{color:var(--hl-k); font-weight:600}
html[data-theme] .hl .t{color:var(--hl-t)}
html[data-theme] .hl .s{color:var(--hl-s)}
html[data-theme] .hl .n{color:var(--hl-n)}
html[data-theme] .hl .f{color:var(--hl-f)}
html[data-theme] .hl .p{color:var(--hl-p)}
@media print{html[data-theme] .code-head .copy{display:none}}

/* плавная смена темы */
html.theme-anim, html.theme-anim *, html.theme-anim *::before{transition:background-color .3s ease, color .3s ease, border-color .3s ease !important}

@media(max-width:680px){
  html[data-theme] .viz{overflow-x:auto; -webkit-overflow-scrolling:touch; margin-left:-18px; margin-right:-18px; padding:0 18px}
  html[data-theme] .viz svg{min-width:600px}
  html[data-theme] .viz figcaption{position:sticky; left:0; max-width:calc(100vw - 36px)}
  html[data-theme] .wrap{padding:20px 18px 64px}
  html[data-theme] header.hero{padding:36px 0 22px}
  html[data-theme] h2{font-size:1.45rem}
}
@media(prefers-reduced-motion:reduce){
  html[data-theme]{scroll-behavior:auto}
  @view-transition{navigation:none}
  html.theme-anim, html.theme-anim *{transition:none !important}
}
@media print{html[data-theme] .top, html[data-theme] .toplink{display:none} html[data-theme] body{background:#fff}}
/* ---------- навигация по конспекту ---------- */
html[data-theme] .progress{position:fixed; top:0; left:0; right:0; height:3px; background:var(--accent); transform-origin:0 50%; transform:scaleX(0); z-index:50; pointer-events:none}
html[data-theme] .side-toc{position:fixed; top:84px; right:max(16px, calc(50% - 410px - 250px)); width:220px; max-height:calc(100vh - 120px); overflow:auto;
  font-size:.85rem; line-height:1.35; opacity:0; visibility:hidden; transform:translateX(6px); transition:opacity .25s, transform .25s, visibility .25s; z-index:20}
html[data-theme] .side-toc.show{opacity:1; visibility:visible; transform:none}
html[data-theme] .side-toc p{font-family:var(--mono); font-size:.72rem; letter-spacing:.04em; text-transform:uppercase; color:var(--muted); margin:0 0 8px}
html[data-theme] .side-toc a{display:block; color:var(--muted); padding:4px 0 4px 12px; border-left:2px solid var(--line); text-decoration:none; transition:color .2s, border-color .2s}
html[data-theme] .side-toc a:hover{color:var(--ink)}
html[data-theme] .side-toc a.on{color:var(--ink); border-left-color:var(--accent)}
html[data-theme] .secbtn{position:fixed; left:16px; bottom:16px; z-index:30; background:var(--card); color:var(--ink); border:1px solid var(--line); border-radius:6px;
  padding:8px 14px; font-family:var(--sans); font-size:.82rem; cursor:pointer; opacity:0; visibility:hidden; transform:translateY(8px); transition:opacity .2s, transform .2s, visibility .2s}
html[data-theme] .secbtn.show{opacity:1; visibility:visible; transform:none}
html[data-theme] .secpanel{position:fixed; left:16px; right:16px; bottom:64px; max-width:420px; max-height:60vh; overflow:auto; z-index:31; background:var(--card);
  border:1px solid var(--line); border-radius:8px; padding:10px 0; box-shadow:0 12px 32px rgba(0,0,0,.18)}
html[data-theme] .secpanel[hidden]{display:none}
html[data-theme] .secpanel a{display:block; padding:8px 16px; color:var(--ink); text-decoration:none; font-size:.92rem}
html[data-theme] .secpanel a.on{color:var(--accent); font-weight:650}
html[data-theme] .pager{display:grid; grid-template-columns:1fr 1fr; gap:16px; margin:48px 0 0; padding-top:20px; border-top:1px solid var(--ink)}
html[data-theme] .pager a{display:block; padding:14px 16px; border:1px solid var(--line); border-radius:8px; color:var(--ink); text-decoration:none; transition:border-color .2s, background-color .2s}
html[data-theme] .pager a:hover{border-color:var(--accent); background:var(--accent-soft)}
html[data-theme] .pager a.next{text-align:right; grid-column:2}
html[data-theme] .pager small{display:block; font-family:var(--mono); font-size:.75rem; color:var(--muted); margin-bottom:4px}
html[data-theme] .pager b{font-family:var(--serif); font-size:1.08rem}
html[data-theme] h2[id], html[data-theme] h3[id]{scroll-margin-top:24px}
@media(min-width:1300px){html[data-theme] .secbtn, html[data-theme] .secpanel{display:none !important}}
@media(max-width:1299px){html[data-theme] .side-toc{display:none}}
@media(max-width:560px){html[data-theme] .pager{grid-template-columns:1fr} html[data-theme] .pager a.next{grid-column:1}}
@media print{html[data-theme] .progress, html[data-theme] .side-toc, html[data-theme] .secbtn, html[data-theme] .secpanel, html[data-theme] .pager{display:none}}
"""

THEME_ANIM_JS = (
    '<script>document.addEventListener("click",function(e){if(e.target.closest&&e.target.closest("#theme-toggle")){'
    'var h=document.documentElement;h.classList.add("theme-anim");setTimeout(function(){h.classList.remove("theme-anim")},350)}},true);'
    'document.addEventListener("click",function(e){var b=e.target.closest&&e.target.closest(".code .copy");if(!b)return;'
    'var pre=b.closest(".code").querySelector("pre"),t=pre.innerText;'
    'function ok(){b.textContent="скопировано ✓";setTimeout(function(){b.textContent="копировать"},1600)}'
    'function sel(){var r=document.createRange();r.selectNodeContents(pre);var x=getSelection();x.removeAllRanges();x.addRange(r);b.textContent="выделено — нажмите ⌘C"}'
    'if(navigator.clipboard){navigator.clipboard.writeText(t).then(ok,sel)}else{sel()}});</script>'
)

# Основной счётчик (стоял только на index.html — на страницах лекций не было
# вообще никакого GoatCounter-тега, поэтому заходы на них не считались).
GOATCOUNTER_BEACON = (
    '<script data-goatcounter="https://vmaiorov.goatcounter.com/count" '
    'async src="//gc.zgo.at/count.js"></script>\n'
)

# Второй, более подробный источник статистики (постраничный) в дополнение к
# GoatCounter — не убирать GoatCounter, просто ещё один беакон.
CF_BEACON = (
    '<script defer src=\'https://static.cloudflareinsights.com/beacon.min.js\' '
    'data-cf-beacon=\'{"token": "82e3760401a547558cc1d22198113255"}\'></script>\n'
)

OLD_TOP = (
    '<button type="button" id="theme-toggle" class="theme-toggle" aria-label="Переключить тему" '
    'title="Светлая / тёмная тема">🌙</button>\n<div class="wrap">\n'
    '<a class="back" href="../index.html">← Все конспекты</a>\n'
)
NEW_TOP = (
    '<div class="wrap">\n<div class="top"><a class="back" href="../index.html">← Все конспекты</a>'
    '<button type="button" id="theme-toggle" class="theme-toggle" aria-label="Переключить тему">тёмная тема</button></div>\n'
)
OLD_LABEL = 'textContent = t === "dark" ? "☀️" : "🌙";'
NEW_LABEL = 'textContent = t === "dark" ? "светлая тема" : "тёмная тема";'


# ---------- подсветка C++ ----------
KEYWORDS = set("""if else for while do return break continue switch case default struct class public private protected
const constexpr static auto using namespace template typename new delete true false nullptr sizeof operator inline
this virtual friend enum typedef goto try catch throw noexcept mutable explicit""".split())
TYPES = set("""int long short double float char bool void unsigned signed size_t string vector map set multiset unordered_map
unordered_set pair queue deque stack priority_queue array bitset ll ld ull ui __int128 int64_t uint64_t int32_t uint32_t
tuple function list greater less std mt19937 complex istream ostream""".split())
TOKEN = re.compile(r"""(?P<c>//[^\n]*|/\*.*?\*/)|(?P<p>^[ \t]*\#[^\n]*)|(?P<s>"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])')|(?P<n>\b(?:0[xX][0-9a-fA-F]+|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)[uUlLfF]*\b)|(?P<w>[A-Za-z_]\w*)""", re.M | re.S)


def highlight(code: str) -> str:
    out, i = [], 0
    for m in TOKEN.finditer(code):
        out.append(html.escape(code[i:m.start()], quote=False))
        tok = html.escape(m.group(0), quote=False)
        kind = m.lastgroup
        if kind == "w":
            w = m.group(0)
            rest = code[m.end():m.end() + 3].lstrip()
            if w in KEYWORDS:
                kind = "k"
            elif w in TYPES:
                kind = "t"
            elif rest.startswith("("):
                kind = "f"
            else:
                kind = None
        out.append(f'<span class="{kind}">{tok}</span>' if kind else tok)
        i = m.end()
    out.append(html.escape(code[i:], quote=False))
    return "".join(out)


def looks_like_cpp(code: str) -> bool:
    return any(x in code for x in (";", "{", "//", "#include", "cin", "cout"))


CODE_WRAP = re.compile(r'<div class="code"><div class="code-head">.*?</div><pre class="hl"><code>(.*?)</code></pre></div>', re.S)
PLAIN = re.compile(r"<pre><code>(.*?)</code></pre>", re.S)


def wrap_code(s: str) -> str:
    def render(raw_html):
        code = html.unescape(re.sub(r"<[^>]+>", "", raw_html))
        cpp = looks_like_cpp(code)
        body = highlight(code) if cpp else html.escape(code, quote=False)
        label = "C++" if cpp else "текст"
        return (f'<div class="code"><div class="code-head"><span>{label}</span>'
                f'<button class="copy" type="button">копировать</button></div>'
                f'<pre class="hl"><code>{body}</code></pre></div>')
    s = CODE_WRAP.sub(lambda m: render(m.group(1)), s)
    s = PLAIN.sub(lambda m: render(m.group(1)), s)
    return s


READER_JS = """<script id="reader">
(function(){
  var heads = [].slice.call(document.querySelectorAll(".wrap h2[id]"));
  if (!heads.length) return;
  var bar = document.createElement("div"); bar.className = "progress"; document.body.appendChild(bar);
  function label(h){ var c = h.cloneNode(true); [].forEach.call(c.querySelectorAll(".ts"), function(x){ x.remove(); });
    return c.textContent.replace(/^\\s*(?:\\d+\\.)+\\s*/, "").trim(); }
  function links(box){ return heads.map(function(h){ var a = document.createElement("a"); a.href = "#" + h.id; a.textContent = label(h); box.appendChild(a); return a; }); }
  var side = document.createElement("nav"); side.className = "side-toc"; side.setAttribute("aria-label", "Разделы");
  side.innerHTML = "<p>Разделы</p>"; var sideLinks = links(side); document.body.appendChild(side);
  var btn = document.createElement("button"); btn.className = "secbtn"; btn.type = "button"; btn.textContent = "≡ разделы";
  btn.setAttribute("aria-expanded", "false");
  var panel = document.createElement("nav"); panel.className = "secpanel"; panel.hidden = true; panel.setAttribute("aria-label", "Разделы");
  var panelLinks = links(panel); document.body.appendChild(panel); document.body.appendChild(btn);
  function toggle(open){ panel.hidden = !open; btn.setAttribute("aria-expanded", open); }
  btn.addEventListener("click", function(e){ e.stopPropagation(); toggle(panel.hidden); });
  panel.addEventListener("click", function(e){ if (e.target.closest("a")) toggle(false); });
  document.addEventListener("click", function(e){ if (!panel.hidden && !panel.contains(e.target)) toggle(false); });
  document.addEventListener("keydown", function(e){ if (e.key === "Escape") toggle(false); });
  var toc = document.querySelector(".toc"); var cur = -1; var ticking = false;
  function update(){
    ticking = false;
    var max = document.documentElement.scrollHeight - innerHeight;
    bar.style.transform = "scaleX(" + (max > 0 ? Math.min(1, scrollY / max) : 0) + ")";
    var past = toc ? toc.getBoundingClientRect().bottom < 0 : scrollY > 400;
    side.classList.toggle("show", past); btn.classList.toggle("show", past);
    var i = -1; for (var k = 0; k < heads.length; k++) if (heads[k].getBoundingClientRect().top < innerHeight * 0.3) i = k;
    if (i !== cur) {
      [sideLinks, panelLinks].forEach(function(l){ if (cur >= 0) l[cur].classList.remove("on"); if (i >= 0) l[i].classList.add("on"); });
      if (i >= 0 && side.classList.contains("show")) { var a = sideLinks[i]; if (a.offsetTop < side.scrollTop || a.offsetTop > side.scrollTop + side.clientHeight - 30) side.scrollTop = a.offsetTop - 60; }
      cur = i;
    }
  }
  addEventListener("scroll", function(){ if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
  addEventListener("resize", update); update();
})();
</script>"""

# ---------- порядок занятий и поиск по разделам (из списка на главной) ----------
LESSON_RE = re.compile(r'\{ n: "Занятие (\d+)", title: "([^"]+)", href: "([^"]+)" \}')
H_RE = re.compile(r'<(h[23])( id="([^"]+)")?>(.*?)</h[23]>', re.S)


def lessons_order():
    idx = (ROOT / "index.html").read_text(encoding="utf-8")
    by_par = {}
    for n, title, href in LESSON_RE.findall(idx):
        by_par.setdefault(href.split("/")[0], []).append((int(n), title, href))
    return by_par


def clean(h):
    h = re.sub(r'<a class="ts".*?</a>', "", h, flags=re.S)
    h = html.unescape(re.sub(r"<[^>]+>", "", h)).strip()
    return re.sub(r"^(?:\d+\.)+\s*", "", h)


def add_h3_ids(s):
    """У подзаголовков h3 появляются id вида s3-2, чтобы на них вели ссылки из поиска."""
    parent, k = None, 0
    def sub(m):
        nonlocal parent, k
        tag, has_id, hid, body = m.groups()
        if tag == "h2":
            parent, k = hid, 0
            return m.group(0)
        if has_id or not parent:
            return m.group(0)
        k += 1
        return f'<h3 id="{parent}-{k}">{body}</h3>'
    return H_RE.sub(sub, s)


def sections(s):
    out = []
    for tag, _has, hid, body in H_RE.findall(s):
        if hid and clean(body):
            out.append([hid, clean(body)])
    return out


def pager(path):
    par = path.parent.name
    rel = f"{par}/{path.name}"
    order = sorted(lessons_order().get(par, []))
    pos = next((i for i, (_n, _t, h) in enumerate(order) if h == rel), None)
    if pos is None:
        return ""
    def card(item, cls, arrow):
        n, title, href = item
        return (f'<a class="{cls}" href="../{href}"><small>{arrow[0]}занятие {n}{arrow[1]}</small>'
                f'<b>{html.escape(title)}</b></a>')
    prev = card(order[pos - 1], "prev", ("← ", "")) if pos > 0 else \
        '<a class="prev" href="../index.html"><small>← назад</small><b>Все конспекты</b></a>'
    nxt = card(order[pos + 1], "next", ("", " →")) if pos + 1 < len(order) else \
        '<a class="next" href="../index.html"><small>дальше</small><b>Все конспекты</b></a>'
    return f'<nav class="pager" aria-label="Соседние занятия">{prev}{nxt}</nav>'


def apply(path: Path) -> str:
    s = path.read_text(encoding="utf-8")
    block = f'<style id="paper">{CSS}</style>\n{THEME_ANIM_JS}\n'
    if '<style id="paper">' in s:
        s = re.sub(r'<style id="paper">.*?</style>\n<script>document\.addEventListener\("click".*?</script>\n', lambda _: block, s, count=1, flags=re.S)
    else:
        s = s.replace("</head>", block + "</head>", 1)
    if "data-goatcounter" not in s:
        s = s.replace("</head>", GOATCOUNTER_BEACON + "</head>", 1)
    if "cloudflareinsights.com" not in s:
        s = s.replace("</head>", CF_BEACON + "</head>", 1)
    s = s.replace(OLD_TOP, NEW_TOP, 1)
    s = s.replace(OLD_LABEL, NEW_LABEL)
    s = wrap_code(s)
    s = add_h3_ids(s)
    nav = pager(path)
    s = re.sub(r'\n?<nav class="pager".*?</nav>', "", s, flags=re.S)
    if nav:
        s = s.replace("\n</div>\n\n<button class=\"toplink\"", "\n" + nav + "\n</div>\n\n<button class=\"toplink\"", 1)
    s = re.sub(r'<script id="reader">.*?</script>\n', "", s, flags=re.S)
    s = s.replace("</body>", READER_JS + "\n</body>", 1)
    path.write_text(s, encoding="utf-8")
    SEARCH[f"{path.parent.name}/{path.name}"] = sections(s)
    ok = '<div class="top">' in s and NEW_LABEL in s
    return "ok" if ok else "проверьте вручную: не найдена шапка или переключатель темы"


def main():
    files = [Path(a) for a in sys.argv[1:]] or sorted(ROOT.glob("parallel-*/*.html"))
    for f in files:
        print(f"{f.name}: {apply(f)}")
    # индекс разделов для поиска на главной
    idx_path = ROOT / "index.html"
    idx = idx_path.read_text(encoding="utf-8")
    m = re.search(r"/\*SECTIONS\*/const SECTIONS = (.*?);/\*/SECTIONS\*/", idx, re.S)
    if m:
        data = json.loads(m.group(1))
        data.update(SEARCH)
        js = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        idx = idx[: m.start(1)] + js + idx[m.end(1):]
        idx_path.write_text(idx, encoding="utf-8")
        print(f"index.html: разделов в поиске — {sum(len(v) for v in data.values())}")


if __name__ == "__main__":
    main()
