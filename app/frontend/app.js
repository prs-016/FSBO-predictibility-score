const HISTORY_MAX = 16;

const statusEl     = document.getElementById("status");
const triggerEl    = document.getElementById("trigger-state");
const topkEl       = document.getElementById("topk");
const noteEl       = document.getElementById("predictor-note");
const featuresEl   = document.getElementById("features-fields");
const historyEl    = document.getElementById("history-list");
const manualForm   = document.getElementById("manual-form");
const manualTopkEl = document.getElementById("manual-topk");
const manualNoteEl = document.getElementById("manual-note");
const manualErrEl  = document.getElementById("manual-error");
const fillBtn      = document.getElementById("manual-fill-from-live");
const placeholder  = document.getElementById("result-placeholder");
const homeScoreEl  = document.getElementById("home-score");
const awayScoreEl  = document.getElementById("away-score");
const diffDisplay  = document.getElementById("diff-display");

let lastLiveFeatures = null;

// ── Score diff live display ─────────────────────────────────────────
function updateDiff() {
  const h = parseInt(homeScoreEl.value) || 0;
  const a = parseInt(awayScoreEl.value) || 0;
  const d = h - a;
  diffDisplay.textContent = (d > 0 ? "+" : "") + d;
  diffDisplay.style.color = d > 0 ? "var(--good)" : d < 0 ? "var(--bad)" : "var(--dim)";
}
homeScoreEl.addEventListener("input", updateDiff);
awayScoreEl.addEventListener("input", updateDiff);

function esc(s) {
  return String(s).replace(/[&<>"']/g, c =>
    ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[c]);
}
function setStatus(txt, cls) {
  statusEl.textContent = txt;
  statusEl.className = "status " + cls;
}
function setTrigger(armed) {
  triggerEl.textContent = armed ? "armed ●" : "waiting…";
  triggerEl.className   = "badge" + (armed ? " badge--armed" : "");
}
function showError(msg) {
  manualErrEl.hidden = !msg;
  manualErrEl.textContent = msg || "";
}

// ── Top-K ───────────────────────────────────────────────────────────
function renderTopK(target, topK) {
  if (!topK || !topK.length) {
    target.innerHTML = '<li class="topk__placeholder">No prediction.</li>';
    return;
  }
  const max = topK[0][1] || 1;
  target.innerHTML = "";
  topK.forEach(([cat, prob], i) => {
    const li = document.createElement("li");
    li.style.setProperty("--bar", (prob / max * 100).toFixed(1) + "%");
    li.innerHTML =
      `<span class="topk__rank">${i+1}</span>` +
      `<span class="topk__category">${esc(cat)}</span>` +
      `<span class="topk__prob">${(prob*100).toFixed(1)}%</span>`;
    target.appendChild(li);
  });
}

// ── Feature row ─────────────────────────────────────────────────────
const FEATURE_LABELS = {
  reception_quality:"Reception", set_number:"Set", score_diff:"Score Diff",
  setter_position:"Setter Pos", consecutive_same:"Streak",
  timeout_active_3:"Post-TO",
  prev_1:"Last", prev_2:"−2", prev_3:"−3", prev_4:"−4", prev_5:"−5",
};
const SHOW_FEATURES = ["reception_quality","set_number","score_diff",
  "setter_position","consecutive_same","timeout_active_3",
  "prev_1","prev_2","prev_3","prev_4","prev_5"];

function renderFeatures(features) {
  if (!features) {
    featuresEl.innerHTML = '<dt>—</dt><dd>awaiting trigger</dd>';
    return;
  }
  featuresEl.innerHTML = SHOW_FEATURES.map(k => {
    const v = features[k];
    const empty = v === null || v === undefined || v === "" || v === "None";
    return `<dt>${FEATURE_LABELS[k]||k}</dt><dd class="${empty?"empty":""}">${esc(empty?"—":String(v))}</dd>`;
  }).join("");
}

// ── History ─────────────────────────────────────────────────────────
function appendHistory(touch, isTrigger) {
  const li = document.createElement("li");
  const side = touch.team_side === "home" ? "H" : "V";
  const atk  = touch.attack_code ? ` (${esc(touch.attack_code)})` : "";
  li.innerHTML = `<strong>#${touch.sequence}</strong> ${side} · ${touch.skill}${esc(touch.evaluation_code||"")}${atk}`;
  if (isTrigger) li.className = "trigger";
  historyEl.prepend(li);
  while (historyEl.children.length > HISTORY_MAX) historyEl.removeChild(historyEl.lastChild);
}

// ── Manual form ─────────────────────────────────────────────────────
const INT_FIELDS  = new Set(["set_number","consecutive_same","timeout_active_3"]);
const NULL_FIELDS = new Set(["setter_position","setter_id"]);

function collectPayload() {
  const fd = new FormData(manualForm);
  const out = {};

  // Compute score_diff from the two separate score inputs
  const home = parseInt(homeScoreEl.value) || 0;
  const away = parseInt(awayScoreEl.value) || 0;
  out.score_diff = home - away;

  // setter_position: convert to int or null
  const sp = manualForm.querySelector('[name="setter_position"]').value.trim();
  out.setter_position = sp ? parseInt(sp) : null;

  for (const [k, raw] of fd.entries()) {
    if (k === "setter_position") continue; // handled above
    const s = String(raw).trim();
    if (INT_FIELDS.has(k)) {
      out[k] = parseInt(s) || 0; continue;
    }
    out[k] = s;
  }
  return out;
}

manualForm.addEventListener("submit", async e => {
  e.preventDefault();
  showError(null);

  let payload;
  try { payload = collectPayload(); }
  catch (err) { showError(err.message); return; }

  manualTopkEl.hidden = false;
  manualTopkEl.innerHTML = '<li class="topk__placeholder">Running model…</li>';
  if (placeholder) placeholder.hidden = true;

  try {
    const res = await fetch("/predict", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      showError(`Server error ${res.status}: ${(await res.text()).slice(0,200)}`);
      manualTopkEl.innerHTML = '<li class="topk__placeholder">Error.</li>';
      return;
    }
    const pred = await res.json();
    renderTopK(manualTopkEl, pred.top_k);
    manualNoteEl.textContent = `${pred.note} · prediction #${pred.prediction_count}`;
  } catch (err) {
    showError("Network error: " + err.message);
    manualTopkEl.innerHTML = '<li class="topk__placeholder">Network error.</li>';
  }
});

// Reset also resets the score display
manualForm.addEventListener("reset", () => {
  setTimeout(updateDiff, 0);
  if (placeholder) placeholder.hidden = false;
  manualTopkEl.hidden = true;
  manualNoteEl.textContent = "";
  showError(null);
});

fillBtn.addEventListener("click", () => {
  if (!lastLiveFeatures) {
    showError("No live trigger yet — wait for a green touch to appear in the history below.");
    return;
  }
  showError(null);
  // score_diff → split back into home/away (can't know exact scores, just show diff)
  const diff = lastLiveFeatures.score_diff || 0;
  homeScoreEl.value = diff > 0 ? diff : 0;
  awayScoreEl.value = diff < 0 ? -diff : 0;
  updateDiff();
  for (const el of manualForm.elements) {
    if (!el.name || !(el.name in lastLiveFeatures)) continue;
    const v = lastLiveFeatures[el.name];
    el.value = (v === null || v === undefined) ? "" : String(v);
  }
});

// ── SSE ─────────────────────────────────────────────────────────────
function connect() {
  setStatus("connecting…", "status--idle");
  setTrigger(false);
  renderFeatures(null);

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
    } catch (err) { console.error("SSE parse error", err); }
  });
  es.addEventListener("ping", () => {});
  es.addEventListener("error", () => setStatus("disconnected — retrying", "status--error"));
}

connect();
