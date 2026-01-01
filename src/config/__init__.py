"""Configuration module for game settings, colors, and paths."""

from .colors import BLACK, GREEN, RED, WHITE, YELLOW
from .paths import ASSETS_DIR, DATA_DIR, ICON_PATHS, PROJECT_ROOT
from .settings import (
    COLUMN_PADDING,
    DEFAULT_LEVELS_CONFIG,
    FPS,
    GAME_HEIGHT,
    GAME_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    UI_PANEL_WIDTH,
    UI_PANEL_X,
)

__all__ = [
    # Settings
    "SCREEN_WIDTH",
    "SCREEN_HEIGHT",
    "GAME_WIDTH",
    "GAME_HEIGHT",
    "FPS",
    "UI_PANEL_WIDTH",
    "UI_PANEL_X",
    "COLUMN_PADDING",
    "DEFAULT_LEVELS_CONFIG",
    # Colors
    "WHITE",
    "RED",
    "BLACK",
    "GREEN",
    "YELLOW",
    # Paths
    "DATA_DIR",
    "ASSETS_DIR",
    "PROJECT_ROOT",
    "ICON_PATHS",
]
