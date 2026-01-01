"""
Enemy abilities system.
"""

from __future__ import annotations

import json
import random
from math import inf
from typing import TYPE_CHECKING, Any

import pygame as pg

from ..config.settings import GAME_HEIGHT, GAME_WIDTH
from ..config.paths import DATA_DIR

if TYPE_CHECKING:
    from .enemy import Enemy


# Lazy-loaded enemy templates cache
_loaded_enemy_templates: dict | None = None


def _get_enemy_templates() -> dict:
    """Load and cache enemy templates."""
    global _loaded_enemy_templates

    if _loaded_enemy_templates is None:
        file_path = DATA_DIR / "enemyTemplates.json"
        try:
            with open(file_path) as f:
                _loaded_enemy_templates = json.load(f)
        except FileNotFoundError:
            print(f"ERROR: Could not find enemyTemplates.json at {file_path}")
            _loaded_enemy_templates = {}
        except json.JSONDecodeError:
            print(f"ERROR: Could not decode enemyTemplates.json at {file_path}")
            _loaded_enemy_templates = {}

    return _loaded_enemy_templates


class EnemyAbility:
    """Base class for enemy abilities."""

    name: str = ""

    def apply(self, enemy: Enemy) -> None:
        pass

    def on_update(self, enemy: Enemy, dt: float) -> None:
        if getattr(enemy, "disabled_abilities", {}).get("active", False):
            return


class FastAbility(EnemyAbility):
    """Increases enemy movement speed."""

    name = "fast"

    def apply(self, enemy: Enemy) -> None:
        enemy.speed += 1


class MagicResistantAbility(EnemyAbility):
    """Makes enemy immune to magic damage."""

    name = "magic_resistant"

    def apply(self, enemy: Enemy) -> None:
        enemy.magic_resistance = inf


class RangedAbility(EnemyAbility):
    """Increases enemy attack range."""

    name = "ranged"

    def apply(self, enemy: Enemy) -> None:
        enemy.attack_range += 50


class TankAbility(EnemyAbility):
    """More HP and armor, less speed."""

    name = "tank"

    def apply(self, enemy: Enemy) -> None:
        enemy.armor += 4
        enemy.max_health *= 2
        enemy.health *= 2
        enemy.speed -= 0.5


class HealerAbility(EnemyAbility):
    """Periodically heals nearby injured allies."""

    name = "healer"

    def __init__(self, heal_amount: int, range: int = 150, cooldown: float = 3.0):
        self.heal_amount = heal_amount
        self.range = range
        self.cooldown = cooldown
        self.timer = 0.0

    def on_update(self, enemy: Enemy, dt: float) -> None:
        if getattr(enemy, "disabled_abilities", {}).get("active", False):
            return

        self.timer += dt / 1000.0
        if self.timer < self.cooldown:
            return

        self.timer = 0.0

        if not hasattr(enemy, "pos") or not hasattr(enemy, "all_enemies"):
            return

        # Find nearby injured allies
        nearby = [
            e
            for e in enemy.all_enemies
            if not e.is_dead()
            and e != enemy
            and e.health < e.max_health
            and enemy.pos.distance_to(e.pos) <= self.range
        ]

        if not nearby:
            return

        # Heal the most injured ally
        target = min(nearby, key=lambda e: e.health / e.max_health)
        target.health = min(target.max_health, target.health + self.heal_amount)

        if hasattr(target, "special_texts"):
            target.special_texts.append(
                {
                    "text": f"+{self.heal_amount}",
                    "pos": target.pos.copy(),
                    "lifetime": 1.0,
                    "color": (0, 255, 0),
                }
            )


class SummonerAbility(EnemyAbility):
    """Periodically summons additional enemies."""

    name = "summoner"

    def __init__(self, summon_count: int, summon_type_id: str, cooldown: float = 5.0):
        self.summon_count = summon_count
        self.summon_type_id = str(summon_type_id)
        self.cooldown = cooldown
        self.timer = 0.0

    def on_update(self, enemy: Enemy, dt: float) -> None:
        if getattr(enemy, "disabled_abilities", {}).get("active", False):
            return

        from .enemy import Enemy as EnemyClass

        self.timer += dt / 1000.0
        if self.timer < self.cooldown:
            return

        self.timer = 0.0

        if not hasattr(enemy, "all_enemies"):
            return

        templates = _get_enemy_templates()
        template = templates.get(self.summon_type_id)
        if not template:
            print(f"Warning: Summoner could not find template ID {self.summon_type_id}")
            return

        for _ in range(self.summon_count):
            start = pg.Vector2(enemy.pos)

            # Create a loop path before resuming normal path
            loop = [
                start,
                start + pg.Vector2(30, 0).rotate(random.uniform(0, 360)),
                start + pg.Vector2(30, 0).rotate(random.uniform(0, 360)),
                start + pg.Vector2(30, 0).rotate(random.uniform(0, 360)),
                start,
            ]

            if enemy.curr_waypoint + 1 < len(enemy.waypoints):
                resume_path = enemy.waypoints[enemy.curr_waypoint + 1 :]
            else:
                resume_path = []

            path = loop + [pg.Vector2(p) for p in resume_path]
            new_enemy = EnemyClass(path, template)
            new_enemy.all_enemies = enemy.all_enemies
            enemy.all_enemies.append(new_enemy)

        enemy.special_texts.append(
            {"text": "Summon!", "pos": enemy.pos.copy(), "lifetime": 1.0, "color": (150, 150, 255)}
        )


class InvisibleAbility(EnemyAbility):
    """Makes enemy invisible to most towers."""

    name = "invisible"

    def apply(self, enemy: Enemy) -> None:
        enemy.is_invisible = True


class DashAbility(EnemyAbility):
    """Periodically dashes forward at high speed."""

    name = "dash"

    def __init__(
        self, speed_multiplier: float = 2.0, dash_duration: float = 1.0, cooldown: float = 5.0
    ):
        self.speed_multiplier = speed_multiplier
        self.dash_duration = dash_duration
        self.cooldown = cooldown
        self.timer = 0.0
        self.dashing = False
        self.dash_timer = 0.0
        self.original_speed = 1.0

    def apply(self, enemy: Enemy) -> None:
        self.original_speed = enemy.speed

    def on_update(self, enemy: Enemy, dt: float) -> None:
        if getattr(enemy, "disabled_abilities", {}).get("active", False):
            return

        dt_sec = dt / 1000.0
        self.timer += dt_sec

        if self.dashing:
            self.dash_timer += dt_sec
            if self.dash_timer >= self.dash_duration:
                enemy.speed = self.original_speed
                self.dashing = False
                self.dash_timer = 0.0
        elif self.timer >= self.cooldown:
            self.original_speed = enemy.speed
            enemy.speed *= self.speed_multiplier
            self.dashing = True
            self.dash_timer = 0.0
            self.timer = 0.0

            if hasattr(enemy, "special_texts"):
                enemy.special_texts.append(
                    {
                        "text": "DASH!",
                        "pos": enemy.pos.copy(),
                        "lifetime": 0.7,
                        "color": (255, 200, 50),
                    }
                )


class BossAbility(EnemyAbility):
    """Boss behavior with phases, teleportation, and glitch effects."""

    name = "boss"

    def __init__(self) -> None:
        self.stage = 1
        self.phase_timer = 0.0
        self.phase_cooldown = 5.0
        self.glitch_spawn_timer = 0.0
        self.active_glitches: list[dict] = []

    def apply(self, enemy: Enemy) -> None:
        enemy.is_invisible = True

    def on_update(self, enemy: Enemy, dt: float) -> None:
        dt_sec = dt / 1000.0

        # Phase transitions based on health
        if enemy.health < enemy.max_health * 0.8 and self.stage == 1:
            enemy.is_invisible = False
            self.stage = 2

        if enemy.health < enemy.max_health * 0.6:
            self.stage = 20

        if self.stage > 1:
            self._update_phase(enemy, dt_sec)

            # Spawn glitch effects
            self.glitch_spawn_timer += dt_sec
            if self.glitch_spawn_timer >= 0.15:
                self.glitch_spawn_timer = 0
                self._spawn_glitches()

        # Update glitch lifetimes
        for glitch in self.active_glitches[:]:
            glitch["time"] -= dt_sec
            if glitch["time"] <= 0:
                self.active_glitches.remove(glitch)

    def _update_phase(self, enemy: Enemy, dt: float) -> None:
        self.phase_timer += dt

        if self.phase_timer >= self.phase_cooldown:
            self.phase_timer = 0
            self.phase_cooldown = random.randint(1, 3)

            # Teleport back and summon
            if enemy.curr_waypoint > 0:
                enemy.curr_waypoint -= 1
                enemy.pos = pg.Vector2(enemy.waypoints[enemy.curr_waypoint])
                self._summon_nearby(enemy, count=7)

    def _spawn_glitches(self) -> None:
        for _ in range(self.stage * 3):
            glitch = {
                "pos": pg.Vector2(
                    random.randint(0, GAME_WIDTH), random.randint(0, GAME_HEIGHT)
                ),
                "size": random.randint(10, 40),
                "color": random.choice([(255, 0, 255), (0, 255, 255), (150, 0, 255)]),
                "time": 0.3,
            }
            self.active_glitches.append(glitch)

    def _summon_nearby(self, enemy: Enemy, count: int = 7, radius: int = 40) -> None:
        from .enemy import Enemy as EnemyClass

        templates = _get_enemy_templates()
        template = templates.get("1")
        if not template:
            return

        for _ in range(count):
            start = pg.Vector2(enemy.pos)
            loop = [
                start,
                start + pg.Vector2(radius, 0).rotate(random.uniform(0, 360)),
                start + pg.Vector2(radius, 0).rotate(random.uniform(0, 360)),
                start + pg.Vector2(radius, 0).rotate(random.uniform(0, 360)),
                start,
            ]

            if enemy.curr_waypoint + 1 < len(enemy.waypoints):
                resume_path = enemy.waypoints[enemy.curr_waypoint + 1 :]
            else:
                resume_path = []

            path = loop + [pg.Vector2(p) for p in resume_path]
            new_enemy = EnemyClass(path, template)
            new_enemy.all_enemies = enemy.all_enemies
            enemy.all_enemies.append(new_enemy)

        enemy.special_texts.append(
            {
                "text": "PHASE SUMMON",
                "pos": enemy.pos.copy(),
                "lifetime": 1.0,
                "color": (200, 100, 255),
            }
        )


class Abilities:
    """Manager for enemy abilities."""

    # Registry of available abilities
    ABILITY_REGISTRY: dict[str, EnemyAbility] = {}

    @classmethod
    def _init_registry(cls) -> None:
        """Initialize the ability registry if empty."""
        if not cls.ABILITY_REGISTRY:
            cls.ABILITY_REGISTRY = {
                "magic_resistant": MagicResistantAbility(),
                "ranged": RangedAbility(),
                "fast": FastAbility(),
                "tank": TankAbility(),
                "summoner1": SummonerAbility(4, "6"),
                "summoner2": SummonerAbility(1, "8", cooldown=5.3),
                "healer": HealerAbility(5),
                "invisible": InvisibleAbility(),
                "inispeed": DashAbility(4.0, 10.0, 10.0),
                "dash": DashAbility(4.0, 1.0, 3.0),
                "boss": BossAbility(),
            }

    def __init__(self) -> None:
        self._init_registry()
        self.abilities: list[EnemyAbility] = []
        self.abilities_dict = self.ABILITY_REGISTRY

    def add_ability(self, ability_name: str) -> None:
        if ability_name in self.abilities_dict:
            # Create a new instance for abilities with state
            ability = self.abilities_dict[ability_name]
            if isinstance(ability, (HealerAbility, SummonerAbility, DashAbility, BossAbility)):
                # Clone stateful abilities by creating new instance
                ability = self._create_ability_instance(ability_name)
            self.abilities.append(ability)

    def _create_ability_instance(self, name: str) -> EnemyAbility:
        if name == "healer":
            return HealerAbility(5)
        elif name == "summoner1":
            return SummonerAbility(4, "6")
        elif name == "summoner2":
            return SummonerAbility(1, "8", 5.3)
        elif name == "dash":
            return DashAbility(4.0, 1.0, 3.0)
        elif name == "inispeed":
            return DashAbility(4.0, 10.0, 10.0)
        elif name == "boss":
            return BossAbility()
        # Default fallback - return existing singleton
        return self.abilities_dict[name]

    def _get_ability_init_args(self, name: str) -> tuple[Any, ...]:
        if name == "healer":
            return (5,)
        elif name == "summoner1":
            return (4, "6")
        elif name == "summoner2":
            return (1, "8", 5.3)
        elif name == "dash":
            return (4.0, 1.0, 3.0)
        elif name == "inispeed":
            return (4.0, 10.0, 10.0)
        return ()

    def remove_ability(self, name: str) -> None:
        self.abilities = [a for a in self.abilities if getattr(a, "name", "") != name]

    def apply_all(self, enemy: Enemy) -> None:
        for ability in self.abilities:
            ability.apply(enemy)

    def update_all(self, enemy: Enemy, dt: float) -> None:
        for ability in self.abilities:
            ability.on_update(enemy, dt)

    def get_ability(self, ability_key: str) -> EnemyAbility | None:
        for ability in self.abilities:
            if ability == self.abilities_dict.get(ability_key):
                return ability
        return None
