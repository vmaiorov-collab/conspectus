#!/usr/bin/env python3
"""Вставляет схемы из figures/<модуль>.py в конспекты.

Каждый модуль задаёт NOTE (путь к конспекту) и FIGS = {номер_figure: (функция, подпись|None)}.
Функция возвращает строку <svg>. Подпись — HTML (можно с $...$ для KaTeX).

    python3 figures/build.py                 # все модули
    python3 figures/build.py matematika      # один модуль
    python3 figures/build.py matematika --preview DIR   # только сохранить svg в DIR
"""
import importlib
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

MODULES = sorted(p.stem for p in HERE.glob("*.py") if p.stem not in {"kit", "build"})


VOID = {"br", "img", "hr", "input", "meta", "link", "source", "wbr", "col", "area", "base", "embed", "param", "track"}


def top_level_end(s, pos):
    """Конец элемента — прямого потомка div.wrap, внутри которого находится позиция pos."""
    wrap = s.index('<div class="wrap">')
    stack = []
    i = wrap + len('<div class="wrap">')
    tag_re = re.compile(r"<(/?)([a-zA-Z][\w-]*)([^>]*?)(/?)>|<!--.*?-->", re.S)
    top_start = None
    while True:
        m = tag_re.search(s, i)
        if not m:
            raise ValueError("не нашёл конец блока")
        i = m.end()
        if m.group(0).startswith("<!--") or not m.group(2):
            continue
        close, name, selfclose = m.group(1), m.group(2).lower(), m.group(4)
        if name in ("script", "style") and not close:
            i = s.index(f"</{name}>", i) + len(name) + 3
            continue
        if not close and (selfclose or name in VOID):
            continue
        if not close:
            if not stack and m.start() <= pos:
                top_start = m.start()
            stack.append(name)
        else:
            if not stack:
                raise ValueError("якорь вне div.wrap")
            stack.pop()
            if not stack and top_start is not None and m.end() > pos:
                return m.end()


def build(name, preview=None):
    mod = importlib.import_module(name)
    if preview:
        out = Path(preview)
        out.mkdir(parents=True, exist_ok=True)
        for n, (fn, _cap) in sorted(getattr(mod, "FIGS", {}).items()):
            (out / f"{name}-{n:02d}.svg").write_text(fn(), encoding="utf-8")
        for fid, _a, fn, _c in getattr(mod, "INSERTS", []):
            (out / f"{name}-{fid}.svg").write_text(fn(), encoding="utf-8")
        return f"svg → {out}"

    path = ROOT / mod.NOTE
    s = path.read_text(encoding="utf-8")
    # новые схемы: INSERTS = [(id, фраза-якорь, функция, подпись)]
    for fid, anchor, fn, cap in getattr(mod, "INSERTS", []):
        block = f'<figure class="viz" data-fig="{fid}">{fn()}<figcaption>{cap}</figcaption></figure>'
        old = re.search(rf'<figure class="viz" data-fig="{re.escape(fid)}">.*?</figure>', s, re.S)
        if old:
            s = s[: old.start()] + block + s[old.end():]
        else:
            at = top_level_end(s, s.index(anchor))
            s = s[:at] + "\n" + block + s[at:]
    figs = [m for m in re.finditer(r"<figure.*?</figure>", s, re.S) if "data-fig=" not in m.group(0)[:60]]
    for n in sorted(getattr(mod, "FIGS", {}), reverse=True):
        fn, cap = mod.FIGS[n]
        m = figs[n - 1]
        block = m.group(0)
        block = re.sub(r"<svg.*?</svg>", lambda _: fn(), block, count=1, flags=re.S)
        if cap is not None:
            block = re.sub(r"<figcaption>.*?</figcaption>", lambda _: f"<figcaption>{cap}</figcaption>", block, count=1, flags=re.S)
        s = s[: m.start()] + block + s[m.end():]
    path.write_text(s, encoding="utf-8")
    return f"{len(getattr(mod, 'FIGS', {})) + len(getattr(mod, 'INSERTS', []))} схем → {mod.NOTE}"


def main():
    args = sys.argv[1:]
    preview = None
    if "--preview" in args:
        i = args.index("--preview")
        preview = args[i + 1]
        del args[i:i + 2]
    for name in args or MODULES:
        print(f"{name}: {build(name, preview)}")


if __name__ == "__main__":
    main()
