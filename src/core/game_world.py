"""
Game World - Pure game state and logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

import pygame as pg

from ..config.paths import DATA_DIR
from ..entities import Enemy, Projectile
from ..systems import (
    BuildingBlueprint,
    BuildManager,
    PlayerAbilities,
    ResourcesManager,
    SpawnController,
    WaveLoader,
)
from ..utils.waypoint_loader import load_waypoints
from .event_manager import (
    EnemyKilledEvent,
    EnemyReachedEndEvent,
    EventManager,
    GameEvent,
    GameOverEvent,
    WaveCompletedEvent,
)

if TYPE_CHECKING:
    from ..entities import Factory, Tower


class GamePhase(Enum):
    """Current phase of gameplay."""

    BUILD = auto()
    WAVE = auto()
    VICTORY = auto()
    DEFEAT = auto()


@dataclass
class GameWorldConfig:
    """Configuration for initializing a game world."""

    level_config: dict[str, Any]
    events: EventManager | None = None


@dataclass
class WaveRewards:
    """Rewards given at end of a wave."""

    gold: int = 0
    wood: int = 0
    metal: int = 0


class GameWorld:
    """Pure game state and logic."""

    def __init__(self, config: GameWorldConfig) -> None:
        self.level_config = config.level_config
        self.events = config.events or EventManager()

        # Systems
        self.build_manager = BuildManager(events=self.events)
        self.spawn_controller = SpawnController(events=self.events)
        self.resources = ResourcesManager(
            initial_gold=self.level_config.get("start_gold", 100),
            initial_wood=self.level_config.get("start_wood", 50),
            initial_metal=self.level_config.get("start_metal", 25),
            initial_health=100,
            events=self.events,
        )

        # Player abilities
        self.player_abilities = PlayerAbilities()
        self.abilities_enabled = self.level_config.get("are_abilities_enabled", True)

        self._load_level_data()

        # Entities
        self.enemies: list[Enemy] = []
        self.projectiles: list[Projectile] = []

        # State
        self.phase = GamePhase.BUILD
        self.current_wave: int = 0
        self.game_speed: float = 1.0

    def _load_level_data(self) -> None:
        """Load waypoints and waves."""
        waypoints_path = DATA_DIR / self.level_config["waypoints_path"]
        self.waypoints = load_waypoints(str(waypoints_path))
        self.road_segments = BuildManager.generate_road_segments(self.waypoints)

        waves_path = DATA_DIR / self.level_config["waves_path"]
        templates_path = DATA_DIR / "enemyTemplates.json"
        self.waves_data = WaveLoader.load_all_waves(
            str(waves_path), str(templates_path), self.waypoints
        )

    @property
    def total_waves(self) -> int:
        return len(self.waves_data)

    @property
    def is_wave_active(self) -> bool:
        return self.phase == GamePhase.WAVE

    @property
    def is_game_over(self) -> bool:
        return self.phase in (GamePhase.VICTORY, GamePhase.DEFEAT)

    @property
    def towers(self) -> list[Tower]:
        return self.build_manager.towers

    @property
    def factories(self) -> list[Factory]:
        return self.build_manager.factories

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------

    def start_wave(self) -> bool:
        """Start the next wave."""
        if self.phase != GamePhase.BUILD:
            return False
        if self.current_wave >= len(self.waves_data):
            return False

        wave_data = self.waves_data[self.current_wave]
        self.spawn_controller.start_wave(wave_data, wave_index=self.current_wave)
        self.phase = GamePhase.WAVE
        return True

    def try_build(self, position: tuple[int, int], blueprint: BuildingBlueprint) -> bool:
        """Attempt to build at position."""
        adjusted = (position[0] - blueprint.width // 2, position[1] - blueprint.height // 2)

        if blueprint.name == "Tower Upgrade":
            return self.build_manager.upgrade_tower(position, blueprint, self.resources)

        if not self.build_manager.can_build_at(
            adjusted, blueprint, self.resources, self.road_segments
        ):
            return False

        if blueprint.build_function:
            return blueprint.build_function(adjusted, blueprint, self.resources)
        return False

    def use_ability(self, ability_name: str, target_pos: tuple[int, int]) -> bool:
        """Use a player ability at target position."""
        if not self.abilities_enabled:
            return False

        if not self.player_abilities.can_use(ability_name, self.resources):
            return False

        return self.player_abilities.use(ability_name, self.resources, target_pos, self.enemies)

    def set_game_speed(self, speed: float) -> None:
        """Set game speed multiplier (0.25 - 4.0)."""
        self.game_speed = max(0.25, min(4.0, speed))

    # -------------------------------------------------------------------------
    # Update
    # -------------------------------------------------------------------------

    def update(self, dt: float) -> None:
        """Update all game systems."""
        if self.is_game_over:
            return

        game_dt = dt * 1000 * self.game_speed

        if self.phase == GamePhase.WAVE:
            wave_complete = self.spawn_controller.update(game_dt, self.enemies)
            if wave_complete:
                self._on_wave_complete()

        self._update_enemies(game_dt)
        self._update_towers(game_dt)
        self._update_projectiles(game_dt)

        if self.abilities_enabled:
            self.player_abilities.update(game_dt, self.enemies)

        if self.resources.is_dead():
            self._on_defeat()

    def _update_enemies(self, game_dt: float) -> None:
        for enemy in self.enemies[:]:
            enemy.all_enemies = self.enemies
            enemy.update(game_dt)

            if enemy.is_dead():
                self._on_enemy_killed(enemy)
            elif enemy.has_finished():
                self._on_enemy_reached_end(enemy)

    def _update_towers(self, dt: float) -> None:
        for tower in self.build_manager.towers:
            tower.update(dt)
            tower.attack(self.enemies, self.projectiles)

    def _update_projectiles(self, game_dt: float) -> None:
        for proj in self.projectiles[:]:
            proj.update(game_dt, self.enemies)
            if not proj.active:
                if hasattr(proj, "on_removed"):
                    proj.on_removed()
                self.projectiles.remove(proj)

    # -------------------------------------------------------------------------
    # Event Handlers
    # -------------------------------------------------------------------------

    def _on_enemy_killed(self, enemy: Enemy) -> None:
        gold_reward = enemy.gold_reward
        self.enemies.remove(enemy)
        self.resources.add_resource("gold", gold_reward)

        self.events.emit(
            GameEvent.ENEMY_KILLED,
            EnemyKilledEvent(enemy=enemy, gold_reward=gold_reward),
        )

    def _on_enemy_reached_end(self, enemy: Enemy) -> None:
        damage = enemy.damage
        self.resources.spend_resource("health", damage)
        self.resources.add_resource("gold", enemy.gold_reward)
        self.enemies.remove(enemy)

        self.events.emit(
            GameEvent.ENEMY_REACHED_END,
            EnemyReachedEndEvent(enemy=enemy, damage=damage),
        )

    def _on_wave_complete(self) -> None:
        wave_data = self.waves_data[self.current_wave]

        rewards = WaveRewards(
            gold=wave_data.get("passive_gold", 0),
            wood=wave_data.get("passive_wood", 0),
            metal=wave_data.get("passive_metal", 0),
        )

        self.resources.add_resource("gold", rewards.gold)
        self.resources.add_resource("wood", rewards.wood)
        self.resources.add_resource("metal", rewards.metal)
        self.build_manager.give_factory_payouts(self.resources)

        self.events.emit(
            GameEvent.WAVE_COMPLETED,
            WaveCompletedEvent(
                wave_index=self.current_wave,
                rewards={"gold": rewards.gold, "wood": rewards.wood, "metal": rewards.metal},
            ),
        )

        self.current_wave += 1
        self.phase = GamePhase.BUILD

        if self.current_wave >= len(self.waves_data):
            self._on_victory()

    def _on_victory(self) -> None:
        self.phase = GamePhase.VICTORY
        self.events.emit(GameEvent.ALL_WAVES_COMPLETED, None)
        self.events.emit(GameEvent.GAME_OVER, GameOverEvent(won=True))
        self.events.emit(GameEvent.GAME_WON, None)

    def _on_defeat(self) -> None:
        self.phase = GamePhase.DEFEAT
        self.events.emit(GameEvent.GAME_OVER, GameOverEvent(won=False))
