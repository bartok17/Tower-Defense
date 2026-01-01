"""
Projectile entity.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

import pygame as pg

from .base_entity import BaseEntity

if TYPE_CHECKING:
    from .enemy import Enemy


class Projectile(BaseEntity):
    """A projectile that tracks and damages enemies. Can be explosive."""

    def __init__(
        self,
        pos: tuple[int, int] | pg.Vector2,
        target: Enemy,
        damage: int,
        damage_type: str,
        speed: float = 5.0,
        explosive: bool = False,
        explosion_radius: int = 30,
        shape: str = "circle",
        color1: tuple[int, int, int] | None = (255, 255, 0),
        color2: tuple[int, int, int] | None = None,
        size: int = 5,
    ) -> None:
        # Convert Vector2 to tuple if needed
        if isinstance(pos, pg.Vector2):
            pos = (int(pos.x), int(pos.y))
        super().__init__(pos)

        self.target = target
        self.damage = damage
        self.damage_type = damage_type
        self.speed = speed
        self.explosive = explosive
        self.explosion_radius = explosion_radius
        self.shape = shape
        self.size = size

        # Active state
        self.active = True

        # Explosion effect state
        self.explosion_timer = 0.0
        self.explosion_duration = 0.3

        # Determine color
        if color2 and color1:
            # Random color between color1 and color2
            r = random.randint(min(color1[0], color2[0]), max(color1[0], color2[0]))
            g = random.randint(min(color1[1], color2[1]), max(color1[1], color2[1]))
            b = random.randint(min(color1[2], color2[2]), max(color1[2], color2[2]))
            self.color = (r, g, b)
        else:
            self.color = color1 or (255, 255, 0)

    def on_removed(self) -> None:
        if self.target and hasattr(self.target, "remove_incoming_damage"):
            self.target.remove_incoming_damage(self.damage)

    def _apply_damage(self, enemies: list[Enemy] | None = None) -> None:
        """Apply damage to target or area if explosive."""
        self._pos = pg.Vector2(self.target.pos)

        if self.explosive and enemies is not None:
            # Area damage
            for enemy in enemies:
                distance = self._pos.distance_to(enemy.pos)
                if distance <= self.explosion_radius:
                    # Damage falloff based on distance
                    damage_factor = max(0.5, 1 - (distance / self.explosion_radius) * 0.5)
                    enemy.take_damage(
                        int(self.damage * damage_factor), damage_type=self.damage_type
                    )
        else:
            # Single target damage
            self.target.take_damage(self.damage, damage_type=self.damage_type)

        self.active = False

        if self.explosive:
            self.explosion_timer = self.explosion_duration

    def update(self, dt: float, enemies: list[Enemy] | None = None) -> None:
        """Update projectile position and check for hit. dt in ms."""
        # Handle explosion effect timer
        if not self.active:
            if self.explosive and self.explosion_timer > 0:
                self.explosion_timer -= dt / 1000.0
            return

        # Check if target is dead
        if self.target.is_dead():
            self.active = False
            return

        # Move toward target
        direction = self.target.pos - self._pos
        distance = direction.length()

        move_distance = self.speed * dt

        if distance < move_distance:
            # Hit target
            self._apply_damage(enemies)
        else:
            # Move toward target
            direction = direction.normalize()
            self._pos += direction * move_distance

    def draw(self, surface: pg.Surface) -> None:
        """Draw the projectile or explosion effect."""
        if self.active:
            # Draw projectile
            if self.shape == "circle":
                pg.draw.circle(surface, self.color, (int(self._pos.x), int(self._pos.y)), self.size)
            elif self.shape == "square":
                rect = pg.Rect(
                    self._pos.x - self.size // 2, self._pos.y - self.size // 2, self.size, self.size
                )
                pg.draw.rect(surface, self.color, rect)
            elif self.shape == "triangle":
                half = self.size // 2
                points = [
                    (self._pos.x, self._pos.y - half),
                    (self._pos.x - half, self._pos.y + half),
                    (self._pos.x + half, self._pos.y + half),
                ]
                pg.draw.polygon(surface, self.color, points)

        elif self.explosive and self.explosion_timer > 0:
            # Draw explosion ring
            pg.draw.circle(
                surface,
                (255, 100, 0),
                (int(self._pos.x), int(self._pos.y)),
                self.explosion_radius,
                2,
            )
