import pygame as pg

class dummyEntity:
    def __init__(self, pos, health=1000):
        self.pos = pg.Vector2(pos)
        self.health = health
        self.max_health = health
        self.healthbar_length = 40
        self.healthbar_height = 5

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def is_dead(self):
        return self.health <= 0

    def draw(self, map_surface):
        pg.draw.circle(map_surface, (255, 255, 0), (int(self.pos.x), int(self.pos.y)), 20)
        pg.draw.rect(map_surface, (255, 0, 0), (self.pos.x - 20, self.pos.y - 30, self.healthbar_length, 5))
        pg.draw.rect(map_surface, (0, 255, 0), (self.pos.x - 20, self.pos.y - 30, self.healthbar_length * (self.health/self.max_health), 5))
