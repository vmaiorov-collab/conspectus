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

// ---------- stats-bot ----------
// /stats, /today, /top — через GoatCounter (основной счётчик, стоит на всех
// страницах). /parallels дополнительно сверяет с Cloudflare Web Analytics —
// вторым, независимым источником, если он настроен.

// ВНИМАНИЕ: это НЕ beacon-токен со страниц (82e37604...) — тот публичный
// "site_token" отличается от внутреннего "site_tag", который требует
// GraphQL. Настоящий site_tag получен через REST
// GET /accounts/{id}/rum/site_info/list (нужно право Account Settings: Read).
const CF_SITE_TAG = "3bc7a8e85403493792aa3186fcccc856";

const PARALLEL_LABELS = {
  "parallel-a": "Параллель A",
  "parallel-ap": "Параллель A'",
  "parallel-b": "Параллель B",
  "parallel-bp": "Параллель B'",
  "parallel-c": "Параллель C",
};

// Публичный site-код из data-goatcounter на страницах (не секрет).
const GC_SITE = "vmaiorov";

function parallelKey(requestPath) {
  let segs = (requestPath || "/").split("/").filter(Boolean);
  if (segs[0] === "conspectus") segs = segs.slice(1);
  return PARALLEL_LABELS[segs[0]] || "Главная / прочее";
}

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

async function fetchTopPaths(env, start, end, limit) {
  const query = `
    query($accountTag: string, $siteTag: string, $start: Time, $end: Time, $limit: Int!) {
      viewer { accounts(filter: {accountTag: $accountTag}) {
        rumPageloadEventsAdaptiveGroups(
          limit: $limit,
          filter: {siteTag: $siteTag, datetime_geq: $start, datetime_leq: $end},
          orderBy: [count_DESC]
        ) { dimensions { requestPath } count }
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

async function gcFetchHits(env, start, limit) {
  const url = new URL(`https://${GC_SITE}.goatcounter.com/api/v0/stats/hits`);
  url.searchParams.set("start", start.toISOString());
  url.searchParams.set("limit", String(limit));
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${env.GC_API_TOKEN}` },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(JSON.stringify(data));
  return data.hits || [];
}

// /stats/total: "total"/"total_utc" — это всё-время тотал (не фильтруется по
// start/end), а по дням в нужном окне нужно суммировать stats[].daily.
async function gcFetchTotal(env, start, end) {
  const url = new URL(`https://${GC_SITE}.goatcounter.com/api/v0/stats/total`);
  url.searchParams.set("start", start.toISOString());
  url.searchParams.set("end", end.toISOString());
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${env.GC_API_TOKEN}` },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(JSON.stringify(data));
  return data.stats || [];
}

function startOfDayUTC(d) {
  const x = new Date(d);
  x.setUTCHours(0, 0, 0, 0);
  return x;
}

async function reportStats(env, days) {
  const end = new Date();
  const start = startOfDayUTC(new Date(end.getTime() - days * 86400000));
  const stats = await gcFetchTotal(env, start, end);
  const todayStr = startOfDayUTC(end).toISOString().slice(0, 10);
  const entries = stats.filter((s) => s.day <= todayStr);
  const total = entries.reduce((a, s) => a + s.daily, 0);
  const avg = entries.length ? total / entries.length : 0;
  const lines = [
    `📊 Статистика conspectus за ${days} дн. (GoatCounter)`,
    `Всего визитов: ${total} (в среднем ${avg.toFixed(1)}/день)`,
  ];
  if (entries.length) {
    const best = entries.reduce((a, b) => (b.daily > a.daily ? b : a));
    lines.push(`Самый активный день: ${best.day} — ${best.daily}`);
  } else {
    lines.push("Данных пока нет.");
  }
  return lines.join("\n");
}

async function reportToday(env) {
  const end = new Date();
  const start = startOfDayUTC(end);
  const stats = await gcFetchTotal(env, start, end);
  const todayStr = start.toISOString().slice(0, 10);
  const today = stats.find((s) => s.day === todayStr);
  return `Сегодня визитов: ${today ? today.daily : 0}`;
}

async function reportTop(env, n) {
  const end = new Date();
  const start = new Date(end.getTime() - 7 * 86400000);
  const hits = await gcFetchHits(env, start, 100);
  if (!hits.length) return "За последние 7 дней пока нет данных.";
  const rows = hits.slice().sort((a, b) => b.count - a.count).slice(0, n);
  const lines = [`Топ-${n} страниц за 7 дней (GoatCounter, просмотров):`];
  rows.forEach((h, i) => {
    lines.push(` ${i + 1}. ${h.path || "/"} — ${h.count}`);
  });
  return lines.join("\n");
}

async function reportParallels(env, days) {
  const end = new Date();
  const start = startOfDayUTC(new Date(end.getTime() - days * 86400000));

  const lines = [`📊 Просмотры по параллелям за ${days} дн.:`];

  try {
    const rows = await fetchTopPaths(env, start, end, 100);
    const totals = {};
    for (const r of rows) totals[parallelKey(r.dimensions.requestPath)] = (totals[parallelKey(r.dimensions.requestPath)] || 0) + r.count;
    lines.push("", "Cloudflare (RUM):");
    if (Object.keys(totals).length) {
      Object.entries(totals)
        .sort((a, b) => b[1] - a[1])
        .forEach(([name, visits]) => lines.push(` ${name} — ${visits}`));
    } else {
      lines.push(" пока нет данных");
    }
  } catch (e) {
    lines.push("", `Cloudflare: ошибка — ${e.message}`);
  }

  try {
    const hits = await gcFetchHits(env, start, 100);
    const totals = {};
    for (const h of hits) totals[parallelKey(h.path)] = (totals[parallelKey(h.path)] || 0) + h.count;
    lines.push("", "GoatCounter:");
    if (Object.keys(totals).length) {
      Object.entries(totals)
        .sort((a, b) => b[1] - a[1])
        .forEach(([name, visits]) => lines.push(` ${name} — ${visits}`));
    } else {
      lines.push(" пока нет данных");
    }
  } catch (e) {
    lines.push("", `GoatCounter: ошибка — ${e.message}`);
  }

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
