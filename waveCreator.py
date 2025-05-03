"""Script to create waves and import them to json"""
import pygame as pg
import json
import os

pg.init()
screen = pg.display.set_mode((1000, 700))
clock = pg.time.Clock()
font = pg.font.SysFont(None, 24)

template = {
    "id": 1,
    "P_time": 0,
    "units": [],
    "mode": 1
}
with open("enemyTemplates.json", "r") as f:
    enemy_templates = json.load(f)
available_units = [{"unit_id": int(k), "number": 1} for k in enemy_templates.keys()]
selected_idx = 0

template_path = "Waves.json"
if os.path.exists(template_path):
    with open(template_path, "r") as f:
        templates = json.load(f)
else:
    templates = {}

def draw_interface():
    screen.fill((30, 30, 30))
    lines_left = [
        f"Wave ID: {template['id']}",
        f"Time: {template['P_time']}  [Q/W]",
        f"Mode: {template['mode']}  [T/Y]",
        "Units in wave:",
    ]
    for unit in template['units']:
        lines_left.append(f"  ID {unit[0]} x {unit[1]}")

    for i, line in enumerate(lines_left):
        text = font.render(line, True, (200, 200, 200))
        screen.blit(text, (20, 20 + i * 25))

    lines_right = ["Available units (TAB to select, S/D - change count, A to add to template):"]
    for i, unit in enumerate(available_units):
        prefix = "-> " if i == selected_idx else "  "
        lines_right.append(f"{prefix}ID {unit['unit_id']} x {unit['number']}")

    for i, line in enumerate(lines_right):
        color = (200, 200, 0) if i == selected_idx + 1 else (200, 200, 200)
        text = font.render(line, True, color)
        screen.blit(text, (450, 20 + i * 25))

    pg.display.flip()

running = True
while running:
    draw_interface()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
            elif event.key == pg.K_RETURN:
                idx = [int(k) for k in templates.keys()]
                next_id = max(idx, default=0) + 1
                template['id'] = next_id
                templates[str(template['id'])] = dict(template)
                templates[str(template['id'])] = dict(template)
                with open(template_path, "w") as f:
                    json.dump(templates, f, indent=2)
                print(f"Saved wave ID {template['id']}")
            elif event.key == pg.K_RIGHT: template['id'] += 1
            elif event.key == pg.K_LEFT: template['id'] = max(1, template['id'] - 1)
            elif event.key == pg.K_q: template['P_time'] = max(0, template['P_time'] - 1)
            elif event.key == pg.K_w: template['P_time'] += 1
            elif event.key == pg.K_t: template['mode'] = max(0, template['mode'] - 1)
            elif event.key == pg.K_y: template['mode'] += 1
            elif event.key == pg.K_TAB: selected_idx = (selected_idx + 1) % len(available_units)
            elif event.key == pg.K_s: available_units[selected_idx]['number'] = max(1, available_units[selected_idx]['number'] - 1)
            elif event.key == pg.K_d: available_units[selected_idx]['number'] += 1
            elif event.key == pg.K_a:
                selected = available_units[selected_idx]
                found = False
                for unit in template['units']:
                    if unit[0] == selected['unit_id']:
                        unit[1] += selected['number']
                        found = True
                        break
                if not found: template['units'].append([selected['unit_id'], selected['number']])
            elif event.key == pg.K_r:
                selected = available_units[selected_idx]
                template['units'] = [unit for unit in template['units'] if unit[0] != selected['unit_id']]

    clock.tick(30)

pg.quit()
