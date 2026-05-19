"""DataVolley scout-code parser, plus an extended-dev format with JSON context.

A real DataVolley `.dvw` file is line-oriented. Scout codes start with `*`
(home) or `a` (visiting). Each is a fixed-position string; see the
character map below. Metadata blocks (`3PLAYERS-H`, `3ATTACKCOMBOS`, etc.)
start with `3` and are skipped.

This parser handles **two line forms**:

  1. Production:   `<scout_code>`
       e.g. `*16A#V5~~4~9`
       Match context (score, set number, point id, phase, setter positions)
       is unavailable from a 12-char scout code alone. In production we'll
       extract this from the full DVW line (which is much wider) — those
       extra positions aren't parsed yet; extend when we have a real file.

  2. Dev (replay):  `<scout_code>|<json_context>`
       e.g. `a17R+~~~~5~1|{"m":"…","s":1,"p":7,"hs":3,"vs":5,…}`
       The replay script emits this so the feature builder can be exercised
       end-to-end without a real DVW file. The `|` and JSON are stripped
       before parsing the scout code.

Scout-code character positions:

    pos  field
    ---  -----
      0  team marker ('*' home, 'a' visiting)
    1-2  player number ('~~' if unknown)
      3  skill code: S R A B D E F
      4  evaluation code: # + ! - / =
    5-6  skill subtype (attack combo for skill=A, set call for skill=E)
      9  start zone (digit 1-9, or '~')
     11  end zone (digit 1-9, or '~')
"""
from __future__ import annotations

import json
from typing import Any, Optional

from .schemas import Touch

_VALID_SKILLS: set[str] = {"S", "R", "A", "B", "D", "E", "F"}

# Short-key → long-key map for the dev replay's inline context.
# Keeps replay lines compact while letting Touch fields be self-documenting.
_CTX_KEY_MAP: dict[str, str] = {
    "m": "match_id",
    "s": "set_number",
    "p": "point_id",
    "hs": "home_score",
    "vs": "visiting_score",
    "hsp": "home_setter_position",
    "vsp": "visiting_setter_position",
    "ph": "phase",
    "sid": "set_player_id",
    "pd": "point_differential",
    "to": "is_timeout",
}


def parse_scout_line(line: str, *, sequence: int) -> Optional[Touch]:
    """Parse one line. Returns None for non-play lines (metadata, blanks, garbage)."""
    if not line:
        return None
    line = line.rstrip("\r\n")
    if not line:
        return None

    # Split off the optional dev-replay context.
    context: dict[str, Any] = {}
    if "|" in line:
        scout_part, _, ctx_part = line.partition("|")
        if ctx_part.strip():
            try:
                raw_ctx = json.loads(ctx_part)
                if isinstance(raw_ctx, dict):
                    for short, long in _CTX_KEY_MAP.items():
                        if short in raw_ctx:
                            context[long] = raw_ctx[short]
            except (json.JSONDecodeError, TypeError):
                # Malformed context shouldn't kill the touch — just ignore it.
                pass
        line = scout_part

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

    return Touch(
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
        **context,
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
