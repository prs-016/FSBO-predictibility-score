"""FastAPI app: serves the frontend and streams predictions over SSE.

Endpoints
---------
GET /             -> serves index.html (the bench UI)
GET /events       -> Server-Sent Events stream of {play, prediction} JSON
GET /healthz      -> liveness check
GET /static/*     -> frontend assets

Run with:
    uvicorn app.backend.main:app --reload --port 8000

Configure the watched DataVolley file with the DVW_PATH environment variable
(default: ./data/live.dvw). Multiple SSE clients can subscribe concurrently;
each gets the same stream of plays as they're parsed from the file.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse

from .ingestor import DvwIngestor
from .predictor import predict as run_predict
from .schemas import Prediction, PredictionInput

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = REPO_ROOT / "app" / "frontend"
DVW_PATH = Path(os.environ.get("DVW_PATH", REPO_ROOT / "data" / "live.dvw"))


class Broadcaster:
    """Fan-out queue: one publisher (ingestor), many subscribers (SSE clients).

    Each subscriber gets its own asyncio.Queue. Slow subscribers are simply
    skipped on overflow rather than backpressuring the publisher — for a
    bench tool that's the right trade-off (a stalled UI shouldn't delay the
    next prediction for everyone else).
    """

    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue[str]] = set()

    def subscribe(self) -> asyncio.Queue[str]:
        q: asyncio.Queue[str] = asyncio.Queue(maxsize=64)
        self._subscribers.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue[str]) -> None:
        self._subscribers.discard(q)

    def publish(self, payload: str) -> None:
        for q in list(self._subscribers):
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                log.warning("dropping SSE message for slow subscriber")


broadcaster = Broadcaster()


async def _ingest_loop(path: Path) -> None:
    """Background task: drain the ingestor and broadcast each touch + (optional) prediction."""
    path.parent.mkdir(parents=True, exist_ok=True)
    ingestor = DvwIngestor(path)
    log.info("ingestor watching %s", path)
    try:
        async for touch, prediction_input, prediction in ingestor.stream():
            payload = json.dumps({
                "touch": touch.model_dump(),
                "features": prediction_input.model_dump() if prediction_input else None,
                "prediction": prediction.model_dump() if prediction else None,
            })
            broadcaster.publish(payload)
    except asyncio.CancelledError:
        log.info("ingest loop cancelled")
        raise
    except Exception:  # noqa: BLE001 — we want to log and keep the server alive
        log.exception("ingest loop crashed")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    task = asyncio.create_task(_ingest_loop(DVW_PATH))
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except (asyncio.CancelledError, Exception):  # noqa: BLE001
            pass


app = FastAPI(title="FSBO live prediction", lifespan=lifespan)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok", "watching": str(DVW_PATH)}


# Counter for the manual prediction path so the response's prediction_count
# is monotonic and distinct from the live ingestor's counter.
_manual_count = 0


@app.post("/predict")
async def predict_manual(payload: PredictionInput) -> Prediction:
    """One-shot prediction from a manually-entered feature row.

    Bypasses the live ingestor entirely — used by the UI's manual-input form
    to exercise the model with arbitrary inputs.
    """
    global _manual_count
    _manual_count += 1
    return run_predict(payload, prediction_count=_manual_count)


@app.get("/events")
async def events(request: Request) -> EventSourceResponse:
    queue = broadcaster.subscribe()

    async def event_generator() -> AsyncIterator[dict]:
        try:
            while True:
                if await request.is_disconnected():
                    return
                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=15.0)
                except asyncio.TimeoutError:
                    # SSE keep-alive comment so proxies don't drop the connection
                    yield {"event": "ping", "data": ""}
                    continue
                yield {"event": "touch", "data": payload}
        finally:
            broadcaster.unsubscribe(queue)

    return EventSourceResponse(event_generator())


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
