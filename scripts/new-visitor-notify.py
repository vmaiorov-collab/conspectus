#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

DEFAULTS = {
    "GC_SITE": "vmaiorov",
    "POLL": "60",
    "SAY": "1",
    "SAY_VOICE": "Milena",
    "STATE": str(Path.home() / ".conspectus-gc-visitors.json"),
    "TELEGRAM_BOT_TOKEN": "",
    "TELEGRAM_CHAT_ID": "",
}


def cfg(name):
    return os.environ.get(name, DEFAULTS.get(name, ""))


def api_get(base, token, path, params):
    url = base + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "User-Agent": "conspectus-new-visitor-notify",
    })
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def visitors_today(base, token):
    now = datetime.now().astimezone()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    data = api_get(base, token, "/stats/total", {
        "start": start.isoformat(),
        "end": now.isoformat(),
    })
    return int(data.get("total", 0))


def load_state(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def save_state(path, state):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(state, fh)
    os.replace(tmp, path)


def notify(text):
    print(time.strftime("[%H:%M:%S]"), text, flush=True)
    if cfg("SAY") not in ("", "0", "false", "no") and sys.platform == "darwin":
        voice = cfg("SAY_VOICE")
        cmd = ["say", "-v", voice, text] if voice else ["say", text]
        try:
            if subprocess.run(cmd, check=False).returncode != 0 and voice:
                subprocess.run(["say", text], check=False)
        except OSError:
            pass
    token = cfg("TELEGRAM_BOT_TOKEN")
    chat = cfg("TELEGRAM_CHAT_ID")
    if token and chat:
        try:
            body = urllib.parse.urlencode({"chat_id": chat, "text": text}).encode()
            req = urllib.request.Request(
                "https://api.telegram.org/bot%s/sendMessage" % token, data=body)
            urllib.request.urlopen(req, timeout=20).read()
        except Exception as exc:
            print("telegram error:", exc, file=sys.stderr, flush=True)


def main():
    token = cfg("GC_TOKEN")
    if not token:
        print("Нет GC_TOKEN. Создай API-ключ в GoatCounter: аккаунт -> API, "
              "и запусти: GC_TOKEN=xxx python3 scripts/new-visitor-notify.py",
              file=sys.stderr)
        return 1

    base = "https://%s.goatcounter.com/api/v0" % cfg("GC_SITE")
    poll = max(1, int(cfg("POLL")))
    state_path = cfg("STATE")
    state = load_state(state_path)

    try:
        current = visitors_today(base, token)
    except Exception as exc:
        print("Не удалось получить данные GoatCounter:", exc, file=sys.stderr)
        return 1

    today = datetime.now().astimezone().date().isoformat()
    if state.get("day") != today:
        state = {"day": today, "last": current}
        save_state(state_path, state)
        print("База на", today, "— посетителей:", current, flush=True)
    elif current > int(state.get("last", 0)):
        state["last"] = current
        save_state(state_path, state)

    while True:
        time.sleep(poll)
        try:
            current = visitors_today(base, token)
        except Exception as exc:
            print("ошибка запроса:", exc, file=sys.stderr, flush=True)
            continue

        today = datetime.now().astimezone().date().isoformat()
        if state.get("day") != today:
            state = {"day": today, "last": current}
            save_state(state_path, state)
            continue

        last = int(state.get("last", 0))
        if current > last:
            diff = current - last
            if diff == 1:
                text = "Новый посетитель! Сегодня всего: %d" % current
            else:
                text = "Новые посетители: +%d. Сегодня всего: %d" % (diff, current)
            notify(text)
            state["last"] = current
            save_state(state_path, state)
        elif current < last:
            state["last"] = current
            save_state(state_path, state)


if __name__ == "__main__":
    raise SystemExit(main())
