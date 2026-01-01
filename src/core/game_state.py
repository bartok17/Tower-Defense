"""
Game state enumeration and state machine.
"""

from enum import Enum, auto


class GameState(Enum):
    """Game states."""

    MAIN_MENU = auto()
    LEVEL_SELECT = auto()
    PRE_WAVE = auto()
    WAVE_ACTIVE = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    VICTORY = auto()
    QUIT = auto()


class GameMode(Enum):
    """Gameplay modes within a level."""

    BUILD_PHASE = auto()
    WAVE_PHASE = auto()
    TRANSITIONING = auto()
