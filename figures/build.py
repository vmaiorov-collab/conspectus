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


def build(name, preview=None):
    mod = importlib.import_module(name)
    if preview:
        out = Path(preview)
        out.mkdir(parents=True, exist_ok=True)
        for n, (fn, _cap) in sorted(mod.FIGS.items()):
            (out / f"{name}-{n:02d}.svg").write_text(fn(), encoding="utf-8")
        return f"{len(mod.FIGS)} svg → {out}"

    path = ROOT / mod.NOTE
    s = path.read_text(encoding="utf-8")
    figs = list(re.finditer(r"<figure.*?</figure>", s, re.S))
    for n in sorted(mod.FIGS, reverse=True):
        fn, cap = mod.FIGS[n]
        m = figs[n - 1]
        block = m.group(0)
        block = re.sub(r"<svg.*?</svg>", lambda _: fn(), block, count=1, flags=re.S)
        if cap is not None:
            block = re.sub(r"<figcaption>.*?</figcaption>", lambda _: f"<figcaption>{cap}</figcaption>", block, count=1, flags=re.S)
        s = s[: m.start()] + block + s[m.end():]
    path.write_text(s, encoding="utf-8")
    return f"{len(mod.FIGS)} схем → {mod.NOTE}"


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
