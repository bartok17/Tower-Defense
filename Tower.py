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
    def __init__(self, range: int, damage: int, reload_time: float,
                 magazine_size: int, magazine_reload_time: float,
                 max_targets: int = 1,
                 damage_type: str ="physical", explosive: bool = False, explosion_radius: int = 30,
                 projectile_shape: str = "circle", projectile_color1: tuple = (255, 255, 0),
                 projectile_color2: tuple = None, projectile_size: int = 5,
                 projectile_speed: float = 10.0,
                 tower_visual_shape_type: str = "circle",
                 tower_visual_points: list = None,
                 tower_visual_size: int = 8,
                 tower_visual_color: tuple = (200, 200, 200)):
        # Tower stats and visuals
        self.explosive = explosive
        self.explosion_radius = explosion_radius
        self.range = range
        self.damage = damage
        self.reload_time = reload_time
        self.magazine_size = magazine_size
        self.magazine_reload_time = magazine_reload_time
        self.max_targets = max_targets
        self.damage_type = damage_type
        self.projectile_shape = projectile_shape
        self.projectile_color1 = projectile_color1
        self.projectile_color2 = projectile_color2
        self.projectile_size = projectile_size
        self.projectile_speed = projectile_speed
        self.tower_visual_shape_type = tower_visual_shape_type
        self.tower_visual_points = tower_visual_points if tower_visual_points is not None else []
        self.tower_visual_size = tower_visual_size
        self.tower_visual_color = tower_visual_color

    def upgrade(self, range_increase=0, damage_increase=0, reload_time_decrease=0,
                  magazine_size_increase=0, magazine_reload_time_decrease=0,
                  max_targets_increase=0, projectile_speed_increase=0):
        # Upgrade tower stats
        self.range += range_increase
        self.damage += damage_increase
        self.reload_time = max(0.01, self.reload_time - reload_time_decrease)
        self.magazine_size = max(1, self.magazine_size + magazine_size_increase)
        self.magazine_reload_time = max(0.1, self.magazine_reload_time - magazine_reload_time_decrease)
        self.max_targets = max(1, self.max_targets + max_targets_increase)
        self.projectile_speed = max(0.1, self.projectile_speed + projectile_speed_increase)


class Tower:
    def __init__(self, pos: tuple[int, int], stats: TowerStats):
        self.pos = pg.math.Vector2(pos)
        self.stats = stats
        self.current_reload = 0
        self.current_magazine_shots = stats.magazine_size
        self.is_reloading_magazine = False
        self.current_magazine_reload_timer = 0
        self.angle = 0.0  # Facing angle in degrees

    def is_in_range(self, enemy: Enemy) -> bool:
        # Check if enemy is within range
        return self.pos.distance_to(pg.math.Vector2(enemy.pos)) <= self.stats.range

    def attack(self, enemies: list[Enemy], waypoints: list[tuple[int, int]], projectiles: list[Projectile]):
        # Find valid targets and fire projectiles
        potential_targets = []
        for enemy_candidate in enemies:
            if enemy_candidate.has_ability(aea.invisibleAbility):
                if not getattr(self, "can_see_invisible", False):
                    continue
            if not enemy_candidate.is_dead() and self.is_in_range(enemy_candidate):
                current_health = getattr(enemy_candidate, 'health', 0)
                inc_damage = getattr(enemy_candidate, 'incoming_damage', 0)
                effective_health = current_health - inc_damage

                potential_damage_dealt = self.stats.damage
                if self.stats.damage_type == "physical":
                    potential_damage_dealt -= getattr(enemy_candidate, 'armor', 0)
                elif self.stats.damage_type == "magic":
                    potential_damage_dealt -= getattr(enemy_candidate, 'magic_resistance', 0)
                potential_damage_dealt = max(0, potential_damage_dealt)

                if effective_health > 0 and potential_damage_dealt > 0:
                    distance = float('inf')
                    if hasattr(enemy_candidate, 'distance_to_end'):
                        distance = enemy_candidate.distance_to_end()
                    potential_targets.append({'enemy': enemy_candidate, 'distance': distance})

        if not potential_targets:
            return

        potential_targets.sort(key=lambda item: item['distance'])

        # Rotate to face closest target
        first_target_enemy = potential_targets[0]['enemy']
        direction_vector = pg.math.Vector2(first_target_enemy.pos) - self.pos
        if direction_vector.length_squared() > 0:
            self.angle = direction_vector.angle_to(pg.math.Vector2(1, 0))

        # Check reload and magazine
        if self.current_reload > 0 or self.current_magazine_shots <= 0:
            return

        attacked_count = 0
        for target_info in potential_targets:
            if attacked_count >= self.stats.max_targets or self.current_magazine_shots <= 0:
                break

            target_enemy = target_info['enemy']
            target_enemy.add_incoming_damage(self.stats.damage)

            new_projectile = Projectile(
                self.pos,
                target_enemy,
                self.stats.damage,
                self.stats.damage_type,
                self.stats.projectile_speed,
                self.stats.explosive,
                self.stats.explosion_radius,
                shape=self.stats.projectile_shape,
                color1=self.stats.projectile_color1,
                color2=self.stats.projectile_color2,
                size=self.stats.projectile_size
            )
            projectiles.append(new_projectile)

            self.current_magazine_shots -= 1
            attacked_count += 1

        if attacked_count > 0:
            self.current_reload = self.stats.reload_time
            # Start magazine reload if needed
            if self.current_magazine_shots < self.stats.magazine_size and not self.is_reloading_magazine:
                self.is_reloading_magazine = True
                self.current_magazine_reload_timer = self.stats.magazine_reload_time
            elif self.current_magazine_shots <= 0 and not self.is_reloading_magazine:
                self.is_reloading_magazine = True
                self.current_magazine_reload_timer = self.stats.magazine_reload_time

    def upgrade(self, range_increase=0, damage_increase=0, reload_time_decrease=0,
                  magazine_size_increase=0, magazine_reload_time_decrease=0,
                  projectile_speed_increase=0):
        # Upgrade tower and adjust magazine shots
        self.stats.upgrade(range_increase, damage_increase, reload_time_decrease,
                           magazine_size_increase, magazine_reload_time_decrease,
                           projectile_speed_increase=projectile_speed_increase)
        if self.current_magazine_shots < self.stats.magazine_size and not self.is_reloading_magazine:
            self.current_magazine_shots = min(self.current_magazine_shots, self.stats.magazine_size)

    def draw(self, surface, draw_range=False):
        # Draw tower shape
        if self.stats.tower_visual_shape_type == "polygon" and self.stats.tower_visual_points:
            base_points = [pg.math.Vector2(p) for p in self.stats.tower_visual_points]
            scaled_points = [p * self.stats.tower_visual_size for p in base_points]
            rotated_points = [p.rotate(-self.angle) for p in scaled_points]
            final_world_points = [(rp.x + self.pos.x, rp.y + self.pos.y) for rp in rotated_points]
            pg.draw.polygon(surface, self.stats.tower_visual_color, final_world_points)
        elif self.stats.tower_visual_shape_type == "circle":
            pg.draw.circle(surface, self.stats.tower_visual_color,
                           (int(self.pos.x), int(self.pos.y)),
                           self.stats.tower_visual_size)
        else:
            pg.draw.circle(surface, (255, 0, 0), (int(self.pos.x), int(self.pos.y)), 5)

        # Optionally draw range
        if draw_range:
            pg.draw.circle(surface, (0, 255, 0), (int(self.pos.x), int(self.pos.y)), self.stats.range, 1)


TOWER_PRESETS = {
    # Tower presets: name -> TowerStats
    "basic":    TowerStats(range=180, damage=10, reload_time=1.0, magazine_size=1, magazine_reload_time=1.0, max_targets=1, explosive=False, damage_type="physical",
                           projectile_shape="circle", projectile_color1=(200, 200, 200), projectile_size=5, projectile_speed=0.5,
                           tower_visual_shape_type="polygon", tower_visual_points=[(1.0, 0.0), (-0.5, 0.7), (-0.5, -0.7)], tower_visual_size=10, tower_visual_color=(180, 180, 180)),
    "sniper":   TowerStats(range=400, damage=50, reload_time=2.5, magazine_size=1, magazine_reload_time=2.5, max_targets=1, explosive=False, damage_type="physical",
                           projectile_shape="triangle", projectile_color1=(100, 100, 255), projectile_size=5, projectile_speed=2,
                           tower_visual_shape_type="polygon", tower_visual_points=[(1.5, 0.0), (-0.7, 0.3), (-0.7, -0.3)], tower_visual_size=12, tower_visual_color=(100, 100, 200)),
    "rapid":    TowerStats(range=160,  damage=10,  reload_time=0.3, magazine_size=10, magazine_reload_time=4.0, max_targets=1, explosive=False, damage_type="physical",
                           projectile_shape="circle", projectile_color1=(0, 255, 0), projectile_size=6, projectile_speed=0.5,
                           tower_visual_shape_type="  polygon", tower_visual_points=[(0.7, -0.7), (0.7, 0.7), (-0.7, 0.7), (-0.7, -0.7)], tower_visual_size=8, tower_visual_color=(0, 200, 0)),
    "cannon":   TowerStats(range=160, damage=15, reload_time=1.5, magazine_size=1, magazine_reload_time=1.5, max_targets=1, explosive=True, explosion_radius=60, damage_type="physical",
                           projectile_shape="circle", projectile_color1=(255, 100, 0), projectile_color2=(255,165,0), projectile_size=8, projectile_speed=0.5,
                           tower_visual_shape_type="polygon", tower_visual_points=[(1,0), (0.5,0.866), (-0.5,0.866), (-1,0), (-0.5,-0.866), (0.5,-0.866)], tower_visual_size=10, tower_visual_color=(200, 80, 0)),
    "flame":    TowerStats(range=160, damage=3, reload_time=0.04, magazine_size=120, magazine_reload_time=8.3, max_targets=3, explosive=False, damage_type="magic",
                           projectile_shape="circle", projectile_color1=(255, 0, 0), projectile_color2=(255,200,0), projectile_size=7, projectile_speed=0.8,
                           tower_visual_shape_type="polygon", tower_visual_points=[(0.8, 0.0), (-0.3, 0.9), (0.0, 0.0), (-0.3, -0.9)], tower_visual_size=11, tower_visual_color=(220, 0, 0)),
    "basic 2": TowerStats(range=200, damage=40, reload_time=1, magazine_size=1, magazine_reload_time=1.0, max_targets=1, explosive=False, damage_type="physical",
                          projectile_shape="circle", projectile_color1=(255, 255, 100), projectile_size=7, projectile_speed=0.7,
                          tower_visual_shape_type="polygon", tower_visual_points=[(1.0, 0.0), (-0.5, 0.7), (-0.5, -0.7)], tower_visual_size=12, tower_visual_color=(255, 255, 100)),
    "cannon 2": TowerStats(range=180, damage=40, reload_time=1.5, magazine_size=1, magazine_reload_time=1.5, max_targets=1, explosive=True, explosion_radius=100, damage_type="physical",
                           projectile_shape="circle", projectile_color1=(255, 180, 0), projectile_color2=(255,200,0), projectile_size=10, projectile_speed=0.7,
                           tower_visual_shape_type="polygon", tower_visual_points=[(1,0), (0.5,0.866), (-0.5,0.866), (-1,0), (-0.5,-0.866), (0.5,-0.866)], tower_visual_size=12, tower_visual_color=(255, 180, 0)),
    "rapid 2": TowerStats(range=180, damage=15, reload_time=0.2, magazine_size=40, magazine_reload_time=12.0, max_targets=1, explosive=False, damage_type="physical",
                           projectile_shape="circle", projectile_color1=(0, 255, 0), projectile_size=8, projectile_speed=0.6,
                           tower_visual_shape_type="polygon", tower_visual_points=[(0.7, -0.7), (0.7, 0.7), (-0.7, 0.7), (-0.7, -0.7)], tower_visual_size=10, tower_visual_color=(0, 200, 0)),
    "sniper 2": TowerStats(range=600, damage=100, reload_time=3.0, magazine_size=1, magazine_reload_time=3.0, max_targets=1, explosive=False, damage_type="physical",
                           projectile_shape="triangle", projectile_color1=(100, 100, 255), projectile_size=8, projectile_speed=3,
                           tower_visual_shape_type="polygon", tower_visual_points=[(1.5, 0.0), (-0.7, 0.3), (-0.7, -0.3)], tower_visual_size=14, tower_visual_color=(100, 100, 200)),
    "flame 2": TowerStats(range=180, damage=4, reload_time=0.03, magazine_size=300, magazine_reload_time=10.0, max_targets=10, explosive=False, damage_type="magic",
                           projectile_shape="circle", projectile_color1=(255, 0, 0), projectile_color2=(255,200,0), projectile_size=9, projectile_speed=1.0,
                           tower_visual_shape_type="polygon", tower_visual_points=[(0.8, 0.0), (-0.3, 0.9), (0.0, 0.0), (-0.3, -0.9)], tower_visual_size=13, tower_visual_color=(220, 0, 0))
}


def create_tower(pos: tuple[int, int], preset_name: str) -> Tower:
    # Instantiate a tower from preset
    stats_template = TOWER_PRESETS.get(preset_name, TOWER_PRESETS["basic"])
    stats = TowerStats(
        range=stats_template.range,
        damage=stats_template.damage,
        reload_time=stats_template.reload_time,
        magazine_size=stats_template.magazine_size,
        magazine_reload_time=stats_template.magazine_reload_time,
        max_targets=stats_template.max_targets,
        damage_type=stats_template.damage_type,
        explosive=stats_template.explosive,
        explosion_radius=stats_template.explosion_radius,
        projectile_shape=stats_template.projectile_shape,
        projectile_color1=stats_template.projectile_color1,
        projectile_color2=stats_template.projectile_color2,
        projectile_size=stats_template.projectile_size,
        projectile_speed=stats_template.projectile_speed,
        tower_visual_shape_type=stats_template.tower_visual_shape_type,
        tower_visual_points=stats_template.tower_visual_points,
        tower_visual_size=stats_template.tower_visual_size,
        tower_visual_color=stats_template.tower_visual_color
    )
    stats.preset_name = preset_name  
    return Tower(pos, stats)
