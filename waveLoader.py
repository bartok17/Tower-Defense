import json
from random import choice
from enemy.enemy import Enemy

def load_enemy_templates(template_path):
    with open(template_path, "r") as f:
        return json.load(f)

def load_waves(waves_path):
    with open(waves_path, "r") as f:
        return json.load(f)

def load_all_waves(waves_path, template_path, waypoints):
    templates = load_enemy_templates(template_path)
    waves_data = load_waves(waves_path)
    all_waves = []

    for wave in waves_data:
        enemies = []
        unit_list = wave["units"]
        p_time = wave["P_time"]
        mode = wave.get("mode", 0)
        for enemy_id, count in unit_list:
            str_id = str(enemy_id)
            template = dict(templates.get(str_id))  
            template["id"] = enemy_id  
            for _ in range(count):
                enemy = Enemy(waypoints[choice(list(waypoints.keys()))], template)
                enemies.append(enemy)

        all_waves.append({
            "P_time": p_time,
            "mode": mode,
            "enemies": enemies
        })

    return all_waves
