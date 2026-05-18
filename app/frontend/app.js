// Bench UI: subscribes to /events (SSE), renders top-K prediction + last play + recent history.

const HISTORY_MAX = 12;

const statusEl = document.getElementById("status");
const topkEl = document.getElementById("topk");
const noteEl = document.getElementById("predictor-note");
const lastPlayEl = document.getElementById("last-play-fields");
const historyEl = document.getElementById("history-list");

function setStatus(text, cls) {
  statusEl.textContent = text;
  statusEl.className = "status " + cls;
}

function renderTopK(topK) {
  if (!topK || topK.length === 0) {
    topkEl.innerHTML = '<li class="topk__placeholder">No prediction yet.</li>';
    return;
  }
  topkEl.innerHTML = "";
  topK.forEach(([category, prob], i) => {
    const li = document.createElement("li");
    li.innerHTML = `
      <span><span class="topk__rank">${i + 1}.</span> <span class="topk__category">${escapeHtml(category)}</span></span>
      <span class="topk__prob">${(prob * 100).toFixed(1)}%</span>
    `;
    topkEl.appendChild(li);
  });
}

function renderLastPlay(play) {
  if (!play) {
    lastPlayEl.innerHTML = "<dt>—</dt><dd>—</dd>";
    return;
  }
  const rows = [
    ["Team", play.team_side],
    ["Player", play.player_number ?? "—"],
    ["Skill", play.skill],
    ["Evaluation", play.evaluation_code || "—"],
    ["Attack code", play.attack_code ?? "—"],
    ["Set code", play.set_code ?? "—"],
    ["Start zone", play.start_zone ?? "—"],
    ["End zone", play.end_zone ?? "—"],
    ["Sequence", play.sequence],
  ];
  lastPlayEl.innerHTML = rows
    .map(([k, v]) => `<dt>${k}</dt><dd>${escapeHtml(String(v))}</dd>`)
    .join("");
}

function appendHistory(play) {
  const li = document.createElement("li");
  const side = play.team_side === "home" ? "H" : "V";
  li.innerHTML = `<strong>#${play.sequence}</strong> ${side} ${play.skill}${escapeHtml(play.evaluation_code || "")} ${play.attack_code ? `(${escapeHtml(play.attack_code)})` : ""}`;
  historyEl.prepend(li);
  while (historyEl.children.length > HISTORY_MAX) {
    historyEl.removeChild(historyEl.lastChild);
  }
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
  ));
}

function connect() {
  setStatus("connecting…", "status--idle");
  const es = new EventSource("/events");

  es.addEventListener("open", () => setStatus("live", "status--live"));

  es.addEventListener("prediction", (e) => {
    try {
      const msg = JSON.parse(e.data);
      renderTopK(msg.prediction?.top_k);
      renderLastPlay(msg.play);
      noteEl.textContent = msg.prediction?.note
        ? `predictor: ${msg.prediction.note} · ${msg.prediction.play_count} plays consumed`
        : "";
      appendHistory(msg.play);
    } catch (err) {
      console.error("bad SSE payload", err, e.data);
    }
  });

  es.addEventListener("ping", () => {
    /* keepalive */
  });

  es.addEventListener("error", () => {
    setStatus("disconnected — retrying", "status--error");
    // EventSource auto-reconnects; we just update UI state.
  });
}

connect();
