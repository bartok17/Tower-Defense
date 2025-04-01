import pygame as pg
import constants as con
import json
import WaypointsCreator as wp
pg.init()
clock = pg.time.Clock()

screen = pg.display.set_mode((con.SCREEN_WIDTH, con.SCREEN_HEIGHT))
pg.display.set_caption("Bardzo fajna gra")

mapName = "map1"


map_img = pg.image.load("map1.png").convert_alpha()
waypoints = wp.load_lists_from_json(mapName + "_waypoints.json")
print("waypoints loaded: ")
print(waypoints)

run = True

while run:

    clock.tick(con.FPS)

    screen.fill("black")

    screen.blit(map_img, (0, 0))

    for name, road in waypoints.items():
        pg.draw.lines(screen,"red", False, road, 2)




    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False

    pg.display.update()