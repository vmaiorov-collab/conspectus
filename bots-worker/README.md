# bots-worker

Cloudflare Worker, принимающий вебхуки Telegram для обоих ботов репозитория
(`idea-bot` — пересылка идей/вопросов, `stats-bot` — статистика по `/stats`,
`/today`, `/top`, `/parallels`). Вебхук вместо long polling: бот отвечает
мгновенно и постоянно «запущен» без отдельной машины или cron.

Логика та же, что в `scripts/idea-bot.py` и `scripts/stats-bot.py` — те
скрипты остаются для локального разового запуска/отладки, но в проде вместо
них работает этот воркер.

## Деплой

```sh
cd bots-worker
CLOUDFLARE_API_TOKEN=xxx CLOUDFLARE_ACCOUNT_ID=xxx npx wrangler deploy
```

Токен должен иметь право **Account → Workers Scripts → Edit**.

## Секреты (`wrangler secret put NAME`)

| Секрет | Значение |
|---|---|
| `IDEA_BOT_TOKEN` | токен бота `@conspectus_csbot` |
| `IDEA_OWNER_CHAT_ID` | chat_id владельца (кому пересылаются идеи) |
| `IDEA_WEBHOOK_SECRET` | случайная строка — сверяется с заголовком `X-Telegram-Bot-Api-Secret-Token` |
| `STATS_BOT_TOKEN` | токен бота статистики |
| `STATS_ALLOWED_CHAT_IDS` | chat_id через запятую, кому бот отвечает |
| `STATS_WEBHOOK_SECRET` | случайная строка, как выше |
| `CF_API_TOKEN` | токен с правом **Account Analytics: Read** (для GraphQL-запросов статистики) |
| `CF_ACCOUNT_ID` | Cloudflare Account ID |

## Подключение вебхука в Telegram

```sh
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  --data-urlencode "url=https://<worker>.workers.dev/idea" \
  --data-urlencode "secret_token=<IDEA_WEBHOOK_SECRET>"
```

Аналогично для `/stats` с `STATS_WEBHOOK_SECRET`.
