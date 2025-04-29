# Tower.py
from Button import Button
from enemy.enemy import Enemy
from dummyEntity import dummyEntity
from random import randint
from random import choice
from projectile import Projectile
import constants as con
import pygame as pg


class TowerStats:
    def __init__(self, range: int, damage: int, reload_time: float):
        self.range = range
        self.damage = damage
        self.reload_time = reload_time

    def upgrade(self, range_increase=0, damage_increase=0, reload_time_decrease=0):
        self.range += range_increase
        self.damage += damage_increase
        self.reload_time = max(0.1, self.reload_time - reload_time_decrease)  # Prevent negative reload


class Tower:
    def __init__(self, pos: tuple[int, int], range, damage, reload_time):
        self.pos = pg.math.Vector2(pos)
        self.stats = TowerStats(range, damage, reload_time)
        self.current_reload = 0

    def is_in_range(self, enemy):
        distance = self.pos.distance_to(pg.math.Vector2(enemy.pos))
        return distance <= self.stats.range

    def attack(self, enemies: list[Enemy], max_targets: int, waypoints: list[tuple[int, int]], projectiles: list):
        if not waypoints or self.current_reload > 0:
            return

        enemies_in_range = [
            (enemy, enemy.distance_to_end())
            for enemy in enemies if self.is_in_range(enemy)
        ]
        enemies_in_range.sort(key=lambda item: item[1])

        for enemy, _ in enemies_in_range[:max_targets]:
            projectile = Projectile(self.pos, enemy, self.stats.damage)
            projectiles.append(projectile)

        self.current_reload = self.stats.reload_time

    def upgrade(self, range_increase=0, damage_increase=0, reload_time_decrease=0):
        self.stats.upgrade(range_increase, damage_increase, reload_time_decrease)

    def draw(self, surface):
        pg.draw.circle(surface, (0, 255, 0), (int(self.pos.x), int(self.pos.y)), self.stats.range, 1)
        pg.draw.circle(surface, (255, 0, 0), (int(self.pos.x), int(self.pos.y)), 5)


TOWER_PRESETS = {
    "basic":    {"range": 100, "damage": 10, "reload_time": 1.0},
    "sniper":   {"range": 200, "damage": 30, "reload_time": 2.5},
    "rapid":    {"range": 80,  "damage": 5,  "reload_time": 0.3},
    "cannon":   {"range": 120, "damage": 20, "reload_time": 1.5},
}

def create_tower(pos, preset_name):
    preset = TOWER_PRESETS[preset_name]
    return Tower(pos, preset["range"], preset["damage"], preset["reload_time"])