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

// ---------- оформление ----------

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const SPARK = "▁▂▃▄▅▆▇█";
const WEEKDAYS = ["вс", "пн", "вт", "ср", "чт", "пт", "сб"];
const PERIODS = [1, 7, 30, 90];

function fmtDay(iso) {
  const d = new Date(iso + "T00:00:00Z");
  return `${iso.slice(8, 10)}.${iso.slice(5, 7)} (${WEEKDAYS[d.getUTCDay()]})`;
}

function spark(values, maxLen = 30) {
  if (!values.length) return "";
  let v = values;
  if (v.length > maxLen) {
    const k = Math.ceil(v.length / maxLen);
    v = [];
    for (let i = 0; i < values.length; i += k) v.push(values.slice(i, i + k).reduce((a, b) => a + b, 0));
  }
  const max = Math.max(...v);
  if (max === 0) return SPARK[0].repeat(v.length);
  return v.map((x) => SPARK[Math.min(7, Math.round((x / max) * 7))]).join("");
}

function bar(value, max, width = 10) {
  const n = max ? Math.max(value > 0 ? 1 : 0, Math.round((value / max) * width)) : 0;
  return "█".repeat(n) + "░".repeat(width - n);
}

function delta(cur, prev) {
  if (!prev) return cur ? "новое" : "—";
  const p = Math.round(((cur - prev) / prev) * 100);
  return `${p > 0 ? "▲ +" : p < 0 ? "▼ −" : "• "}${Math.abs(p)}%`;
}

const periodLabel = (d) => (d === 1 ? "сегодня" : `${d} дн.`);

// Список дней [start..today] с нулями для пропущенных.
function fillDays(stats, start, end) {
  const map = new Map(stats.map((s) => [s.day, s.daily]));
  const out = [];
  const last = startOfDayUTC(end).getTime();
  for (let t = startOfDayUTC(start).getTime(); t <= last; t += 86400000) {
    const day = new Date(t).toISOString().slice(0, 10);
    out.push({ day, daily: map.get(day) || 0 });
  }
  return out;
}

// ---------- отчёты (HTML) ----------

async function reportStats(env, days) {
  const end = new Date();
  const span = Math.max(days - 1, 0);
  const start = startOfDayUTC(new Date(end.getTime() - span * 86400000));
  const prevStart = startOfDayUTC(new Date(start.getTime() - days * 86400000));
  const prevEnd = new Date(start.getTime() - 1);
  // GoatCounter обрезает окно по своей таймзоне и теряет край периода, поэтому
  // берём с запасом в сутки с обеих сторон, а нужные дни отбирает fillDays.
  const pad = (d, k) => new Date(d.getTime() + k * 86400000);
  const [cur, prev] = await Promise.all([
    gcFetchTotal(env, pad(start, -1), pad(end, 1)),
    gcFetchTotal(env, pad(prevStart, -1), pad(prevEnd, 1)),
  ]);
  const rows = fillDays(cur, start, end);
  const total = rows.reduce((a, s) => a + s.daily, 0);
  const prevTotal = fillDays(prev, prevStart, prevEnd).reduce((a, s) => a + s.daily, 0);
  const avg = rows.length ? total / rows.length : 0;
  const best = rows.reduce((a, b) => (b.daily > a.daily ? b : a), rows[0] || { day: "", daily: 0 });

  const lines = [`📊 <b>Статистика conspectus</b> · ${periodLabel(days)}`, ""];
  lines.push(`👥 Визитов: <b>${total}</b>  <i>${delta(total, prevTotal)} к прошлому периоду (${prevTotal})</i>`);
  if (days > 1) {
    lines.push(`📈 В среднем: <b>${avg.toFixed(1)}</b> в день`);
    if (best.daily > 0) lines.push(`🔥 Рекорд: <b>${best.daily}</b> — ${fmtDay(best.day)}`);
    lines.push("", `<code>${spark(rows.map((r) => r.daily))}</code>`);
    lines.push(`<i>${rows[0].day.slice(8)}.${rows[0].day.slice(5, 7)} → сегодня</i>`);
  }
  if (!total) lines.push("", "Данных пока нет.");
  return lines.join("\n");
}

async function reportTop(env, days, n = 8) {
  const end = new Date();
  const start = startOfDayUTC(new Date(end.getTime() - Math.max(days - 1, 0) * 86400000));
  const hits = await gcFetchHits(env, start, 100);
  const head = `🏆 <b>Топ страниц</b> · ${periodLabel(days)}`;
  if (!hits.length) return `${head}\n\nПока нет данных.`;
  const rows = hits.slice().sort((a, b) => b.count - a.count).slice(0, n);
  const max = rows[0].count;
  const medals = ["🥇", "🥈", "🥉"];
  const lines = [head, ""];
  rows.forEach((h, i) => {
    lines.push(`${medals[i] || `<b>${i + 1}.</b>`} <code>${esc(h.path || "/")}</code>`);
    lines.push(`     <code>${bar(h.count, max)}</code> <b>${h.count}</b>`);
  });
  return lines.join("\n");
}

function sumByParallel(items, getPath, getCount) {
  const totals = {};
  for (const it of items) {
    const k = parallelKey(getPath(it));
    totals[k] = (totals[k] || 0) + getCount(it);
  }
  return Object.entries(totals).sort((a, b) => b[1] - a[1]);
}

function parallelBlock(title, entries) {
  const out = [`<b>${title}</b>`];
  if (!entries.length) return out.concat("  пока нет данных");
  const max = entries[0][1];
  const all = entries.reduce((a, [, v]) => a + v, 0);
  for (const [name, v] of entries) {
    out.push(`  ${esc(name)}`);
    out.push(`  <code>${bar(v, max)}</code> <b>${v}</b> · ${Math.round((v / all) * 100)}%`);
  }
  return out;
}

async function reportParallels(env, days) {
  const end = new Date();
  const start = startOfDayUTC(new Date(end.getTime() - Math.max(days - 1, 0) * 86400000));
  const lines = [`🧩 <b>Просмотры по параллелям</b> · ${periodLabel(days)}`];

  try {
    const hits = await gcFetchHits(env, start, 100);
    lines.push("", ...parallelBlock("🐐 GoatCounter", sumByParallel(hits, (h) => h.path, (h) => h.count)));
  } catch (e) {
    lines.push("", `🐐 GoatCounter: ошибка — ${esc(e.message)}`);
  }
  return lines.join("\n");
}

// ---------- кнопки ----------

const VIEWS = [
  ["stats", "📊 Сводка"],
  ["top", "🏆 Топ"],
  ["par", "🧩 Параллели"],
];

// callback_data: "<view>:<days>", например "stats:7"
function keyboard(view, days) {
  const periods = PERIODS.map((d) => ({
    text: d === days ? `• ${d === 1 ? "Сегодня" : d + " дн."} •` : d === 1 ? "Сегодня" : `${d} дн.`,
    callback_data: `${view}:${d}`,
  }));
  const views = VIEWS.map(([v, label]) => ({
    text: v === view ? `✔ ${label}` : label,
    callback_data: `${v}:${days}`,
  }));
  return {
    inline_keyboard: [
      periods,
      views,
      [
        { text: "🔄 Обновить", callback_data: `${view}:${days}` },
        { text: "🌐 Открыть сайт", url: "https://vmaiorov-collab.github.io/conspectus/" },
      ],
    ],
  };
}

async function render(env, view, days) {
  if (view === "top") return reportTop(env, days);
  if (view === "par") return reportParallels(env, days);
  return reportStats(env, days);
}

const STATS_HELP =
  "👋 <b>Бот статистики conspectus</b>\n\n" +
  "Выберите период и раздел кнопками ниже — сообщение обновится на месте.\n\n" +
  "Команды: /stats [дни] · /today · /top [дни] · /parallels [дни]";

function clampDays(arg, def = 7) {
  const n = parseInt(arg, 10);
  return Number.isFinite(n) && n >= 1 ? Math.min(n, 365) : def;
}

async function handleStats(update, env) {
  const token = env.STATS_BOT_TOKEN;

  // нажатие на кнопку
  const cq = update.callback_query;
  if (cq) {
    const m = cq.message;
    if (!m) return;
    const [view, d] = (cq.data || "").split(":");
    const days = clampDays(d);
    let text;
    try {
      text = await render(env, view, days);
    } catch (e) {
      text = `⚠️ Не удалось получить статистику: ${esc(e.message)}`;
    }
    try {
      await tgCall(token, "editMessageText", {
        chat_id: m.chat.id,
        message_id: m.message_id,
        text,
        parse_mode: "HTML",
        disable_web_page_preview: true,
        reply_markup: keyboard(view, days),
      });
      await tgCall(token, "answerCallbackQuery", { callback_query_id: cq.id });
    } catch (e) {
      // «message is not modified» при повторном нажатии — не ошибка
      await tgCall(token, "answerCallbackQuery", {
        callback_query_id: cq.id,
        text: String(e.message).includes("not modified") ? "Уже актуально ✅" : "Ошибка обновления",
      }).catch(() => {});
    }
    return;
  }

  const msg = update.message;
  if (!msg || !msg.text || !msg.text.startsWith("/")) return;
  const chatId = String(msg.chat.id);

  const parts = msg.text.trim().split(/\s+/);
  const cmd = parts[0].split("@")[0].toLowerCase();
  const arg = parts[1];
  let text, view = "stats", days = 7;
  try {
    if (cmd === "/start" || cmd === "/help") {
      text = STATS_HELP;
    } else if (cmd === "/stats") {
      days = clampDays(arg);
      text = await reportStats(env, days);
    } else if (cmd === "/today") {
      days = 1;
      text = await reportStats(env, 1);
    } else if (cmd === "/top") {
      view = "top";
      days = clampDays(arg);
      text = await reportTop(env, days);
    } else if (cmd === "/parallels") {
      view = "par";
      days = clampDays(arg);
      text = await reportParallels(env, days);
    }
  } catch (e) {
    text = `⚠️ Не удалось получить статистику: ${esc(e.message)}`;
  }
  if (text) {
    await tgCall(token, "sendMessage", {
      chat_id: chatId,
      text,
      parse_mode: "HTML",
      disable_web_page_preview: true,
      reply_markup: keyboard(view, days),
    });
  }
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
      if (url.pathname === "/report") {
        // внутренний вызов от olymp-notes-bots: единый бот показывает и эту статистику
        if (!env.REPORT_KEY || request.headers.get("X-Report-Key") !== env.REPORT_KEY) {
          return new Response("forbidden", { status: 403 });
        }
        const { view, days } = await request.json();
        return new Response(await render(env, view, clampDays(days)));
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
