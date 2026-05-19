// Bench UI:
//   - subscribes to /events (SSE) for live touches + predictions
//   - exposes a manual form that POSTs to /predict for ad-hoc inference
//
// Two prediction surfaces:
//   • "Live prediction" panel — driven by SSE; only updates on opponent good receptions
//   • "Manual prediction" panel — driven by the form; updates on Predict click

const HISTORY_MAX = 14;

// ───── Live SSE elements ─────────────────────────────────────────────
const statusEl = document.getElementById("status");
const triggerStateEl = document.getElementById("trigger-state");
const topkEl = document.getElementById("topk");
const noteEl = document.getElementById("predictor-note");
const featuresEl = document.getElementById("features-fields");
const lastTouchEl = document.getElementById("last-touch-fields");
const historyEl = document.getElementById("history-list");

// ───── Manual form elements ─────────────────────────────────────────
const manualForm = document.getElementById("manual-form");
const manualTopkEl = document.getElementById("manual-topk");
const manualNoteEl = document.getElementById("manual-note");
const manualErrorEl = document.getElementById("manual-error");
const fillFromLiveBtn = document.getElementById("manual-fill-from-live");

// Last live PredictionInput received, used by "Fill from last live trigger".
let lastLiveFeatures = null;

const FEATURE_ORDER = [
  ["match_id", "match_id"],
  ["segment_id", "segment_id"],
  ["set_number", "set_number"],
  ["point_id", "point_id"],
  ["score_diff", "score_diff"],
  ["setter_position", "setter_position"],
  ["setter_id", "setter_id"],
  ["reception_quality", "reception_quality"],
  ["consecutive_same", "consecutive_same"],
  ["timeout_active_3", "timeout_active_3"],
  ["prev_1", "prev_1"],
  ["prev_2", "prev_2"],
  ["prev_3", "prev_3"],
  ["prev_4", "prev_4"],
  ["prev_5", "prev_5"],
];

const NUMERIC_KEYS = new Set([
  "segment_id", "set_number", "point_id", "score_diff", "setter_position",
  "consecutive_same", "timeout_active_3",
]);

// Form fields that should be sent as integers (or null if blank).
const INT_FIELDS = new Set([
  "segment_id", "set_number", "point_id", "score_diff", "setter_position",
  "consecutive_same", "timeout_active_3",
]);

// Form fields that may be null/blank.
const NULLABLE_FIELDS = new Set([
  "match_id", "point_id", "setter_position", "setter_id",
]);

function setStatus(text, cls) {
  statusEl.textContent = text;
  statusEl.className = "status " + cls;
}

function setTrigger(armed) {
  if (armed) {
    triggerStateEl.textContent = "armed";
    triggerStateEl.className = "badge badge--armed";
  } else {
    triggerStateEl.textContent = "waiting…";
    triggerStateEl.className = "badge badge--idle";
  }
}

function renderTopK(target, topK) {
  if (!topK || topK.length === 0) {
    target.innerHTML = '<li class="topk__placeholder">No prediction.</li>';
    return;
  }
  target.innerHTML = "";
  topK.forEach(([category, prob], i) => {
    const li = document.createElement("li");
    li.innerHTML = `
      <span><span class="topk__rank">${i + 1}.</span> <span class="topk__category">${escapeHtml(category)}</span></span>
      <span class="topk__prob">${(prob * 100).toFixed(1)}%</span>
    `;
    target.appendChild(li);
  });
}

function renderFeatures(features) {
  if (!features) {
    featuresEl.innerHTML = '<dt>—</dt><dd class="is-empty">awaiting opponent reception</dd>';
    return;
  }
  featuresEl.innerHTML = FEATURE_ORDER
    .map(([label, key]) => {
      const v = features[key];
      const isEmpty = v === null || v === undefined || v === "" || v === "None";
      const cls = isEmpty ? "is-empty" : (NUMERIC_KEYS.has(key) ? "is-numeric" : "");
      const display = isEmpty ? "—" : String(v);
      return `<dt>${label}</dt><dd class="${cls}">${escapeHtml(display)}</dd>`;
    })
    .join("");
}

function renderLastTouch(touch) {
  if (!touch) {
    lastTouchEl.innerHTML = "<dt>—</dt><dd>—</dd>";
    return;
  }
  const rows = [
    ["Sequence", touch.sequence],
    ["Team", touch.team_side],
    ["Player", touch.player_number ?? "—"],
    ["Skill", touch.skill],
    ["Evaluation", touch.evaluation_code || "—"],
    ["Attack code", touch.attack_code ?? "—"],
    ["Set code", touch.set_code ?? "—"],
    ["Start zone", touch.start_zone ?? "—"],
    ["End zone", touch.end_zone ?? "—"],
    ["Phase", touch.phase ?? "—"],
  ];
  lastTouchEl.innerHTML = rows
    .map(([k, v]) => `<dt>${k}</dt><dd>${escapeHtml(String(v))}</dd>`)
    .join("");
}

function appendHistory(touch, isTrigger) {
  const li = document.createElement("li");
  const side = touch.team_side === "home" ? "H" : "V";
  li.innerHTML = `<strong>#${touch.sequence}</strong> ${side} ${touch.skill}${escapeHtml(touch.evaluation_code || "")} ${touch.attack_code ? `(${escapeHtml(touch.attack_code)})` : ""}`;
  if (isTrigger) li.className = "is-trigger";
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

// ───── Manual form ──────────────────────────────────────────────────

function collectFormPayload() {
  const fd = new FormData(manualForm);
  const payload = {};
  for (const [key, raw] of fd.entries()) {
    const str = String(raw).trim();
    if (str === "" && NULLABLE_FIELDS.has(key)) {
      payload[key] = null;
      continue;
    }
    if (INT_FIELDS.has(key)) {
      if (str === "") {
        if (NULLABLE_FIELDS.has(key)) payload[key] = null;
        // else: omit, let backend default apply
        continue;
      }
      const n = Number(str);
      if (!Number.isFinite(n)) {
        throw new Error(`${key} must be a number (got "${str}")`);
      }
      payload[key] = Math.trunc(n);
      continue;
    }
    payload[key] = str;
  }
  return payload;
}

function setManualError(msg) {
  if (!msg) {
    manualErrorEl.hidden = true;
    manualErrorEl.textContent = "";
  } else {
    manualErrorEl.hidden = false;
    manualErrorEl.textContent = msg;
  }
}

async function submitManual(event) {
  event.preventDefault();
  setManualError(null);

  let payload;
  try {
    payload = collectFormPayload();
  } catch (err) {
    setManualError(err.message);
    return;
  }

  try {
    const res = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const text = await res.text();
      setManualError(`HTTP ${res.status}: ${text.slice(0, 200)}`);
      return;
    }
    const prediction = await res.json();
    renderTopK(manualTopkEl, prediction.top_k);
    manualNoteEl.textContent = `predictor: ${prediction.note} · manual prediction #${prediction.prediction_count}`;
  } catch (err) {
    setManualError(`network error: ${err.message}`);
  }
}

function fillFormFromLive() {
  if (!lastLiveFeatures) {
    setManualError("no live trigger yet — wait for a green-highlighted touch to appear first.");
    return;
  }
  setManualError(null);
  for (const el of manualForm.elements) {
    if (!el.name) continue;
    const v = lastLiveFeatures[el.name];
    if (v === null || v === undefined) {
      el.value = "";
    } else {
      el.value = String(v);
    }
  }
}

// ───── SSE connect ──────────────────────────────────────────────────

function connect() {
  setStatus("connecting…", "status--idle");
  setTrigger(false);
  renderFeatures(null);

  const es = new EventSource("/events");

  es.addEventListener("open", () => setStatus("live", "status--live"));

  es.addEventListener("touch", (e) => {
    try {
      const msg = JSON.parse(e.data);
      renderLastTouch(msg.touch);
      const isTrigger = msg.features !== null && msg.features !== undefined;
      appendHistory(msg.touch, isTrigger);
      if (isTrigger) {
        setTrigger(true);
        lastLiveFeatures = msg.features;
        renderFeatures(msg.features);
        renderTopK(topkEl, msg.prediction?.top_k);
        noteEl.textContent = msg.prediction?.note
          ? `predictor: ${msg.prediction.note} · prediction #${msg.prediction.prediction_count}`
          : "";
      } else {
        setTrigger(false);
      }
    } catch (err) {
      console.error("bad SSE payload", err, e.data);
    }
  });

  es.addEventListener("ping", () => { /* keepalive */ });

  es.addEventListener("error", () => {
    setStatus("disconnected — retrying", "status--error");
  });
}

manualForm.addEventListener("submit", submitManual);
fillFromLiveBtn.addEventListener("click", fillFormFromLive);

connect();
