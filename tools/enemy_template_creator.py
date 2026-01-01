"""
Enemy Template Creator Tool.

Controls:
    - Arrow keys: Change enemy ID
    - W/S: Health
    - A/D: Speed
    - Q/E: Radius
    - T/G: Armor
    - Y/H: Magic resistance
    - U/J: Attack range
    - N/M: Damage
    - K/L: Attack speed
    - O/P: Gold reward
    - Z/X/C: RGB color channels
    - V: Cycle shape
    - Tab: Select ability
    - R: Toggle selected ability
    - Enter: Save template
    - ESC: Quit
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pygame as pg

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from src.config.colors import UI_BACKGROUND
from src.config.paths import DATA_DIR

# Screen settings
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 520

# Available options
SHAPES = ["circle", "square", "triangle", "hexagon"]
ABILITIES = [
    "magic_resistant",
    "ranged",
    "boss",
    "fast",
    "tank",
    "healer",
    "summoner1",
    "summoner2",
    "invisible",
    "dash",
    "inispeed",
]


def get_default_template() -> dict:
    """Return a default enemy template."""
    return {
        "id": 1,
        "name": "New Enemy",
        "health": 300,
        "speed": 2.0,
        "armor": 1,
        "damage": 1,
        "magic_resistance": 1,
        "attack_range": 50,
        "attack_speed": 1.0,
        "color": [255, 255, 255],
        "radius": 10,
        "abilities": [],
        "shape": "circle",
        "gold_reward": 10,
    }


def load_templates(filepath: Path) -> dict:
    """Load existing templates from JSON."""
    if filepath.exists():
        with open(filepath) as f:
            return json.load(f)
    return {}


def save_templates(filepath: Path, templates: dict) -> None:
    """Save templates to JSON."""
    with open(filepath, "w") as f:
        json.dump(templates, f, indent=2)


def draw_enemy_preview(
    screen: pg.Surface, template: dict, center: tuple[int, int]
) -> None:
    """Draw a preview of the enemy shape."""
    color = tuple(template["color"])
    radius = template["radius"]
    shape = template["shape"]
    cx, cy = center

    if shape == "circle":
        pg.draw.circle(screen, color, center, radius)
    elif shape == "square":
        rect = pg.Rect(cx - radius, cy - radius, radius * 2, radius * 2)
        pg.draw.rect(screen, color, rect)
    elif shape == "triangle":
        points = [
            (cx, cy - radius),
            (cx - radius, cy + radius),
            (cx + radius, cy + radius),
        ]
        pg.draw.polygon(screen, color, points)
    elif shape == "hexagon":
        points = []
        for i in range(6):
            angle = i * math.pi / 3
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            points.append((x, y))
        pg.draw.polygon(screen, color, points)


def draw_interface(
    screen: pg.Surface,
    font: pg.font.Font,
    template: dict,
    selected_ability_idx: int,
    selected_shape_idx: int,
    templates: dict,
) -> None:
    """Draw the editor interface."""
    screen.fill(UI_BACKGROUND)

    # Draw enemy preview
    draw_enemy_preview(screen, template, (580, 200))

    # Preview label
    preview_label = font.render("Preview", True, (150, 150, 150))
    screen.blit(preview_label, (555, 280))

    # Template count
    count_text = font.render(f"Templates in file: {len(templates)}", True, (100, 200, 100))
    screen.blit(count_text, (480, 20))

    # Main controls
    lines = [
        f"ID: {template['id']}  [← →]",
        f"Name: {template.get('name', 'Unnamed')}  [F2 to edit]",
        f"Health: {template['health']}  [W/S]",
        f"Speed: {template['speed']:.1f}  [A/D]",
        f"Armor: {template['armor']}  [T/G]",
        f"Magic Res: {template['magic_resistance']}  [Y/H]",
        f"Radius: {template['radius']}  [Q/E]",
        f"Color RGB: {template['color']}  [Z/X/C]",
        f"Shape: {template['shape']}  [V] ({selected_shape_idx + 1}/{len(SHAPES)})",
        f"Range: {template['attack_range']}  [U/J]",
        f"Damage: {template['damage']}  [N/M]",
        f"Attack Speed: {template['attack_speed']:.1f}  [K/L]",
        f"Gold Reward: {template['gold_reward']}  [O/P]",
        "",
        f"Abilities: {template['abilities']}",
        f"Selected: {ABILITIES[selected_ability_idx]}  [Tab]",
        "[R] Toggle ability",
        "",
        "[Enter] Save  |  [Del] Delete  |  [ESC] Quit",
    ]

    y = 20
    for line in lines:
        color = (200, 200, 200) if line else (100, 100, 100)
        text = font.render(line, True, color)
        screen.blit(text, (20, y))
        y += 25

    pg.display.flip()


def main() -> None:
    """Run the enemy template creator."""
    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("Enemy Template Creator")
    clock = pg.time.Clock()
    font = pg.font.SysFont(None, 24)

    template_path = DATA_DIR / "enemyTemplates.json"
    templates = load_templates(template_path)
    template = get_default_template()

    # Set next available ID
    if templates:
        max_id = max(int(k) for k in templates.keys())
        template["id"] = max_id + 1

    selected_ability_idx = 0
    selected_shape_idx = 0

    print("Enemy Template Creator")
    print(f"Loaded {len(templates)} existing templates from {template_path}")
    print("\nUse keyboard controls to edit. Press Enter to save.")

    running = True
    while running:
        draw_interface(
            screen, font, template, selected_ability_idx, selected_shape_idx, templates
        )

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            elif event.type == pg.KEYDOWN:
                key = event.key

                if key == pg.K_ESCAPE:
                    running = False

                elif key == pg.K_RETURN:
                    # Save template
                    template["shape"] = SHAPES[selected_shape_idx]
                    template_id = str(template["id"])
                    templates[template_id] = dict(template)
                    save_templates(template_path, templates)
                    print(f"Saved template ID {template_id}: {template['name']}")

                    # Prepare for next template
                    template = get_default_template()
                    template["id"] = max(int(k) for k in templates.keys()) + 1

                elif key == pg.K_DELETE:
                    # Delete current template ID if it exists
                    template_id = str(template["id"])
                    if template_id in templates:
                        del templates[template_id]
                        save_templates(template_path, templates)
                        print(f"Deleted template ID {template_id}")

                elif key == pg.K_F2:
                    # Edit name
                    pg.display.iconify()
                    new_name = input(f"Enter name (current: {template['name']}): ").strip()
                    if new_name:
                        template["name"] = new_name

                # Navigation
                elif key == pg.K_RIGHT:
                    template["id"] += 1
                    # Load existing template if available
                    if str(template["id"]) in templates:
                        template = dict(templates[str(template["id"])])
                        shape = template.get("shape", "circle")
                        selected_shape_idx = SHAPES.index(shape) if shape in SHAPES else 0
                elif key == pg.K_LEFT:
                    template["id"] = max(1, template["id"] - 1)
                    if str(template["id"]) in templates:
                        template = dict(templates[str(template["id"])])
                        shape = template.get("shape", "circle")
                        selected_shape_idx = SHAPES.index(shape) if shape in SHAPES else 0

                # Stats
                elif key == pg.K_w:
                    template["health"] += 10
                elif key == pg.K_s:
                    template["health"] = max(10, template["health"] - 10)
                elif key == pg.K_d:
                    template["speed"] = round(template["speed"] + 0.1, 1)
                elif key == pg.K_a:
                    template["speed"] = max(0.1, round(template["speed"] - 0.1, 1))
                elif key == pg.K_q:
                    template["radius"] = max(3, template["radius"] - 1)
                elif key == pg.K_e:
                    template["radius"] = min(50, template["radius"] + 1)
                elif key == pg.K_t:
                    template["armor"] = max(0, template["armor"] - 1)
                elif key == pg.K_g:
                    template["armor"] += 1
                elif key == pg.K_y:
                    template["magic_resistance"] = max(0, template["magic_resistance"] - 1)
                elif key == pg.K_h:
                    template["magic_resistance"] += 1
                elif key == pg.K_u:
                    template["attack_range"] += 5
                elif key == pg.K_j:
                    template["attack_range"] = max(0, template["attack_range"] - 5)
                elif key == pg.K_n:
                    template["damage"] = max(0, template["damage"] - 1)
                elif key == pg.K_m:
                    template["damage"] += 1
                elif key == pg.K_k:
                    template["attack_speed"] = max(0.1, round(template["attack_speed"] - 0.1, 1))
                elif key == pg.K_l:
                    template["attack_speed"] = round(template["attack_speed"] + 0.1, 1)
                elif key == pg.K_o:
                    template["gold_reward"] = max(0, template["gold_reward"] - 1)
                elif key == pg.K_p:
                    template["gold_reward"] += 1

                # Color (hold shift for -5)
                elif key == pg.K_z:
                    delta = -5 if pg.key.get_mods() & pg.KMOD_SHIFT else 5
                    template["color"][0] = (template["color"][0] + delta) % 256
                elif key == pg.K_x:
                    delta = -5 if pg.key.get_mods() & pg.KMOD_SHIFT else 5
                    template["color"][1] = (template["color"][1] + delta) % 256
                elif key == pg.K_c:
                    delta = -5 if pg.key.get_mods() & pg.KMOD_SHIFT else 5
                    template["color"][2] = (template["color"][2] + delta) % 256

                # Shape
                elif key == pg.K_v:
                    selected_shape_idx = (selected_shape_idx + 1) % len(SHAPES)
                    template["shape"] = SHAPES[selected_shape_idx]

                # Abilities
                elif key == pg.K_TAB:
                    selected_ability_idx = (selected_ability_idx + 1) % len(ABILITIES)
                elif key == pg.K_r:
                    ability = ABILITIES[selected_ability_idx]
                    if ability in template["abilities"]:
                        template["abilities"].remove(ability)
                        print(f"Removed ability: {ability}")
                    else:
                        template["abilities"].append(ability)
                        print(f"Added ability: {ability}")

        clock.tick(30)

    pg.quit()


if __name__ == "__main__":
    main()
