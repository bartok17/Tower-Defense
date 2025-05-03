import pygame as pg
import constants as con
from waypointsCreator import load_lists_from_json
import waveLoader as wl
from Button import Button
from Tower import Tower, create_tower
from dummyEntity import dummyEntity


def main():
    screen, clock = initialize_game()
    map_img, button_img, waypoints = load_assets()

    test_button = Button(con.SCREEN_WIDTH - 200, 120, button_img, True)
    base = dummyEntity((900, 900))

    projectiles, enemies_list, spawned_towers = [], [], []
    waves = wl.load_all_waves("waves.json", "enemyTemplates.json", waypoints)
    current_wave, wave_cooldown, enemy_spawn_index = 0, 0, 0

    run = True
    while run:
        clock_tick = clock.tick(con.FPS)
        screen.fill("black")
        screen.blit(map_img, (0, 0))

        draw_waypoints(screen, waypoints)
        if test_button.draw(screen):
            print("Test button pressed")

        run = handle_events(spawned_towers)
        current_wave, wave_cooldown, enemy_spawn_index = handle_waves(
            clock_tick, waves, current_wave, wave_cooldown, enemy_spawn_index, enemies_list
        )

        update_game_state(clock_tick, screen, base, enemies_list, spawned_towers, waypoints, projectiles)
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
    return map_img, button_img, waypoints


def handle_events(spawned_towers):
    for event in pg.event.get():
        if event.type == pg.QUIT:
            return False
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            keys = pg.key.get_pressed()
            if keys[pg.K_1]:
                handle_tower_creation(spawned_towers, preset="basic")
            elif keys[pg.K_2]:
                handle_tower_creation(spawned_towers, preset="sniper")
            elif keys[pg.K_3]:
                handle_tower_creation(spawned_towers, preset="cannon")
            elif keys[pg.K_4]:
                handle_tower_creation(spawned_towers, preset="flame")
            else:
                handle_tower_creation(spawned_towers, preset="basic")

        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_u:
                for tower in spawned_towers:
                    tower.upgrade(range_increase=10, damage_increase=5, reload_time_decrease=0.1)

    return True


def handle_tower_creation(spawned_towers,preset = "basic"):
    keys = pg.key.get_pressed()
    
    mouse_pos = pg.mouse.get_pos()
    new_tower = create_tower(mouse_pos, preset)
    spawned_towers.append(new_tower)
    print(f"Created a Tower at {mouse_pos}")


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
                enemy_spawn_index, wave_cooldown = 0, 0
    return current_wave, wave_cooldown, enemy_spawn_index


def update_game_state(clock_tick, screen, base, enemies_list, spawned_towers, waypoints, projectiles):
    update_enemies(clock_tick, enemies_list, base, screen)
    update_towers(clock_tick, spawned_towers, enemies_list, waypoints, screen, projectiles)
    update_projectiles(clock_tick, projectiles, screen)
    base.draw(screen)


def update_enemies(clock_tick, enemies_list, base, screen):
    for enemy in enemies_list[:]:
        enemy.draw(screen)
        if enemy.pos.distance_to(base.pos) > enemy.attack_range:
            enemy.update()
        else:
            handle_enemy_attack(clock_tick, enemy, base)
        if enemy.is_dead():
            enemies_list.remove(enemy)


def handle_enemy_attack(clock_tick, enemy, base):
    enemy.attack_cooldown -= clock_tick / 1000
    if enemy.attack_cooldown <= 0:
        base.take_damage(enemy.damage)
        enemy.attack_cooldown = enemy.attack_speed
        if base.is_dead():
            base.health = base.max_health  # Reset for now


def update_towers(clock_tick, towers, enemies_list, waypoints, screen, projectiles):
    for tower in towers:
        tower.attack(enemies_list, 1, waypoints, projectiles)
        tower.current_reload -= clock_tick / 1000
        tower.draw(screen)


def update_projectiles(clock_tick, projectiles, screen):
    for projectile in projectiles[:]:
        projectile.update(clock_tick)
        if not projectile.active:
            projectiles.remove(projectile)
        projectile.draw(screen)


if __name__ == "__main__":
    main()
