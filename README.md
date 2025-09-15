# Tower Defense — Launch Instructions

This project is a Pygame-based tower defense game. To play, run the main script and use the in-game UI to build

Links to key files:
- Main entry point: [main.py](main.py)
- Constants (resolution, asset paths): [scripts/constants.py](scripts/constants.py)
- Wave editor (optional tool): [scripts/waveCreator.py](scripts/waveCreator.py)
- Enemy template editor (optional tool): [scripts/enemyTemplateCreator.py](scripts/enemyTemplateCreator.py)

## 1) Requirements
- Python 3.12 (recommended)
- pip (Python package manager)

## 2) Launch the game
Run from the repository root:
```sh
python main.py
```

If you use Visual Studio Code, use the integrated terminal from the project root and run the same command.

## 3) How to play (quick guide)
- Level flow:
  - Start game → select a level → prepare (build phase) → start the wave → defend → repeat.
- Build panel:
  - Click the sliding toggle on the right edge to open/close the build panel.
  - Click a factory or tower button to select a blueprint, then click on the map to place it.
  - A green/red ghost shows valid placement and whether you can afford it.
  - If upgrades are enabled for a level, use the “Tower Upgrade” button and click a tower to upgrade.
- Start wave:
  - In the prepare phase, click “Start Wave” to begin the next wave.
- Abilities (if enabled):
  - Click an ability button (Fireball, Scanner, Disruptor, Glue), then click on the map to target.
- Pause and speed:
  - Pause: press Esc or click the yellow “II” button at the bottom-left.
  - Game speed: use the “<<” and “>>” buttons in the bottom-right.
- Debug toggles:
  - F: show FPS
  - R: show roads/paths
  - V: show tower ranges

## 3) Potential problems and solutions
- Window is too large:
  - In the constants.py change resolution to fit the desired display.