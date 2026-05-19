"""Replay a Volleymetrics CSV export into a `.dvw` file, simulating live scouting.

Reads `Play-by-Play.csv` row-by-row, projects each playable row into one
"extended scout-code" line, and appends it to the watched `.dvw` file with
a configurable delay. The backend ingestor sees those lines exactly as it
would during a live match.

Line format (dev only — not strict DataVolley):

    <scout_code>|<json_context>

Where `scout_code` is a fixed-position 12-char DataVolley scout code and
`json_context` is a compact JSON object carrying match-level context the
12-char scout code can't represent (score, set/point id, phase, etc.).
The backend parser reads both halves; production DVW would put this same
context in extra positional fields of the full scout-code line.

Usage:
    python scripts/replay_csv_to_dvw.py \\
        --csv Play-by-Play.csv \\
        --out data/live.dvw \\
        --delay 1.0 \\
        --reset

Flags:
    --reset   truncate the output file before starting (default: append)
    --delay   seconds between emitted plays (default 1.0; use 0 for max speed)
    --limit   stop after N plays (default: no limit)
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from typing import Optional

# Map the CSV's human-readable skill_type to a single DataVolley skill char.
# Order matters: check "reception" before "serve" so reception rows aren't
# misclassified as serves.
_SKILL_KEYWORDS: tuple[tuple[str, str], ...] = (
    ("reception", "R"),
    ("serve", "S"),
    ("attack", "A"),
    ("block", "B"),
    ("dig", "D"),
    ("set", "E"),
    ("freeball", "F"),
    ("free", "F"),
)


def _skill_char(skill_type: str) -> Optional[str]:
    s = skill_type.lower().strip()
    if not s:
        return None
    for needle, code in _SKILL_KEYWORDS:
        if needle in s:
            return code
    return None


def _team_marker(row: dict[str, str]) -> Optional[str]:
    team = row.get("team", "").strip()
    home = row.get("home_team", "").strip()
    visiting = row.get("visiting_team", "").strip()
    if not team:
        return None
    if team == home:
        return "*"
    if team == visiting:
        return "a"
    return None


def _scout_code(row: dict[str, str]) -> Optional[str]:
    """Build the 12-char fixed-position scout code. Returns None to skip the row."""
    team_marker = _team_marker(row)
    if team_marker is None:
        return None
    skill = _skill_char(row.get("skill_type", ""))
    if skill is None:
        return None

    player_raw = row.get("player_number", "").strip()
    try:
        player = f"{int(player_raw):02d}" if player_raw else "~~"
    except ValueError:
        player = "~~"

    evaluation = (row.get("evaluation_code") or "~").strip()[:1] or "~"

    subtype_source = row.get("attack_code") if skill == "A" else row.get("set_code") if skill == "E" else ""
    subtype = (subtype_source or "").strip()
    if len(subtype) >= 2:
        subtype_chars = subtype[:2]
    elif len(subtype) == 1:
        subtype_chars = subtype + "~"
    else:
        subtype_chars = "~~"

    start_zone = (row.get("start_zone") or "").strip()
    end_zone = (row.get("end_zone") or "").strip()
    sz = start_zone if start_zone.isdigit() and len(start_zone) == 1 else "~"
    ez = end_zone if end_zone.isdigit() and len(end_zone) == 1 else "~"

    chars = ["~"] * 12
    chars[0] = team_marker
    chars[1] = player[0]
    chars[2] = player[1]
    chars[3] = skill
    chars[4] = evaluation
    chars[5] = subtype_chars[0]
    chars[6] = subtype_chars[1]
    chars[9] = sz
    chars[11] = ez
    return "".join(chars)


def _context(row: dict[str, str]) -> dict:
    """Extract the match-level context the 12-char scout code can't carry."""
    def _int(key: str) -> Optional[int]:
        v = (row.get(key) or "").strip()
        try:
            return int(v)
        except (ValueError, TypeError):
            return None

    def _str(key: str) -> Optional[str]:
        v = (row.get(key) or "").strip()
        return v or None

    is_timeout = (row.get("timeout") or "").strip().lower() == "t"
    ctx = {
        "m": _str("match_id"),
        "s": _int("set_number"),
        "p": _int("point_id"),
        "hs": _int("home_score"),
        "vs": _int("visiting_score"),
        "hsp": _int("home_setter_position"),
        "vsp": _int("visiting_setter_position"),
        # Use the CSV's `phase` column (NOT `attack_phase`). Training code's
        # FBSO filter is `point_df['phase'] == 'Reception'`, which is the
        # downstream truth for prev_1..prev_5 / consecutive_same.
        "ph": _str("phase"),
        "sid": _str("set_player_id"),
        "pd": _int("point_differential"),
        "to": True if is_timeout else None,
    }
    # Drop keys with None values to keep the line compact.
    return {k: v for k, v in ctx.items() if v is not None}


def _build_line(row: dict[str, str]) -> Optional[str]:
    code = _scout_code(row)
    if code is None:
        return None
    ctx = _context(row)
    if ctx:
        return f"{code}|{json.dumps(ctx, separators=(',', ':'))}"
    return code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=Path("Play-by-Play.csv"))
    parser.add_argument("--out", type=Path, default=Path("data/live.dvw"))
    parser.add_argument("--delay", type=float, default=1.0, help="seconds between plays")
    parser.add_argument("--limit", type=int, default=0, help="stop after N plays (0 = no limit)")
    parser.add_argument("--reset", action="store_true", help="truncate output before starting")
    args = parser.parse_args()

    if not args.csv.exists():
        print(f"error: {args.csv} not found", file=sys.stderr)
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.reset and args.out.exists():
        args.out.unlink()
    args.out.touch(exist_ok=True)

    emitted = 0
    with args.csv.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            line = _build_line(row)
            if line is None:
                continue
            with args.out.open("a") as out:
                out.write(line + "\n")
            emitted += 1
            print(f"#{emitted} -> {line}")
            if args.limit and emitted >= args.limit:
                break
            if args.delay > 0:
                time.sleep(args.delay)

    print(f"done. emitted {emitted} plays to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
