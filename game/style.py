"""ANSI colour helpers.

The engine's text is structured — location headers, NPC names, enemy
threats, quest tags, lore titles, rep deltas, item names — and colour
helps the eye sort them at a glance. This module is a narrow wrapper
that gives every call-site a short helper (`style.npc(name)`,
`style.enemy(name)`, `style.loc(name)`, …) and lets the engine flip
colour off for tests, pipes, or terminals that don't want it.

Policy:

* Colour is **off by default**. The engine's REPL enables it once at
  boot when stdout is a TTY and the environment doesn't request
  no-colour via `NO_COLOR` or `CLICOLOR=0`.
* `--no-color` on the CLI forces it off.
* Tests that construct `Game` directly never see colour because the
  REPL path isn't executed.
* Every helper is a no-op when colour is off — the raw string passes
  through unchanged. This keeps `"expected" in text` assertions honest.
"""
from __future__ import annotations
import os
import sys
from typing import Optional


# ANSI SGR sequences. Keep this tight — a handful of semantic names, not
# every colour under the sky. The goal is a consistent palette, not a
# holiday lights display.
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

FG_BLACK   = "\033[30m"
FG_RED     = "\033[31m"
FG_GREEN   = "\033[32m"
FG_YELLOW  = "\033[33m"
FG_BLUE    = "\033[34m"
FG_MAGENTA = "\033[35m"
FG_CYAN    = "\033[36m"
FG_WHITE   = "\033[37m"

BRIGHT_RED     = "\033[91m"
BRIGHT_GREEN   = "\033[92m"
BRIGHT_YELLOW  = "\033[93m"
BRIGHT_BLUE    = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN    = "\033[96m"
BRIGHT_WHITE   = "\033[97m"


# Module-level switch. Engine flips this in repl().
_enabled = False
# Whether the caller has explicitly set the value (via --color / --no-color
# or a `color on|off` command). When True, auto_detect() becomes a no-op
# so CLI flags aren't silently overridden by TTY detection.
_explicit = False


def enabled() -> bool:
    return _enabled


def set_enabled(on: bool) -> None:
    """Turn colour on or off globally. Marks the setting explicit."""
    global _enabled, _explicit
    _enabled = bool(on)
    _explicit = True


def is_explicit() -> bool:
    return _explicit


def auto_detect(force: Optional[bool] = None) -> bool:
    """Decide whether colour should be on.

    * `force=True`  → enable unconditionally (explicit).
    * `force=False` → disable unconditionally (explicit).
    * `force=None`  → honor environment and TTY:
        - `NO_COLOR` set (any value, even empty) → off.
        - `CLICOLOR=0` → off.
        - `CLICOLOR_FORCE=1` → on regardless of TTY.
        - stdout must be a TTY otherwise → off.
        - else → on.
        The auto-detect result is **not** marked explicit, so a later
        explicit call can still override it.
    Returns the final enabled state.
    """
    global _enabled
    if force is True:
        set_enabled(True)
        return True
    if force is False:
        set_enabled(False)
        return False
    if "NO_COLOR" in os.environ:
        _enabled = False
        return False
    if os.environ.get("CLICOLOR") == "0":
        _enabled = False
        return False
    if os.environ.get("CLICOLOR_FORCE") == "1":
        _enabled = True
        return True
    try:
        is_tty = sys.stdout.isatty()
    except Exception:
        is_tty = False
    _enabled = is_tty
    return is_tty


# ---- Low-level wrap -------------------------------------------------------

def wrap(s: str, *codes: str) -> str:
    """Wrap `s` in the given SGR codes. No-op when colour is disabled."""
    if not _enabled or not s:
        return s
    return "".join(codes) + s + RESET


# ---- Semantic helpers -----------------------------------------------------
# These are the names the engine should reach for. Keep the palette stable.

def title(s: str) -> str:
    """Region / location titles, section headers."""
    return wrap(s, BOLD, BRIGHT_WHITE)


def loc(s: str) -> str:
    """Location names inline (e.g. 'Verdant Bamboo Sea' in the prompt)."""
    return wrap(s, BRIGHT_CYAN)


def region(s: str) -> str:
    return wrap(s, DIM, FG_CYAN)


def npc(s: str) -> str:
    """An ally, vendor, quest-giver, or neutral NPC."""
    return wrap(s, BRIGHT_GREEN)


def enemy(s: str) -> str:
    """A hostile / combat-target."""
    return wrap(s, BRIGHT_RED)


def companion(s: str) -> str:
    """Your bonded ally (a stronger green, more saturated than NPC)."""
    return wrap(s, BOLD, BRIGHT_GREEN)


def quest(s: str) -> str:
    """Quest names, [QUEST ACCEPTED], [QUEST COMPLETE] tags."""
    return wrap(s, BRIGHT_YELLOW)


def lore(s: str) -> str:
    """Lore titles, [Lore recorded] tag."""
    return wrap(s, FG_YELLOW)


def item(s: str) -> str:
    """Item names in listings, drops, rewards."""
    return wrap(s, BRIGHT_CYAN)


def technique(s: str) -> str:
    return wrap(s, BRIGHT_MAGENTA)


def realm(s: str) -> str:
    return wrap(s, FG_MAGENTA)


def rep_delta(value: int) -> str:
    """Reputation delta — green when friendly, red when hostile, dim when 0."""
    if value > 0:
        return wrap(f"+{value}", BRIGHT_GREEN)
    if value < 0:
        return wrap(str(value), BRIGHT_RED)
    return wrap("+0", DIM)


def rep_value(value: int) -> str:
    """A rep value (not a delta). Signed, colored."""
    if value > 0:
        return wrap(f"+{value}", FG_GREEN)
    if value < 0:
        return wrap(f"{value}", FG_RED)
    return wrap("0", DIM)


def sect_aligned(alignment: str, s: str) -> str:
    """Color a sect name by its alignment."""
    a = (alignment or "").lower()
    if a == "righteous":
        return wrap(s, BRIGHT_CYAN)
    if a == "demonic":
        return wrap(s, BRIGHT_RED)
    return wrap(s, FG_YELLOW)  # neutral / unknown


def dim(s: str) -> str:
    """De-emphasise something — unexplored exits, legend text, hints."""
    return wrap(s, DIM)


def bold(s: str) -> str:
    return wrap(s, BOLD)


def warn(s: str) -> str:
    """A low-stakes warning — 'you cannot afford', 'not here'."""
    return wrap(s, FG_YELLOW)


def alert(s: str) -> str:
    """A high-stakes alert — 'you collapse', 'fatal'."""
    return wrap(s, BOLD, BRIGHT_RED)


def good(s: str) -> str:
    """A positive beat — quest complete, bond deepens, breakthrough."""
    return wrap(s, BRIGHT_GREEN)


# ---- HP / Qi bars ---------------------------------------------------------

def hp_bar(current: int, maximum: int) -> str:
    """Colorize an "HP n/n" string based on the fraction."""
    text = f"HP {current}/{maximum}"
    if maximum <= 0:
        return text
    frac = max(0.0, min(1.0, current / maximum))
    if not _enabled:
        return text
    if frac >= 0.66:
        return wrap(text, BRIGHT_GREEN)
    if frac >= 0.33:
        return wrap(text, BRIGHT_YELLOW)
    return wrap(text, BRIGHT_RED)


def qi_bar(current: int, maximum: int) -> str:
    text = f"Qi {current}/{maximum}"
    if not _enabled or maximum <= 0:
        return text
    frac = max(0.0, min(1.0, current / maximum))
    if frac >= 0.66:
        return wrap(text, BRIGHT_CYAN)
    if frac >= 0.33:
        return wrap(text, FG_CYAN)
    return wrap(text, DIM + FG_CYAN)
