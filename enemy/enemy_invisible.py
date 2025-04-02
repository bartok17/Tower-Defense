from enemy.enemy import Enemy
import pygame as pg

class Enemy_invisible(Enemy):
    def __init__(self, waypoints):
        super().__init__(waypoints)
        self.is_invisible = True
    
    def take_damage(self, amount, can_see_invisible=False):
        if self.is_invisible and not can_see_invisible:
            return
        super().take_damage(amount)

    def reveal(self):
        self.is_invisible = False

    def draw(self, map_surface):
        if not self.is_invisible: super().draw(map_surface)
        else: 
            r = 0
            g = 211 * (self.health/self.max_health)
            b = 255 * (1 - self.health/self.max_health)
            pg.draw.circle(map_surface, (r, g, b), (int(self.pos.x), int(self.pos.y)), 10)