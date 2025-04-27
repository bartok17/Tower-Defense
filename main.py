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

test_button = Button(con.SCREEN_WIDTH -200,120,button_img,True)
#Test entity for attacks
base = dummyEntity((900, 900))
#Enemies start values
waves = wl.load_all_waves("waves.json", "enemyTemplates.json", waypoints)
current_wave = 0
wave_timer = 0
wave_cooldown = 0
enemy_spawn_index = 0
enemies_list = []
spawned_enemies = []

#Enemies start values end
run = True

while run:

    clock_tick = clock.tick(con.FPS)

    screen.fill("black")

    screen.blit(map_img, (0, 0))

    for name, road in waypoints.items():
        pg.draw.lines(screen,"red", False, road, 2)

    if test_button.draw(screen):
        print("test button pressed")


    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
    #Kontrola fal
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
        if distance_to_target > enemy.attack_range: enemy.update()
        else:
            enemy.attack_cooldown -= clock_tick / 1000
            if enemy.attack_cooldown <= 0:
                base.take_damage(enemy.damage)
                enemy.attack_cooldown = enemy.attack_speed
                if base.is_dead():
                    base.health = base.max_health  # Reset na razie
        if enemy.is_dead(): enemies_list.remove(enemy)
    #Koniec kontroli fal
    base.draw(screen)
    
    pg.display.update()