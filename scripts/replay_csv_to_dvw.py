"""Replay combined_dvw.csv into a .dvw file, simulating live scouting.

Reads combined_dvw.csv row-by-row, projects each playable row into one
"extended scout-code" line, and appends it to the watched .dvw file with
a configurable delay. The backend ingestor sees those lines exactly as it
would during a live match.

Line format (dev only):
    <scout_code>|<json_context>

Usage:
    python scripts/replay_csv_to_dvw.py \
        --csv combined_dvw.csv \
        --out data/live.dvw \
        --delay 0.5 \
        --reset \
        --team-id 1378

Flags:
    --reset    truncate the output file before starting
    --delay    seconds between emitted plays (default 0.5)
    --limit    stop after N plays (0 = no limit)
    --team-id  only replay rows for this team_id (0 = all teams)
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from typing import Optional

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
    for needle, code in _SKILL_KEYWORDS:
        if needle in s:
            return code
    return None


def _team_marker(row: dict) -> Optional[str]:
    """Return '*' (home) or 'a' (visiting) based on team vs home/visiting columns."""
    team    = str(row.get("team", "") or "").strip()
    home    = str(row.get("home_team", "") or "").strip()
    visiting = str(row.get("visiting_team", "") or "").strip()
    if not team:
        return None
    if team == home:
        return "*"
    if team == visiting:
        return "a"
    return None


def _scout_code(row: dict) -> Optional[str]:
    marker = _team_marker(row)
    if marker is None:
        return None
    skill = _skill_char(str(row.get("skill_type", "") or ""))
    if skill is None:
        return None

    player_raw = str(row.get("player_number", "") or "").strip()
    try:
        player = f"{int(float(player_raw)):02d}" if player_raw else "~~"
    except (ValueError, TypeError):
        player = "~~"

    evaluation = str(row.get("evaluation_code", "") or "~").strip()[:1] or "~"

    subtype_src = row.get("attack_code") if skill == "A" else row.get("set_code") if skill == "E" else ""
    subtype = str(subtype_src or "").strip()
    if len(subtype) >= 2:
        subtype_chars = subtype[:2]
    elif len(subtype) == 1:
        subtype_chars = subtype + "~"
    else:
        subtype_chars = "~~"

    sz_raw = str(row.get("start_zone", "") or "").strip()
    ez_raw = str(row.get("end_zone", "") or "").strip()
    sz = sz_raw if sz_raw.isdigit() and len(sz_raw) == 1 else "~"
    ez = ez_raw if ez_raw.isdigit() and len(ez_raw) == 1 else "~"

    chars = ["~"] * 12
    chars[0] = marker
    chars[1] = player[0] if len(player) > 0 else "~"
    chars[2] = player[1] if len(player) > 1 else "~"
    chars[3] = skill
    chars[4] = evaluation
    chars[5] = subtype_chars[0]
    chars[6] = subtype_chars[1]
    chars[9] = sz
    chars[11] = ez
    return "".join(chars)


def _safe_int(row: dict, key: str) -> Optional[int]:
    v = str(row.get(key, "") or "").strip()
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return None


def _safe_str(row: dict, key: str) -> Optional[str]:
    v = str(row.get(key, "") or "").strip()
    return v or None


def _context(row: dict) -> dict:
    # combined_dvw.csv uses home_score / visiting_score (cols 80/81)
    is_timeout = str(row.get("timeout", "") or "").strip().lower() == "t"
    ctx = {
        "m":   _safe_str(row, "match_id"),
        "s":   _safe_int(row, "set_number"),
        "p":   _safe_int(row, "point_id"),
        "hs":  _safe_int(row, "home_score"),
        "vs":  _safe_int(row, "visiting_score"),
        "hsp": _safe_int(row, "home_setter_position"),
        "vsp": _safe_int(row, "visiting_setter_position"),
        "ph":  _safe_str(row, "phase"),
        "sid": _safe_str(row, "set_player_id"),
        "pd":  _safe_int(row, "point_differential"),
        "to":  True if is_timeout else None,
    }
    return {k: v for k, v in ctx.items() if v is not None}


def _build_line(row: dict) -> Optional[str]:
    code = _scout_code(row)
    if code is None:
        return None
    ctx = _context(row)
    return f"{code}|{json.dumps(ctx, separators=(',', ':'))}" if ctx else code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv",     type=Path,  default=Path("combined_dvw.csv"))
    parser.add_argument("--out",     type=Path,  default=Path("data/live.dvw"))
    parser.add_argument("--delay",   type=float, default=0.5)
    parser.add_argument("--limit",   type=int,   default=0)
    parser.add_argument("--reset",   action="store_true")
    parser.add_argument("--team-id", type=str,   default="",
                        help="filter to this team_id (e.g. 1378 for UCSD); 0 or blank = all teams")
    args = parser.parse_args()

    if not args.csv.exists():
        print(f"error: {args.csv} not found. Pass --csv path/to/combined_dvw.csv", file=sys.stderr)
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.reset and args.out.exists():
        args.out.unlink()
    args.out.touch(exist_ok=True)

    team_filter = str(args.team_id).strip()

    emitted = 0
    with args.csv.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if team_filter and team_filter not in ("0", ""):
                row_tid = str(row.get("team_id", "") or "").strip()
                # Handle float-formatted IDs e.g. "1378.0"
                try:
                    if int(float(row_tid)) != int(float(team_filter)):
                        continue
                except (ValueError, TypeError):
                    continue

            line = _build_line(row)
            if line is None:
                continue

            with args.out.open("a") as out:
                out.write(line + "\n")

            emitted += 1
            print(f"#{emitted} {line[:80]}")

            if args.limit and emitted >= args.limit:
                break
            if args.delay > 0:
                time.sleep(args.delay)

    print(f"done. emitted {emitted} plays -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
