import pygame as pg

class Projectile:
    def __init__(self, pos, target, damage, speed=5):
        self.pos = pg.Vector2(pos)
        self.target = target  
        self.damage = damage
        self.speed = speed
        self.active = True

    def update(self):
        if not self.active or self.target.is_dead():
            self.active = False
            return

        direction = (self.target.pos - self.pos)
        distance = direction.length()
        if distance < self.speed:
            self.pos = self.target.pos
            self.target.take_damage(self.damage)
            self.active = False
        else:
            direction = direction.normalize()
            self.pos += direction * self.speed

    def draw(self, surface):
        if self.active:
            pg.draw.circle(surface, (255, 255, 0), (int(self.pos.x), int(self.pos.y)), 5)