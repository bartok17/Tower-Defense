import pygame as pg
import random

class Projectile:
    def __init__(self, pos, target, damage, damage_type, speed=5, explosive=False, explosion_radius=30,
                 shape="circle", color1=(255, 255, 0), color2=None, size=5):
        self.pos = pg.Vector2(pos)
        self.target = target  
        self.damage = damage
        self.speed = speed
        self.active = True
        self.explosive = explosive
        self.explosion_radius = explosion_radius
        self.damage_type = damage_type
        self.shape = shape
        self.size = size

        if color2:
            # Pick a random color between color1 and color2
            r = random.randint(min(color1[0], color2[0]), max(color1[0], color2[0]))
            g = random.randint(min(color1[1], color2[1]), max(color1[1], color2[1]))
            b = random.randint(min(color1[2], color2[2]), max(color1[2], color2[2]))
            self.color = (r, g, b)
        else:
            self.color = color1

    def on_removed(self):
        # Remove incoming damage from the target if possible
        if self.target and hasattr(self.target, 'remove_incoming_damage'):
            self.target.remove_incoming_damage(self.damage)

    def finish(self, enemies_list=None):
        # Deal damage to target or area if explosive
        self.pos = self.target.pos
        if self.explosive and enemies_list is not None:
            for enemy in enemies_list:
                if self.pos.distance_to(enemy.pos) <= self.explosion_radius:
                    distance = self.pos.distance_to(enemy.pos)
                    damage_factor = max(0.5, 1 - (distance / self.explosion_radius) * 0.5)
                    enemy.take_damage(self.damage * damage_factor, damage_type=self.damage_type)
        else:
            self.target.take_damage(self.damage, damage_type=self.damage_type)
        self.active = False

    def update(self, clock_Tick, enemies_list=None):
        # Move projectile and check for collision with target
        if not self.active or self.target.is_dead():
            self.active = False
            return

        direction = (self.target.pos - self.pos)
        distance = direction.length()
        if distance < self.speed * clock_Tick:
            self.finish(enemies_list)
        else:
            direction = direction.normalize()
            self.pos += direction * self.speed * clock_Tick

    def draw(self, surface):
        # Draw projectile or explosion effect
        if self.active:
            if self.shape == "circle":
                pg.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.size)
            elif self.shape == "square":
                rect = pg.Rect(self.pos.x - self.size // 2, self.pos.y - self.size // 2, self.size, self.size)
                pg.draw.rect(surface, self.color, rect)
            elif self.shape == "triangle":
                half_size = self.size // 2
                points = [
                    (self.pos.x, self.pos.y - half_size),
                    (self.pos.x - half_size, self.pos.y + half_size),
                    (self.pos.x + half_size, self.pos.y + half_size)
                ]
                pg.draw.polygon(surface, self.color, points)
        elif self.explosive:
            pg.draw.circle(surface, (255, 100, 0), (int(self.pos.x), int(self.pos.y)), self.explosion_radius, 2)
