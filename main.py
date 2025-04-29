import pygame as pg
import constants as con
from waypointsCreator import load_lists_from_json
import waveLoader as wl
from Button import Button
from Tower import Tower, TowerStats,create_tower
from dummyEntity import dummyEntity
from economy import ResourcesManager
from building.buildingBlueprint import BuildingBlueprint
import building.buildManager as bm 



# Main game loop
def main():
    screen, clock = initialize_game()
    map_img, button_img, waypoints, building_buttons, building_blueprints = load_assets()

    #test_button = Button(con.SCREEN_WIDTH - 200, 120, button_img, True)
    base = dummyEntity((900, 900))

    projectiles = []

    waves = wl.load_all_waves("waves.json", "enemyTemplates.json", waypoints)
    current_wave = 0
    wave_cooldown = 0
    enemy_spawn_index = 0
    enemies_list = []
    mode = "Playing"
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

        # if test_button.draw(screen):
        #     print("Test button pressed")
        bm.update_factories(clock_tick, resources_manager)
        bm.draw_factories(screen)

        for idx, btn in enumerate(building_buttons):
            if btn.draw(screen):
                selected_blueprint = building_blueprints[idx]
                mode = "Building"
        run, selected_blueprint = handle_events(bm.towers, selected_blueprint, resources_manager, road_seg)
        if mode == "Building" and selected_blueprint:
            selected_blueprint.draw_ghost(screen, resources_manager, road_seg)
        current_wave, wave_cooldown, enemy_spawn_index = handle_waves(
            clock_tick, waves, current_wave, wave_cooldown, enemy_spawn_index, enemies_list
        )

        update_enemies(clock_tick, enemies_list, base, screen, resources_manager)
        update_towers(clock_tick, bm.towers, enemies_list, waypoints, screen, projectiles)
        update_projectiles(clock_tick, projectiles,screen=screen,enemies_list=enemies_list)
        base.draw(screen)
        pg.display.update()

def initialize_game():
    pg.init()
    screen = pg.display.set_mode((con.SCREEN_WIDTH, con.SCREEN_HEIGHT))
    pg.display.set_caption("Bardzo fajna gra")
    clock = pg.time.Clock()
    return screen, clock


def load_assets():
    map_img = pg.image.load("map1.png").convert_alpha()
    button_img = pg.image.load("button_template.png").convert_alpha()
    waypoints = load_lists_from_json("map1_waypoints.json")
    print("Waypoints loaded:", waypoints)
    factory_metal_img = pg.image.load("factory_metal_icon.png").convert_alpha()
    factory_wood_img = pg.image.load("factory_wood_icon.png").convert_alpha()
    tower_img = pg.image.load("button_template.png").convert_alpha()  # Tymczasowy obrazek dla wieży
    building_blueprints = [
        BuildingBlueprint("Metal Factory", factory_metal_img, {"gold": 50, "metal": 20}, 40, 40, bm.build_factory, resource="metal"),
        BuildingBlueprint("Wood Factory", factory_wood_img, {"gold": 40, "wood": 10}, 40, 40, bm.build_factory, resource="wood"),
        BuildingBlueprint("Basic Tower", tower_img, {"gold": 100, "wood": 50}, 40, 40, bm.build_tower, resource=None),
    ]
    building_buttons = []
    for i, blueprint in enumerate(building_blueprints):
        button = Button(con.SCREEN_WIDTH - 80, 50 + i * 80, blueprint.image)
        building_buttons.append(button)
    return map_img, button_img, waypoints, building_buttons, building_blueprints
def handle_events(spawned_towers, selected_blueprint, resources_manager, road_seg):
    for event in pg.event.get():
        if event.type == pg.QUIT:
            return False, selected_blueprint

        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            keys = pg.key.get_pressed()
            mouse_pos = pg.mouse.get_pos()
            if keys[pg.K_LCTRL] or keys[pg.K_RCTRL]:
                new_tower = create_tower(mouse_pos, "basic")
                spawned_towers.append(new_tower)
                print(f"Created a Tower at {mouse_pos}")
            elif selected_blueprint:
                import building.buildManager as bm
                if bm.try_build(mouse_pos, selected_blueprint, resources_manager, road_seg):
                    print(f"Built {selected_blueprint.name} at {mouse_pos}")
                    selected_blueprint = None

    return True, selected_blueprint


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
        distance_to_target = enemy.pos.distance_to(base.pos)
        if distance_to_target > enemy.attack_range:
            enemy.update()
        else:
            enemy.attack_cooldown -= clock_tick / 1000
            if enemy.attack_cooldown <= 0:
                base.take_damage(enemy.damage)
                enemy.attack_cooldown = enemy.attack_speed
                base.health = base.max_health  # Reset for now
        if enemy.is_dead():
            enemies_list.remove(enemy)
            resources_manager.add("gold", 50)
def update_towers(clock_tick, towers: list[Tower], enemies_list, waypoints, screen, projectiles):
    for tower in towers:
        tower.attack(enemies_list, 1, waypoints, projectiles)
        tower.current_reload -= clock_tick / 1000
        tower.draw(screen)
def update_projectiles(clock_tick, projectiles,screen, enemies_list):
    for projectile in projectiles[:]:
        projectile.update(enemies_list)
        if not projectile.active:
            projectiles.remove(projectile)
        projectile.draw(screen)

if __name__ == "__main__":
    main()