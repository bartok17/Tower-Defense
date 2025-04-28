# Tower.py
from Button import Button
from enemy.enemy import Enemy
from dummyEntity import dummyEntity
from random import randint
from random import choice
from projectile import Projectile
import constants as con
import pygame as pg


class Tower:
    def __init__(self, pos: tuple[int, int], range, damage, reload_time):
        self.pos = pg.math.Vector2(pos) 
        self.range = range
        self.damage = damage
        self.reload_time = reload_time
        self.current_reload = 0

    def is_in_range(self, enemy):
        distance = self.pos.distance_to(pg.math.Vector2(enemy.pos))  # Use Vector2 distance_to
        
        return distance <= self.range

    def attack(self, enemies: list[Enemy], max_targets: int, waypoints: list[tuple[int, int]], projectiles: list):
        if not waypoints or self.current_reload > 0:
                return

        enemies_in_range = [
            (enemy, enemy.distance_to_end())
            for enemy in enemies if self.is_in_range(enemy)
        ]
        enemies_in_range.sort(key=lambda item: item[1])

        for enemy, _ in enemies_in_range[:max_targets]:
            # Instead of direct damage, spawn a projectile
            projectile = Projectile(self.pos, enemy, self.damage)
            projectiles.append(projectile)

        self.current_reload = self.reload_time
    def draw(self, surface):
        pg.draw.circle(surface, (0, 255, 0), (int(self.pos.x), int(self.pos.y)), self.range, 1)
        pg.draw.circle(surface, (255, 0, 0), (int(self.pos.x), int(self.pos.y)), 5)