#!/usr/bin/env python3
"""Интерактивный Telegram-бот для статистики conspectus (Cloudflare Web Analytics).

В отличие от new-visitor-notify.py (фоновые уведомления о каждом посетителе
через GoatCounter), этот бот отвечает на команды по запросу, используя
Cloudflare Web Analytics (RUM) — второй, более подробный источник статистики,
подключённый beacon-скриптом на каждой странице сайта.

Данные читаются через Cloudflare GraphQL Analytics API, dataset
rumPageloadEventsAdaptiveGroups, отфильтрованный по siteTag (= тот же токен,
что в beacon-скрипте на страницах). Публичной документации по этому датасету
нет — схема (поля siteTag/requestPath/date, sum.visits, orderBy
sum_visits_DESC) подтверждена живыми запросами к API.

Рассчитан на запуск по расписанию (например GitHub Actions, раз в 5 минут),
а не как постоянно работающий процесс: за один запуск забирает все новые
сообщения через Telegram getUpdates, отвечает и подтверждает (ack) их —
так состояние между запусками хранить не нужно.

Команды:
    /stats [дни]   — сводка за период (по умолчанию 7 дней)
    /today         — посетители сегодня
    /top [n]       — топ-N страниц за 7 дней (по умолчанию 5)
    /help          — список команд

Только пользователи из ALLOWED_CHAT_IDS получают ответ — это публичный бот
Telegram, и без белого списка статистику сайта смог бы запросить кто угодно,
кто найдёт бота.

    CF_ACCOUNT_ID=xxx CF_API_TOKEN=yyy TELEGRAM_BOT_TOKEN=zzz \\
        ALLOWED_CHAT_IDS=5066064774 python3 scripts/stats-bot.py
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

DEFAULTS = {
    # Публичный токен beacon-скрипта (встроен в HTML каждой страницы, не секрет).
    "CF_SITE_TAG": "82e3760401a547558cc1d22198113255",
}
CF_GRAPHQL_URL = "https://api.cloudflare.com/client/v4/graphql"


def cfg(name):
    return os.environ.get(name, DEFAULTS.get(name, ""))


def allowed_chat_ids():
    raw = cfg("ALLOWED_CHAT_IDS")
    return {s.strip() for s in raw.split(",") if s.strip()}


# ---------- Cloudflare GraphQL Analytics ----------

def cf_query(api_token, query, variables):
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(CF_GRAPHQL_URL, data=body, headers={
        "Authorization": "Bearer " + api_token,
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("errors"):
        raise RuntimeError(str(data["errors"]))
    accounts = data["data"]["viewer"]["accounts"]
    return accounts[0] if accounts else {}


def fetch_by_date(api_token, account_id, site_tag, start, end):
    query = """
    query($accountTag: string, $siteTag: string, $start: Time, $end: Time) {
      viewer { accounts(filter: {accountTag: $accountTag}) {
        rumPageloadEventsAdaptiveGroups(
          limit: 100,
          filter: {siteTag: $siteTag, datetime_geq: $start, datetime_leq: $end},
          orderBy: [date_ASC]
        ) { dimensions { date } sum { visits } }
      } }
    }
    """
    acc = cf_query(api_token, query, {
        "accountTag": account_id, "siteTag": site_tag,
        "start": start.isoformat(), "end": end.isoformat(),
    })
    return acc.get("rumPageloadEventsAdaptiveGroups", [])


def fetch_top_paths(api_token, account_id, site_tag, start, end, limit):
    query = """
    query($accountTag: string, $siteTag: string, $start: Time, $end: Time, $limit: Int!) {
      viewer { accounts(filter: {accountTag: $accountTag}) {
        rumPageloadEventsAdaptiveGroups(
          limit: $limit,
          filter: {siteTag: $siteTag, datetime_geq: $start, datetime_leq: $end},
          orderBy: [sum_visits_DESC]
        ) { dimensions { requestPath } sum { visits } }
      } }
    }
    """
    acc = cf_query(api_token, query, {
        "accountTag": account_id, "siteTag": site_tag,
        "start": start.isoformat(), "end": end.isoformat(), "limit": limit,
    })
    return acc.get("rumPageloadEventsAdaptiveGroups", [])


def report_stats(api_token, account_id, site_tag, days):
    end = datetime.now().astimezone()
    start = (end - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
    rows = fetch_by_date(api_token, account_id, site_tag, start, end)
    by_day = {r["dimensions"]["date"]: r["sum"]["visits"] for r in rows}
    total = sum(by_day.values())
    avg = total / len(by_day) if by_day else 0.0
    lines = [f"\U0001F4CA Статистика conspectus за {days} дн. (Cloudflare)",
             f"Всего визитов: {total} (в среднем {avg:.1f}/день)"]
    if by_day:
        best_day = max(by_day.items(), key=lambda kv: kv[1])
        lines.append(f"Самый активный день: {best_day[0]} — {best_day[1]}")
    else:
        lines.append("Данных пока нет (беакон недавно подключён).")
    return "\n".join(lines)


def report_today(api_token, account_id, site_tag):
    end = datetime.now().astimezone()
    start = end.replace(hour=0, minute=0, second=0, microsecond=0)
    rows = fetch_by_date(api_token, account_id, site_tag, start, end)
    total = sum(r["sum"]["visits"] for r in rows)
    return f"Сегодня визитов: {total}"


def report_top(api_token, account_id, site_tag, n):
    end = datetime.now().astimezone()
    start = end - timedelta(days=7)
    rows = fetch_top_paths(api_token, account_id, site_tag, start, end, n)
    if not rows:
        return "За последние 7 дней пока нет данных."
    lines = [f"Топ-{n} страниц за 7 дней (Cloudflare):"]
    for i, r in enumerate(rows, 1):
        path = r["dimensions"]["requestPath"] or "/"
        lines.append(f" {i}. {path} — {r['sum']['visits']}")
    return "\n".join(lines)


PARALLEL_LABELS = {
    "parallel-a": "Параллель A",
    "parallel-ap": "Параллель A'",
    "parallel-b": "Параллель B",
    "parallel-bp": "Параллель B'",
    "parallel-c": "Параллель C",
}


def report_parallels(api_token, account_id, site_tag, days):
    end = datetime.now().astimezone()
    start = (end - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
    rows = fetch_top_paths(api_token, account_id, site_tag, start, end, 100)
    if not rows:
        return f"За последние {days} дн. пока нет данных."

    totals = {}
    for r in rows:
        path = (r["dimensions"]["requestPath"] or "/").lstrip("/")
        prefix = path.split("/", 1)[0]
        key = PARALLEL_LABELS.get(prefix, "Главная / прочее")
        totals[key] = totals.get(key, 0) + r["sum"]["visits"]

    lines = [f"\U0001F4CA Визиты по параллелям за {days} дн. (Cloudflare):"]
    for name, visits in sorted(totals.items(), key=lambda kv: kv[1], reverse=True):
        lines.append(f" {name} — {visits}")
    return "\n".join(lines)


HELP = (
    "Команды:\n"
    "/stats [дни] — сводка за период (по умолчанию 7)\n"
    "/today — посетители сегодня\n"
    "/top [n] — топ-N страниц за 7 дней (по умолчанию 5)\n"
    "/parallels [дни] — визиты по параллелям A/A'/B/B'/C (по умолчанию 7)"
)


def handle_command(api_token, account_id, site_tag, text):
    parts = text.strip().split()
    cmd = parts[0].split("@")[0].lower()
    arg = parts[1] if len(parts) > 1 else None
    try:
        if cmd in ("/start", "/help"):
            return HELP
        if cmd == "/stats":
            return report_stats(api_token, account_id, site_tag, int(arg) if arg else 7)
        if cmd == "/today":
            return report_today(api_token, account_id, site_tag)
        if cmd == "/top":
            return report_top(api_token, account_id, site_tag, int(arg) if arg else 5)
        if cmd == "/parallels":
            return report_parallels(api_token, account_id, site_tag, int(arg) if arg else 7)
    except (ValueError, RuntimeError, urllib.error.URLError) as exc:
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
    cf_token = cfg("CF_API_TOKEN")
    account_id = cfg("CF_ACCOUNT_ID")
    site_tag = cfg("CF_SITE_TAG")
    allowed = allowed_chat_ids()
    if not bot_token or not cf_token or not account_id:
        print("Нужны TELEGRAM_BOT_TOKEN, CF_API_TOKEN и CF_ACCOUNT_ID в окружении.", file=sys.stderr)
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
        reply = handle_command(cf_token, account_id, site_tag, text)
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
