# Tower Defense

A Pygame-based tower defense game featuring multiple levels, diverse tower types, enemy abilities, and resource management.

## Features

- **Multiple Levels** — 4 unique maps with distinct waypoint configurations
- **Tower Variety** — Different tower types with unique stats, damage types, and projectile behaviors
- **Enemy Abilities** — Enemies with special abilities (invisibility, speed dash, boss mechanics, etc.)
- **Resource Management** — Gold, wood, and metal economy with factories for passive income
- **Player Abilities** — Fireball, Scanner, Disruptor, and Glue abilities for tactical gameplay
- **Dynamic Scaling** — Window automatically scales to fit your display

## Project Structure

```
Tower-Defense/
├── run_game.py              # Game launcher
├── pyproject.toml           # Project configuration & dependencies
├── src/                     # Source code
│   ├── main.py              # Application entry point
│   ├── config/              # Configuration (settings, paths, colors)
│   ├── core/                # Core game logic
│   │   ├── game.py          # Main game loop & context
│   │   ├── game_world.py    # Game state & world logic
│   │   ├── game_state.py    # State management
│   │   └── event_manager.py # Pub/sub event system
│   ├── entities/            # Game entities
│   │   ├── base_entity.py   # Abstract base class
│   │   ├── tower.py         # Tower entity
│   │   ├── enemy.py         # Enemy entity
│   │   ├── projectile.py    # Projectile entity
│   │   ├── factory.py       # Resource factory
│   │   └── abilities.py     # Enemy abilities system
│   ├── systems/             # Game systems
│   │   ├── build_manager.py # Building placement & management
│   │   ├── spawn_system.py  # Wave spawning logic
│   │   ├── economy_system.py# Resource management
│   │   └── player_abilities.py # Player ability system
│   ├── ui/                  # User interface
│   │   ├── ui_manager.py    # UI coordination
│   │   ├── components/      # Reusable UI components (Button, HUD)
│   │   └── screens/         # Game screens (Menu, Level Select, Game, Ending)
│   └── utils/               # Utility modules
├── data/                    # JSON configuration files
│   ├── enemyTemplates.json  # Enemy type definitions
│   ├── tower_presets.json   # Tower type definitions
│   ├── levels_config.json   # Level configurations
│   ├── waves_level*.json    # Wave definitions per level
│   └── map*_waypoints.json  # Waypoint paths per map
├── assets/                  # Game assets (images, fonts)
├── tools/                   # Development tools
│   ├── enemy_template_creator.py # Enemy template editor
│   ├── wave_creator.py      # Wave configuration editor
│   └── waypoint_creator.py  # Map waypoint editor
└── tests/                   # Unit tests
```

## Requirements

- Python 3.10+
- pygame >= 2.5.0

## Installation

### Using pip

```bash
# Clone the repository
git clone https://github.com/bartok17/Tower-Defense.git
cd Tower-Defense

# Install dependencies
pip install pygame

# Or install with dev dependencies
pip install -e ".[dev]"
```

### Using the package

```bash
pip install -e .
tower-defense  # Run via entry point
```

## Running the Game

```bash
python run_game.py
```

Or if installed as a package:

```bash
tower-defense
```

## How to Play

### Game Flow
1. **Main Menu** → Select a level
2. **Build Phase** — Place towers and factories before starting
3. **Wave Phase** — Defend against enemy waves
4. **Repeat** — Earn resources, upgrade defenses, survive all waves

### Controls

| Action | Control |
|--------|---------|
| Open/Close Build Panel | Click toggle on right edge |
| Place Building | Select from panel, click on map |
| Start Wave | Click "Start Wave" button |
| Use Ability | Select ability, click target location |
| Pause | `Esc` or click pause button (⏸) |
| Adjust Speed | `<<` / `>>` buttons |
| Toggle FPS | `F` |
| Toggle Roads | `R` |
| Toggle Tower Ranges | `V` |

### Building
- **Factories** — Generate passive resources each wave
- **Towers** — Attack enemies within range
- Green ghost = valid placement & affordable
- Red ghost = invalid placement or insufficient resources

### Player Abilities
- **Fireball** — Instant AOE damage
- **Scanner** — Reveals invisible enemies
- **Disruptor** — Silences enemy abilities
- **Glue** — Slows enemies in area

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type checking
mypy src/
```

### Development Tools

Located in `tools/`:
- **Wave Creator** — Visual wave configuration editor
- **Enemy Template Creator** — Enemy type designer
- **Waypoint Creator** — Map path editor

## Configuration

Game settings can be modified in:
- `src/config/settings.py` — Window size, game constants
- `data/` — JSON files for enemies, towers, waves, and levels

## License

MIT License — See [pyproject.toml](pyproject.toml) for details.

## Authors

Bartosz Tokarz, Markexus
