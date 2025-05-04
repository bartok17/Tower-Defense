import pygame as pg
import os
import constants as con

class Factory:
    def __init__(self, pos, resource_type, production_rate, interval):
        self.pos = pos
        self.resource_type = resource_type
        self.production_rate = production_rate
        self.interval = interval
        self.timer = 0

    def update(self, time, manager):
        self.timer += time
        if self.timer >= self.interval:
            manager.add(self.resource_type, self.production_rate)
            self.timer = 0

    def draw(self, screen):
        if self.resource_type == "wood":
            factory_image = pg.image.load(os.path.join(con.ASSETS_DIR, "factory_wood_icon.png")).convert_alpha()
        elif self.resource_type == "metal":
            factory_image = pg.image.load(os.path.join(con.ASSETS_DIR, "factory_metal_icon.png")).convert_alpha()
        screen.blit(factory_image, (self.pos[0], self.pos[1]))
