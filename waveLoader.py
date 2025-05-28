import json
from random import choice, uniform
from enemy.enemy import Enemy
import os
import constants as con
from path_utils import generate_offset_path

waves_path = os.path.join(con.DATA_DIR, "waves.json")
template_path = os.path.join(con.DATA_DIR, "enemyTemplates.json")

DEFAULT_INTER_ENEMY_SPAWN_DELAY_MS = 500

def load_enemy_templates(template_path):
    with open(template_path, "r") as f:
        return json.load(f)

def load_waves(waves_path):
    with open(waves_path, "r") as f:
        return json.load(f)

def load_all_waves(waves_path, template_path, waypoints):
    templates = load_enemy_templates(template_path)
    waves_data_from_file = load_waves(waves_path)
    all_processed_waves_sorted = []

    # Ensure waves are processed in order by wave ID
    sorted_wave_ids = []
    if isinstance(waves_data_from_file, dict):
        try:
            sorted_wave_ids = sorted(waves_data_from_file.keys(), key=int)
        except ValueError:
            print(f"Warning: Could not sort wave IDs numerically from {waves_path}. Using default order.")
            sorted_wave_ids = waves_data_from_file.keys()
    else:
        print(f"Warning: Expected a dictionary of waves in {waves_path}, got {type(waves_data_from_file)}.")
        return []

    for wave_id_str in sorted_wave_ids:
        wave_content = waves_data_from_file[wave_id_str]
        p_time = wave_content.get("P_time", 10)
        mode = wave_content.get("mode", 0)
        passive_gold = wave_content.get("passive_gold", 0)
        passive_wood = wave_content.get("passive_wood", 0)
        passive_metal = wave_content.get("passive_metal", 0)
        unit_definitions = wave_content.get("units", [])

        enemy_groups_for_wave = []
        for unit_entry in unit_definitions:
            enemy_id, count, delay_after_group_sec = -1, 0, 0.0
            inter_spawn_delay_ms = DEFAULT_INTER_ENEMY_SPAWN_DELAY_MS

            if isinstance(unit_entry, list):
                if len(unit_entry) == 4:
                    enemy_id, count, delay_after_group_sec, inter_spawn_delay_ms = unit_entry
                elif len(unit_entry) == 3:
                    enemy_id, count, delay_after_group_sec = unit_entry
                elif len(unit_entry) == 2:
                    enemy_id, count = unit_entry
                    delay_after_group_sec = 0.0
                else:
                    print(f"Warning: Malformed unit entry in wave {wave_id_str}: {unit_entry}. Skipping.")
                    continue
            else:
                print(f"Warning: Unit entry is not a list in wave {wave_id_str}: {unit_entry}. Skipping.")
                continue

            str_id = str(enemy_id)
            if str_id not in templates:
                print(f"Warning: Enemy template ID '{enemy_id}' not found for wave {wave_id_str}. Skipping this unit group.")
                continue

            template_copy = dict(templates[str_id])
            template_copy["id"] = enemy_id

            enemies_in_this_group = []
            for _ in range(count):
                # Randomize path and offset for each enemy
                chosen_path_name = choice(list(waypoints.keys()))
                original_path_tuples = waypoints[chosen_path_name]
                enemy_offset = uniform(-20.0, 20.0)
                offset_enemy_path = generate_offset_path(original_path_tuples, enemy_offset)
                enemy = Enemy(offset_enemy_path, template_copy)
                enemies_in_this_group.append(enemy)

            if enemies_in_this_group:
                enemy_groups_for_wave.append({
                    "enemies_to_spawn": enemies_in_this_group,
                    "delay_after_group": delay_after_group_sec,
                    "inter_enemy_spawn_delay_ms": inter_spawn_delay_ms
                })

        all_processed_waves_sorted.append({
            "P_time": p_time,
            "mode": mode,
            "enemy_groups": enemy_groups_for_wave,
            "passive_gold": passive_gold,
            "passive_wood": passive_wood,
            "passive_metal": passive_metal
        })

    return all_processed_waves_sorted

def load_wave_by_id(waves_path, template_path, wave_id_to_load, waypoints):
    templates = load_enemy_templates(template_path)
    waves_data_from_file = load_waves(waves_path)

    wave_content = waves_data_from_file.get(str(wave_id_to_load))
    if not wave_content:
        print(f"Warning: Wave ID {wave_id_to_load} not found in {waves_path}.")
        return None

    p_time = wave_content.get("P_time", 10)
    mode = wave_content.get("mode", 0)
    passive_gold = wave_content.get("passive_gold", 0)
    passive_wood = wave_content.get("passive_wood", 0)
    passive_metal = wave_content.get("passive_metal", 0)
    unit_definitions = wave_content.get("units", [])

    enemy_groups_for_wave = []
    for unit_entry in unit_definitions:
        enemy_id, count, delay_after_group_sec = -1, 0, 0.0
        inter_spawn_delay_ms = DEFAULT_INTER_ENEMY_SPAWN_DELAY_MS

        if isinstance(unit_entry, list):
            if len(unit_entry) == 4:
                enemy_id, count, delay_after_group_sec, inter_spawn_delay_ms = unit_entry
            elif len(unit_entry) == 3:
                enemy_id, count, delay_after_group_sec = unit_entry
            elif len(unit_entry) == 2:
                enemy_id, count = unit_entry
                delay_after_group_sec = 0.0
            else:
                print(f"Warning: Malformed unit entry in wave {wave_id_to_load}: {unit_entry}. Skipping.")
                continue
        else:
            print(f"Warning: Unit entry is not a list in wave {wave_id_to_load}: {unit_entry}. Skipping.")
            continue

        str_id = str(enemy_id)
        if str_id not in templates:
            print(f"Warning: Enemy template ID '{enemy_id}' not found for wave {wave_id_to_load}. Skipping.")
            continue

        template_copy = dict(templates[str_id])
        template_copy["id"] = enemy_id

        enemies_in_this_group = []
        for _ in range(count):
            chosen_path_name = choice(list(waypoints.keys()))
            original_path_tuples = waypoints[chosen_path_name]
            enemy_offset = uniform(-20.0, 20.0)
            offset_enemy_path = generate_offset_path(original_path_tuples, enemy_offset)
            enemy = Enemy(offset_enemy_path, template_copy)
            enemies_in_this_group.append(enemy)

        if enemies_in_this_group:
            enemy_groups_for_wave.append({
                "enemies_to_spawn": enemies_in_this_group,
                "delay_after_group": delay_after_group_sec,
                "inter_enemy_spawn_delay_ms": inter_spawn_delay_ms
            })

    return {
        "P_time": p_time,
        "mode": mode,
        "enemy_groups": enemy_groups_for_wave,
        "passive_gold": passive_gold,
        "passive_wood": passive_wood,
        "passive_metal": passive_metal
    }
