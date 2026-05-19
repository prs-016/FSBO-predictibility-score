"""DataVolley file ingestor.

Tails a `.dvw` file as the scout writes it, parses each new line into a
`Touch`, runs the feature builder, and — when the feature builder emits a
`PredictionInput` (i.e. the opponent just made a good reception) — calls
the predictor. Streams `(Touch, Optional[PredictionInput], Optional[Prediction])`
tuples through an async iterator.

This file owns the file-watch side of the pipeline. Stateful match
bookkeeping lives in `features.py` + `state.py`.
"""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import AsyncIterator, Optional

from watchfiles import awatch

from .features import FeatureBuilder
from .predictor import predict
from .parser import parse_scout_line
from .schemas import Prediction, PredictionInput, TeamSide, Touch

log = logging.getLogger(__name__)


class DvwIngestor:
    """Watches a .dvw file; emits a tuple per parsed touch."""

    def __init__(self, path: Path, *, opponent_side: TeamSide = "visiting") -> None:
        self.path = path
        self._offset = 0
        self._sequence = 0
        self._features = FeatureBuilder(opponent_side=opponent_side)

    async def stream(self) -> AsyncIterator[tuple[Touch, Optional[PredictionInput], Optional[Prediction]]]:
        """Yield `(touch, prediction_input | None, prediction | None)` per parsed line.

        Drains any pre-existing content on startup, then waits for changes.
        """
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

    async def _drain(self) -> AsyncIterator[tuple[Touch, Optional[PredictionInput], Optional[Prediction]]]:
        if not self.path.exists():
            return
        size = self.path.stat().st_size
        if size < self._offset:
            log.warning("ingestor: %s shrank (%d -> %d); restarting from 0", self.path, self._offset, size)
            self._offset = 0
            self._sequence = 0
            self._features = FeatureBuilder(opponent_side=self._features.opponent_side)
        if size == self._offset:
            return

        loop = asyncio.get_running_loop()
        chunk = await loop.run_in_executor(None, self._read_appended, size)
        self._offset = size

        for line in chunk.splitlines():
            self._sequence += 1
            touch = parse_scout_line(line, sequence=self._sequence)
            if touch is None:
                continue
            prediction_input = self._features.update(touch)
            prediction = (
                predict(prediction_input, prediction_count=self._features.prediction_count)
                if prediction_input is not None
                else None
            )
            yield touch, prediction_input, prediction

    def _read_appended(self, size: int) -> str:
        with open(self.path, "rb") as f:
            f.seek(self._offset)
            data = f.read(size - self._offset)
        return data.decode("latin-1", errors="replace")
