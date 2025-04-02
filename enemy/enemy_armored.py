from enemy.enemy import Enemy
import pygame as pg

class Enemy_armored(Enemy):
    def __init__(self, waypoints):
        super().__init__(waypoints)
        self.armor = 10
        self.max_health = 500
        self.health = self.max_health
        self.speed = 1.5

    def draw(self, map_surface):
        r = 255 * (1 - self.health/self.max_health)
        g = 127 * (self.health/self.max_health)
        b = 0
        pg.draw.circle(map_surface, (r, g, b), (int(self.pos.x), int(self.pos.y)), 10)