import pygame as pg
import constants as con
from waypointsCreator import load_lists_from_json
import waveLoader as wl
from Button import Button
from Tower import Tower, create_tower
from dummyEntity import dummyEntity
from economy import ResourcesManager
from building import BuildingBlueprint
from typing import List
from projectile import Projectile
import building.buildManager as bm
from endingScreen import EndingScreen
from userInterface import UserInterface
import os
import json
import random

LEVELS_CONFIG_FILENAME = "levels_config.json"

class GameState:
    MAIN_MENU = 0
    LEVEL_SELECT = 1
    PRE_WAVE = 2
    WAVE_ACTIVE = 3
    GAME_OVER = 4
    VICTORY = 5
    QUIT = 6

def initialize_game():
    pg.init()
    screen = pg.display.set_mode((con.SCREEN_WIDTH, con.SCREEN_HEIGHT), pg.SCALED | pg.RESIZABLE)

    pg.display.set_caption("Bardzo fajna gra")
    clock = pg.time.Clock()
    return screen, clock

def load_assets(level_config):
    os.makedirs(con.ASSETS_DIR, exist_ok=True)
    map_img = pg.image.load(os.path.join(con.ASSETS_DIR, level_config["map_image_path"])).convert_alpha()
    button_img = pg.image.load(os.path.join(con.ASSETS_DIR, "button_template.png")).convert_alpha()
    factory_metal_img = pg.image.load(os.path.join(con.ASSETS_DIR, "factory_metal_icon.png")).convert_alpha()
    factory_wood_img = pg.image.load(os.path.join(con.ASSETS_DIR, "factory_wood_icon.png")).convert_alpha()
    tower_basic_img = pg.image.load(os.path.join(con.ASSETS_DIR, "tower_basic_icon.png")).convert_alpha()
    tower_cannon_img = pg.image.load(os.path.join(con.ASSETS_DIR, "tower_cannon_icon.png")).convert_alpha()
    tower_flame_img = pg.image.load(os.path.join(con.ASSETS_DIR, "tower_flame_icon.png")).convert_alpha()
    tower_rapid_img = pg.image.load(os.path.join(con.ASSETS_DIR, "tower_rapid_icon.png")).convert_alpha()
    tower_sniper_img = pg.image.load(os.path.join(con.ASSETS_DIR, "tower_sniper_icon.png")).convert_alpha()

    waypoints_path = os.path.join(con.DATA_DIR, level_config["waypoints_path"])
    waypoints = load_lists_from_json(waypoints_path)

    factory_blueprints = [
        BuildingBlueprint("Metal Factory", factory_metal_img, {"gold": 60}, 40, 40,
                          bm.build_factory, resource="metal", payout_per_wave=10),
        BuildingBlueprint("Wood Factory", factory_wood_img, {"gold": 40}, 40, 40,
                          bm.build_factory, resource="wood", payout_per_wave=15),
    ]

    # Master list of all possible tower blueprints
    all_tower_blueprints_data = [
        {"name": "Tower - basic", "image": tower_basic_img, "cost": {"gold": 50}, "width": 40, "height": 40, "build_function": bm.build_tower, "tower_type": "basic"},
        {"name": "Tower - cannon", "image": tower_cannon_img, "cost": {"gold": 150, "wood": 70, "metal": 20}, "width": 40, "height": 40, "build_function": bm.build_tower, "tower_type": "cannon"},
        {"name": "Tower - flame", "image": tower_flame_img, "cost": {"gold": 200, "wood": 100}, "width": 40, "height": 40, "build_function": bm.build_tower, "tower_type": "flame"},
        {"name": "Tower - rapid", "image": tower_rapid_img, "cost": {"gold": 150, "wood": 20}, "width": 40, "height": 40, "build_function": bm.build_tower, "tower_type": "rapid"},
        {"name": "Tower - sniper", "image": tower_sniper_img, "cost": {"gold": 200, "metal": 10}, "width": 40, "height": 40, "build_function": bm.build_tower, "tower_type": "sniper"},
    ]

    level_tower_blueprints = []
    available_tower_types = level_config.get("available_towers", []) # Get allowed types, default to empty list

    for data in all_tower_blueprints_data:
        if data["tower_type"] in available_tower_types:
            level_tower_blueprints.append(
                BuildingBlueprint(data["name"], data["image"], data["cost"], data["width"], data["height"],
                                  data["build_function"], tower_type=data["tower_type"])
            )

    factory_buttons = []
    tower_buttons = []
    # Button positioning can remain similar, but will now use the filtered blueprints
    # Assuming UserInterface or button drawing logic handles positioning dynamically or you adjust here
    # For simplicity, this example keeps the original button creation loop structure
    # but iterates over the filtered `level_tower_blueprints`.

    for i, blueprint in enumerate(factory_blueprints): # Factories are not level-restricted in this example
        btn = Button(0, 0, blueprint.image, blueprint.name, width=blueprint.width, height=blueprint.height, )
        factory_buttons.append(btn)

    for i, blueprint in enumerate(level_tower_blueprints):
        # You might want to adjust button positioning if the number of towers changes significantly
        btn = Button(con.SCREEN_WIDTH - 80, 50 + i * 60, blueprint.image, blueprint.name, width=blueprint.width, height=blueprint.height)
        tower_buttons.append(btn)
        
    return map_img, button_img, waypoints, factory_buttons, factory_blueprints, tower_buttons, level_tower_blueprints # Return filtered tower blueprints

def draw_waypoints(screen, waypoints):
    for name, road in waypoints.items():
        pg.draw.lines(screen, "red", False, road, 2)

def update_enemies(clock_tick, enemies_list, base, resources_manager):
    for e in enemies_list:
        e.all_enemies = enemies_list
        e.enemies_ref = enemies_list
    for enemy in enemies_list[:]:
        enemy.update(clock_tick)
        if enemy.has_finished():
            resources_manager.spend_resource("health", 10)
            enemies_list.remove(enemy)
            continue
        if enemy.is_dead():
            enemies_list.remove(enemy)
            resources_manager.add_resource("gold", enemy.gold_reward)

def update_towers(clock_tick, towers, enemies_list, waypoints, projectiles):
    delta_time_seconds = clock_tick / 1000.0
    for tower in towers:
        # Manage cooldown between shots
        if tower.current_reload > 0:
            tower.current_reload -= delta_time_seconds
            tower.current_reload = max(0, tower.current_reload)

        # Manage magazine reloading
        if tower.is_reloading_magazine:
            tower.current_magazine_reload_timer -= delta_time_seconds
            if tower.current_magazine_reload_timer <= 0:
                tower.current_magazine_shots = tower.stats.magazine_size
                tower.is_reloading_magazine = False
                tower.current_magazine_reload_timer = 0 # Reset magazine reload timer
        else:
            # If magazine isn't full and not currently reloading, start the reload process
            if tower.current_magazine_shots < tower.stats.magazine_size:
                tower.is_reloading_magazine = True
                tower.current_magazine_reload_timer = tower.stats.magazine_reload_time

        # Tower attempts to attack targets
        tower.attack(enemies_list, waypoints, projectiles)

def update_projectiles(clock_tick: int, projectiles: List[Projectile], enemies_list: list):
    for projectile in projectiles[:]:
        projectile.update(clock_tick, enemies_list)
        if not projectile.active:
            if hasattr(projectile, 'on_removed'):
                projectile.on_removed()
            projectiles.remove(projectile)

def run_main_menu(screen, clock):
    title_font = pg.font.Font(None, 74)
    button_font = pg.font.Font(None, 50)
    title_text = title_font.render("Tower Defense Game", True, (200, 200, 200))
    title_rect = title_text.get_rect(center=(con.SCREEN_WIDTH // 2, con.SCREEN_HEIGHT // 4))

    start_button = Button(
        con.SCREEN_WIDTH // 2 - 150, con.SCREEN_HEIGHT // 2 - 50, None,
        text="Start Game", text_color=(255, 255, 255), font_size=40,
        width=300, height=60, color=(0, 180, 0)
    )
    quit_button = Button(
        con.SCREEN_WIDTH // 2 - 150, con.SCREEN_HEIGHT // 2 + 40, None,
        text="Quit", text_color=(255, 255, 255), font_size=40,
        width=300, height=60, color=(180, 0, 0)
    )

    running = True
    next_state = GameState.MAIN_MENU

    while running:
        mouse_pos = pg.mouse.get_pos()
        for event in pg.event.get():

            if event.type == pg.QUIT:
                running = False
                next_state = GameState.QUIT
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if start_button.is_clicked(mouse_pos):
                    running = False
                    next_state = GameState.LEVEL_SELECT
                elif quit_button.is_clicked(mouse_pos):
                    running = False
                    next_state = GameState.QUIT

        screen.fill((30, 30, 30))
        screen.blit(title_text, title_rect)
        start_button.draw(screen)
        quit_button.draw(screen)
        pg.display.update()
        clock.tick(con.FPS)

    return next_state

def run_level_select(screen, clock, levels_config):
    title_font = pg.font.Font(None, 60)
    level_button_height = 50
    level_button_spacing = 20
    start_y = 150

    title_text = title_font.render("Select Level", True, (200, 200, 200))
    title_rect = title_text.get_rect(center=(con.SCREEN_WIDTH // 2, 70))

    level_buttons = []
    for i, level_conf in enumerate(levels_config):
        if level_conf["unlocked"]:
            btn_text = level_conf["name"]
            btn_color = (0, 150, 150)
        else:
            btn_text = f"{level_conf['name']} (Locked)"
            btn_color = (100, 100, 100)

        button = Button(
            con.SCREEN_WIDTH // 2 - 200, start_y + i * (level_button_height + level_button_spacing),
            None, text=btn_text, text_color=(255,255,255), font_size=30,
            width=400, height=level_button_height, color=btn_color
        )
        level_buttons.append({"button": button, "config": level_conf, "unlocked": level_conf["unlocked"]})

    back_button = Button(
        50, con.SCREEN_HEIGHT - 70, None, text="Back", text_color=(255,255,255), font_size=30,
        width=100, height=40, color=(150,150,0)
    )

    running = True
    next_state = GameState.LEVEL_SELECT
    selected_level_config = None

    while running:
        mouse_pos = pg.mouse.get_pos()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                next_state = GameState.QUIT
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if back_button.is_clicked(mouse_pos):
                    running = False
                    next_state = GameState.MAIN_MENU
                for item in level_buttons:
                    if item["unlocked"] and item["button"].is_clicked(mouse_pos):
                        running = False
                        selected_level_config = item["config"]
                        next_state = GameState.PRE_WAVE
                        break

        screen.fill((40, 40, 40))
        screen.blit(title_text, title_rect)
        for item in level_buttons:
            item["button"].draw(screen)
        back_button.draw(screen)
        pg.display.update()
        clock.tick(con.FPS)

    return next_state, selected_level_config

def run_game_loop(screen, clock, selected_level_config):
    (map_img, button_img, waypoints,
    factory_buttons, factory_blueprints,
    tower_buttons, tower_blueprints) = load_assets(selected_level_config)
    base = dummyEntity((0, 0))
    projectiles = []
    waves_data_list = wl.load_all_waves(
        os.path.join(con.DATA_DIR, selected_level_config["waves_path"]),
        os.path.join(con.DATA_DIR, "enemyTemplates.json"), waypoints)
    game_state_internal = "running"
    current_game_mode = GameState.PRE_WAVE
    current_wave_index = 0
    enemies_list = []
    selected_blueprint = None

    initial_gold = selected_level_config.get("start_gold", 100)
    initial_wood = selected_level_config.get("start_wood", 50)
    initial_metal = selected_level_config.get("start_metal", 25)
    initial_health = 100
    resources_manager = ResourcesManager(
        initial_gold=initial_gold,
        initial_wood=initial_wood,
        initial_metal=initial_metal,
        initial_health=initial_health
    )
    ui = UserInterface()

    road_seg = bm.generate_road_segments(waypoints)
    current_wave_data = None
    wave_preparation_timer = 0
    time_since_last_spawn_in_wave = 0

    # Variables for managing enemy spawning sequence within a wave
    current_group_idx_in_wave = 0
    spawn_idx_within_group = 0
    inter_group_delay_timer = 0.0

    start_wave_button = Button(
        con.SCREEN_WIDTH // 2 - 100, con.SCREEN_HEIGHT - 70, None,
        text=f"Start Wave {current_wave_index + 1}", text_color=(255, 255, 255), font_size=28,
        width=200, height=40, color=(0, 150, 0)
    )
    bm.factories.clear()
    bm.towers.clear()

    level_was_won = False

    while game_state_internal == "running":
        clock_tick = clock.tick(con.FPS)
        mouse_pos = pg.mouse.get_pos()

        for event in pg.event.get():
            ui.handle_panel_toggle(event, con.SCREEN_WIDTH, con.SCREEN_HEIGHT)
            if event.type == pg.QUIT:
                game_state_internal = "quit_to_menu"
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                clicked_on_ui_button_this_frame = False
                if current_game_mode == GameState.PRE_WAVE and \
                   current_wave_index < len(waves_data_list) and \
                   start_wave_button.is_clicked(mouse_pos):
                    current_game_mode = GameState.WAVE_ACTIVE
                    current_wave_data = waves_data_list[current_wave_index]
                    wave_preparation_timer = current_wave_data.get("P_time", 0) * 1000

                    # Reset wave-specific spawning variables
                    time_since_last_spawn_in_wave = 0
                    current_group_idx_in_wave = 0
                    spawn_idx_within_group = 0
                    inter_group_delay_timer = 0.0

                    start_wave_button.text = f"Wave {current_wave_index + 1} Active"
                    selected_blueprint = None
                    clicked_on_ui_button_this_frame = True
                if not clicked_on_ui_button_this_frame:
                    for idx, btn in enumerate(factory_buttons):
                        if btn.is_clicked(mouse_pos):
                            selected_blueprint = factory_blueprints[idx]
                            clicked_on_ui_button_this_frame = True
                            break

                    if not clicked_on_ui_button_this_frame:
                        for idx, btn in enumerate(tower_buttons):
                            if btn.is_clicked(mouse_pos):
                                selected_blueprint = tower_blueprints[idx]
                                clicked_on_ui_button_this_frame = True
                                break
                if selected_blueprint and not clicked_on_ui_button_this_frame:
                    adjusted_pos = (mouse_pos[0] - selected_blueprint.width // 2, mouse_pos[1] - selected_blueprint.height // 2 )
                    if bm.try_build(adjusted_pos, selected_blueprint, resources_manager, road_seg):
                        selected_blueprint = None
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if selected_blueprint:
                        selected_blueprint = None

        if game_state_internal == "quit_to_menu":
            return GameState.MAIN_MENU, level_was_won # Return to main menu if quit event occurs

        if current_game_mode == GameState.PRE_WAVE:
            if current_wave_index < len(waves_data_list):
                 start_wave_button.text = f"Start Wave {current_wave_index + 1}"
            else:
                 start_wave_button.text = "All Waves Cleared!"

        elif current_game_mode == GameState.WAVE_ACTIVE:
            wave_preparation_timer -= clock_tick
            if wave_preparation_timer <= 0 and current_wave_data:
                # Handles the spawning of enemies in the current wave
                if inter_group_delay_timer > 0:
                    inter_group_delay_timer -= clock_tick
                    if inter_group_delay_timer < 0:
                        inter_group_delay_timer = 0.0
                else:
                    enemy_groups_in_wave = current_wave_data.get("enemy_groups", [])
                    if current_group_idx_in_wave < len(enemy_groups_in_wave):
                        current_group_info = enemy_groups_in_wave[current_group_idx_in_wave]
                        enemies_to_spawn_this_group = current_group_info["enemies_to_spawn"]
                        delay_after_this_group_seconds = current_group_info["delay_after_group"]
                        current_inter_enemy_spawn_delay = current_group_info.get("inter_enemy_spawn_delay_ms", 500)

                        if spawn_idx_within_group < len(enemies_to_spawn_this_group):
                            time_since_last_spawn_in_wave += clock_tick
                            if time_since_last_spawn_in_wave >= current_inter_enemy_spawn_delay:
                                enemy_instance = enemies_to_spawn_this_group[spawn_idx_within_group]
                                enemies_list.append(enemy_instance)
                                spawn_idx_within_group += 1
                                time_since_last_spawn_in_wave = 0
                        else:
                            current_group_idx_in_wave += 1
                            spawn_idx_within_group = 0
                            inter_group_delay_timer = delay_after_this_group_seconds * 1000.0
                    elif len(enemies_list) == 0:
                        # Actions after all enemies in the current wave are cleared
                        resources_manager.add_resource("gold", current_wave_data.get("passive_gold", 0))
                        resources_manager.add_resource("wood", current_wave_data.get("passive_wood", 0))
                        resources_manager.add_resource("metal", current_wave_data.get("passive_metal", 0))
                        for factory_instance in bm.factories:
                            resource_type, amount = factory_instance.get_wave_payout()
                            resources_manager.add_resource(resource_type, amount)

                        current_wave_index += 1
                        if current_wave_index >= len(waves_data_list):
                            game_state_internal = "victory"
                            level_was_won = True
                        else:
                            current_game_mode = GameState.PRE_WAVE
                            start_wave_button.text = f"Start Wave {current_wave_index + 1}"

        bm.update_factories(clock_tick, resources_manager)
        update_enemies(clock_tick, enemies_list, base, resources_manager)
        update_towers(clock_tick, bm.towers, enemies_list, waypoints, projectiles)
        update_projectiles(clock_tick, projectiles, enemies_list)

        if resources_manager.get_resource("health") <= 0:
            game_state_internal = "game_over"

        screen.fill("black")
        screen.blit(map_img, (0, 0))
        draw_waypoints(screen, waypoints)
        ui.draw_resources(screen, resources_manager.resources, wave_index=current_wave_index, total_waves=len(waves_data_list))
        ui.draw_build_panel(screen, factory_buttons, tower_buttons)
        bm.draw_factories(screen)
        for tower_instance in bm.towers: tower_instance.draw(screen)
        for enemy_instance in enemies_list: enemy_instance.draw(screen)
        for projectile_instance in projectiles: projectile_instance.draw(screen)
        if selected_blueprint:
            selected_blueprint.draw_ghost(screen, resources_manager, road_seg)
        if current_game_mode == GameState.PRE_WAVE and current_wave_index < len(waves_data_list):
            start_wave_button.draw(screen)
        elif current_wave_index >= len(waves_data_list) and game_state_internal == "running":
             all_waves_cleared_text = pg.font.Font(None, 40).render("Level Cleared!", True, (0,255,0))
             screen.blit(all_waves_cleared_text, (con.SCREEN_WIDTH // 2 - all_waves_cleared_text.get_width() // 2, con.SCREEN_HEIGHT - 60))
        pg.display.update()

    if game_state_internal == "quit_to_menu":
        return GameState.MAIN_MENU, level_was_won

    if game_state_internal == "game_over" or game_state_internal == "victory":
        end_screen = EndingScreen(screen, game_won=level_was_won)
        end_screen_action = "running"
        while end_screen_action == "running":
            end_screen_action, _ = end_screen.handle_events()
            if end_screen_action == "quit":
                return GameState.QUIT, level_was_won
            end_screen.draw()
            clock.tick(con.FPS)

        if end_screen_action == "play_again":
            return GameState.PRE_WAVE, False # Return to pre-wave state for the same level
        elif end_screen_action == "main_menu":
            return GameState.LEVEL_SELECT, level_was_won # Return to level select

    return GameState.LEVEL_SELECT, level_was_won # Default return to level select

def load_levels_config(file_path, default_config):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Configuration file not found, create one with default settings
        print(f"'{file_path}' not found. Creating with default configuration.")
        save_levels_config(file_path, default_config)
        return default_config
    except json.JSONDecodeError:
        # Error reading configuration file, use default settings and save them
        print(f"Error decoding JSON from '{file_path}'. Using default configuration.")
        save_levels_config(file_path, default_config)
        return default_config

def save_levels_config(file_path, config_data):
    try:
        with open(file_path, 'w') as f:
            json.dump(config_data, f, indent=4)
    except IOError:
        # Error saving configuration
        print(f"Error: Could not save levels configuration to '{file_path}'.")


if __name__ == "__main__":
    screen, clock = initialize_game()
    os.makedirs(con.DATA_DIR, exist_ok=True) # Ensure data directory exists
    levels_config_filepath = os.path.join(con.DATA_DIR, LEVELS_CONFIG_FILENAME)
    LEVELS_CONFIG = load_levels_config(levels_config_filepath, con.LEVELS_CONFIG)
    application_state = GameState.MAIN_MENU
    selected_level_conf = None

    while application_state != GameState.QUIT:
        if application_state == GameState.MAIN_MENU:
            application_state = run_main_menu(screen, clock)
        elif application_state == GameState.LEVEL_SELECT:
            application_state, selected_level_conf = run_level_select(screen, clock, LEVELS_CONFIG)
        elif application_state == GameState.PRE_WAVE:
            if selected_level_conf:
                next_app_state_from_game, level_was_won = run_game_loop(screen, clock, selected_level_conf)
                application_state = next_app_state_from_game
                if level_was_won:
                    # Unlock the next level if the current one was won
                    current_level_index = -1
                    for i, lc in enumerate(LEVELS_CONFIG):
                        if lc["id"] == selected_level_conf["id"]:
                            current_level_index = i
                            break
                    if current_level_index != -1 and current_level_index + 1 < len(LEVELS_CONFIG):
                        if not LEVELS_CONFIG[current_level_index + 1]["unlocked"]:
                            LEVELS_CONFIG[current_level_index + 1]["unlocked"] = True
                            save_levels_config(levels_config_filepath, LEVELS_CONFIG)
                            print(f"Unlocked and saved: {LEVELS_CONFIG[current_level_index + 1]['name']}")
            else:
                # If no level is selected (e.g., backed out from level select), return to main menu
                application_state = GameState.MAIN_MENU
    pg.quit()

