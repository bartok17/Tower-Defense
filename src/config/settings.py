"""
Game settings and configuration constants.
"""

# Internal game resolution
GAME_WIDTH: int = 1000
GAME_HEIGHT: int = 1000

# Display settings 
SCREEN_WIDTH: int = 1000  # Default, overridden at startup
SCREEN_HEIGHT: int = 1000  # Default, overridden at startup
FPS: int = 60

# Scale factor for window (0.8 = 80% of screen height)
WINDOW_SCALE_FACTOR: float = 0.85

# UI layout settings
UI_PANEL_WIDTH: int = 180
UI_PANEL_X: int = GAME_WIDTH - 200
COLUMN_PADDING: int = 10

# Gameplay settings
DEFAULT_PLAYER_HEALTH: int = 100
DEFAULT_START_GOLD: int = 100
DEFAULT_START_WOOD: int = 50
DEFAULT_START_METAL: int = 25

# Road/Path settings
ROAD_COLLISION_THICKNESS: int = 100

# Ghost preview settings
GHOST_ALPHA: int = 120
PAUSE_OVERLAY_ALPHA: int = 128

# Spawn settings
DEFAULT_INTER_ENEMY_SPAWN_DELAY_MS: int = 500

# Level configuration (default)
DEFAULT_LEVELS_CONFIG: list[dict] = [
    {
        "id": "level1",
        "name": "Beginning",
        "map_image_path": "map1.png",
        "waypoints_path": "map1_waypoints.json",
        "waves_path": "waves_level1.json",
        "thumbnail_path": "level1_thumb.png",
        "unlocked": True,
        "start_gold": 200,
        "start_wood": 100,
        "start_metal": 50,
    },
    {
        "id": "level2",
        "name": "Hexagon Valley",
        "map_image_path": "map2.png",
        "waypoints_path": "map2_waypoints.json",
        "waves_path": "waves_level2.json",
        "thumbnail_path": "level2_thumb.png",
        "unlocked": True,
        "start_gold": 150,
        "start_wood": 150,
        "start_metal": 150,
    },
]
