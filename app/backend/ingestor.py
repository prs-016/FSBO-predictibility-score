"""DataVolley file ingestor.

Tails a `.dvw` file as the scout writes it, parses each new scout-code line,
and yields `(Play, Prediction)` pairs through an async queue.

The ingestor is intentionally minimal:

  * **Source-agnostic at the file boundary.** Today the source is a local
    path. Tomorrow it could be an HTTP-mounted file from the scout's laptop
    over LAN (the openvolley pattern). Only the path/URL changes; the rest
    of the pipeline stays the same.

  * **No rally bookkeeping.** Scoring, rotation, and rally segmentation
    are stateful concerns that belong in the feature builder. The ingestor
    just streams Plays in file order.

  * **Restart-safe via byte offset.** We remember how many bytes of the
    file we've already consumed so a restart (or rotation) re-reads only
    new content. On truncation/shrinkage we re-read from zero.
"""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import AsyncIterator

from watchfiles import Change, awatch

from .features import FeatureBuilder
from .parser import parse_scout_line
from .predictor import predict
from .schemas import Play, Prediction

log = logging.getLogger(__name__)


class DvwIngestor:
    """Watches a .dvw file and emits (Play, Prediction) pairs as new lines appear."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._offset = 0
        self._sequence = 0
        self._features = FeatureBuilder()

    async def stream(self) -> AsyncIterator[tuple[Play, Prediction]]:
        """Yield (Play, Prediction) pairs as the watched file grows.

        Emits everything currently in the file on startup, then waits for changes.
        """
        # Initial drain — file may already have content (mid-match restart, replay underway).
        async for item in self._drain():
            yield item

        if not self.path.exists():
            log.info("ingestor: %s does not exist yet; awaiting creation", self.path)

        async for changes in awatch(self.path.parent):
            relevant = any(Path(p) == self.path for _change, p in changes)
            if not relevant:
                continue
            async for item in self._drain():
                yield item

    async def _drain(self) -> AsyncIterator[tuple[Play, Prediction]]:
        """Read everything appended since `self._offset` and emit parsed plays."""
        if not self.path.exists():
            return
        size = self.path.stat().st_size
        if size < self._offset:
            # File was truncated/rotated; restart from beginning.
            log.warning("ingestor: %s shrank (%d -> %d); restarting from 0", self.path, self._offset, size)
            self._offset = 0
            self._sequence = 0
            self._features = FeatureBuilder()
        if size == self._offset:
            return

        # Read appended bytes. Holding open briefly is fine for a local file.
        loop = asyncio.get_running_loop()
        chunk = await loop.run_in_executor(None, self._read_appended, size)
        self._offset = size

        for line in chunk.splitlines():
            self._sequence += 1
            play = parse_scout_line(line, sequence=self._sequence)
            if play is None:
                continue
            features = self._features.update(play)
            prediction = predict(features, last_play=play)
            yield play, prediction

    def _read_appended(self, size: int) -> str:
        with open(self.path, "rb") as f:
            f.seek(self._offset)
            data = f.read(size - self._offset)
        # DataVolley files are typically Windows-1252; latin-1 is a safe superset.
        return data.decode("latin-1", errors="replace")
