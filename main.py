import pygame as pg
import constants as con
import json
import waypointsCreator as wp
from Button import Button

from enemy import Enemy, Enemy_invisible, Enemy_armored, Enemy_magic_resistant
from dummyEntity import dummyEntity
from random import randint
from random import choice


pg.init()
clock = pg.time.Clock()

screen = pg.display.set_mode((con.SCREEN_WIDTH, con.SCREEN_HEIGHT))
pg.display.set_caption("Bardzo fajna gra")

mapName = "map1"


map_img = pg.image.load("map1.png").convert_alpha()
button_img = pg.image.load("button_template.png").convert_alpha()

waypoints = wp.load_lists_from_json(mapName + "_waypoints.json")
print("waypoints loaded: ")
print(waypoints)

test_button = Button(con.SCREEN_WIDTH -200,120,button_img,True)
#Test entity for attacks
base = dummyEntity((900, 900))
#Enemies start values
enemies_list = []
enemies_spawn_timer = 0
enemies_next_spawntime = randint(1000, 5000)
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
    #Enemies main start
    enemies_spawn_timer += clock.get_time()
    if enemies_spawn_timer >= enemies_next_spawntime:
        enemy_path = choice(["road1", "road2"])
        enemy_class = choice([Enemy, Enemy_invisible, Enemy_armored, Enemy_magic_resistant])
        new_enemy = enemy_class(waypoints[enemy_path])
        enemies_list.append(new_enemy)
        enemies_spawn_timer = 0
        enemies_next_spawntime = randint(1000, 5000)
    for enemy in enemies_list:
        enemy.take_damage(1) #FOR TESTING ONLY
        enemy.draw(screen)
        distance_to_target = enemy.pos.distance_to(base.pos)
        if distance_to_target > enemy.attack_range: enemy.update()
        elif distance_to_target <= enemy.attack_range:
            enemy.attack_cooldown -= clock_tick / 1000
            if enemy.attack_cooldown <= 0:
                base.take_damage(enemy.damage)
                enemy.attack_cooldown = enemy.attack_speed
                if base.is_dead():
                    # print("Game Over")
                    # run = False
                    base.health = base.max_health
        if enemy.is_dead():
            enemies_list.remove(enemy)
    base.draw(screen)
    #Enemies main end
    pg.display.update()