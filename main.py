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
import os

# Main game loop
def main():
    screen, clock = initialize_game()
    map_img, button_img, waypoints, building_buttons, building_blueprints = load_assets()
    mode = con.STATE_PLAYING
    base = dummyEntity((0, 0))
    projectiles = []
    waves = wl.load_all_waves(os.path.join(con.DATA_DIR, "waves.json"),os.path.join(con.DATA_DIR, "enemyTemplates.json") , waypoints)
    current_wave = 0
    wave_cooldown = 0
    enemy_spawn_index = 0
    enemies_list = []
    selected_blueprint = None
    resources_manager = ResourcesManager()
    road_seg = bm.generate_road_segments(waypoints)

    run = True

    while run:
        clock_tick = clock.tick(con.FPS)
        screen.fill("black")
        screen.blit(map_img, (0, 0))

        draw_waypoints(screen, waypoints)
        resources_manager.draw_resources(screen)

        run, selected_blueprint, mode = handle_events(
            bm.towers,
            selected_blueprint,
            resources_manager,
            road_seg,
            mode
        )
        if mode in (con.STATE_PLAYING, con.STATE_BUILDING):
            for idx, btn in enumerate(building_buttons):
                if btn.draw(screen):
                    selected_blueprint = building_blueprints[idx]
                    mode = con.STATE_BUILDING
        if mode == con.STATE_BUILDING and selected_blueprint:
            selected_blueprint.draw_ghost(screen, resources_manager, road_seg)
        
        current_wave, wave_cooldown, enemy_spawn_index = handle_waves(
            clock_tick, waves, current_wave, wave_cooldown, enemy_spawn_index, enemies_list
        )
        update_game(
            clock_tick,
            resources_manager,
            screen,
            enemies_list,
            base,
            waypoints,
            projectiles,
            mode
        )
        if resources_manager.get_resource("health") <= 0:
            mode = con.STATE_GAME_OVER
        texts(mode, screen)
        pg.display.update()


def initialize_game():
    pg.init()
    screen = pg.display.set_mode((con.SCREEN_WIDTH, con.SCREEN_HEIGHT))
    pg.display.set_caption("Bardzo fajna gra")
    clock = pg.time.Clock()
    return screen, clock

import os

def load_assets():
    os.makedirs(con.DATA_DIR, exist_ok=True)
    os.makedirs(con.ASSETS_DIR, exist_ok=True)

    # ASSETS
    map_img = pg.image.load(os.path.join(con.ASSETS_DIR, "map1.png")).convert_alpha()
    button_img = pg.image.load(os.path.join(con.ASSETS_DIR, "button_template.png")).convert_alpha()

    factory_metal_img = pg.image.load(os.path.join(con.ASSETS_DIR, "factory_metal_icon.png")).convert_alpha()
    factory_wood_img = pg.image.load(os.path.join(con.ASSETS_DIR, "factory_wood_icon.png")).convert_alpha()

    tower_basic_img = pg.image.load(os.path.join(con.ASSETS_DIR, "tower_basic_icon.png")).convert_alpha() 
    tower_cannon_img = pg.image.load(os.path.join(con.ASSETS_DIR, "tower_cannon_icon.png")).convert_alpha()
    tower_flame_img = pg.image.load(os.path.join(con.ASSETS_DIR, "tower_flame_icon.png")).convert_alpha()
    tower_rapid_img = pg.image.load(os.path.join(con.ASSETS_DIR, "tower_rapid_icon.png")).convert_alpha()
    tower_sniper_img = pg.image.load(os.path.join(con.ASSETS_DIR, "tower_sniper_icon.png")).convert_alpha()

    # DATA
    waypoints_path = os.path.join(con.DATA_DIR, "map1_waypoints.json")
    waypoints = load_lists_from_json(waypoints_path)
    print("Waypoints loaded:", waypoints)

    # BLUEPRINTS
    building_blueprints = [
        BuildingBlueprint("Metal Factory", factory_metal_img, {"gold": 50, "metal": 20}, 40, 40, bm.build_factory, resource="metal"),
        BuildingBlueprint("Wood Factory", factory_wood_img, {"gold": 40, "wood": 10}, 40, 40, bm.build_factory, resource="wood"),
        BuildingBlueprint("Tower - basic", tower_basic_img, {"gold": 100, "wood": 50}, 40, 40, bm.build_tower),
        BuildingBlueprint("Tower - cannon", tower_cannon_img, {"gold": 150, "wood": 70}, 40, 40, bm.build_tower),
        BuildingBlueprint("Tower - flame", tower_flame_img, {"gold": 120, "wood": 60}, 40, 40, bm.build_tower),
        BuildingBlueprint("Tower - rapid", tower_rapid_img, {"gold": 80, "wood": 40}, 40, 40, bm.build_tower),
        BuildingBlueprint("Tower - sniper", tower_sniper_img, {"gold": 200, "wood": 100}, 40, 40, bm.build_tower),
    ]

    # BUTTONS
    building_buttons = [
        Button(con.SCREEN_WIDTH - 80, 50 + i * 80, blueprint.image)
        for i, blueprint in enumerate(building_blueprints)
    ]

    return map_img, button_img, waypoints, building_buttons, building_blueprints

def texts(mode, screen):
    match mode:
        case con.STATE_MENU:
            font = pg.font.SysFont(None, 80)
            text = font.render("Press ENTER to Start", True, (255, 255, 255))
            text_rect = text.get_rect(center=(con.SCREEN_WIDTH // 2, con.SCREEN_HEIGHT // 2))
            screen.blit(text, text_rect)
        case con.STATE_PAUSED:
            font = pg.font.SysFont(None, 100)
            text = font.render("PAUSED", True, (255, 255, 0))
            text_rect = text.get_rect(center=(con.SCREEN_WIDTH // 2, con.SCREEN_HEIGHT // 2))
            screen.blit(text, text_rect)
        case con.STATE_GAME_OVER:
            font = pg.font.SysFont(None, 100)
            text = font.render("GAME OVER", True, (255, 0, 0))
            text_rect = text.get_rect(center=(con.SCREEN_WIDTH // 2, con.SCREEN_HEIGHT // 2))
            screen.blit(text, text_rect)
def handle_events(spawned_towers, selected_blueprint, resources_manager, road_seg, mode):
    for event in pg.event.get():
        if event.type == pg.QUIT:
            return False, selected_blueprint, mode

        if event.type == pg.KEYDOWN:
            match mode: 
                case con.STATE_MENU:
                    if event.key == pg.K_RETURN:
                        print("Starting game!")
                        mode = con.STATE_PLAYING
                case con.STATE_PAUSED:
                    if event.key == pg.K_p:
                        print("Unpaused!")
                        mode = con.STATE_PLAYING
                case con.STATE_PLAYING | con.STATE_BUILDING:
                    if event.key == pg.K_p:
                        print("Paused!")
                        mode = con.STATE_PAUSED

        if mode in (con.STATE_PLAYING, con.STATE_BUILDING):
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                keys = pg.key.get_pressed()
                mouse_pos = pg.mouse.get_pos()
                if keys[pg.K_LCTRL] or keys[pg.K_RCTRL]:
                    new_tower = create_tower(mouse_pos, "basic")
                    spawned_towers.append(new_tower)
                    print(f"Created a Tower at {mouse_pos}")
                elif selected_blueprint:
                    if bm.try_build(mouse_pos, selected_blueprint, resources_manager, road_seg):
                        print(f"Built {selected_blueprint.name} at {mouse_pos}")
                        selected_blueprint = None

    return True, selected_blueprint, mode


def draw_waypoints(screen, waypoints):
    for name, road in waypoints.items():
        pg.draw.lines(screen, "red", False, road, 2)

def handle_waves(clock_tick, waves, current_wave, wave_cooldown, enemy_spawn_index, enemies_list):
    if current_wave < len(waves):
        wave_data = waves[current_wave]
        wave_cooldown += clock_tick
        if wave_cooldown >= wave_data["P_time"] * 1000:
            if enemy_spawn_index < len(wave_data["enemies"]):
                enemies_list.append(wave_data["enemies"][enemy_spawn_index])
                enemy_spawn_index += 1
            else:
                current_wave += 1
                enemy_spawn_index = 0
                wave_cooldown = 0
    return current_wave, wave_cooldown, enemy_spawn_index

def update_enemies(clock_tick, enemies_list, base, screen, resources_manager):
    for enemy in enemies_list[:]:
        enemy.draw(screen)
        if enemy.pos.distance_to(base.pos) > enemy.attack_range:
            enemy.update()
            if enemy.has_finished(): 
                print("Enemy reached the base!")
                resources_manager.spend({"health": 10})
                enemies_list.remove(enemy)
        else:
            enemy.attack_cooldown -= clock_tick / 1000
            if enemy.attack_cooldown <= 0:
                base.take_damage(enemy.damage)
                enemy.attack_cooldown = enemy.attack_speed
                base.health = base.max_health  # Reset for now
        if enemy.is_dead():
            enemies_list.remove(enemy)
            resources_manager.add("gold", 50)
        
def update_towers(clock_tick, towers, enemies_list, waypoints, screen, projectiles):
    for tower in towers:
        tower.attack(enemies_list, 1, waypoints, projectiles)
        tower.current_reload -= clock_tick / 1000
        tower.draw(screen)

def update_projectiles(clock_tick: int, projectiles: List[Projectile], screen: pg.Surface, enemies_list: list):
    for projectile in projectiles[:]:
        projectile.update(clock_tick,enemies_list)
        if not projectile.active:
            projectiles.remove(projectile)
        projectile.draw(screen)
def update_game(clock_tick, resources_manager, screen, enemies_list, base, waypoints, projectiles, mode):
    if mode in (con.STATE_PLAYING, con.STATE_BUILDING):
        bm.update_factories(clock_tick, resources_manager)
        bm.draw_factories(screen)
        update_enemies(clock_tick, enemies_list, base, screen, resources_manager)
        update_towers(clock_tick, bm.towers, enemies_list, waypoints, screen, projectiles)
        update_projectiles(clock_tick, projectiles, screen, enemies_list)

if __name__ == "__main__":
    main()
