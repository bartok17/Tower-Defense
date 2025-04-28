import pygame as pg
import constants as con
import json
import waypointsCreator as wp
import waveCreator as wc
import waveLoader as wl
from Button import Button
from enemy.enemy import Enemy
from dummyEntity import dummyEntity
from random import randint
from random import choice
from economy import ResourcesManager
from building.buildingBlueprint import BuildingBlueprint
import building.buildManager as bm 

pg.init()
clock = pg.time.Clock()

screen = pg.display.set_mode((con.SCREEN_WIDTH, con.SCREEN_HEIGHT))
pg.display.set_caption("Bardzo fajna gra")

map_name = "map1"

map_img = pg.image.load("map1.png").convert_alpha()
button_img = pg.image.load("button_template.png").convert_alpha()

waypoints = wp.load_lists_from_json(map_name + "_waypoints.json")
print("waypoints loaded: ")
print(waypoints)
road_rects = []

for name, points in waypoints.items():
    for i in range(len(points) - 1):
        start = points[i]
        end = points[i + 1]
        rect = pg.Rect(min(start[0], end[0]), min(start[1], end[1]),
                       abs(start[0] - end[0]) or 10,
                       abs(start[1] - end[1]) or 10) 
        road_rects.append(rect)

base = dummyEntity((900, 900))

factory_metal_img = pg.image.load("factory_metal_icon.png").convert_alpha()
factory_wood_img = pg.image.load("factory_wood_icon.png").convert_alpha()

#DO JSONA
building_blueprints = [
    BuildingBlueprint(
        "Metal Factory", factory_metal_img,
        {"gold": 50, "metal": 20},
        40, 40, bm.build_factory, resource="metal"
    ),
    BuildingBlueprint(
        "Wood Factory", factory_wood_img,
        {"gold": 40, "wood": 10},
        40, 40, bm.build_factory, resource="wood"
    ),
]


building_buttons = []
for i, blueprint in enumerate(building_blueprints):
    button = Button(con.SCREEN_WIDTH - 80, 50 + i * 80, blueprint.image)
    building_buttons.append(button)


waves = wl.load_all_waves("waves.json", "enemyTemplates.json", waypoints)
current_wave = 0
wave_timer = 0
wave_cooldown = 0
enemy_spawn_index = 0
enemies_list = []
spawned_enemies = []

mode = "Playing"
selected_blueprint = None
resource_manager = ResourcesManager()

run = True

while run:

    clock_tick = clock.tick(con.FPS)
    screen.fill("black")
    bm.update_factories(clock_tick, resource_manager)

    screen.blit(map_img, (0, 0))
    for name, road in waypoints.items():
        pg.draw.lines(screen, "red", False, road, 2)

    resource_manager.draw_resources(screen)


    for idx, btn in enumerate(building_buttons):
        if btn.draw(screen):
            selected_blueprint = building_blueprints[idx]
            mode = "Building"
            print(f"Selected: {selected_blueprint.name}")

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False

        if event.type == pg.MOUSEBUTTONDOWN:
            if mode == "Building" and selected_blueprint:
                mouse_pos = pg.mouse.get_pos()
                if bm.try_build(mouse_pos, selected_blueprint, resource_manager, road_rects):
                    selected_blueprint = None
                    mode = "Playing"

    if mode == "Building" and selected_blueprint:
        mouse_pos = pg.mouse.get_pos()

        can_build = bm.can_build_at(mouse_pos, selected_blueprint, resource_manager, road_rects)

        ghost_img = selected_blueprint.image.copy()

        if can_build: ghost_img.fill((0, 255, 0, 100), special_flags=pg.BLEND_RGBA_MULT)  # Zielony duch
        else: ghost_img.fill((255, 0, 0, 100), special_flags=pg.BLEND_RGBA_MULT)  # Czerwony duch
        screen.blit(ghost_img, (mouse_pos[0] - selected_blueprint.width // 2, mouse_pos[1] - selected_blueprint.height // 2))

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

    for enemy in enemies_list:
        enemy.draw(screen)
        distance_to_target = enemy.pos.distance_to(base.pos)
        if distance_to_target > enemy.attack_range:
            enemy.update()
        else:
            enemy.attack_cooldown -= clock_tick / 1000
            if enemy.attack_cooldown <= 0:
                base.take_damage(enemy.damage)
                enemy.attack_cooldown = enemy.attack_speed
                if base.is_dead():
                    base.health = base.max_health  # Reset na razie
        if enemy.is_dead():
            enemies_list.remove(enemy)
    bm.draw_factories(screen)
    base.draw(screen)
    pg.display.update()
