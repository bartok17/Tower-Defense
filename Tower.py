# Tower.py
from Button import Button
from enemy.enemy import Enemy
from dummyEntity import dummyEntity
from random import randint, choice
from projectile import Projectile
import constants as con
import pygame as pg


class TowerStats:
    def __init__(self, range: int, damage: int, reload_time: float,damage_Type = "phisical" , explosive: bool = False, explosion_radius: int = 30):
        self.explosive = explosive
        self.explosion_radius = explosion_radius
        self.range = range
        self.damage = damage
        self.reload_time = reload_time
        self.damage_type = damage_Type 


    def upgrade(self, range_increase=0, damage_increase=0, reload_time_decrease=0):
        self.range += range_increase
        self.damage += damage_increase
        self.reload_time = max(0.01, self.reload_time - reload_time_decrease)  # Prevent negative reload


class Tower:
    def __init__(self, pos: tuple[int, int], stats: TowerStats):
        self.pos = pg.math.Vector2(pos)
        self.stats = stats
        self.current_reload = 0

    def is_in_range(self, enemy: Enemy) -> bool:
        return self.pos.distance_to(pg.math.Vector2(enemy.pos)) <= self.stats.range

    def attack(self, enemies: list[Enemy], max_targets: int, waypoints: list[tuple[int, int]], projectiles: list[Projectile]):
        if not waypoints or self.current_reload > 0:
            return

        enemies_in_range = [
            (enemy, enemy.distance_to_end())
            for enemy in enemies if self.is_in_range(enemy)
        ]
        enemies_in_range.sort(key=lambda item: item[1])

        attacked = False
        for enemy, _ in enemies_in_range[:max_targets]:
            projectile = Projectile(
                self.pos, enemy, self.stats.damage, 0.5, self.stats.explosive, self.stats.explosion_radius
            )
            projectiles.append(projectile)
            attacked = True

        if attacked:
            self.current_reload = self.stats.reload_time

    def upgrade(self, range_increase=0, damage_increase=0, reload_time_decrease=0):
        self.stats.upgrade(range_increase, damage_increase, reload_time_decrease)

    def draw(self, surface):
        pg.draw.circle(surface, (0, 255, 0), (int(self.pos.x), int(self.pos.y)), self.stats.range, 1)
        pg.draw.circle(surface, (255, 0, 0), (int(self.pos.x), int(self.pos.y)), 5)


TOWER_PRESETS = {
    "basic":    TowerStats(range=100, damage=10, reload_time=1.0, explosive=False, damage_Type = "phisical"),
    "sniper":   TowerStats(range=200, damage=30, reload_time=2.5, explosive=False, damage_Type = "phisical"),
    "rapid":    TowerStats(range=80,  damage=5,  reload_time=0.3, explosive=False, damage_Type = "phisical"),
    "cannon":   TowerStats(range=120, damage=20, reload_time=1.5, explosive=True, explosion_radius=60, damage_Type = "phisical"),
    "flame":    TowerStats(range=100, damage=15, reload_time=0.1, explosive=False, damage_Type = "magic"),
}


def create_tower(pos: tuple[int, int], preset_name: str) -> Tower:
    stats = TOWER_PRESETS.get(preset_name, TOWER_PRESETS["basic"])
    stats = TowerStats(
        range=stats.range,
        damage=stats.damage,
        reload_time=stats.reload_time,
        damage_Type=stats.damage_type,
        explosive=stats.explosive,
        explosion_radius=stats.explosion_radius
    )
    return Tower(pos, stats)
