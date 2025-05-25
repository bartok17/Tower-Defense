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

ENEMY_INTER_SPAWN_DELAY = 500  # ms

def main():
    screen, clock = initialize_game()
    map_img, button_img, waypoints, building_buttons, building_blueprints = load_assets()

    base = dummyEntity((0, 0))
    projectiles = []
    waves_data_list = wl.load_all_waves(
        os.path.join(con.DATA_DIR, "waves.json"),
        os.path.join(con.DATA_DIR, "enemyTemplates.json"), waypoints)

    game_state = "running"
    current_game_mode = "PRE_WAVE"
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

    while game_state == "running":
        clock_tick = clock.tick(con.FPS)
        mouse_pos = pg.mouse.get_pos()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_state = "quit"
            
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                clicked_on_ui_button_this_frame = False
                
                if current_game_mode == "PRE_WAVE" and \
                   current_wave_index < len(waves_data_list) and \
                   start_wave_button.is_clicked(mouse_pos):
                    current_game_mode = "WAVE_ACTIVE"
                    current_wave_data = waves_data_list[current_wave_index]
                    wave_preparation_timer = current_wave_data.get("P_time", 0) * 1000
                    enemy_spawn_index_in_wave = 0
                    time_since_last_spawn_in_wave = 0
                    start_wave_button.text = f"Wave {current_wave_index + 1} Active"
                    selected_blueprint = None
                    clicked_on_ui_button_this_frame = True
                
                if not clicked_on_ui_button_this_frame:
                    for idx, btn in enumerate(building_buttons):
                        if btn.is_clicked(mouse_pos):
                            selected_blueprint = building_blueprints[idx]
                            clicked_on_ui_button_this_frame = True
                            break 
                
                if selected_blueprint and not clicked_on_ui_button_this_frame:
                    if bm.try_build(mouse_pos, selected_blueprint, resources_manager, road_seg):
                        selected_blueprint = None
            
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if selected_blueprint:
                        selected_blueprint = None

        if game_state == "quit":
            break
        
        if current_game_mode == "PRE_WAVE":
            if current_wave_index < len(waves_data_list):
                 start_wave_button.text = f"Start Wave {current_wave_index + 1}"
            else:
                 start_wave_button.text = "All Waves Cleared!"

        elif current_game_mode == "WAVE_ACTIVE":
            wave_preparation_timer -= clock_tick
            if wave_preparation_timer <= 0 and current_wave_data:
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
                    resources_manager.add_resource("gold", current_wave_data.get("passive_gold", 0))
                    resources_manager.add_resource("wood", current_wave_data.get("passive_wood", 0))
                    resources_manager.add_resource("metal", current_wave_data.get("passive_metal", 0))
                    
                    for factory_instance in bm.factories:
                        resource_type, amount = factory_instance.get_wave_payout()
                        resources_manager.add_resource(resource_type, amount)

                    current_wave_index += 1
                    if current_wave_index >= len(waves_data_list):
                        game_state = "victory"
                    else:
                        current_game_mode = "PRE_WAVE"
                        start_wave_button.text = f"Start Wave {current_wave_index + 1}"
        
        bm.update_factories(clock_tick, resources_manager) 
        update_enemies(clock_tick, enemies_list, base, resources_manager)
        update_towers(clock_tick, bm.towers, enemies_list, waypoints, projectiles)
        update_projectiles(clock_tick, projectiles, enemies_list)

        if resources_manager.get_resource("health") <= 0:
            game_state = "game_over"

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
        
        if current_game_mode == "PRE_WAVE" and current_wave_index < len(waves_data_list):
            start_wave_button.draw(screen)
        elif current_wave_index >= len(waves_data_list) and game_state == "running":
             all_waves_cleared_text = pg.font.Font(None, 40).render("All waves cleared!", True, (0,255,0))
             screen.blit(all_waves_cleared_text, (con.SCREEN_WIDTH // 2 - all_waves_cleared_text.get_width() // 2, con.SCREEN_HEIGHT - 60))

        pg.display.update()

    if game_state == "game_over" or game_state == "victory":
        is_victory = (game_state == "victory")
        end_screen = EndingScreen(screen, game_won=is_victory)
        end_screen_action = "running"
        while end_screen_action == "running":
            end_screen_action, _ = end_screen.handle_events()
            end_screen.draw()
            clock.tick(con.FPS) 

        if end_screen_action == "play_again":
            main()
        elif end_screen_action == "quit" or end_screen_action == "main_menu":
             game_state = "quit"
           
    pg.quit()


def initialize_game():
    pg.init()
    screen = pg.display.set_mode((con.SCREEN_WIDTH, con.SCREEN_HEIGHT))
    pg.display.set_caption("Bardzo fajna gra")
    clock = pg.time.Clock()
    return screen, clock

def load_assets():
    os.makedirs(con.DATA_DIR, exist_ok=True)
    os.makedirs(con.ASSETS_DIR, exist_ok=True)

    map_img = pg.image.load(os.path.join(con.ASSETS_DIR, "map1.png")).convert_alpha()
    button_img = pg.image.load(os.path.join(con.ASSETS_DIR, "button_template.png")).convert_alpha()

    factory_metal_img = pg.image.load(os.path.join(con.ASSETS_DIR, "factory_metal_icon.png")).convert_alpha()
    factory_wood_img = pg.image.load(os.path.join(con.ASSETS_DIR, "factory_wood_icon.png")).convert_alpha()

    tower_basic_img = pg.image.load(os.path.join(con.ASSETS_DIR, "tower_basic_icon.png")).convert_alpha() 
    tower_cannon_img = pg.image.load(os.path.join(con.ASSETS_DIR, "tower_cannon_icon.png")).convert_alpha()
    tower_flame_img = pg.image.load(os.path.join(con.ASSETS_DIR, "tower_flame_icon.png")).convert_alpha()
    tower_rapid_img = pg.image.load(os.path.join(con.ASSETS_DIR, "tower_rapid_icon.png")).convert_alpha()
    tower_sniper_img = pg.image.load(os.path.join(con.ASSETS_DIR, "tower_sniper_icon.png")).convert_alpha()

    waypoints_path = os.path.join(con.DATA_DIR, "map1_waypoints.json")
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
    for name, road in waypoints.items():
        pg.draw.lines(screen, "red", False, road, 2)

def update_enemies(clock_tick, enemies_list, base, resources_manager):
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
    for tower in towers:
        if tower.current_reload > 0:
            tower.current_reload -= clock_tick / 1000.0
            tower.current_reload = max(0, tower.current_reload)
        tower.attack(enemies_list, 1, waypoints, projectiles)

def update_projectiles(clock_tick: int, projectiles: List[Projectile], enemies_list: list):
    for projectile in projectiles[:]:
        projectile.update(clock_tick, enemies_list)
        if not projectile.active:
            projectiles.remove(projectile)

if __name__ == "__main__":
    main()
