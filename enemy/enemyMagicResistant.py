from enemy.enemy import Enemy
import pygame as pg

class EnemyMagicResistant(Enemy):
    def __init__(self, waypoints):
        super().__init__(waypoints)
        self.magic_resistance = 0 
        self.max_health = 200
        self.health = self.max_health
    def draw(self, map_surface):
        r = 255 * (1-self.health/self.max_health)
        g = 0 
        b = 255 * (self.health/self.max_health)
        pg.draw.circle(map_surface, (r, g, b), (int(self.pos.x), int(self.pos.y)), 10)