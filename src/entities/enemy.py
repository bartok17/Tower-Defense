"""
Enemy entity and abilities system.

Enemies move along paths and can have various abilities.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

import pygame as pg

from ..config.settings import GAME_WIDTH
from .base_entity import BaseEntity

if TYPE_CHECKING:
    from .abilities import EnemyAbility

# Global font cache
_enemy_font: pg.font.Font | None = None


class Enemy(BaseEntity):
    """An enemy that moves along waypoints toward the player's base."""

    def __init__(
        self, waypoints: list[tuple[int, int]] | list[pg.Vector2], template: dict[str, Any]
    ) -> None:
        # Convert Vector2s to tuples if needed
        converted_waypoints: list[tuple[int, int]] = [
            (int(p[0]), int(p[1])) if isinstance(p, pg.Vector2) else p for p in waypoints
        ]
        super().__init__(converted_waypoints[0] if converted_waypoints else (0, 0))

        self.id = int(template.get("id", 1))
        self.waypoints = waypoints
        self.curr_waypoint = 0

        # Stats
        self.speed = template.get("speed", 1.0)
        self.health = template.get("health", 300)
        self.max_health = self.health
        self.armor = template.get("armor", 1)
        self.magic_resistance = template.get("magic_resistance", 1)

        # Combat
        self.attack_range = template.get("attack_range", 50)
        self.attack_speed = template.get("attack_speed", 1.0)
        self.attack_cooldown = 0
        self.damage_multiplier = 1
        self.damage = template.get("damage", 10)
        self.gold_reward = template.get("gold_reward", 5)

        # Ability state
        self.is_invisible = False
        self.incoming_damage = 0
        self.disabled_abilities = {"active": False, "timer": 0.0, "expires_in": 0.0}
        self.was_glued = False  # For player glue ability

        # Visual
        self.color = tuple(template.get("color", [255, 255, 255]))
        self.radius = template.get("radius", 10)
        self.shape = template.get("shape", "circle")
        self.special_texts: list[dict] = []

        # Abilities
        from .abilities import Abilities

        self.abilities = Abilities()
        for ability_name in template.get("abilities", []):
            self.abilities.add_ability(ability_name)
        self.abilities.apply_all(self)

        # Reference to all enemies (set by spawner)
        self.all_enemies: list[Enemy] = []
        self.enemies_ref: list[Enemy] = []  # Alias

        # Pre-render shape for efficiency
        self._pre_rendered_shape: pg.Surface | None = None
        self._render_shape()

    def _render_shape(self) -> None:
        """Pre-render the enemy shape for efficient drawing."""
        r, g, b = self.color
        draw_alpha = 60 if self.is_invisible else 255

        size = self.radius * 2
        self._pre_rendered_shape = pg.Surface((size, size), pg.SRCALPHA)

        center = self.radius

        if self.shape == "circle":
            pg.draw.circle(
                self._pre_rendered_shape, (r, g, b, draw_alpha), (center, center), self.radius
            )
        elif self.shape == "square":
            pg.draw.rect(self._pre_rendered_shape, (r, g, b, draw_alpha), (0, 0, size, size))
        elif self.shape == "triangle":
            points = [(center, 0), (0, size), (size, size)]
            pg.draw.polygon(self._pre_rendered_shape, (r, g, b, draw_alpha), points)
        elif self.shape == "hexagon":
            points = []
            for i in range(6):
                angle_rad = i * math.pi / 3
                x = center + self.radius * math.cos(angle_rad)
                y = center + self.radius * math.sin(angle_rad)
                points.append((x, y))
            pg.draw.polygon(self._pre_rendered_shape, (r, g, b, draw_alpha), points)
        elif self.shape == "glitch_hex":
            direction = pg.Vector2(self.radius, 0)
            points = [
                (center + d.x, center + d.y) for d in [direction.rotate(i * 60) for i in range(6)]
            ]
            pg.draw.polygon(self._pre_rendered_shape, (r, g, b, draw_alpha), points, width=2)

    def update(self, dt: float) -> None:
        """Update enemy position and state (dt in milliseconds)."""
        # Move toward next waypoint
        if self.curr_waypoint + 1 < len(self.waypoints):
            next_target = pg.Vector2(self.waypoints[self.curr_waypoint + 1])
            direction = next_target - self._pos
            if direction.length_squared() > 0:
                direction = direction.normalize()

            move_distance = self.speed * (dt / 20.0)  # Legacy timing
            self._pos += direction * move_distance

            if self._pos.distance_to(next_target) < move_distance:
                self._pos = next_target
                self.curr_waypoint += 1

        # Update abilities
        if self.abilities:
            self.abilities.update_all(self, dt)

        # Update floating texts
        for ft in self.special_texts[:]:
            ft["lifetime"] -= dt / 1000.0
            ft["pos"].y -= 0.2
            if ft["lifetime"] <= 0:
                self.special_texts.remove(ft)

        # Update ability disable timer
        if self.disabled_abilities["active"]:
            self.disabled_abilities["timer"] += dt
            if self.disabled_abilities["timer"] >= self.disabled_abilities["expires_in"] * 1000:
                self.disabled_abilities["active"] = False
                self.disabled_abilities["timer"] = 0.0

    def draw(self, surface: pg.Surface) -> None:
        global _enemy_font

        # Draw shape
        if self._pre_rendered_shape:
            surface.blit(
                self._pre_rendered_shape, (self._pos.x - self.radius, self._pos.y - self.radius)
            )

        # Initialize font
        if _enemy_font is None:
            if not pg.font.get_init():
                pg.font.init()
            _enemy_font = pg.font.Font(None, 24)

        # Draw floating texts
        for ft in self.special_texts:
            alpha = int(255 * (ft["lifetime"] / 1.0))
            text_surface = _enemy_font.render(ft["text"], True, ft["color"])
            text_surface.set_alpha(alpha)
            surface.blit(text_surface, (ft["pos"].x - text_surface.get_width() // 2, ft["pos"].y - 20))

        # Draw boss health bar if applicable
        if self.has_ability_type("boss"):
            self._draw_boss_healthbar(surface)

    def _draw_boss_healthbar(self, surface: pg.Surface) -> None:
        bar_width = 600
        bar_height = 25
        bar_x = (GAME_WIDTH - bar_width) // 2
        bar_y = 150

        hpbar = pg.Surface((bar_width, bar_height), pg.SRCALPHA)
        hpbar.fill((100, 0, 0, 70))

        hp_ratio = self.health / self.max_health
        hp_rect = pg.Rect(0, 0, int(bar_width * hp_ratio), bar_height)
        pg.draw.rect(hpbar, (255, 0, 255, 70), hp_rect)

        surface.blit(hpbar, (bar_x, bar_y))

        boss_font = pg.font.Font(None, 24)
        text = boss_font.render("BOSS - 404", True, (0, 0, 0))
        text.set_alpha(200)
        surface.blit(text, (bar_x, bar_y + 3))

    def take_damage(self, amount: int, damage_type: str = "physical") -> None:
        """Apply damage after armor/magic resistance."""
        if damage_type == "magic":
            amount -= self.magic_resistance
        elif damage_type == "physical":
            amount -= self.armor

        amount = max(0, amount)
        self.health -= amount

        if self.health < 0:
            self.health = 0

    def is_dead(self) -> bool:
        return bool(self.health <= 0)

    def has_finished(self) -> bool:
        return bool(self.curr_waypoint >= len(self.waypoints) - 1)

    def distance_to_end(self) -> float:
        total_distance = 0.0
        current = self._pos

        for i in range(self.curr_waypoint + 1, len(self.waypoints)):
            next_wp = pg.Vector2(self.waypoints[i])
            total_distance += current.distance_to(next_wp)
            current = next_wp

        return total_distance

    def add_incoming_damage(self, amount: int) -> None:
        self.incoming_damage += amount

    def remove_incoming_damage(self, amount: int) -> None:
        self.incoming_damage = max(0, self.incoming_damage - amount)

    def get_effective_health(self) -> int:
        return int(self.health - self.incoming_damage)

    def has_ability_type(self, ability_name: str) -> bool:
        return ability_name in [getattr(a, "name", "") for a in self.abilities.abilities]

    def has_ability(self, ability_class: type) -> bool:
        return any(isinstance(a, ability_class) for a in self.abilities.abilities)

    def get_ability(self, ability_key: str) -> EnemyAbility | None:
        return self.abilities.get_ability(ability_key)
