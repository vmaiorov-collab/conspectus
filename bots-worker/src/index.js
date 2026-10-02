// conspectus-bots: один Cloudflare Worker, два вебхука (idea / stats).
// Логика перенесена из scripts/idea-bot.py и scripts/stats-bot.py (conspectus
// репозиторий) — здесь это вебхуки, а не поллинг, поэтому бот живёт всегда
// и отвечает мгновенно, без cron-задержки и без постоянно работающей машины.

async function tgCall(token, method, params) {
  const res = await fetch(`https://api.telegram.org/bot${token}/${method}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  const data = await res.json();
  if (!data.ok) throw new Error(JSON.stringify(data));
  return data.result;
}

// ---------- idea-bot ----------

const GREETING =
  "Привет! Это бот конспектов лекций по олимпиадному программированию.\n\n" +
  "Напишите сюда идею, пожелание или найденную ошибку — одним или несколькими сообщениями. " +
  "Можно прикладывать скриншоты.\n\n" +
  "Сайт: https://vmaiorov-collab.github.io/conspectus/";
const THANKS = "Спасибо! Передал автору конспектов 🙌";

function who(user) {
  let name = [user.first_name, user.last_name].filter(Boolean).join(" ");
  if (user.username) name += ` (@${user.username})`;
  return name || String(user.id);
}

async function handleIdea(update, env) {
  const msg = update.message;
  if (!msg) return;
  const token = env.IDEA_BOT_TOKEN;
  const owner = env.IDEA_OWNER_CHAT_ID;
  const chatId = String(msg.chat.id);
  const text = msg.text || "";

  if (msg.chat.type !== "private") return;

  if (chatId === owner) {
    // ответ владельца на пересланную идею → автору
    const reply = msg.reply_to_message;
    const marker = (reply && (reply.text || reply.caption)) || "";
    if (marker.includes("#u")) {
      const target = marker.split("#u")[1].split(/\s/)[0];
      await tgCall(token, "copyMessage", { chat_id: target, from_chat_id: chatId, message_id: msg.message_id });
      await tgCall(token, "sendMessage", { chat_id: owner, text: "✅ Отправлено", reply_to_message_id: msg.message_id });
    } else if (text.startsWith("/start")) {
      await tgCall(token, "sendMessage", {
        chat_id: owner,
        text: "Вы владелец: сюда приходят идеи. Чтобы ответить автору — «Ответить» на его сообщение.",
      });
    }
    return;
  }

  if (text.startsWith("/start")) {
    await tgCall(token, "sendMessage", { chat_id: chatId, text: GREETING, disable_web_page_preview: true });
    return;
  }

  const header = `💡 Идея от ${who(msg.from || {})}\n#u${chatId}`;
  await tgCall(token, "sendMessage", { chat_id: owner, text: header });
  const sent = await tgCall(token, "copyMessage", { chat_id: owner, from_chat_id: chatId, message_id: msg.message_id });
  await tgCall(token, "sendMessage", {
    chat_id: owner,
    text: `↩️ «Ответить» на это сообщение — ответ уйдёт автору\n#u${chatId}`,
    reply_to_message_id: sent.message_id,
  });
  await tgCall(token, "sendMessage", { chat_id: chatId, text: THANKS });
}

// ---------- stats-bot (Cloudflare Web Analytics GraphQL) ----------

// Публичный токен beacon-скрипта (встроен в HTML каждой страницы, не секрет).
const CF_SITE_TAG = "82e3760401a547558cc1d22198113255";

const PARALLEL_LABELS = {
  "parallel-a": "Параллель A",
  "parallel-ap": "Параллель A'",
  "parallel-b": "Параллель B",
  "parallel-bp": "Параллель B'",
  "parallel-c": "Параллель C",
};

async function cfQuery(env, query, variables) {
  const res = await fetch("https://api.cloudflare.com/client/v4/graphql", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.CF_API_TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query, variables }),
  });
  const data = await res.json();
  if (data.errors) throw new Error(JSON.stringify(data.errors));
  const accounts = data.data.viewer.accounts;
  return accounts.length ? accounts[0] : {};
}

async function fetchByDate(env, start, end) {
  const query = `
    query($accountTag: string, $siteTag: string, $start: Time, $end: Time) {
      viewer { accounts(filter: {accountTag: $accountTag}) {
        rumPageloadEventsAdaptiveGroups(
          limit: 100,
          filter: {siteTag: $siteTag, datetime_geq: $start, datetime_leq: $end},
          orderBy: [date_ASC]
        ) { dimensions { date } sum { visits } }
      } }
    }`;
  const acc = await cfQuery(env, query, {
    accountTag: env.CF_ACCOUNT_ID,
    siteTag: CF_SITE_TAG,
    start: start.toISOString(),
    end: end.toISOString(),
  });
  return acc.rumPageloadEventsAdaptiveGroups || [];
}

async function fetchTopPaths(env, start, end, limit) {
  const query = `
    query($accountTag: string, $siteTag: string, $start: Time, $end: Time, $limit: Int!) {
      viewer { accounts(filter: {accountTag: $accountTag}) {
        rumPageloadEventsAdaptiveGroups(
          limit: $limit,
          filter: {siteTag: $siteTag, datetime_geq: $start, datetime_leq: $end},
          orderBy: [sum_visits_DESC]
        ) { dimensions { requestPath } sum { visits } }
      } }
    }`;
  const acc = await cfQuery(env, query, {
    accountTag: env.CF_ACCOUNT_ID,
    siteTag: CF_SITE_TAG,
    start: start.toISOString(),
    end: end.toISOString(),
    limit,
  });
  return acc.rumPageloadEventsAdaptiveGroups || [];
}

function startOfDayUTC(d) {
  const x = new Date(d);
  x.setUTCHours(0, 0, 0, 0);
  return x;
}

async function reportStats(env, days) {
  const end = new Date();
  const start = startOfDayUTC(new Date(end.getTime() - days * 86400000));
  const rows = await fetchByDate(env, start, end);
  const byDay = {};
  for (const r of rows) byDay[r.dimensions.date] = r.sum.visits;
  const entries = Object.entries(byDay);
  const total = entries.reduce((a, [, v]) => a + v, 0);
  const avg = entries.length ? total / entries.length : 0;
  const lines = [
    `📊 Статистика conspectus за ${days} дн. (Cloudflare)`,
    `Всего визитов: ${total} (в среднем ${avg.toFixed(1)}/день)`,
  ];
  if (entries.length) {
    const best = entries.reduce((a, b) => (b[1] > a[1] ? b : a));
    lines.push(`Самый активный день: ${best[0]} — ${best[1]}`);
  } else {
    lines.push("Данных пока нет (беакон недавно подключён).");
  }
  return lines.join("\n");
}

async function reportToday(env) {
  const end = new Date();
  const start = startOfDayUTC(end);
  const rows = await fetchByDate(env, start, end);
  const total = rows.reduce((a, r) => a + r.sum.visits, 0);
  return `Сегодня визитов: ${total}`;
}

async function reportTop(env, n) {
  const end = new Date();
  const start = new Date(end.getTime() - 7 * 86400000);
  const rows = await fetchTopPaths(env, start, end, n);
  if (!rows.length) return "За последние 7 дней пока нет данных.";
  const lines = [`Топ-${n} страниц за 7 дней (Cloudflare):`];
  rows.forEach((r, i) => {
    lines.push(` ${i + 1}. ${r.dimensions.requestPath || "/"} — ${r.sum.visits}`);
  });
  return lines.join("\n");
}

async function reportParallels(env, days) {
  const end = new Date();
  const start = startOfDayUTC(new Date(end.getTime() - days * 86400000));
  const rows = await fetchTopPaths(env, start, end, 100);
  if (!rows.length) return `За последние ${days} дн. пока нет данных.`;
  const totals = {};
  for (const r of rows) {
    const path = (r.dimensions.requestPath || "/").replace(/^\//, "");
    const prefix = path.split("/")[0];
    const key = PARALLEL_LABELS[prefix] || "Главная / прочее";
    totals[key] = (totals[key] || 0) + r.sum.visits;
  }
  const lines = [`📊 Визиты по параллелям за ${days} дн. (Cloudflare):`];
  Object.entries(totals)
    .sort((a, b) => b[1] - a[1])
    .forEach(([name, visits]) => lines.push(` ${name} — ${visits}`));
  return lines.join("\n");
}

const STATS_HELP = [
  "Команды:",
  "/stats [дни] — сводка за период (по умолчанию 7)",
  "/today — посетители сегодня",
  "/top [n] — топ-N страниц за 7 дней (по умолчанию 5)",
  "/parallels [дни] — визиты по параллелям A/A'/B/B'/C (по умолчанию 7)",
].join("\n");

async function handleStats(update, env) {
  const msg = update.message;
  if (!msg || !msg.text || !msg.text.startsWith("/")) return;
  const allowed = new Set(
    (env.STATS_ALLOWED_CHAT_IDS || "").split(",").map((s) => s.trim()).filter(Boolean)
  );
  const chatId = String(msg.chat.id);
  if (!allowed.has(chatId)) return;

  const parts = msg.text.trim().split(/\s+/);
  const cmd = parts[0].split("@")[0].toLowerCase();
  const arg = parts[1];
  let reply;
  try {
    if (cmd === "/start" || cmd === "/help") reply = STATS_HELP;
    else if (cmd === "/stats") reply = await reportStats(env, arg ? parseInt(arg, 10) : 7);
    else if (cmd === "/today") reply = await reportToday(env);
    else if (cmd === "/top") reply = await reportTop(env, arg ? parseInt(arg, 10) : 5);
    else if (cmd === "/parallels") reply = await reportParallels(env, arg ? parseInt(arg, 10) : 7);
  } catch (e) {
    reply = `Не удалось получить статистику: ${e.message}`;
  }
  if (reply) await tgCall(env.STATS_BOT_TOKEN, "sendMessage", { chat_id: chatId, text: reply });
}

// ---------- routing ----------

export default {
  async fetch(request, env) {
    if (request.method !== "POST") return new Response("ok");
    const url = new URL(request.url);
    try {
      if (url.pathname === "/idea") {
        if (request.headers.get("X-Telegram-Bot-Api-Secret-Token") !== env.IDEA_WEBHOOK_SECRET) {
          return new Response("forbidden", { status: 403 });
        }
        await handleIdea(await request.json(), env);
        return new Response("ok");
      }
      if (url.pathname === "/stats") {
        if (request.headers.get("X-Telegram-Bot-Api-Secret-Token") !== env.STATS_WEBHOOK_SECRET) {
          return new Response("forbidden", { status: 403 });
        }
        await handleStats(await request.json(), env);
        return new Response("ok");
      }
    } catch (e) {
      console.error(e);
      return new Response("ok"); // всегда 200 — иначе Telegram будет ретраить бесконечно
    }
    return new Response("not found", { status: 404 });
  },
};
