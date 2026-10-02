#!/usr/bin/env python3
"""Разовый отчёт по статистике посещений conspectus (GoatCounter API).

В отличие от new-visitor-notify.py (который живёт в фоне и уведомляет о каждом
новом посетителе), этот скрипт запускается по требованию или по расписанию
(cron/launchd) и присылает один агрегированный отчёт: сколько заходов всего,
средняя посещаемость в день и какие страницы/лекции популярнее.

GoatCounter не хранит персистентный ID посетителя между днями, поэтому
«новых пользователей» в строгом смысле (новый человек vs вернувшийся) API не
отдаёт — здесь под «новыми посетителями за день» понимается дневной счётчик
уникальных посетителей (GoatCounter считает уникальность в рамках дня по
отпечатку браузера, без куки).

    GC_TOKEN=xxx python3 scripts/stats-report.py            # за последние 7 дней
    GC_TOKEN=xxx python3 scripts/stats-report.py --days 30  # за последние 30 дней
"""
import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta


DEFAULTS = {
    "GC_SITE": "vmaiorov",
    "TELEGRAM_BOT_TOKEN": "",
    "TELEGRAM_CHAT_ID": "",
}


def cfg(name):
    return os.environ.get(name, DEFAULTS.get(name, ""))


def api_get(base, token, path, params):
    url = base + path
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "User-Agent": "conspectus-stats-report",
    })
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_total(base, token, start, end):
    return api_get(base, token, "/stats/total", {
        "start": start.isoformat(), "end": end.isoformat(),
    })


def fetch_hits(base, token, start, end, limit=100):
    return api_get(base, token, "/stats/hits", {
        "start": start.isoformat(), "end": end.isoformat(), "limit": limit,
    })


def notify(text):
    print(text, flush=True)
    token = cfg("TELEGRAM_BOT_TOKEN")
    chat = cfg("TELEGRAM_CHAT_ID")
    if token and chat:
        try:
            body = urllib.parse.urlencode({"chat_id": chat, "text": text}).encode()
            req = urllib.request.Request(
                "https://api.telegram.org/bot%s/sendMessage" % token, data=body)
            urllib.request.urlopen(req, timeout=20).read()
        except urllib.error.URLError as exc:
            print("telegram error:", exc)


def build_report(days, total_data, hits_data):
    stats_by_day = {s["day"][:10]: s["daily"] for s in total_data.get("stats", [])}
    daily_counts = list(stats_by_day.values())
    total = total_data.get("total", 0)
    avg = total / len(daily_counts) if daily_counts else 0.0
    today = datetime.now().astimezone().date().isoformat()
    today_count = stats_by_day.get(today, 0)

    lines = [f"\U0001F4CA Статистика conspectus за {days} дн."]
    lines.append(f"Всего посетителей: {total} (в среднем {avg:.1f}/день)")
    lines.append(f"Сегодня: {today_count}")

    if daily_counts:
        best_day = max(stats_by_day.items(), key=lambda kv: kv[1])
        lines.append(f"Самый активный день: {best_day[0]} — {best_day[1]}")

    hits = sorted(hits_data.get("hits", []), key=lambda h: h.get("count", 0), reverse=True)
    if hits:
        lines.append("Топ страниц:")
        for i, h in enumerate(hits[:5], 1):
            title = h.get("title") or h.get("path")
            lines.append(f" {i}. {title} — {h.get('count', 0)}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=7, help="период отчёта в днях (по умолчанию 7)")
    args = parser.parse_args()

    token = cfg("GC_TOKEN")
    if not token:
        print("Нет GC_TOKEN. Создай API-ключ в GoatCounter: аккаунт -> API, "
              "и запусти: GC_TOKEN=xxx python3 scripts/stats-report.py")
        return 1

    base = "https://%s.goatcounter.com/api/v0" % cfg("GC_SITE")
    end = datetime.now().astimezone()
    start = (end - timedelta(days=args.days)).replace(hour=0, minute=0, second=0, microsecond=0)

    try:
        total_data = fetch_total(base, token, start, end)
        hits_data = fetch_hits(base, token, start, end)
    except urllib.error.URLError as exc:
        print("Не удалось получить данные GoatCounter:", exc)
        return 1

    notify(build_report(args.days, total_data, hits_data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
