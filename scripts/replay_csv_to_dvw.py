"""Replay a Volleymetrics CSV export into a `.dvw` file, simulating live scouting.

Reads `Play-by-Play.csv` row-by-row, projects each playable row into one
DataVolley scout-code line, and appends it to the watched `.dvw` file with a
configurable delay. The backend ingestor sees those lines exactly as it would
during a live match.

This is a dev tool — it does not generate fully-spec-compliant DataVolley
files. It only encodes the fields the current parser reads (team, player,
skill, evaluation, attack/set subcode, zones). Other DataVolley fields are
filled with `~` to keep column positions intact.

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


def _build_scout_line(row: dict[str, str]) -> Optional[str]:
    """Project a CSV row into one DataVolley scout-code line, or None to skip."""
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

    # Fixed-position scout code, 12 chars:
    #   0   : team marker (* or a)
    #   1-2 : player number
    #   3   : skill
    #   4   : evaluation
    #   5-6 : skill subtype (attack/set combo)
    #   7-8 : reserved padding
    #   9   : start zone
    #   10  : reserved
    #   11  : end zone
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
    # Touch the file so the backend's watcher sees it immediately.
    args.out.touch(exist_ok=True)

    emitted = 0
    with args.csv.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            line = _build_scout_line(row)
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
