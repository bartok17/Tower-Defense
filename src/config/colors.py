"""
Color constants used throughout the game.

All colors are RGB/RGBA tuples.
"""


Color = tuple[int, int, int]
ColorAlpha = tuple[int, int, int, int]

# Basic colors
WHITE: Color = (255, 255, 255)
BLACK: Color = (0, 0, 0)
RED: Color = (255, 0, 0)
GREEN: Color = (0, 255, 0)
BLUE: Color = (0, 0, 255)
YELLOW: Color = (255, 255, 0)
ORANGE: Color = (255, 165, 0)
PURPLE: Color = (128, 0, 128)
CYAN: Color = (0, 255, 255)
MAGENTA: Color = (255, 0, 255)

# UI colors
UI_BACKGROUND: Color = (30, 30, 30)
UI_PANEL_BG: ColorAlpha = (30, 30, 30, 180)
UI_BORDER: Color = (255, 255, 255)
UI_TEXT: Color = (255, 255, 255)
UI_TEXT_DISABLED: Color = (100, 100, 100)

# Button colors
BUTTON_DEFAULT: Color = (200, 200, 200)
BUTTON_HOVER: Color = (150, 150, 150)
BUTTON_PRESSED: Color = (100, 100, 100)
BUTTON_DISABLED: Color = (80, 80, 80)

# Game element colors
HEALTH_BAR_BG: Color = (100, 0, 0)
HEALTH_BAR_FILL: Color = (255, 0, 0)
HEALTH_BAR_BOSS: ColorAlpha = (255, 0, 255, 70)

# Effect colors
EXPLOSION_COLOR: Color = (255, 100, 0)
FIREBALL_COLOR: Color = (255, 50, 0)
SCANNER_COLOR: ColorAlpha = (0, 200, 0, 80)
DISRUPTOR_COLOR: ColorAlpha = (255, 255, 0, 90)
GLUE_COLOR: ColorAlpha = (120, 120, 255, 60)

# Build ghost colors
GHOST_VALID: ColorAlpha = (0, 200, 0, 100)
GHOST_INVALID: ColorAlpha = (200, 0, 0, 100)
