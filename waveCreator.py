"""Script to create waves and import them to json"""
import pygame as pg
import json
import os
import constants as con

os.makedirs(con.DATA_DIR, exist_ok=True)

pg.init()
screen = pg.display.set_mode((1000, 700))
clock = pg.time.Clock()
font = pg.font.SysFont(None, 24)

template = {
    "id": 1,
    "P_time": 0,
    "inter_wave_delay": 30,
    "passive_gold": 50,
    "passive_wood": 25,
    "passive_metal": 25,
    "units": [],
    "mode": 1
}
with open(os.path.join(con.DATA_DIR, "enemyTemplates.json"), "r") as f:
    enemy_templates = json.load(f)
available_units = [{"unit_id": int(k), "number": 1} for k in enemy_templates.keys()]
selected_idx = 0

template_path = os.path.join(con.DATA_DIR, "Waves.json")
if os.path.exists(template_path):
    with open(template_path, "r") as f:
        templates = json.load(f)
else:
    templates = {}

def draw_interface():
    screen.fill((30, 30, 30))
    lines_left = [
        f"Wave ID: {template['id']}",
        f"Prep Time (P_time): {template['P_time']}  [Q/W]",
        f"Inter-Wave Delay: {template['inter_wave_delay']} [E/R]",
        f"Mode: {template['mode']}  [T/Y]",
        f"Passive Gold: {template['passive_gold']} [U/I]",
        f"Passive Wood: {template['passive_wood']} [J/K]",
        f"Passive Metal: {template['passive_metal']} [N/M]",
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
                # Save current wave
                idx = [int(k) for k in templates.keys()]
                next_id = max(idx, default=0) + 1
                template['id'] = next_id
                templates[str(template['id'])] = dict(template)
                with open(template_path, "w") as f:
                    json.dump(templates, f, indent=2)
                print(f"Saved wave ID {template['id']}")
            elif event.key == pg.K_RIGHT:
                template['id'] += 1
            elif event.key == pg.K_LEFT:
                template['id'] = max(1, template['id'] - 1)
            elif event.key == pg.K_q:
                template['P_time'] = max(0, template['P_time'] - 1)
            elif event.key == pg.K_w:
                template['P_time'] += 1
            elif event.key == pg.K_e:
                template['inter_wave_delay'] = max(0, template['inter_wave_delay'] - 1)
            elif event.key == pg.K_r:
                template['inter_wave_delay'] += 1
            elif event.key == pg.K_t:
                template['mode'] = max(0, template['mode'] - 1)
            elif event.key == pg.K_y:
                template['mode'] += 1
            # Passive income controls
            elif event.key == pg.K_u:
                template['passive_gold'] = max(0, template['passive_gold'] - 5)
            elif event.key == pg.K_i:
                template['passive_gold'] += 5
            elif event.key == pg.K_j:
                template['passive_wood'] = max(0, template['passive_wood'] - 5)
            elif event.key == pg.K_k:
                template['passive_wood'] += 5
            elif event.key == pg.K_n:
                template['passive_metal'] = max(0, template['passive_metal'] - 5)
            elif event.key == pg.K_m:
                template['passive_metal'] += 5
            elif event.key == pg.K_TAB:
                selected_idx = (selected_idx + 1) % len(available_units)
            elif event.key == pg.K_s:
                available_units[selected_idx]['number'] = max(1, available_units[selected_idx]['number'] - 1)
            elif event.key == pg.K_d:
                available_units[selected_idx]['number'] += 1
            elif event.key == pg.K_a:
                # Add selected unit to wave
                selected = available_units[selected_idx]
                found = False
                for unit in template['units']:
                    if unit[0] == selected['unit_id']:
                        unit[1] += selected['number']
                        found = True
                        break
                if not found:
                    template['units'].append([selected['unit_id'], selected['number']])
            elif event.key == pg.K_r:
                # Remove selected unit from wave
                selected = available_units[selected_idx]
                template['units'] = [unit for unit in template['units'] if unit[0] != selected['unit_id']]

    clock.tick(30)

pg.quit()
