# 🏐 FSBO Predictability Score: UCSD Triton Analytics

![Volleyball Analytics Header](assets/header.png)

## 📊 Overview

The **FSBO (First Swing Side Out)** Predictability Score project is a data-driven initiative aimed at decoding the offensive patterns of the **UC San Diego (UCSD) Volleyball** team. By leveraging granular play-by-play data, this project builds a predictive ecosystem to anticipate attack locations following high-quality service receptions.

In elite volleyball, "winning the first swing" is a critical factor in side-out efficiency. This project utilizes machine learning to transform raw historical data into actionable insights for scouting and strategic optimization.

---

## 📂 Data

> **⚠️ Dataset not included in this repository.**
>
> The primary dataset (`combined_dvw.csv`) is **~244 MB** and exceeds GitHub's 100 MB file size limit. It is stored in Google Drive and loaded directly in the model script at runtime:
>
> ```python
> SOURCE_FILE = '/content/drive/MyDrive/combined_dvw.csv'
> ```
>
> To run the model, upload `combined_dvw.csv` to the root of your Google Drive (`My Drive/combined_dvw.csv`) and mount Drive in Colab as normal
---

## 🚀 Key Features

### 🔍 Predictive Intelligence
- **Multi-Class Classification**: Predicts the target attack location across four primary zones: `Front`, `Middle`, `Back`, and `Pipe`.
- **Advanced Modeling**: Orchestrates Gradient Boosting and Neural Network architectures to maximize predictive accuracy.

### 🧠 Temporal Memory Architecture
- **Sliding Window Context**: Incorporates the last 5 attack sequences (`prev_1` through `prev_5`) as inputs, capturing the setter's recent tendencies and situational bias.
- **Momentum Tracking**: Quantifies offensive "streaks" using a `consecutive_same` attack variable to identify repetitive play-calling patterns.

### 📍 Spatial & Contextual Inputs
- **Rotation Logic**: Models the impact of `setter_position` (rotations 1-6) on offensive distribution.
- **Game Flow**: Integrates `score_diff` and `set_number` to account for high-pressure adjustments and late-set decision-making.

---

## 🛠️ Technical Stack

| Category | Tools |
| :--- | :--- |
| **Language** | ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) |
| **Data Processing** | `Pandas`, `NumPy`, `Scikit-Learn` |
| **Machine Learning** | `XGBoost/GradientBoosting`, `PyTorch` |
| **Visualization** | `Seaborn`, `Matplotlib` |

---

## 📈 Exploratory Data Analysis

The project includes a robust EDA suite centered on the **UCSD Triton's** offensive profile:
- **Target Distribution**: Analyzes the frequency of sets to different hitters.
- **Quality Correlation**: Maps `reception_quality` (Perfect vs. Positive) to the eventual attack outcome.
- **Setter Profiling**: Unique identifiers for `setter_id` allow for individual-based tendency tracking.

---

## 📂 Project Structure

```bash
├── fsbo_final_model.py        # Main analytics and modeling script (replaces FSBO_tritonball.ipynb)
├── app/
│   ├── backend/               # FastAPI + SSE backend (ingestor → predictor → /events)
│   │   ├── main.py            # ASGI app + /events SSE stream + /healthz
│   │   ├── ingestor.py        # Watches the live .dvw file, drains new scout codes
│   │   ├── parser.py          # DataVolley scout-code → Play
│   │   ├── features.py        # ⛳ STUB — feature builder (plug real one in here)
│   │   ├── predictor.py       # ⛳ STUB — model interface (plug real model in here)
│   │   └── schemas.py         # Pydantic types (Play, Prediction)
│   └── frontend/              # Bench UI (vanilla HTML + JS, subscribes via SSE)
├── scripts/
│   └── replay_csv_to_dvw.py   # Dev tool — replays combined_dvw.csv into a .dvw file
├── data/                      # Created on first run; default location of live.dvw
├── assets/                    # Project visualizations and branding
└── README.md                  # Project documentation
```

---

## ⚙️ Model — Installation & Usage

1. **Install dependencies**:
   ```bash
   pip install pandas numpy torch scikit-learn seaborn matplotlib
   ```

2. **Add the dataset to Google Drive**:
   Upload `combined_dvw.csv` to the root of your Google Drive (`My Drive/combined_dvw.csv`).

3. **Run the model**:
   Open `fsbo_final_model.py` in Google Colab, mount your Drive when prompted, and execute.

---

## 🛰️ Live Prediction App

A FastAPI backend tails the scout's local DataVolley file (`.dvw`) and pushes
predictions to a browser-based bench UI over Server-Sent Events. The model and
feature builder are currently stubs — they'll be swapped for the real artifacts
in `app/backend/predictor.py` and `app/backend/features.py`.

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run (with simulated live data)

In one terminal — start the backend:

```bash
source .venv/bin/activate
uvicorn app.backend.main:app --reload --port 8000
```

Then open <http://localhost:8000> in a browser. You should see "live" in the
header and an "Awaiting first play…" placeholder.

In a second terminal — replay the historical CSV as if it were live scouting:

```bash
source .venv/bin/activate
python scripts/replay_csv_to_dvw.py --reset --delay 1.0
```

Each emitted play should appear in the UI within ~1 second.

### Run (against a real scout's `.dvw` file)

Set `DVW_PATH` to the scout's safety file. On the same machine:

```bash
DVW_PATH=/path/to/scout/match.dvw uvicorn app.backend.main:app --port 8000
```

Across a LAN: mount or sync the scout's file directory to the bench laptop
(Syncthing or a simple SMB/AFP share works), then point `DVW_PATH` at the
synced copy. Latency on a local network is well under one second — far below
the rally cycle.

### Endpoints

| Path | Purpose |
| :--- | :--- |
| `GET /`         | Bench UI |
| `GET /events`   | Server-Sent Events stream of `{play, prediction}` JSON |
| `GET /healthz`  | Returns `{status, watching}` |

### Plugging the real model in

When the trained model is ready, only two files change:

* `app/backend/features.py` → fill `FeatureBuilder.update` so it returns the feature row your model expects (`prev_1..prev_5`, rotation, score, etc.).
* `app/backend/predictor.py` → load the model artifact at import time and return real `top_k` probabilities from `predict()`.

Everything upstream (ingestor, SSE, UI) is unchanged.

---

## 🏛️ Acknowledgments
This project is dedicated to the **UC San Diego Athletics** department and the Triton Volleyball program. Data processing techniques were developed to enhance competitive performance through advanced sport science and statistical modeling.

---
<p align="center">
  <i>"Predicting the swing before it happens."</i>
</p>
