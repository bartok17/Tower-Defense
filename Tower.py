# Tower.py
from Button import Button
from enemy.enemy import Enemy
from dummyEntity import dummyEntity
from random import randint, choice
from projectile import Projectile
import constants as con
import pygame as pg
import enemy.abstractEnemyAbilities as aea

class TowerStats:
    def __init__(self, range: int, damage: int, reload_time: float, damage_Type="phisical", explosive: bool = False, explosion_radius: int = 30):
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
        if self.current_reload > 0:
            return

        potential_targets = []
        for enemy_candidate in enemies:
            if enemy_candidate.has_ability(aea.invisibleAbility):
                if not getattr(self, "can_see_invisible", False):
                    continue
            if not enemy_candidate.is_dead() and self.is_in_range(enemy_candidate):
                current_health = getattr(enemy_candidate, 'health', 0)
                inc_damage = getattr(enemy_candidate, 'incoming_damage', 0)
                effective_health = current_health - inc_damage
                if effective_health > 0:
                    # Prefer enemies closer to the end
                    distance = float('inf')
                    if hasattr(enemy_candidate, 'distance_to_end'):
                        distance = enemy_candidate.distance_to_end()
                    potential_targets.append({'enemy': enemy_candidate, 'distance': distance})

        if not potential_targets:
            return

        potential_targets.sort(key=lambda item: item['distance'])

        attacked_count = 0
        for target_info in potential_targets:
            if attacked_count >= max_targets:
                break

            target_enemy = target_info['enemy']

            # Projectile should call target_enemy.add_incoming_damage(self.stats.damage)
            new_projectile = Projectile(
                self.pos, 
                target_enemy, 
                self.stats.damage, 
                0.5,  # Projectile speed
                self.stats.explosive, 
                self.stats.explosion_radius
            )
            projectiles.append(new_projectile)
            attacked_count += 1

        if attacked_count > 0:
            self.current_reload = self.stats.reload_time

    def upgrade(self, range_increase=0, damage_increase=0, reload_time_decrease=0):
        self.stats.upgrade(range_increase, damage_increase, reload_time_decrease)

    def draw(self, surface):
        pg.draw.circle(surface, (0, 255, 0), (int(self.pos.x), int(self.pos.y)), self.stats.range, 1)
        pg.draw.circle(surface, (255, 0, 0), (int(self.pos.x), int(self.pos.y)), 5)


TOWER_PRESETS = {
    "basic":    TowerStats(range=150, damage=10, reload_time=1.0, explosive=False, damage_Type="phisical"),
    "sniper":   TowerStats(range=400, damage=50, reload_time=2.5, explosive=False, damage_Type="phisical"),
    "rapid":    TowerStats(range=120,  damage=5,  reload_time=0.3, explosive=False, damage_Type="phisical"),
    "cannon":   TowerStats(range=150, damage=10, reload_time=1.5, explosive=True, explosion_radius=60, damage_Type="phisical"),
    "flame":    TowerStats(range=100, damage=2, reload_time=0.1, explosive=False, damage_Type="magic"),
}


def create_tower(pos: tuple[int, int], preset_name: str) -> Tower:
    # Copy stats to avoid shared state between towers
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
