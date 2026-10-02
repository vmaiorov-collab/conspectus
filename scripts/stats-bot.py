#!/usr/bin/env python3
"""Интерактивный Telegram-бот для статистики conspectus (GoatCounter API).

В отличие от stats-report.py (разовый вывод) и new-visitor-notify.py (фоновые
уведомления о каждом посетителе), этот бот отвечает на команды по запросу.
Рассчитан на запуск по расписанию (например GitHub Actions, раз в 5 минут),
а не как постоянно работающий процесс: за один запуск забирает все новые
сообщения через Telegram getUpdates, отвечает и подтверждает (ack) их —
так состояние между запусками хранить не нужно (следующий запуск не увидит
уже обработанные сообщения, даже без локального файла offset).

Команды:
    /stats [дни]   — сводка за период (по умолчанию 7 дней)
    /today         — посетители сегодня
    /top [n]       — топ-N страниц за 7 дней (по умолчанию 5)
    /help          — список команд

Только пользователи из ALLOWED_CHAT_IDS получают ответ — это публичный бот
Telegram, и без белого списка статистику сайта смог бы запросить кто угодно,
кто найдёт бота.

    GC_TOKEN=xxx TELEGRAM_BOT_TOKEN=yyy ALLOWED_CHAT_IDS=5066064774 \\
        python3 scripts/stats-bot.py
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

DEFAULTS = {"GC_SITE": "vmaiorov"}


def cfg(name):
    return os.environ.get(name, DEFAULTS.get(name, ""))


def allowed_chat_ids():
    raw = cfg("ALLOWED_CHAT_IDS")
    return {s.strip() for s in raw.split(",") if s.strip()}


# ---------- GoatCounter ----------

def gc_get(token, path, params):
    base = "https://%s.goatcounter.com/api/v0" % cfg("GC_SITE")
    url = base + path + "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "User-Agent": "conspectus-stats-bot",
    })
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_total(token, start, end):
    return gc_get(token, "/stats/total", {"start": start.isoformat(), "end": end.isoformat()})


def fetch_hits(token, start, end, limit=100):
    return gc_get(token, "/stats/hits", {"start": start.isoformat(), "end": end.isoformat(), "limit": limit})


def report_stats(token, days):
    end = datetime.now().astimezone()
    start = (end - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
    total_data = fetch_total(token, start, end)
    stats_by_day = {s["day"][:10]: s["daily"] for s in total_data.get("stats", [])}
    total = total_data.get("total", 0)
    avg = total / len(stats_by_day) if stats_by_day else 0.0
    lines = [f"\U0001F4CA Статистика conspectus за {days} дн.", f"Всего посетителей: {total} (в среднем {avg:.1f}/день)"]
    if stats_by_day:
        best_day = max(stats_by_day.items(), key=lambda kv: kv[1])
        lines.append(f"Самый активный день: {best_day[0]} — {best_day[1]}")
    return "\n".join(lines)


def report_today(token):
    end = datetime.now().astimezone()
    start = end.replace(hour=0, minute=0, second=0, microsecond=0)
    data = fetch_total(token, start, end)
    return f"Сегодня посетителей: {data.get('total', 0)}"


def report_top(token, n):
    end = datetime.now().astimezone()
    start = end - timedelta(days=7)
    data = fetch_hits(token, start, end)
    hits = sorted(data.get("hits", []), key=lambda h: h.get("count", 0), reverse=True)
    if not hits:
        return "За последние 7 дней пока нет данных."
    lines = [f"Топ-{n} страниц за 7 дней:"]
    for i, h in enumerate(hits[:n], 1):
        title = h.get("title") or h.get("path")
        lines.append(f" {i}. {title} — {h.get('count', 0)}")
    return "\n".join(lines)


HELP = (
    "Команды:\n"
    "/stats [дни] — сводка за период (по умолчанию 7)\n"
    "/today — посетители сегодня\n"
    "/top [n] — топ-N страниц за 7 дней (по умолчанию 5)"
)


def handle_command(gc_token, text):
    parts = text.strip().split()
    cmd = parts[0].split("@")[0].lower()
    arg = parts[1] if len(parts) > 1 else None
    try:
        if cmd in ("/start", "/help"):
            return HELP
        if cmd == "/stats":
            return report_stats(gc_token, int(arg) if arg else 7)
        if cmd == "/today":
            return report_today(gc_token)
        if cmd == "/top":
            return report_top(gc_token, int(arg) if arg else 5)
    except (ValueError, urllib.error.URLError) as exc:
        return f"Не удалось получить статистику: {exc}"
    return None


# ---------- Telegram ----------

def tg_call(bot_token, method, params):
    url = f"https://api.telegram.org/bot{bot_token}/{method}"
    req = urllib.request.Request(url, data=urllib.parse.urlencode(params).encode())
    with urllib.request.urlopen(req, timeout=40) as resp:
        return json.loads(resp.read().decode("utf-8"))


def send_message(bot_token, chat_id, text):
    tg_call(bot_token, "sendMessage", {"chat_id": chat_id, "text": text})


def main():
    bot_token = cfg("TELEGRAM_BOT_TOKEN")
    gc_token = cfg("GC_TOKEN")
    allowed = allowed_chat_ids()
    if not bot_token or not gc_token:
        print("Нужны TELEGRAM_BOT_TOKEN и GC_TOKEN в окружении.", file=sys.stderr)
        return 1
    if not allowed:
        print("ALLOWED_CHAT_IDS не задан — бот не будет отвечать никому.", file=sys.stderr)

    try:
        resp = tg_call(bot_token, "getUpdates", {"timeout": 0})
    except urllib.error.URLError as exc:
        print("ошибка getUpdates:", exc, file=sys.stderr)
        return 1

    updates = resp.get("result", [])
    last_offset = None
    for update in updates:
        last_offset = update["update_id"]
        message = update.get("message") or {}
        text = message.get("text", "")
        chat_id = str(message.get("chat", {}).get("id", ""))
        if not text.startswith("/") or chat_id not in allowed:
            continue
        reply = handle_command(gc_token, text)
        if reply:
            try:
                send_message(bot_token, chat_id, reply)
            except urllib.error.URLError as exc:
                print("ошибка sendMessage:", exc, file=sys.stderr)

    if last_offset is not None:
        try:
            tg_call(bot_token, "getUpdates", {"offset": last_offset + 1, "timeout": 0})
        except urllib.error.URLError as exc:
            print("ошибка ack getUpdates:", exc, file=sys.stderr)

    print(f"Обработано сообщений: {len(updates)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
