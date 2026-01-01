"""
Player abilities system.

Handles player-activated skills like Fireball, Scanner, Disruptor, and Glue.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pygame as pg

if TYPE_CHECKING:
    from ..entities import Enemy
    from .economy_system import ResourcesManager


@dataclass
class AbilityEffect:
    """Tracks an active ability effect."""

    active: bool = False
    timer: float = 0.0
    duration: float = 5.0
    pos: pg.Vector2 | None = None


@dataclass
class AbilityCost:
    """Cost for using an ability."""

    gold: int = 0
    wood: int = 0
    metal: int = 0

    def to_dict(self) -> dict[str, int]:
        """Convert to dictionary for ResourcesManager."""
        costs = {}
        if self.gold > 0:
            costs["gold"] = self.gold
        if self.wood > 0:
            costs["wood"] = self.wood
        if self.metal > 0:
            costs["metal"] = self.metal
        return costs


# Ability configurations
ABILITY_COSTS: dict[str, AbilityCost] = {
    "fireball": AbilityCost(gold=70),
    "scanner": AbilityCost(gold=30, metal=15, wood=15),
    "disruptor": AbilityCost(gold=100, metal=30, wood=30),
    "glue": AbilityCost(gold=10, wood=50),
}

ABILITY_RADII: dict[str, int] = {
    "fireball": 80,
    "scanner": 150,
    "disruptor": 120,
    "glue": 100,
}

ABILITY_DURATIONS: dict[str, float] = {
    "scanner": 5.0,
    "disruptor": 10.0,
    "glue": 5.0,
}


class PlayerAbilities:
    """
    Manages player-activated abilities.

    Abilities:
    - Fireball: Instant AOE damage
    - Scanner: Reveals invisible enemies in radius for duration
    - Disruptor: Silences enemy abilities for duration
    - Glue: Slows enemies that enter radius
    """

    def __init__(self) -> None:
        self.selected_ability: str | None = None

        # Active effects
        self.effects: dict[str, AbilityEffect] = {
            "scanner": AbilityEffect(duration=ABILITY_DURATIONS["scanner"]),
            "disruptor": AbilityEffect(duration=ABILITY_DURATIONS["disruptor"]),
            "glue": AbilityEffect(duration=ABILITY_DURATIONS["glue"]),
        }

        # Fireball visual effect
        self.fireball_pos: pg.Vector2 | None = None
        self.fireball_timer: float = 0.0
        self.fireball_visual_duration: float = 0.5

    def can_use(self, name: str, resources: ResourcesManager) -> bool:
        """Check if player can afford an ability."""
        cost = ABILITY_COSTS.get(name)
        if not cost:
            return False
        return resources.can_afford(cost.to_dict())

    def select(self, name: str) -> None:
        """Select an ability for use."""
        self.selected_ability = name

    def deselect(self) -> None:
        """Deselect current ability."""
        self.selected_ability = None

    def use(
        self, name: str, resources: ResourcesManager, pos: tuple[int, int], enemies: list[Enemy]
    ) -> bool:
        """Use ability at position. Returns True if successful."""
        cost = ABILITY_COSTS.get(name)
        if not cost:
            return False

        if not resources.can_afford(cost.to_dict()):
            return False

        # Deduct cost
        resources.spend_multiple(cost.to_dict())

        # Activate ability
        target = pg.Vector2(pos)

        if name == "fireball":
            self._use_fireball(target, enemies)
        elif name == "scanner":
            self._use_scanner(target)
        elif name == "disruptor":
            self._use_disruptor(target, enemies)
        elif name == "glue":
            self._use_glue(target)

        self.selected_ability = None
        return True

    def _use_fireball(self, pos: pg.Vector2, enemies: list[Enemy]) -> None:
        """Fireball: Instant AOE damage."""
        radius = ABILITY_RADII["fireball"]
        damage = 100

        for enemy in enemies:
            if enemy.pos.distance_to(pos) <= radius:
                enemy.take_damage(damage)

        # Visual effect
        self.fireball_pos = pos
        self.fireball_timer = self.fireball_visual_duration

    def _use_scanner(self, pos: pg.Vector2) -> None:
        """Scanner: Reveal invisible enemies."""
        effect = self.effects["scanner"]
        effect.active = True
        effect.timer = 0.0
        effect.pos = pos

    def _use_disruptor(self, pos: pg.Vector2, enemies: list[Enemy]) -> None:
        """Disruptor: Silence enemy abilities."""
        radius = ABILITY_RADII["disruptor"]
        duration = ABILITY_DURATIONS["disruptor"]

        for enemy in enemies:
            if enemy.pos.distance_to(pos) <= radius:
                # Disable abilities
                enemy.disabled_abilities = {"active": True, "expires_in": duration}
                # Visual feedback
                if hasattr(enemy, "special_texts"):
                    enemy.special_texts.append(
                        {
                            "text": "Silenced!",
                            "pos": enemy.pos.copy(),
                            "lifetime": 1.0,
                            "color": (255, 255, 0),
                        }
                    )

        effect = self.effects["disruptor"]
        effect.active = True
        effect.timer = 0.0
        effect.pos = pos

    def _use_glue(self, pos: pg.Vector2) -> None:
        """Glue: Slow enemies in area."""
        effect = self.effects["glue"]
        effect.active = True
        effect.timer = 0.0
        effect.pos = pos

    def update(self, dt_ms: float, enemies: list[Enemy]) -> None:
        """Update active ability effects. dt_ms in milliseconds."""
        # Fireball visual timer
        if self.fireball_timer > 0:
            self.fireball_timer -= dt_ms / 1000.0
            if self.fireball_timer <= 0:
                self.fireball_timer = 0
                self.fireball_pos = None

        # Scanner effect
        scanner = self.effects["scanner"]
        if scanner.active and scanner.pos:
            scanner.timer += dt_ms / 1000.0
            if scanner.timer >= scanner.duration:
                scanner.active = False
                scanner.pos = None
                scanner.timer = 0.0
            else:
                radius = ABILITY_RADII["scanner"]
                for enemy in enemies:
                    if getattr(enemy, "is_invisible", False):
                        if enemy.pos.distance_to(scanner.pos) <= radius:
                            # Reveal enemy
                            if hasattr(enemy, "abilities") and hasattr(
                                enemy.abilities, "remove_ability"
                            ):
                                enemy.abilities.remove_ability("invisible")
                            enemy.is_invisible = False

        # Glue effect
        glue = self.effects["glue"]
        if glue.active and glue.pos:
            glue.timer += dt_ms / 1000.0
            if glue.timer >= glue.duration:
                glue.active = False
                glue.pos = None
                glue.timer = 0.0
            else:
                radius = ABILITY_RADII["glue"]
                for enemy in enemies:
                    if enemy.pos.distance_to(glue.pos) <= radius:
                        if not getattr(enemy, "was_glued", False):
                            enemy.speed *= 0.70
                            enemy.was_glued = True
                            if hasattr(enemy, "special_texts"):
                                enemy.special_texts.append(
                                    {
                                        "text": "Slowed",
                                        "pos": enemy.pos.copy(),
                                        "lifetime": 1.0,
                                        "color": (100, 150, 255),
                                    }
                                )

        # Disruptor effect timer
        disruptor = self.effects["disruptor"]
        if disruptor.active:
            disruptor.timer += dt_ms / 1000.0
            if disruptor.timer >= disruptor.duration:
                disruptor.active = False
                disruptor.pos = None
                disruptor.timer = 0.0

    def draw(self, surface: pg.Surface) -> None:
        """Draw active ability effects."""
        # Fireball strike indicator
        if self.fireball_pos and self.fireball_timer > 0:
            radius = ABILITY_RADII["fireball"]
            pg.draw.circle(
                surface,
                (255, 50, 0),
                (int(self.fireball_pos.x), int(self.fireball_pos.y)),
                radius,
                3,
            )

        # Scanner effect
        scanner = self.effects["scanner"]
        if scanner.active and scanner.pos:
            self._draw_effect_circle(
                surface, scanner.pos, ABILITY_RADII["scanner"], (0, 200, 0, 80)
            )

        # Disruptor effect
        disruptor = self.effects["disruptor"]
        if disruptor.active and disruptor.pos:
            self._draw_effect_circle(
                surface, disruptor.pos, ABILITY_RADII["disruptor"], (255, 255, 0, 90)
            )

        # Glue effect
        glue = self.effects["glue"]
        if glue.active and glue.pos:
            self._draw_effect_circle(surface, glue.pos, ABILITY_RADII["glue"], (120, 120, 255, 60))

    def _draw_effect_circle(
        self, surface: pg.Surface, pos: pg.Vector2, radius: int, color: tuple[int, int, int, int]
    ) -> None:
        """Draw a semi-transparent effect circle."""
        overlay = pg.Surface((radius * 2, radius * 2), pg.SRCALPHA)
        pg.draw.circle(overlay, color, (radius, radius), radius, 3)
        surface.blit(overlay, (pos.x - radius, pos.y - radius))

    def draw_targeting(self, surface: pg.Surface, mouse_pos: tuple[int, int] | None = None) -> None:
        """Draw targeting indicator when ability is selected."""
        if not self.selected_ability:
            return

        if mouse_pos is None:
            mouse_pos = pg.mouse.get_pos()
        radius = ABILITY_RADII.get(self.selected_ability, 50)

        # Color based on ability
        colors = {
            "fireball": (255, 100, 0, 100),
            "scanner": (0, 255, 0, 100),
            "disruptor": (255, 255, 0, 100),
            "glue": (100, 100, 255, 100),
        }
        color = colors.get(self.selected_ability, (255, 255, 255, 100))

        overlay = pg.Surface((radius * 2, radius * 2), pg.SRCALPHA)
        pg.draw.circle(overlay, color, (radius, radius), radius)
        pg.draw.circle(overlay, (255, 255, 255, 150), (radius, radius), radius, 2)
        surface.blit(overlay, (mouse_pos[0] - radius, mouse_pos[1] - radius))
