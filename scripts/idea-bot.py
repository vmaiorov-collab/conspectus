#!/usr/bin/env python3
"""Telegram-бот для идей и предложений по конспектам.

Любое сообщение боту пересылается владельцу (TELEGRAM_CHAT_ID).
Владелец отвечает автору, нажав «Ответить» на пересланном сообщении.

Запускается разово (а не как вечный процесс с long polling): забирает все
накопившиеся сообщения через getUpdates, обрабатывает и подтверждает (ack)
их, затем завершается. Рассчитан на запуск по расписанию (например GitHub
Actions раз в 5 минут) — состояние между запусками хранить не нужно,
неподтверждённые сообщения просто останутся в очереди Telegram до следующего
запуска.
"""
import json
import os
import sys
import urllib.parse
import urllib.request

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
OWNER = os.environ.get("TELEGRAM_CHAT_ID", "")
API = f"https://api.telegram.org/bot{TOKEN}/"

GREETING = (
    "Привет! Это бот конспектов лекций по олимпиадному программированию.\n\n"
    "Напишите сюда идею, пожелание или найденную ошибку — одним или несколькими сообщениями. "
    "Можно прикладывать скриншоты.\n\n"
    "Сайт: https://vmaiorov-collab.github.io/conspectus/"
)
THANKS = "Спасибо! Передал автору конспектов 🙌"


def call(method, **params):
    data = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None}).encode()
    with urllib.request.urlopen(API + method, data=data, timeout=70) as r:
        res = json.load(r)
    if not res.get("ok"):
        raise RuntimeError(res)
    return res["result"]


def who(user):
    name = " ".join(filter(None, [user.get("first_name"), user.get("last_name")]))
    if user.get("username"):
        name += f" (@{user['username']})"
    return name or str(user["id"])


def handle(msg):
    chat_id = str(msg["chat"]["id"])
    text = msg.get("text", "")

    if msg["chat"].get("type") != "private":
        return

    if chat_id == OWNER:
        # ответ владельца на пересланную идею → автору
        reply = msg.get("reply_to_message") or {}
        marker = reply.get("text", "") or reply.get("caption", "")
        if "#u" in marker:
            target = marker.rsplit("#u", 1)[1].split()[0]
            call("copyMessage", chat_id=target, from_chat_id=chat_id, message_id=msg["message_id"])
            call("sendMessage", chat_id=OWNER, text="✅ Отправлено", reply_to_message_id=msg["message_id"])
        elif text.startswith("/start"):
            call("sendMessage", chat_id=OWNER, text="Вы владелец: сюда приходят идеи. Чтобы ответить автору — «Ответить» на его сообщение.")
        return

    if text.startswith("/start"):
        call("sendMessage", chat_id=chat_id, text=GREETING, disable_web_page_preview="true")
        return

    user = msg.get("from", {})
    header = f"💡 Идея от {who(user)}\n#u{chat_id}"
    call("sendMessage", chat_id=OWNER, text=header)
    sent = call("copyMessage", chat_id=OWNER, from_chat_id=chat_id, message_id=msg["message_id"])
    # подпись-маркер к копии, чтобы можно было ответить прямо на неё
    call("sendMessage", chat_id=OWNER, text=f"↩️ «Ответить» на это сообщение — ответ уйдёт автору\n#u{chat_id}",
         reply_to_message_id=sent["message_id"])
    call("sendMessage", chat_id=chat_id, text=THANKS)


def main():
    if not TOKEN:
        sys.exit("TELEGRAM_BOT_TOKEN не задан (.env)")
    if not OWNER:
        sys.exit("TELEGRAM_CHAT_ID не задан: напишите боту /start и узнайте свой chat id")

    updates = call("getUpdates", timeout=0, allowed_updates='["message"]')
    last_offset = None
    for upd in updates:
        last_offset = upd["update_id"]
        if "message" in upd:
            try:
                handle(upd["message"])
            except Exception as e:
                print("ошибка обработки:", e, flush=True)

    if last_offset is not None:
        call("getUpdates", offset=last_offset + 1, timeout=0)

    print(f"обработано сообщений: {len(updates)}", flush=True)


if __name__ == "__main__":
    main()
