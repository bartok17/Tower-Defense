"""
Wave Creator Tool.

Controls:
    - UP/DOWN: Change wave ID
    - Q/W: Prep time
    - E/R: Inter-wave delay
    - T/Y: Mode
    - U/I: Passive gold
    - J/K: Passive wood
    - O/P: Passive metal
    - Tab: Select enemy template
    - S/D: Adjust selected template count
    - A: Add unit entry to wave
    - Ctrl+UP/DOWN: Select unit entry in wave
    - Ctrl+LEFT/RIGHT: Adjust entry count
    - Alt+LEFT/RIGHT: Adjust delay after group
    - Shift+LEFT/RIGHT: Adjust inter-spawn delay
    - Backspace: Remove selected entry
    - X: Remove all entries of selected type
    - F1: New wave
    - F2: Load wave by ID
    - Enter: Save wave to memory
    - Delete: Delete wave from memory
    - F12: Save all to file
    - ESC: Quit
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pygame as pg

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from src.config.paths import DATA_DIR
from src.config.settings import DEFAULT_INTER_ENEMY_SPAWN_DELAY_MS

# Screen settings
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700


def get_default_wave() -> dict:
    """Return a default wave template."""
    return {
        "id": 1,
        "P_time": 10,
        "inter_wave_delay": 30,
        "passive_gold": 50,
        "passive_wood": 25,
        "passive_metal": 25,
        "units": [],
        "mode": 1,
    }


def migrate_wave_format(wave: dict) -> dict:
    """Ensure wave units have 4 elements: [id, count, delay, spawn_delay]."""
    if "units" not in wave:
        wave["units"] = []
        return wave

    migrated = []
    for entry in wave["units"]:
        if not isinstance(entry, list):
            continue
        if len(entry) == 2:
            migrated.append([entry[0], entry[1], 1.0, DEFAULT_INTER_ENEMY_SPAWN_DELAY_MS])
        elif len(entry) == 3:
            migrated.append([entry[0], entry[1], entry[2], DEFAULT_INTER_ENEMY_SPAWN_DELAY_MS])
        elif len(entry) >= 4:
            migrated.append(list(entry[:4]))
    wave["units"] = migrated
    return wave


def load_waves(filepath: Path) -> dict[str, dict]:
    """Load waves from JSON file."""
    if not filepath.exists():
        return {}
    with open(filepath) as f:
        data = json.load(f)
    # Migrate all waves
    return {k: migrate_wave_format(v) for k, v in data.items()}


def save_waves(filepath: Path, waves: dict[str, dict]) -> None:
    """Save waves to JSON file."""
    with open(filepath, "w") as f:
        json.dump(waves, f, indent=2)


def load_enemy_templates() -> dict:
    """Load enemy templates for reference."""
    filepath = DATA_DIR / "enemyTemplates.json"
    if filepath.exists():
        with open(filepath) as f:
            return json.load(f)
    return {}


class WaveCreator:
    """Wave creator application."""

    def __init__(self) -> None:
        pg.init()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Wave Creator")
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont(None, 24)
        self.font_small = pg.font.SysFont(None, 20)

        self.enemy_templates = load_enemy_templates()
        self.available_units = [
            {"id": int(k), "name": v.get("name", f"Unit {k}"), "count": 1}
            for k, v in self.enemy_templates.items()
        ]

        self.waves: dict[str, dict] = {}
        self.wave_file: Path | None = None
        self.current_wave = get_default_wave()
        self.active_wave_id: int | None = None

        self.selected_unit_idx = 0
        self.selected_entry_idx = -1

        self.status_message = ""
        self.status_timer = 0

    def set_status(self, msg: str, duration: int = 120) -> None:
        """Set a temporary status message."""
        self.status_message = msg
        self.status_timer = duration

    def choose_file(self) -> bool:
        """Choose or create a wave file via console."""
        print("\n=== Wave File Management ===")
        print("(N)ew file or (E)dit existing?")
        choice = input("> ").strip().lower()

        if choice == "n":
            name = input("Enter base name (e.g., level1): ").strip()
            if not name:
                print("No name entered.")
                return False
            self.wave_file = DATA_DIR / f"waves_{name}.json"
            if self.wave_file.exists():
                overwrite = input(f"{self.wave_file.name} exists. Overwrite? (y/N): ").strip().lower()
                if overwrite != "y":
                    return False
            self.waves = {}
            print(f"Created: {self.wave_file}")
            return True

        elif choice == "e":
            wave_files = list(DATA_DIR.glob("waves_*.json"))
            if not wave_files:
                print("No wave files found.")
                return self.choose_file()

            print("\nAvailable files:")
            for i, f in enumerate(wave_files):
                print(f"  {i + 1}. {f.name}")

            try:
                idx = int(input(f"Select (1-{len(wave_files)}): ").strip()) - 1
                if 0 <= idx < len(wave_files):
                    self.wave_file = wave_files[idx]
                    self.waves = load_waves(self.wave_file)
                    print(f"Loaded {len(self.waves)} waves from {self.wave_file.name}")

                    # Load first wave
                    if self.waves:
                        first_id = sorted(self.waves.keys(), key=int)[0]
                        self.active_wave_id = int(first_id)
                        self.current_wave = dict(self.waves[first_id])
                        if self.current_wave["units"]:
                            self.selected_entry_idx = 0
                    return True
            except (ValueError, IndexError):
                print("Invalid selection.")
                return False

        return False

    def draw(self) -> None:
        """Draw the interface."""
        self.screen.fill((30, 30, 30))

        # File info
        file_name = self.wave_file.name if self.wave_file else "None"
        self._draw_text(f"File: {file_name}", 20, 20, (200, 200, 0))

        active_str = str(self.active_wave_id) if self.active_wave_id else "NEW"
        self._draw_text(
            f"Wave ID: {self.current_wave['id']} (Loaded: {active_str})",
            20, 45, (200, 200, 0)
        )

        # Wave properties
        y = 80
        props = [
            f"Wave ID: {self.current_wave['id']}  [UP/DOWN]",
            f"Prep Time: {self.current_wave['P_time']}s  [Q/W]",
            f"Inter-Wave Delay: {self.current_wave['inter_wave_delay']}s  [E/R]",
            f"Mode: {self.current_wave['mode']}  [T/Y]",
            f"Passive Gold: {self.current_wave['passive_gold']}  [U/I]",
            f"Passive Wood: {self.current_wave['passive_wood']}  [J/K]",
            f"Passive Metal: {self.current_wave['passive_metal']}  [O/P]",
            "",
            "Units in wave (CTRL+UP/DOWN to select):",
        ]

        for line in props:
            self._draw_text(line, 20, y, (200, 200, 200))
            y += 25

        # Unit entries
        if not self.current_wave["units"]:
            self._draw_text("  (No units)", 20, y, (150, 150, 150))
            y += 25
        else:
            for i, entry in enumerate(self.current_wave["units"]):
                unit_id, count, delay, spawn_delay = entry
                name = self.enemy_templates.get(str(unit_id), {}).get("name", f"Unit {unit_id}")
                prefix = ">> " if i == self.selected_entry_idx else "   "
                text = f"{prefix}{name} x{count}, Delay: {delay:.1f}s, Spawn: {spawn_delay}ms"
                color = (255, 255, 100) if i == self.selected_entry_idx else (200, 200, 200)
                self._draw_text(text, 20, y, color)
                y += 22

        if self.selected_entry_idx >= 0 and self.current_wave["units"]:
            self._draw_text(
                "  CTRL+L/R: count | ALT+L/R: delay | SHIFT+L/R: spawn | BACKSPACE: remove",
                20, y, (150, 150, 150)
            )

        # Right panel - enemy templates
        x_right = 520
        self._draw_text("Enemy Templates [Tab to select, A to add]:", x_right, 80, (200, 200, 200))

        for i, unit in enumerate(self.available_units):
            prefix = "-> " if i == self.selected_unit_idx else "   "
            text = f"{prefix}{unit['name']} (ID:{unit['id']}) x{unit['count']}"
            color = (200, 200, 0) if i == self.selected_unit_idx else (180, 180, 180)
            self._draw_text(text, x_right, 105 + i * 22, color)

        self._draw_text("[S/D] adjust count, [X] remove type from wave", x_right, 105 + len(self.available_units) * 22 + 10, (150, 150, 150))

        # Waves in file
        self._draw_text("Waves in file:", x_right, 20, (150, 150, 255))
        sorted_ids = sorted(self.waves.keys(), key=int)
        waves_text = ", ".join(sorted_ids[:20])
        if len(sorted_ids) > 20:
            waves_text += f"... (+{len(sorted_ids) - 20})"
        self._draw_text(waves_text or "(none)", x_right, 45, (150, 150, 255))

        # Instructions
        y_instr = SCREEN_HEIGHT - 100
        instructions = [
            "F1: New Wave | F2: Load Wave | ENTER: Save to Memory | DEL: Delete from Memory",
            "F12: SAVE TO FILE | ESC: Quit",
        ]
        for i, line in enumerate(instructions):
            self._draw_text(line, 20, y_instr + i * 20, (100, 255, 100), self.font_small)

        # Status message
        if self.status_timer > 0:
            self._draw_text(self.status_message, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 30, (255, 255, 0))
            self.status_timer -= 1

        pg.display.flip()

    def _draw_text(
        self,
        text: str,
        x: int,
        y: int,
        color: tuple[int, int, int],
        font: pg.font.Font | None = None,
    ) -> None:
        """Draw text at position."""
        font = font or self.font
        surface = font.render(text, True, color)
        self.screen.blit(surface, (x, y))

    def handle_event(self, event: pg.event.Event) -> bool:
        """Handle input event. Returns False to quit."""
        if event.type == pg.QUIT:
            return False

        if event.type != pg.KEYDOWN:
            return True

        key = event.key
        mods = pg.key.get_mods()
        ctrl = mods & pg.KMOD_CTRL
        alt = mods & pg.KMOD_ALT
        shift = mods & pg.KMOD_SHIFT

        # Modifier combinations for entry editing
        if ctrl:
            if key == pg.K_UP and self.current_wave["units"]:
                self.selected_entry_idx = max(0, self.selected_entry_idx - 1)
            elif key == pg.K_DOWN and self.current_wave["units"]:
                self.selected_entry_idx = min(len(self.current_wave["units"]) - 1, self.selected_entry_idx + 1)
            elif key == pg.K_LEFT and 0 <= self.selected_entry_idx < len(self.current_wave["units"]):
                self.current_wave["units"][self.selected_entry_idx][1] = max(1, self.current_wave["units"][self.selected_entry_idx][1] - 1)
            elif key == pg.K_RIGHT and 0 <= self.selected_entry_idx < len(self.current_wave["units"]):
                self.current_wave["units"][self.selected_entry_idx][1] += 1
            return True

        if alt:
            if 0 <= self.selected_entry_idx < len(self.current_wave["units"]):
                if key == pg.K_LEFT:
                    self.current_wave["units"][self.selected_entry_idx][2] = max(0, round(self.current_wave["units"][self.selected_entry_idx][2] - 0.1, 1))
                elif key == pg.K_RIGHT:
                    self.current_wave["units"][self.selected_entry_idx][2] = round(self.current_wave["units"][self.selected_entry_idx][2] + 0.1, 1)
            return True

        if shift:
            if 0 <= self.selected_entry_idx < len(self.current_wave["units"]):
                if key == pg.K_LEFT:
                    self.current_wave["units"][self.selected_entry_idx][3] = max(0, self.current_wave["units"][self.selected_entry_idx][3] - 50)
                elif key == pg.K_RIGHT:
                    self.current_wave["units"][self.selected_entry_idx][3] += 50
            return True

        # Regular keys
        if key == pg.K_ESCAPE:
            return False

        elif key == pg.K_UP:
            self.current_wave["id"] += 1
        elif key == pg.K_DOWN:
            self.current_wave["id"] = max(1, self.current_wave["id"] - 1)

        elif key == pg.K_q:
            self.current_wave["P_time"] = max(0, self.current_wave["P_time"] - 1)
        elif key == pg.K_w:
            self.current_wave["P_time"] += 1
        elif key == pg.K_e:
            self.current_wave["inter_wave_delay"] = max(0, self.current_wave["inter_wave_delay"] - 1)
        elif key == pg.K_r:
            self.current_wave["inter_wave_delay"] += 1
        elif key == pg.K_t:
            self.current_wave["mode"] = max(0, self.current_wave["mode"] - 1)
        elif key == pg.K_y:
            self.current_wave["mode"] += 1
        elif key == pg.K_u:
            self.current_wave["passive_gold"] = max(0, self.current_wave["passive_gold"] - 5)
        elif key == pg.K_i:
            self.current_wave["passive_gold"] += 5
        elif key == pg.K_j:
            self.current_wave["passive_wood"] = max(0, self.current_wave["passive_wood"] - 5)
        elif key == pg.K_k:
            self.current_wave["passive_wood"] += 5
        elif key == pg.K_o:
            self.current_wave["passive_metal"] = max(0, self.current_wave["passive_metal"] - 5)
        elif key == pg.K_p:
            self.current_wave["passive_metal"] += 5

        elif key == pg.K_TAB:
            self.selected_unit_idx = (self.selected_unit_idx + 1) % len(self.available_units)
        elif key == pg.K_s:
            self.available_units[self.selected_unit_idx]["count"] = max(1, self.available_units[self.selected_unit_idx]["count"] - 1)
        elif key == pg.K_d:
            self.available_units[self.selected_unit_idx]["count"] += 1

        elif key == pg.K_a:
            unit = self.available_units[self.selected_unit_idx]
            self.current_wave["units"].append([unit["id"], unit["count"], 1.0, DEFAULT_INTER_ENEMY_SPAWN_DELAY_MS])
            self.selected_entry_idx = len(self.current_wave["units"]) - 1
            self.set_status(f"Added {unit['count']}x {unit['name']}")

        elif key == pg.K_x:
            unit_id = self.available_units[self.selected_unit_idx]["id"]
            before = len(self.current_wave["units"])
            self.current_wave["units"] = [u for u in self.current_wave["units"] if u[0] != unit_id]
            if len(self.current_wave["units"]) < before:
                self.set_status(f"Removed all entries of unit {unit_id}")
                self.selected_entry_idx = min(self.selected_entry_idx, len(self.current_wave["units"]) - 1)

        elif key == pg.K_BACKSPACE:
            if 0 <= self.selected_entry_idx < len(self.current_wave["units"]):
                self.current_wave["units"].pop(self.selected_entry_idx)
                self.selected_entry_idx = min(self.selected_entry_idx, len(self.current_wave["units"]) - 1)
                self.set_status("Removed entry")

        elif key == pg.K_F1:
            self.current_wave = get_default_wave()
            if self.waves:
                self.current_wave["id"] = max(int(k) for k in self.waves.keys()) + 1
            self.active_wave_id = None
            self.selected_entry_idx = -1
            self.set_status("New wave buffer")

        elif key == pg.K_F2:
            pg.display.iconify()
            try:
                wave_id = input(f"Load wave ID (available: {', '.join(sorted(self.waves.keys(), key=int))}): ").strip()
                if wave_id in self.waves:
                    self.current_wave = dict(self.waves[wave_id])
                    self.active_wave_id = int(wave_id)
                    self.selected_entry_idx = 0 if self.current_wave["units"] else -1
                    self.set_status(f"Loaded wave {wave_id}")
                else:
                    self.set_status(f"Wave {wave_id} not found")
            except Exception as e:
                self.set_status(f"Error: {e}")

        elif key == pg.K_RETURN:
            wave_id = str(self.current_wave["id"])
            self.waves[wave_id] = dict(self.current_wave)
            self.active_wave_id = int(wave_id)
            self.set_status(f"Saved wave {wave_id} to memory")

        elif key == pg.K_DELETE:
            if self.active_wave_id is not None:
                wave_id = str(self.active_wave_id)
                if wave_id in self.waves:
                    del self.waves[wave_id]
                    self.set_status(f"Deleted wave {wave_id}")
                    self.current_wave = get_default_wave()
                    self.active_wave_id = None

        elif key == pg.K_F12:
            if self.wave_file:
                save_waves(self.wave_file, self.waves)
                self.set_status(f"Saved {len(self.waves)} waves to {self.wave_file.name}")
            else:
                self.set_status("No file selected!")

        return True

    def run(self) -> None:
        """Run the wave creator."""
        if not self.choose_file():
            print("No file selected. Exiting.")
            pg.quit()
            return

        running = True
        while running:
            self.draw()

            for event in pg.event.get():
                if not self.handle_event(event):
                    running = False
                    break

            self.clock.tick(30)

        pg.quit()


def main() -> None:
    """Entry point."""
    creator = WaveCreator()
    creator.run()


if __name__ == "__main__":
    main()
