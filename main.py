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
import os

ENEMY_INTER_SPAWN_DELAY = 500  # ms between enemy spawns

class GameState:
    MAIN_MENU = 0
    LEVEL_SELECT = 1
    PRE_WAVE = 2
    WAVE_ACTIVE = 3
    GAME_OVER = 4
    VICTORY = 5
    QUIT = 6

def main():
    screen, clock = initialize_game()
    game_state = "running"
    current_game_mode = GameState.PRE_WAVE
    current_wave_index = 0

    while game_state == "running":
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_state = "quit"
        
        if current_game_mode == GameState.PRE_WAVE:
            next_state = run_main_menu(screen, clock)
            if next_state == GameState.QUIT:
                game_state = "quit"
            elif next_state == GameState.LEVEL_SELECT:
                current_game_mode = GameState.LEVEL_SELECT
                current_wave_index = 0 # reset wave index

        elif current_game_mode == GameState.LEVEL_SELECT:
            next_state, selected_level_config = run_level_select(screen, clock, con.LEVELS_CONFIG)
            if next_state == GameState.MAIN_MENU:
                current_game_mode = GameState.PRE_WAVE 
            elif next_state == GameState.PRE_WAVE:
                current_game_mode = GameState.PRE_WAVE
                current_wave_index = 0
                # run_game_loop would be called here in a more complete design
    
        screen.fill((30, 30, 30))
        pg.display.update()
        clock.tick(con.FPS)
    
    pg.quit()

def initialize_game():
    pg.init()
    screen = pg.display.set_mode((con.SCREEN_WIDTH, con.SCREEN_HEIGHT))
    pg.display.set_caption("Bardzo fajna gra")
    clock = pg.time.Clock()
    return screen, clock

def load_assets(level_config):
    # Loads all images and blueprints for a given level
    os.makedirs(con.DATA_DIR, exist_ok=True)
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

    building_blueprints = [
        BuildingBlueprint("Metal Factory", factory_metal_img, {"gold": 50, "metal": 20}, 40, 40, 
                          bm.build_factory, resource="metal", payout_per_wave=10),
        BuildingBlueprint("Wood Factory", factory_wood_img, {"gold": 40, "wood": 10}, 40, 40, 
                          bm.build_factory, resource="wood", payout_per_wave=15),
        BuildingBlueprint("Tower - basic", tower_basic_img, {"gold": 100, "wood": 50}, 40, 40, 
                          bm.build_tower, tower_type="basic"),
        BuildingBlueprint("Tower - cannon", tower_cannon_img, {"gold": 150, "wood": 70}, 40, 40, 
                          bm.build_tower, tower_type="cannon"),
        BuildingBlueprint("Tower - flame", tower_flame_img, {"gold": 120, "wood": 60}, 40, 40, 
                          bm.build_tower, tower_type="flame"),
        BuildingBlueprint("Tower - rapid", tower_rapid_img, {"gold": 80, "wood": 40}, 40, 40, 
                          bm.build_tower, tower_type="rapid"),
        BuildingBlueprint("Tower - sniper", tower_sniper_img, {"gold": 200, "wood": 100}, 40, 40, 
                          bm.build_tower, tower_type="sniper"),
    ]
    building_buttons = []
    button_start_y = 50
    button_spacing = 60
    for i, blueprint in enumerate(building_blueprints):
        button = Button(con.SCREEN_WIDTH - 80, button_start_y + i * button_spacing, blueprint.image, 
                        width=blueprint.width, height=blueprint.height)
        building_buttons.append(button)
    return map_img, button_img, waypoints, building_buttons, building_blueprints

def draw_waypoints(screen, waypoints):
    # Draws all waypoint paths for debugging
    for name, road in waypoints.items():
        pg.draw.lines(screen, "red", False, road, 2)

def update_enemies(clock_tick, enemies_list, base, resources_manager):
    # Updates all enemies, handles attacking base and death
    for enemy in enemies_list[:]:
        if enemy.pos.distance_to(base.pos) > enemy.attack_range:
            enemy.update()
            if enemy.has_finished():
                resources_manager.spend_resource("health", 10)
                enemies_list.remove(enemy)
        else:
            enemy.attack_cooldown -= clock_tick / 1000.0
            if enemy.attack_cooldown <= 0:
                resources_manager.spend_resource("health", enemy.damage)
                enemy.attack_cooldown = enemy.attack_speed
        
        if enemy.is_dead():
            enemies_list.remove(enemy)
            resources_manager.add_resource("gold", getattr(enemy, 'gold_reward', 50)) 
        
def update_towers(clock_tick, towers, enemies_list, waypoints, projectiles):
    # Updates all towers and triggers attacks
    for tower in towers:
        if tower.current_reload > 0:
            tower.current_reload -= clock_tick / 1000.0
            tower.current_reload = max(0, tower.current_reload)
        tower.attack(enemies_list, 1, waypoints, projectiles)

def update_projectiles(clock_tick: int, projectiles: List[Projectile], enemies_list: list):
    # Updates all projectiles and removes inactive ones
    for projectile in projectiles[:]:
        projectile.update(clock_tick, enemies_list)
        if not projectile.active:
            projectiles.remove(projectile)

def run_main_menu(screen, clock):
    # Main menu with Start and Quit buttons
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
    # Level selection screen, disables locked levels
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
    # Main gameplay loop for a selected level
    map_img, button_img, waypoints, building_buttons, building_blueprints = load_assets(selected_level_config)
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
    resources_manager = ResourcesManager()
    road_seg = bm.generate_road_segments(waypoints)
    current_wave_data = None
    wave_preparation_timer = 0 
    enemy_spawn_index_in_wave = 0
    time_since_last_spawn_in_wave = 0
    start_wave_button = Button(
        con.SCREEN_WIDTH // 2 - 100, con.SCREEN_HEIGHT - 70, None,
        text=f"Start Wave {current_wave_index + 1}", text_color=(255, 255, 255), font_size=28,
        width=200, height=40, color=(0, 150, 0)
    )
    bm.factories.clear()
    bm.towers.clear()

    while game_state_internal == "running":
        clock_tick = clock.tick(con.FPS)
        mouse_pos = pg.mouse.get_pos()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_state_internal = "quit_to_menu"
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                clicked_on_ui_button_this_frame = False
                # Start wave button
                if current_game_mode == GameState.PRE_WAVE and \
                   current_wave_index < len(waves_data_list) and \
                   start_wave_button.is_clicked(mouse_pos):
                    current_game_mode = GameState.WAVE_ACTIVE
                    current_wave_data = waves_data_list[current_wave_index]
                    wave_preparation_timer = current_wave_data.get("P_time", 0) * 1000
                    enemy_spawn_index_in_wave = 0
                    time_since_last_spawn_in_wave = 0
                    start_wave_button.text = f"Wave {current_wave_index + 1} Active"
                    selected_blueprint = None
                    clicked_on_ui_button_this_frame = True
                # Building buttons
                if not clicked_on_ui_button_this_frame:
                    for idx, btn in enumerate(building_buttons):
                        if btn.is_clicked(mouse_pos):
                            selected_blueprint = building_blueprints[idx]
                            clicked_on_ui_button_this_frame = True
                            break 
                # Place building
                if selected_blueprint and not clicked_on_ui_button_this_frame:
                    if bm.try_build(mouse_pos, selected_blueprint, resources_manager, road_seg):
                        selected_blueprint = None
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if selected_blueprint:
                        selected_blueprint = None
        
        if game_state_internal == "quit_to_menu":
            return GameState.MAIN_MENU

        if current_game_mode == GameState.PRE_WAVE:
            if current_wave_index < len(waves_data_list):
                 start_wave_button.text = f"Start Wave {current_wave_index + 1}"
            else:
                 start_wave_button.text = "All Waves Cleared!"

        elif current_game_mode == GameState.WAVE_ACTIVE:
            wave_preparation_timer -= clock_tick
            if wave_preparation_timer <= 0 and current_wave_data:
                # Spawn enemies for current wave
                if enemy_spawn_index_in_wave < len(current_wave_data.get("enemies", [])):
                    time_since_last_spawn_in_wave += clock_tick
                    if time_since_last_spawn_in_wave >= ENEMY_INTER_SPAWN_DELAY:
                        try:
                            if current_wave_data.get("enemies") and enemy_spawn_index_in_wave < len(current_wave_data["enemies"]):
                                enemy_instance = current_wave_data["enemies"][enemy_spawn_index_in_wave]
                                if enemy_instance is None:
                                    enemy_spawn_index_in_wave += 1 
                                    time_since_last_spawn_in_wave = 0
                                else:
                                    enemies_list.append(enemy_instance)
                                    enemy_spawn_index_in_wave += 1
                                    time_since_last_spawn_in_wave = 0
                        except Exception as e:
                            enemy_spawn_index_in_wave += 1 
                            time_since_last_spawn_in_wave = 0
                elif len(enemies_list) == 0:
                    # End of wave: payout and factories
                    resources_manager.add_resource("gold", current_wave_data.get("passive_gold", 0))
                    resources_manager.add_resource("wood", current_wave_data.get("passive_wood", 0))
                    resources_manager.add_resource("metal", current_wave_data.get("passive_metal", 0))
                    for factory_instance in bm.factories:
                        resource_type, amount = factory_instance.get_wave_payout()
                        resources_manager.add_resource(resource_type, amount)
                    current_wave_index += 1
                    if current_wave_index >= len(waves_data_list):
                        game_state_internal = "victory"
                    else:
                        current_game_mode = GameState.PRE_WAVE
                        start_wave_button.text = f"Start Wave {current_wave_index + 1}"
        
        bm.update_factories(clock_tick, resources_manager)
        update_enemies(clock_tick, enemies_list, base, resources_manager)
        update_towers(clock_tick, bm.towers, enemies_list, waypoints, projectiles)
        update_projectiles(clock_tick, projectiles, enemies_list)

        if resources_manager.get_resource("health") <= 0:
            game_state_internal = "game_over"

        # --- Drawing ---
        screen.fill("black")
        screen.blit(map_img, (0, 0))
        draw_waypoints(screen, waypoints)
        resources_manager.draw_resources(screen)
        bm.draw_factories(screen)
        for tower_instance in bm.towers: tower_instance.draw(screen)
        for enemy_instance in enemies_list: enemy_instance.draw(screen)
        for projectile_instance in projectiles: projectile_instance.draw(screen)
        for btn in building_buttons:
            btn.draw(screen)
        if selected_blueprint:
            selected_blueprint.draw_ghost(screen, resources_manager, road_seg)
        if current_game_mode == GameState.PRE_WAVE and current_wave_index < len(waves_data_list):
            start_wave_button.draw(screen)
        elif current_wave_index >= len(waves_data_list) and game_state_internal == "running":
             all_waves_cleared_text = pg.font.Font(None, 40).render("Level Cleared!", True, (0,255,0))
             screen.blit(all_waves_cleared_text, (con.SCREEN_WIDTH // 2 - all_waves_cleared_text.get_width() // 2, con.SCREEN_HEIGHT - 60))
        pg.display.update()

    # End screen (victory or game over)
    if game_state_internal == "game_over" or game_state_internal == "victory":
        is_victory = (game_state_internal == "victory")
        end_screen = EndingScreen(screen, game_won=is_victory)
        end_screen_action = "running"
        while end_screen_action == "running":
            end_screen_action, _ = end_screen.handle_events()
            if end_screen_action == "quit":
                return GameState.QUIT 
            end_screen.draw()
            clock.tick(con.FPS) 
        if end_screen_action == "play_again":
            return GameState.PRE_WAVE
        elif end_screen_action == "main_menu":
            return GameState.LEVEL_SELECT
    return GameState.LEVEL_SELECT

if __name__ == "__main__":
    screen, clock = initialize_game()
    LEVELS_CONFIG = con.LEVELS_CONFIG
    application_state = GameState.MAIN_MENU
    selected_level_conf = None

    while application_state != GameState.QUIT:
        if application_state == GameState.MAIN_MENU:
            application_state = run_main_menu(screen, clock)
        elif application_state == GameState.LEVEL_SELECT:
            application_state, selected_level_conf = run_level_select(screen, clock, LEVELS_CONFIG)
        elif application_state == GameState.PRE_WAVE:
            if selected_level_conf:
                game_result_state = run_game_loop(screen, clock, selected_level_conf)
                if game_result_state == GameState.PRE_WAVE:
                    application_state = GameState.PRE_WAVE
                elif game_result_state == GameState.QUIT:
                    application_state = GameState.QUIT
                else:
                    application_state = GameState.LEVEL_SELECT 
                    # Unlock next level if victory
                    # for i, lc in enumerate(LEVELS_CONFIG):
                    #     if lc["id"] == selected_level_conf["id"] and game_result_state == "victory":
                    #         if i + 1 < len(LEVELS_CONFIG):
                    #             LEVELS_CONFIG[i+1]["unlocked"] = True
                    #         break
            else:
                application_state = GameState.MAIN_MENU
    pg.quit()
