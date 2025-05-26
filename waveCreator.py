import pygame as pg
import json
import os
import constants as con
import glob

os.makedirs(con.DATA_DIR, exist_ok=True)

pg.init()
screen_width = 1000
screen_height = 700
screen = pg.display.set_mode((screen_width, screen_height))
pg.display.set_caption("Wave Creator")
clock = pg.time.Clock()
font = pg.font.SysFont(None, 24)
font_small = pg.font.SysFont(None, 20)

def get_default_wave_template():
    return {
        "id": 1,
        "P_time": 10,
        "inter_wave_delay": 30,
        "passive_gold": 50,
        "passive_wood": 25,
        "passive_metal": 25,
        "units": [],
        "mode": 1
    }

def choose_wave_file():
    print("\nWave File Management:")
    action = input("Create (N)ew wave file or (E)dit existing? (N/E): ").strip().lower()
    if action == 'n':
        base_name = input("Enter a base name for the new wave file (e.g., level1, tutorial): ").strip()
        if not base_name:
            print("No name entered. Exiting.")
            return None, None
        file_path = os.path.join(con.DATA_DIR, f"waves_{base_name}.json")
        if os.path.exists(file_path):
            overwrite = input(f"File '{file_path}' already exists. Overwrite with empty data? (y/N): ").strip().lower()
            if overwrite != 'y':
                print("Exiting to prevent overwrite.")
                return None, None
        print(f"Creating new wave file: {file_path}")
        return file_path, {}
    elif action == 'e':
        wave_files = glob.glob(os.path.join(con.DATA_DIR, "waves_*.json"))
        if not wave_files:
            print("No existing wave files (waves_*.json) found in data directory.")
            new_file_choice = input("Create a new one instead? (Y/n): ").strip().lower()
            if new_file_choice == 'n':
                return None, None
            else:
                base_name = input("Enter a base name for the new wave file (e.g., level1): ").strip()
                if not base_name:
                    print("No name entered. Exiting.")
                    return None, None
                file_path = os.path.join(con.DATA_DIR, f"waves_{base_name}.json")
                print(f"Creating new wave file: {file_path}")
                return file_path, {}
        print("Available wave files:")
        for i, f_path in enumerate(wave_files):
            print(f"  {i+1}. {os.path.basename(f_path)}")
        try:
            choice = int(input(f"Enter number of file to edit (1-{len(wave_files)}): ").strip()) - 1
            if 0 <= choice < len(wave_files):
                file_path = wave_files[choice]
                print(f"Loading wave file: {file_path}")
                with open(file_path, "r") as f:
                    try:
                        loaded_waves = json.load(f)
                        return file_path, loaded_waves
                    except json.JSONDecodeError:
                        print(f"Error: File '{file_path}' is not valid JSON. Starting with empty data for this file.")
                        return file_path, {}
            else:
                print("Invalid choice.")
                return None, None
        except ValueError:
            print("Invalid input.")
            return None, None
    else:
        print("Invalid action.")
        return None, None

current_wave_file_path, all_waves_in_file = choose_wave_file()

if current_wave_file_path is None:
    pg.quit()
    exit()

current_wave_edit_buffer = get_default_wave_template()
active_wave_id = None

if all_waves_in_file:
    first_wave_id_str = sorted(all_waves_in_file.keys(), key=lambda x: int(x))[0]
    active_wave_id = int(first_wave_id_str)
    current_wave_edit_buffer = dict(all_waves_in_file[first_wave_id_str])
else:
    current_wave_edit_buffer['id'] = 1

with open(os.path.join(con.DATA_DIR, "enemyTemplates.json"), "r") as f:
    enemy_templates_data = json.load(f)
available_units_for_selection = [{"unit_id": int(k), "name": enemy_templates_data[k].get("name", f"Unit {k}"), "number": 1} for k in enemy_templates_data.keys()]
selected_unit_idx = 0
status_message = ""
status_message_timer = 0

def set_status_message(msg, duration=120):
    global status_message, status_message_timer
    status_message = msg
    status_message_timer = duration

def draw_interface():
    global status_message, status_message_timer
    screen.fill((30, 30, 30))

    file_info_text = font.render(f"Editing File: {os.path.basename(current_wave_file_path)}", True, (200, 200, 0))
    screen.blit(file_info_text, (20, 20))
    
    active_wave_text_val = str(active_wave_id) if active_wave_id is not None else "NEW (Not in file yet)"
    active_wave_info = font.render(f"Active Wave ID in Editor: {current_wave_edit_buffer['id']} (Loaded: {active_wave_text_val})", True, (200, 200, 0))
    screen.blit(active_wave_info, (20, 50))

    y_offset = 90
    lines_left = [
        f"Wave ID (in editor): {current_wave_edit_buffer['id']}  [UP/DOWN to change]",
        f"Prep Time (P_time): {current_wave_edit_buffer['P_time']}s  [Q/W]",
        f"Inter-Wave Delay: {current_wave_edit_buffer['inter_wave_delay']}s [E/R]",
        f"Mode: {current_wave_edit_buffer['mode']}  [T/Y]",
        f"Passive Gold: {current_wave_edit_buffer['passive_gold']} [U/I]",
        f"Passive Wood: {current_wave_edit_buffer['passive_wood']} [J/K]",
        f"Passive Metal: {current_wave_edit_buffer['passive_metal']} [O/P]",
        "Units in this wave (ID, Count):",
    ]
    for unit_data in current_wave_edit_buffer['units']:
        unit_id, unit_count = unit_data[0], unit_data[1]
        unit_name = enemy_templates_data.get(str(unit_id), {}).get("name", f"Unknown Unit {unit_id}")
        lines_left.append(f"  {unit_name} (ID:{unit_id}) x {unit_count}")

    for i, line in enumerate(lines_left):
        text = font.render(line, True, (200, 200, 200))
        screen.blit(text, (20, y_offset + i * 25))

    x_offset_right = 500
    lines_right = ["Available Enemy Templates (TAB to select, S/D count, A to add, X to remove selected type from wave):"]
    for i, unit_sel_info in enumerate(available_units_for_selection):
        prefix = "-> " if i == selected_unit_idx else "   "
        lines_right.append(f"{prefix}{unit_sel_info['name']} (ID:{unit_sel_info['unit_id']}) x {unit_sel_info['number']}")
    
    for i, line in enumerate(lines_right):
        color = (200, 200, 0) if i == selected_unit_idx + 1 and i > 0 else (200, 200, 200)
        text = font.render(line, True, color)
        screen.blit(text, (x_offset_right, y_offset + i * 25))

    waves_in_file_title = font.render("Waves in this File (IDs):", True, (150, 150, 255))
    screen.blit(waves_in_file_title, (x_offset_right, 20))
    
    sorted_wave_ids = sorted(all_waves_in_file.keys(), key=lambda x: int(x))
    max_waves_to_display = 15
    for i, wave_id_str in enumerate(sorted_wave_ids):
        if i >= max_waves_to_display:
            more_text = font_small.render(f"...and {len(sorted_wave_ids) - max_waves_to_display} more.", True, (150,150,255))
            screen.blit(more_text, (x_offset_right, 50 + (i) * 20))
            break
        color = (0, 255, 0) if active_wave_id is not None and int(wave_id_str) == active_wave_id else (150, 150, 255)
        text = font_small.render(f"  Wave {wave_id_str}", True, color)
        screen.blit(text, (x_offset_right, 50 + i * 20))
    if not sorted_wave_ids:
        text = font_small.render("  (No waves saved in memory for this file yet)", True, (150,150,150))
        screen.blit(text, (x_offset_right, 50))

    y_instr_start = screen_height - 100
    instructions = [
        "F1: New Wave | F2: Load Wave (console) | ENTER: Save Wave to Memory | DEL: Delete Active Wave from Memory",
        "F12: SAVE ALL WAVES TO FILE | ESC: Quit (without saving to file unless F12 was used)"
    ]
    for i, line in enumerate(instructions):
        text = font_small.render(line, True, (100, 255, 100))
        screen.blit(text, (20, y_instr_start + i * 20))
    
    if status_message_timer > 0:
        status_text_surf = font.render(status_message, True, (255, 255, 0))
        status_rect = status_text_surf.get_rect(center=(screen_width // 2, screen_height - 25))
        screen.blit(status_text_surf, status_rect)
        status_message_timer -= 1
    else:
        status_message = ""

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
            elif event.key == pg.K_UP:
                current_wave_edit_buffer['id'] = max(1, current_wave_edit_buffer['id'] + 1)
            elif event.key == pg.K_DOWN:
                current_wave_edit_buffer['id'] = max(1, current_wave_edit_buffer['id'] - 1)
            elif event.key == pg.K_q:
                current_wave_edit_buffer['P_time'] = max(0, current_wave_edit_buffer['P_time'] - 1)
            elif event.key == pg.K_w:
                current_wave_edit_buffer['P_time'] += 1
            elif event.key == pg.K_e:
                current_wave_edit_buffer['inter_wave_delay'] = max(0, current_wave_edit_buffer['inter_wave_delay'] - 1)
            elif event.key == pg.K_r:
                current_wave_edit_buffer['inter_wave_delay'] += 1
            elif event.key == pg.K_t:
                current_wave_edit_buffer['mode'] = max(0, current_wave_edit_buffer['mode'] - 1)
            elif event.key == pg.K_y:
                current_wave_edit_buffer['mode'] += 1
            elif event.key == pg.K_u:
                current_wave_edit_buffer['passive_gold'] = max(0, current_wave_edit_buffer['passive_gold'] - 5)
            elif event.key == pg.K_i:
                current_wave_edit_buffer['passive_gold'] += 5
            elif event.key == pg.K_j:
                current_wave_edit_buffer['passive_wood'] = max(0, current_wave_edit_buffer['passive_wood'] - 5)
            elif event.key == pg.K_k:
                current_wave_edit_buffer['passive_wood'] += 5
            elif event.key == pg.K_o:
                current_wave_edit_buffer['passive_metal'] = max(0, current_wave_edit_buffer['passive_metal'] - 5)
            elif event.key == pg.K_p:
                current_wave_edit_buffer['passive_metal'] += 5
            elif event.key == pg.K_TAB:
                selected_unit_idx = (selected_unit_idx + 1) % len(available_units_for_selection)
            elif event.key == pg.K_s:
                available_units_for_selection[selected_unit_idx]['number'] = max(1, available_units_for_selection[selected_unit_idx]['number'] - 1)
            elif event.key == pg.K_d:
                available_units_for_selection[selected_unit_idx]['number'] += 1
            elif event.key == pg.K_a:
                selected_unit_info = available_units_for_selection[selected_unit_idx]
                unit_id_to_add = selected_unit_info['unit_id']
                num_to_add = selected_unit_info['number']
                found = False
                for unit_in_wave in current_wave_edit_buffer['units']:
                    if unit_in_wave[0] == unit_id_to_add:
                        unit_in_wave[1] += num_to_add
                        found = True
                        break
                if not found:
                    current_wave_edit_buffer['units'].append([unit_id_to_add, num_to_add])
                set_status_message(f"Added {num_to_add} of Unit ID {unit_id_to_add} to wave buffer.")
            elif event.key == pg.K_x:
                unit_id_to_remove = available_units_for_selection[selected_unit_idx]['unit_id']
                initial_len = len(current_wave_edit_buffer['units'])
                current_wave_edit_buffer['units'] = [u for u in current_wave_edit_buffer['units'] if u[0] != unit_id_to_remove]
                if len(current_wave_edit_buffer['units']) < initial_len:
                    set_status_message(f"Removed Unit ID {unit_id_to_remove} from wave buffer.")
                else:
                    set_status_message(f"Unit ID {unit_id_to_remove} not in wave buffer.")
            elif event.key == pg.K_F1:
                active_wave_id = None 
                current_wave_edit_buffer = get_default_wave_template()
                if all_waves_in_file:
                    next_id_val = max((int(k) for k in all_waves_in_file.keys()), default=0) + 1
                else:
                    next_id_val = 1
                current_wave_edit_buffer['id'] = next_id_val
                set_status_message(f"Cleared buffer for new wave. Suggested ID: {next_id_val}")
            elif event.key == pg.K_F2:
                pg.display.iconify()
                try:
                    load_id_str = input(f"Enter Wave ID to load from memory (Available: {', '.join(sorted(all_waves_in_file.keys(), key=int))}): ").strip()
                    if load_id_str in all_waves_in_file:
                        active_wave_id = int(load_id_str)
                        current_wave_edit_buffer = dict(all_waves_in_file[load_id_str])
                        set_status_message(f"Loaded Wave ID {active_wave_id} into buffer.")
                    else:
                        set_status_message(f"Error: Wave ID {load_id_str} not found in memory for this file.")
                except Exception as e:
                    set_status_message(f"Error during load: {e}")
            elif event.key == pg.K_RETURN:
                editor_wave_id = current_wave_edit_buffer['id']
                editor_wave_id_str = str(editor_wave_id)
                if active_wave_id is not None and active_wave_id != editor_wave_id:
                    if editor_wave_id_str in all_waves_in_file:
                        set_status_message(f"Error: Target ID {editor_wave_id} already exists. Cannot change ID to this.")
                        current_wave_edit_buffer['id'] = active_wave_id
                    else:
                        del all_waves_in_file[str(active_wave_id)]
                        all_waves_in_file[editor_wave_id_str] = dict(current_wave_edit_buffer)
                        active_wave_id = editor_wave_id
                        set_status_message(f"Wave ID changed from {str(active_wave_id)} to {editor_wave_id_str} and saved to memory.")
                elif editor_wave_id_str in all_waves_in_file and active_wave_id is None:
                    set_status_message(f"Error: ID {editor_wave_id_str} already exists. Choose a different ID for this new wave.")
                else:
                    all_waves_in_file[editor_wave_id_str] = dict(current_wave_edit_buffer)
                    active_wave_id = editor_wave_id
                    set_status_message(f"Wave ID {editor_wave_id_str} saved/updated in memory.")
            elif event.key == pg.K_DELETE:
                if active_wave_id is not None:
                    wave_id_to_delete_str = str(active_wave_id)
                    if wave_id_to_delete_str in all_waves_in_file:
                        del all_waves_in_file[wave_id_to_delete_str]
                        set_status_message(f"Deleted Wave ID {wave_id_to_delete_str} from memory.")
                        active_wave_id = None
                        current_wave_edit_buffer = get_default_wave_template()
                        if all_waves_in_file:
                            current_wave_edit_buffer['id'] = max((int(k) for k in all_waves_in_file.keys()), default=0) + 1
                        else:
                            current_wave_edit_buffer['id'] = 1
                    else:
                        set_status_message(f"Error: Active Wave ID {active_wave_id} not in memory (should not happen).")
                else:
                    set_status_message("No active wave loaded to delete. Buffer is for a new wave.")
            elif event.key == pg.K_F12:
                try:
                    with open(current_wave_file_path, "w") as f:
                        json.dump(all_waves_in_file, f, indent=2)
                    set_status_message(f"All waves saved to file: {os.path.basename(current_wave_file_path)}")
                except Exception as e:
                    set_status_message(f"Error saving to file: {e}")

    clock.tick(30)

pg.quit()
