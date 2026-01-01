"""
Path configuration for assets and data files.
"""

from pathlib import Path

# Project root is two levels up from this file (src/config/paths.py -> project root)
PROJECT_ROOT: Path = Path(__file__).parent.parent.parent.resolve()

# Main directories
DATA_DIR: Path = PROJECT_ROOT / "data"
ASSETS_DIR: Path = PROJECT_ROOT / "assets"
SRC_DIR: Path = PROJECT_ROOT / "src"

DATA_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

LEVELS_CONFIG_FILENAME: str = "levels_config.json"
ENEMY_TEMPLATES_FILENAME: str = "enemyTemplates.json"
TOWER_PRESETS_FILENAME: str = "tower_presets.json"

# Icon paths
ICON_PATHS: dict[str, str] = {
    "health": str(ASSETS_DIR / "heart.png"),
    "wave": str(ASSETS_DIR / "skull.png"),
    "gold": str(ASSETS_DIR / "gold.png"),
    "wood": str(ASSETS_DIR / "wood.png"),
    "metal": str(ASSETS_DIR / "metal.png"),
}


def get_asset_path(filename: str) -> Path:
    """Get the full path to an asset file."""
    return ASSETS_DIR / filename


def get_data_path(filename: str) -> Path:
    """Get the full path to a data file."""
    return DATA_DIR / filename
