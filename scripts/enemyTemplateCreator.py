import pygame as pg
import json
import os
import constants as con

pg.init()
screen = pg.display.set_mode((640, 480))
clock = pg.time.Clock()
font = pg.font.SysFont(None, 24)

template = {
    "id": 1,
    "health": 300,
    "speed": 2,
    "armor": 1,
    "damage": 1,
    "magic_resistance": 1,
    "attack_range": 50,
    "attack_speed": 1.0,
    "color": [255, 255, 255],
    "radius": 10,
    "abilities": [],
    "shape": "circle",  # Enemy shape type
    "gold_reward": 10
}

abilities_list = ["magic_resistant", "ranged", "boss", "fast", "slow", "healer", "tank", "summoner", "invisible"]
selected_ability_index = 0

shapes_list = ["circle", "square", "triangle"]
selected_shape_index = 0

template_path = os.path.join(con.DATA_DIR, "enemyTemplates.json")
if os.path.exists(template_path):
    with open(template_path, "r") as f:
        templates = json.load(f)
else:
    templates = {}

def draw_interface():
    screen.fill((30, 30, 30))
    # Draw enemy preview
    if template["shape"] == "circle":
        pg.draw.circle(screen, template["color"], (500, 200), template["radius"])
    elif template["shape"] == "square":
        rect = pg.Rect(500 - template["radius"], 200 - template["radius"], template["radius"] * 2, template["radius"] * 2)
        pg.draw.rect(screen, template["color"], rect)
    elif template["shape"] == "triangle":
        points = [
            (500, 200 - template["radius"]),
            (500 - template["radius"], 200 + template["radius"]),
            (500 + template["radius"], 200 + template["radius"])
        ]
        pg.draw.polygon(screen, template["color"], points)
    
    lines = [
        f"ID: {template['id']} ← →",
        f"Health: {template['health']}  [W/S]",
        f"Speed: {template['speed']}  [A/D]",
        f"Armor: {template['armor']}  [T/G]",
        f"Magic Res: {template['magic_resistance']}  [Y/H]",
        f"Radius: {template['radius']}  [Q/E]",
        f"Color RGB: {template['color']}  [Z/X/C]",
        f"Shape: {template['shape']}  [V]",
        f"Range: {template['attack_range']}  [U/J]",
        f"Damage: {template['damage']}  [N/M]",
        f"Attack speed: {template['attack_speed']} [K/L]",
        f"Gold Reward: {template['gold_reward']} [O/P]", 
        f"Abilities: {template['abilities']}",
        f"Selected ability: {abilities_list[selected_ability_index]}  [Tab]",
        f"[R] Add/Remove ability",
        f"[Enter] Save | [ESC] Quit"
    ]
    
    for i, line in enumerate(lines):
        text = font.render(line, True, (200, 200, 200))
        screen.blit(text, (20, 20 + i * 25))
    
    pg.display.flip()

running = True
while running:
    draw_interface()
    for event in pg.event.get():
        if event.type == pg.QUIT: running = False
        elif event.type == pg.KEYDOWN:
            match event.key:
                case pg.K_ESCAPE: running = False
                case pg.K_RETURN:
                    used_ids = [int(i) for i in templates.keys()]
                    next_id = max(used_ids, default=0) + 1
                    template["id"] = next_id
                    template["shape"] = shapes_list[selected_shape_index]
                    templates[str(template["id"])] = dict(template)
                    with open(template_path, "w") as f:
                        json.dump(templates, f, indent=2)
                    print(f"Saved template with ID {template['id']}")
                case pg.K_RIGHT: template["id"] += 1
                case pg.K_LEFT: template["id"] = max(1, template["id"] - 1)
                case pg.K_w: template["health"] += 5
                case pg.K_s: template["health"] = max(5, template["health"] - 5)
                case pg.K_a: template["speed"] = max(0.1, round(template["speed"] - 0.1, 1))
                case pg.K_d: template["speed"] = round(template["speed"] + 0.1, 1)
                case pg.K_o: template["gold_reward"] = max(0, template["gold_reward"] - 1) 
                case pg.K_p: template["gold_reward"] += 1 
                case pg.K_q: template["radius"] = max(2, template["radius"] - 1)
                case pg.K_e: template["radius"] += 1
                case pg.K_n: template["damage"] = max(0, template["damage"] - 1)
                case pg.K_m: template["damage"] += 1
                case pg.K_k: template["attack_speed"] = max(0.1, round(template["attack_speed"] - 0.1, 1))
                case pg.K_l: template["attack_speed"] = round(template["attack_speed"] + 0.1, 1)
                case pg.K_z: template["color"][0] = (template["color"][0] + 5) % 256
                case pg.K_x: template["color"][1] = (template["color"][1] + 5) % 256
                case pg.K_c: template["color"][2] = (template["color"][2] + 5) % 256
                case pg.K_t: template["armor"] = max(0.1, round(template["armor"] - 0.1, 1))
                case pg.K_g: template["armor"] = round(template["armor"] + 0.1, 1)
                case pg.K_y: template["magic_resistance"] = max(0.1, round(template["magic_resistance"] - 0.1, 1))
                case pg.K_h: template["magic_resistance"] = round(template["magic_resistance"] + 0.1, 1)
                case pg.K_u: template["attack_range"] += 5
                case pg.K_j: template["attack_range"] = max(0, template["attack_range"] - 5)
                case pg.K_TAB: selected_ability_index = (selected_ability_index + 1) % len(abilities_list)
                case pg.K_r:
                    ability = abilities_list[selected_ability_index]
                    if ability in template["abilities"]: template["abilities"].remove(ability)
                    else: template["abilities"].append(ability)
                case pg.K_v:
                    selected_shape_index = (selected_shape_index + 1) % len(shapes_list)
                    template["shape"] = shapes_list[selected_shape_index]
pg.quit()
