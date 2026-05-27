const HISTORY_MAX = 16;

const statusEl      = document.getElementById("status");
const triggerEl     = document.getElementById("trigger-state");
const topkEl        = document.getElementById("topk");
const noteEl        = document.getElementById("predictor-note");
const featuresEl    = document.getElementById("features-fields");
const historyEl     = document.getElementById("history-list");
const manualForm    = document.getElementById("manual-form");
const manualTopkEl  = document.getElementById("manual-topk");
const manualNoteEl  = document.getElementById("manual-note");
const manualErrEl   = document.getElementById("manual-error");
const fillBtn       = document.getElementById("manual-fill-from-live");
const resultPanel   = document.getElementById("manual-result-panel");

let lastLiveFeatures = null;

// ── helpers ───────────────────────────────────────────────
function esc(s) {
  return String(s).replace(/[&<>"']/g, c =>
    ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[c]);
}
function setStatus(txt, cls) {
  statusEl.textContent = txt; statusEl.className = "status " + cls;
}
function setTrigger(armed) {
  triggerEl.textContent = armed ? "armed ●" : "waiting…";
  triggerEl.className   = "badge" + (armed ? " badge--armed" : "");
}

// ── render top-k with probability bars ───────────────────
function renderTopK(target, topK) {
  if (!topK || !topK.length) {
    target.innerHTML = '<li class="topk__placeholder">No prediction available.</li>';
    return;
  }
  const max = topK[0][1];
  target.innerHTML = "";
  topK.forEach(([cat, prob], i) => {
    const li = document.createElement("li");
    li.style.setProperty("--bar", (prob / (max || 1) * 100).toFixed(1) + "%");
    li.innerHTML =
      `<span class="topk__rank">${i+1}</span>` +
      `<span class="topk__category">${esc(cat)}</span>` +
      `<span class="topk__prob">${(prob*100).toFixed(1)}%</span>`;
    target.appendChild(li);
  });
}

// ── render live feature row ───────────────────────────────
const FEATURE_LABELS = {
  reception_quality: "Reception",
  set_number:        "Set",
  score_diff:        "Score Diff",
  setter_position:   "Setter Pos",
  consecutive_same:  "Streak",
  timeout_active_3:  "Post-TO",
  prev_1: "Last Attack", prev_2: "−2", prev_3: "−3", prev_4: "−4", prev_5: "−5",
  setter_id: "Setter ID",
};
const SHOW_FEATURES = ["reception_quality","set_number","score_diff","setter_position",
                       "consecutive_same","timeout_active_3","prev_1","prev_2","prev_3"];

function renderFeatures(features) {
  if (!features) {
    featuresEl.innerHTML = '<dt>—</dt><dd class="empty">awaiting trigger</dd>';
    return;
  }
  featuresEl.innerHTML = SHOW_FEATURES.map(k => {
    const v = features[k];
    const empty = v === null || v === undefined || v === "" || v === "None";
    return `<dt>${FEATURE_LABELS[k]||k}</dt><dd class="${empty?"empty":""}">${esc(empty?"—":String(v))}</dd>`;
  }).join("");
}

// ── history ───────────────────────────────────────────────
function appendHistory(touch, isTrigger) {
  const li = document.createElement("li");
  const side = touch.team_side === "home" ? "H" : "V";
  const atk  = touch.attack_code ? ` (${esc(touch.attack_code)})` : "";
  li.innerHTML = `<strong>#${touch.sequence}</strong> ${side} · ${touch.skill}${esc(touch.evaluation_code||"")}${atk}`;
  if (isTrigger) li.className = "trigger";
  historyEl.prepend(li);
  while (historyEl.children.length > HISTORY_MAX) historyEl.removeChild(historyEl.lastChild);
}

// ── manual form ───────────────────────────────────────────
const INT_FIELDS = new Set(["score_diff","setter_position","set_number","consecutive_same","timeout_active_3"]);
const NULL_FIELDS = new Set(["setter_position","setter_id","match_id","point_id"]);

function collectPayload() {
  const fd = new FormData(manualForm);
  const out = {};
  for (const [k, raw] of fd.entries()) {
    const s = String(raw).trim();
    if (!s && NULL_FIELDS.has(k)) { out[k] = null; continue; }
    if (INT_FIELDS.has(k)) {
      if (!s) continue;
      const n = Number(s);
      if (!Number.isFinite(n)) throw new Error(`${k} must be a number`);
      out[k] = Math.trunc(n); continue;
    }
    out[k] = s;
  }
  return out;
}

function showError(msg) {
  manualErrEl.hidden = !msg; manualErrEl.textContent = msg || "";
}

manualForm.addEventListener("submit", async e => {
  e.preventDefault(); showError(null);
  let payload;
  try { payload = collectPayload(); } catch(err) { showError(err.message); return; }
  try {
    const res = await fetch("/predict", {
      method: "POST", headers: {"Content-Type":"application/json"},
      body: JSON.stringify(payload)
    });
    if (!res.ok) { showError(`HTTP ${res.status}: ${(await res.text()).slice(0,200)}`); return; }
    const pred = await res.json();
    // Show result
    const placeholder = resultPanel.querySelector(".result-panel__placeholder");
    if (placeholder) placeholder.remove();
    manualTopkEl.hidden = false;
    renderTopK(manualTopkEl, pred.top_k);
    manualNoteEl.textContent = `${pred.note} · prediction #${pred.prediction_count}`;
  } catch(err) { showError("Network error: " + err.message); }
});

fillBtn.addEventListener("click", () => {
  if (!lastLiveFeatures) { showError("no live trigger yet — wait for a green touch in the history."); return; }
  showError(null);
  for (const el of manualForm.elements) {
    if (!el.name || !(el.name in lastLiveFeatures)) continue;
    const v = lastLiveFeatures[el.name];
    el.value = (v === null || v === undefined) ? "" : String(v);
  }
});

// ── SSE ───────────────────────────────────────────────────
function connect() {
  setStatus("connecting…", "status--idle");
  setTrigger(false);
  const es = new EventSource("/events");
  es.addEventListener("open", () => setStatus("live", "status--live"));
  es.addEventListener("touch", e => {
    try {
      const msg = JSON.parse(e.data);
      const isTrigger = !!(msg.features);
      appendHistory(msg.touch, isTrigger);
      if (isTrigger) {
        setTrigger(true);
        lastLiveFeatures = msg.features;
        renderFeatures(msg.features);
        renderTopK(topkEl, msg.prediction?.top_k);
        noteEl.textContent = msg.prediction?.note
          ? `${msg.prediction.note} · #${msg.prediction.prediction_count}` : "";
      } else {
        setTrigger(false);
      }
    } catch(err) { console.error("SSE parse error", err); }
  });
  es.addEventListener("ping", () => {});
  es.addEventListener("error", () => setStatus("disconnected — retrying", "status--error"));
}

connect();
