#!/usr/bin/env python3
"""Entry point for Jade Wind Chronicles."""
import sys
from game.engine import Game
from game import style

if __name__ == "__main__":
    # Honor --no-color / --color flags. Otherwise the REPL auto-detects.
    if "--no-color" in sys.argv or "--nocolor" in sys.argv:
        style.auto_detect(force=False)
    elif "--color" in sys.argv or "--force-color" in sys.argv:
        style.auto_detect(force=True)
    Game().repl()
