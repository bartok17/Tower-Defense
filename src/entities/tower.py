"""
Tower entity and related classes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pygame as pg

from ..config.paths import DATA_DIR
from .base_entity import BaseEntity

if TYPE_CHECKING:
    from .enemy import Enemy
    from .projectile import Projectile


@dataclass
class ProjectileConfig:
    """Configuration for projectiles fired by a tower."""

    shape: str = "circle"
    color_primary: tuple[int, int, int] = (255, 255, 0)
    color_secondary: tuple[int, int, int] | None = None
    size: int = 5
    speed: float = 10.0


@dataclass
class TowerVisualConfig:
    """Configuration for tower visual appearance."""

    shape_type: str = "circle"
    points: list[tuple[float, float]] = field(default_factory=list)
    size: int = 8
    color: tuple[int, int, int] = (200, 200, 200)


@dataclass
class TowerStats:
    """Complete statistics for a tower type."""

    range: int = 180
    damage: int = 10
    reload_time: float = 1.0
    magazine_size: int = 1
    magazine_reload_time: float = 1.0
    max_targets: int = 1
    damage_type: str = "physical"
    explosive: bool = False
    explosion_radius: int = 30

    # Projectile configuration
    projectile_shape: str = "circle"
    projectile_color1: tuple[int, int, int] | None = (255, 255, 0)
    projectile_color2: tuple[int, int, int] | None = None
    projectile_size: int = 5
    projectile_speed: float = 10.0

    # Visual configuration
    tower_visual_shape_type: str = "circle"
    tower_visual_points: list[tuple[float, float]] = field(default_factory=list)
    tower_visual_size: int = 8
    tower_visual_color: tuple[int, int, int] = (200, 200, 200)

    # Metadata
    preset_name: str = ""

    def upgrade(
        self,
        range_increase: int = 0,
        damage_increase: int = 0,
        reload_time_decrease: float = 0,
        magazine_size_increase: int = 0,
        magazine_reload_time_decrease: float = 0,
        max_targets_increase: int = 0,
        projectile_speed_increase: float = 0,
    ) -> None:
        self.range += range_increase
        self.damage += damage_increase
        self.reload_time = max(0.01, self.reload_time - reload_time_decrease)
        self.magazine_size = max(1, self.magazine_size + magazine_size_increase)
        self.magazine_reload_time = max(
            0.1, self.magazine_reload_time - magazine_reload_time_decrease
        )
        self.max_targets = max(1, self.max_targets + max_targets_increase)
        self.projectile_speed = max(0.1, self.projectile_speed + projectile_speed_increase)


class Tower(BaseEntity):
    """A defensive tower that attacks enemies within range."""

    def __init__(self, pos: tuple[int, int], stats: TowerStats) -> None:
        super().__init__(pos)
        self.stats = stats

        # Firing state
        self.current_reload: float = 0.0
        self.current_magazine_shots: int = stats.magazine_size
        self.is_reloading_magazine: bool = False
        self.current_magazine_reload_timer: float = 0.0

        # Visual state
        self.angle: float = 0.0

        # Special abilities
        self.can_see_invisible: bool = False

    def is_in_range(self, enemy: Enemy) -> bool:
        return self.distance_to(enemy) <= self.stats.range

    def get_valid_targets(
        self, enemies: list[Enemy], can_see_invisible: bool = False
    ) -> list[dict]:
        """Get targets sorted by distance to end, filtered by visibility and range."""

        potential_targets = []

        for enemy in enemies:
            # Skip invisible enemies if we can't see them
            if enemy.is_invisible and not (self.can_see_invisible or can_see_invisible):
                continue

            # Skip dead enemies or out of range
            if enemy.is_dead() or not self.is_in_range(enemy):
                continue

            # Calculate effective health (accounting for incoming damage)
            effective_health = enemy.health - enemy.incoming_damage

            # Calculate potential damage after resistances
            potential_damage = self.stats.damage
            if self.stats.damage_type == "physical":
                potential_damage -= enemy.armor
            elif self.stats.damage_type == "magic":
                potential_damage -= enemy.magic_resistance
            potential_damage = max(0, potential_damage)

            # Only target if we can deal damage and enemy isn't effectively dead
            if effective_health > 0 and potential_damage > 0:
                distance = (
                    enemy.distance_to_end() if hasattr(enemy, "distance_to_end") else float("inf")
                )
                potential_targets.append({"enemy": enemy, "distance": distance})

        # Sort by distance to end (closest to base first)
        potential_targets.sort(key=lambda t: float(str(t["distance"])))
        return potential_targets

    def attack(self, enemies: list[Enemy], projectiles: list[Projectile]) -> None:
        from .projectile import Projectile

        potential_targets = self.get_valid_targets(enemies, self.can_see_invisible)

        if not potential_targets:
            return

        # Rotate to face closest target
        first_target = potential_targets[0]["enemy"]
        direction = pg.Vector2(first_target.pos) - self._pos
        if direction.length_squared() > 0:
            self.angle = direction.angle_to(pg.Vector2(1, 0))

        # Check if we can fire
        if self.current_reload > 0 or self.current_magazine_shots <= 0:
            return

        # Fire at targets up to max_targets
        attacked_count = 0
        for target_info in potential_targets:
            if attacked_count >= self.stats.max_targets:
                break
            if self.current_magazine_shots <= 0:
                break

            target = target_info["enemy"]
            target.add_incoming_damage(self.stats.damage)

            # Create projectile
            projectile = Projectile(
                pos=self._pos,
                target=target,
                damage=self.stats.damage,
                damage_type=self.stats.damage_type,
                speed=self.stats.projectile_speed,
                explosive=self.stats.explosive,
                explosion_radius=self.stats.explosion_radius,
                shape=self.stats.projectile_shape,
                color1=self.stats.projectile_color1,
                color2=self.stats.projectile_color2,
                size=self.stats.projectile_size,
            )
            projectiles.append(projectile)

            self.current_magazine_shots -= 1
            attacked_count += 1

        # Start reload
        if attacked_count > 0:
            self.current_reload = self.stats.reload_time

            # Start magazine reload if needed
            if self.current_magazine_shots <= 0 and not self.is_reloading_magazine:
                self.is_reloading_magazine = True
                self.current_magazine_reload_timer = self.stats.magazine_reload_time

    def update(self, dt: float) -> None:
        """Update tower timers. dt in milliseconds."""
        dt_sec = dt / 1000.0
        
        # Update shot reload
        if self.current_reload > 0:
            self.current_reload = max(0, self.current_reload - dt_sec)

        # Update magazine reload
        if self.is_reloading_magazine:
            self.current_magazine_reload_timer -= dt_sec
            if self.current_magazine_reload_timer <= 0:
                self.current_magazine_shots = self.stats.magazine_size
                self.is_reloading_magazine = False
                self.current_magazine_reload_timer = 0
        elif self.current_magazine_shots < self.stats.magazine_size:
            # Start magazine reload
            self.is_reloading_magazine = True
            self.current_magazine_reload_timer = self.stats.magazine_reload_time

    def draw(self, surface: pg.Surface, draw_range: bool = False) -> None:
        # Draw tower shape
        if self.stats.tower_visual_shape_type == "polygon" and self.stats.tower_visual_points:
            # Draw polygon shape rotated to face angle
            base_points = [pg.Vector2(p) for p in self.stats.tower_visual_points]
            scaled_points = [p * self.stats.tower_visual_size for p in base_points]
            rotated_points = [p.rotate(-self.angle) for p in scaled_points]
            final_points = [(p.x + self._pos.x, p.y + self._pos.y) for p in rotated_points]
            pg.draw.polygon(surface, self.stats.tower_visual_color, final_points)
        elif self.stats.tower_visual_shape_type == "circle":
            pg.draw.circle(
                surface,
                self.stats.tower_visual_color,
                (int(self._pos.x), int(self._pos.y)),
                self.stats.tower_visual_size,
            )
        else:
            # Fallback
            pg.draw.circle(surface, (255, 0, 0), (int(self._pos.x), int(self._pos.y)), 5)

        # Optionally draw range circle
        if draw_range:
            pg.draw.circle(
                surface, (0, 255, 0), (int(self._pos.x), int(self._pos.y)), self.stats.range, 1
            )

    def upgrade(self, **kwargs: int | float | str | bool) -> None:
        self.stats.upgrade(**kwargs)  # type: ignore[arg-type]

        # Ensure magazine is capped at new size
        if self.current_magazine_shots > self.stats.magazine_size:
            self.current_magazine_shots = self.stats.magazine_size


# Tower preset loading
_TOWER_PRESETS: dict[str, TowerStats] = {}


def _default_tower_presets() -> dict[str, TowerStats]:
    """Fallback presets if JSON fails to load."""
    return {
        "basic": TowerStats(
            range=180,
            damage=10,
            reload_time=1.0,
            magazine_size=1,
            magazine_reload_time=1.0,
            max_targets=1,
            explosive=False,
            damage_type="physical",
            projectile_shape="circle",
            projectile_color1=(200, 200, 200),
            projectile_size=5,
            projectile_speed=0.5,
            tower_visual_shape_type="polygon",
            tower_visual_points=[(1.0, 0.0), (-0.5, 0.7), (-0.5, -0.7)],
            tower_visual_size=10,
            tower_visual_color=(180, 180, 180),
            preset_name="basic",
        )
    }


def load_tower_presets(json_path: str | None = None) -> dict[str, TowerStats]:
    """Load tower presets from JSON file, using default path if None."""
    global _TOWER_PRESETS

    if json_path is None:
        json_path = str(DATA_DIR / "tower_presets.json")

    try:
        with open(json_path) as f:
            raw = json.load(f)
    except Exception as e:
        print(f"Error loading tower presets from {json_path}: {e}")
        _TOWER_PRESETS = _default_tower_presets()
        return _TOWER_PRESETS

    presets: dict[str, TowerStats] = {}

    for name, data in raw.items():
        try:
            # Convert color lists to tuples
            color1 = tuple(data["projectile_color1"]) if data.get("projectile_color1") else None
            color2 = tuple(data["projectile_color2"]) if data.get("projectile_color2") else None
            visual_color = tuple(data.get("tower_visual_color", [200, 200, 200]))
            visual_points = [tuple(p) for p in data.get("tower_visual_points", [])]

            stats = TowerStats(
                range=data.get("range", 180),
                damage=data.get("damage", 10),
                reload_time=data.get("reload_time", 1.0),
                magazine_size=data.get("magazine_size", 1),
                magazine_reload_time=data.get("magazine_reload_time", 1.0),
                max_targets=data.get("max_targets", 1),
                damage_type=data.get("damage_type", "physical"),
                explosive=data.get("explosive", False),
                explosion_radius=data.get("explosion_radius", 30),
                projectile_shape=data.get("projectile_shape", "circle"),
                projectile_color1=color1,
                projectile_color2=color2,
                projectile_size=data.get("projectile_size", 5),
                projectile_speed=data.get("projectile_speed", 1.0),
                tower_visual_shape_type=data.get("tower_visual_shape_type", "circle"),
                tower_visual_points=visual_points,
                tower_visual_size=data.get("tower_visual_size", 8),
                tower_visual_color=visual_color,
                preset_name=name,
            )
            presets[name] = stats
        except Exception as e:
            print(f"Warning: Skipping invalid tower preset '{name}': {e}")

    if not presets:
        print("Error: No valid tower presets loaded. Using defaults.")
        presets = _default_tower_presets()

    _TOWER_PRESETS = presets
    return presets


def get_tower_presets() -> dict[str, TowerStats]:
    """Get loaded tower presets, loading from file if needed."""
    if not _TOWER_PRESETS:
        load_tower_presets()
    return _TOWER_PRESETS


def create_tower(pos: tuple[int, int], preset_name: str) -> Tower:
    """Create a tower from a preset name."""
    presets = get_tower_presets()
    template = presets.get(preset_name) or presets.get("basic")

    if template is None:
        raise ValueError(f"No tower preset found for '{preset_name}' or 'basic'")

    # Create a copy of the stats
    stats = TowerStats(
        range=template.range,
        damage=template.damage,
        reload_time=template.reload_time,
        magazine_size=template.magazine_size,
        magazine_reload_time=template.magazine_reload_time,
        max_targets=template.max_targets,
        damage_type=template.damage_type,
        explosive=template.explosive,
        explosion_radius=template.explosion_radius,
        projectile_shape=template.projectile_shape,
        projectile_color1=template.projectile_color1,
        projectile_color2=template.projectile_color2,
        projectile_size=template.projectile_size,
        projectile_speed=template.projectile_speed,
        tower_visual_shape_type=template.tower_visual_shape_type,
        tower_visual_points=template.tower_visual_points.copy(),
        tower_visual_size=template.tower_visual_size,
        tower_visual_color=template.tower_visual_color,
        preset_name=preset_name,
    )

    tower = Tower(pos, stats)

    # Special case: sniper can see invisible
    if preset_name == "sniper":
        tower.can_see_invisible = True

    return tower
