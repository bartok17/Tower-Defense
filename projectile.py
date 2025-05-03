import pygame as pg

class Projectile:
    def __init__(self, pos, target, damage, speed=5, explosive=False, explosion_radius=30):
        self.pos = pg.Vector2(pos)
        self.target = target  
        self.damage = damage
        self.speed = speed
        self.active = True
        self.explosive = explosive
        self.explosion_radius = explosion_radius

    def finish(self, enemies_list=None):
        self.pos = self.target.pos
        if self.explosive and enemies_list is not None:
            for enemy in enemies_list:
                if self.pos.distance_to(enemy.pos) <= self.explosion_radius:
                    enemy.take_damage(self.damage)
        else:
            self.target.take_damage(self.damage)
        self.active = False
    def update(self, enemies_list=None):
        if not self.active or self.target.is_dead():
            self.active = False
            return

        direction = (self.target.pos - self.pos)
        distance = direction.length()
        if distance < self.speed * (pg.time.get_ticks() / 1000):
            self.finish(enemies_list)
            
        else:
            direction = direction.normalize()
            self.pos += direction * self.speed * (pg.time.get_ticks() / 1000)


    def draw(self, surface):
        if self.active:
            pg.draw.circle(surface, (255, 255, 0), (int(self.pos.x), int(self.pos.y)), 5)
        elif self.explosive:
            # Draw explosion effect (optional)
            pg.draw.circle(surface, (255, 100, 0), (int(self.pos.x), int(self.pos.y)), self.explosion_radius, 2)