"""DataVolley scout-code parser.

DataVolley `.dvw` files are line-oriented text files. The relevant lines for
live prediction are the **scout codes** — one line per coded touch — which
start with `*` (home team) or `a` (visiting team). Metadata blocks at the top
of the file start with `3` (e.g. `3PLAYERS-H`, `3ATTACKCOMBOS`) and are
skipped.

Scout code character positions (the subset we need):

    pos  field
    ---  -----
      0  team marker ('*' home, 'a' visiting)
    1-2  player number (2-digit, zero-padded; '~~' if unknown)
      3  skill code: S R A B D E F
      4  evaluation code: # + ! - / =
    5-6  skill subtype (attack combo for skill=A, set call for skill=E)
      9  start zone (digit 1-9, or '~')
     11  end zone (digit 1-9, or '~')

This parser handles the fields the next-attack predictor needs. Fields beyond
that are preserved in `Play.raw` so downstream code can extract more without
re-reading the file.

Rally/score/setter-position tracking is NOT done here — those are stateful and
belong in the feature builder (see `features.py`). The parser is pure: one
line in, zero-or-one `Play` out.

Reference: https://github.com/openvolley/datavolley
"""
from __future__ import annotations

from typing import Optional

from .schemas import Play, Skill

_VALID_SKILLS: set[str] = {"S", "R", "A", "B", "D", "E", "F"}


def parse_scout_line(line: str, *, sequence: int) -> Optional[Play]:
    """Parse one scout-code line. Returns None for non-play lines.

    `sequence` is the monotonic line-order id supplied by the ingestor.
    """
    if not line:
        return None
    line = line.rstrip("\r\n")
    if len(line) < 5:
        return None

    head = line[0]
    if head == "*":
        team_side: str = "home"
    elif head == "a":
        team_side = "visiting"
    else:
        return None

    player_number = _safe_int(line[1:3])

    skill_char = line[3]
    if skill_char not in _VALID_SKILLS:
        return None

    evaluation_code = line[4]

    attack_code: Optional[str] = None
    set_code: Optional[str] = None
    subtype = line[5:7] if len(line) >= 7 else ""
    subtype = subtype.replace("~", "").strip() or None
    if skill_char == "A":
        attack_code = subtype
    elif skill_char == "E":
        set_code = subtype

    start_zone = _safe_digit(line[9]) if len(line) > 9 else None
    end_zone = _safe_digit(line[11]) if len(line) > 11 else None

    return Play(
        sequence=sequence,
        team_side=team_side,  # type: ignore[arg-type]
        player_number=player_number,
        skill=skill_char,  # type: ignore[arg-type]
        evaluation_code=evaluation_code,
        attack_code=attack_code,
        set_code=set_code,
        start_zone=start_zone,
        end_zone=end_zone,
        raw=line,
    )


def _safe_int(s: str) -> Optional[int]:
    s = s.strip().replace("~", "")
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        return None


def _safe_digit(c: str) -> Optional[int]:
    if not c or c == "~" or not c.isdigit():
        return None
    return int(c)
