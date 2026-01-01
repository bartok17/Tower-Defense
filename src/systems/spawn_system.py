"""
Spawn system - Wave loading and enemy spawning.

Handles loading wave data and spawning enemies.
"""

from __future__ import annotations

import json
from random import choice, uniform
from typing import TYPE_CHECKING

from ..core.event_manager import EnemySpawnedEvent, EventManager, GameEvent, WaveStartedEvent
from ..entities import Enemy
from ..utils.path_utils import generate_offset_path

if TYPE_CHECKING:
    pass


DEFAULT_INTER_ENEMY_SPAWN_DELAY_MS: int = 500


class WaveLoader:
    """Loads and parses wave data from JSON files."""

    @staticmethod
    def load_enemy_templates(template_path: str) -> dict:
        with open(template_path) as f:
            data: dict = json.load(f)
            return data

    @staticmethod
    def load_waves_file(waves_path: str) -> dict:
        with open(waves_path) as f:
            data: dict = json.load(f)
            return data

    @classmethod
    def load_all_waves(
        cls, waves_path: str, template_path: str, waypoints: dict[str, list[tuple[int, int]]]
    ) -> list[dict]:
        """Load and process all waves for a level."""
        templates = cls.load_enemy_templates(template_path)
        waves_data = cls.load_waves_file(waves_path)

        processed_waves = []

        # Sort wave IDs numerically
        if isinstance(waves_data, dict):
            try:
                sorted_ids = sorted(waves_data.keys(), key=int)
            except ValueError:
                print("Warning: Could not sort wave IDs numerically")
                sorted_ids = list(waves_data.keys())
        else:
            print(f"Warning: Expected dict of waves, got {type(waves_data)}")
            return []

        for wave_id in sorted_ids:
            wave_content = waves_data[wave_id]
            processed_wave = cls._process_wave(wave_id, wave_content, templates, waypoints)
            processed_waves.append(processed_wave)

        return processed_waves

    @classmethod
    def _process_wave(
        cls,
        wave_id: str,
        wave_content: dict,
        templates: dict,
        waypoints: dict[str, list[tuple[int, int]]],
    ) -> dict:
        """Process a single wave definition."""
        p_time = wave_content.get("P_time", 10)
        mode = wave_content.get("mode", 0)
        passive_gold = wave_content.get("passive_gold", 0)
        passive_wood = wave_content.get("passive_wood", 0)
        passive_metal = wave_content.get("passive_metal", 0)
        unit_definitions = wave_content.get("units", [])

        enemy_groups = []

        for unit_entry in unit_definitions:
            group = cls._process_unit_entry(unit_entry, wave_id, templates, waypoints)
            if group:
                enemy_groups.append(group)

        return {
            "P_time": p_time,
            "mode": mode,
            "enemy_groups": enemy_groups,
            "passive_gold": passive_gold,
            "passive_wood": passive_wood,
            "passive_metal": passive_metal,
        }

    @classmethod
    def _process_unit_entry(
        cls,
        unit_entry: list,
        wave_id: str,
        templates: dict,
        waypoints: dict[str, list[tuple[int, int]]],
    ) -> dict | None:
        """Process a single unit entry in a wave."""
        # Parse unit entry format: [enemy_id, count, delay, spawn_delay]
        enemy_id, count, delay_after = -1, 0, 0.0
        inter_spawn_delay = DEFAULT_INTER_ENEMY_SPAWN_DELAY_MS

        if not isinstance(unit_entry, list):
            print(f"Warning: Unit entry is not a list in wave {wave_id}")
            return None

        if len(unit_entry) == 4:
            enemy_id, count, delay_after, inter_spawn_delay = unit_entry
        elif len(unit_entry) == 3:
            enemy_id, count, delay_after = unit_entry
        elif len(unit_entry) == 2:
            enemy_id, count = unit_entry
        else:
            print(f"Warning: Malformed unit entry in wave {wave_id}: {unit_entry}")
            return None

        # Get template
        str_id = str(enemy_id)
        if str_id not in templates:
            print(f"Warning: Enemy template ID '{enemy_id}' not found")
            return None

        template = dict(templates[str_id])
        template["id"] = enemy_id

        # Create enemies
        enemies = []
        for _ in range(count):
            # Random path and offset
            chosen_path = choice(list(waypoints.keys()))
            original_path = waypoints[chosen_path]
            offset = uniform(-25.0, 25.0)
            offset_path = generate_offset_path(original_path, offset)

            enemy = Enemy(offset_path, template)
            enemies.append(enemy)

        if not enemies:
            return None

        return {
            "enemies_to_spawn": enemies,
            "delay_after_group": delay_after,
            "inter_enemy_spawn_delay_ms": inter_spawn_delay,
        }


class SpawnController:
    """
    Controls enemy spawning during waves.
    """

    def __init__(self, events: EventManager | None = None) -> None:
        self.current_wave_data: dict | None = None
        self.current_group_idx: int = 0
        self.spawn_idx_in_group: int = 0
        self.inter_group_delay_timer: float = 0.0
        self.time_since_last_spawn: float = 0.0
        self.wave_prep_timer: float = 0.0
        self.events = events
        self._current_wave_index: int = 0

    def start_wave(self, wave_data: dict, wave_index: int = 0) -> None:
        """Start spawning a new wave."""
        self.current_wave_data = wave_data
        self.wave_prep_timer = wave_data.get("P_time", 0) * 1000
        self.current_group_idx = 0
        self.spawn_idx_in_group = 0
        self.inter_group_delay_timer = 0.0
        self.time_since_last_spawn = 0.0
        self._current_wave_index = wave_index

        # Emit wave started event
        if self.events:
            self.events.emit(
                GameEvent.WAVE_STARTED,
                WaveStartedEvent(
                    wave_index=wave_index,
                    wave_data=wave_data,
                ),
            )

    def reset(self) -> None:
        """Reset spawn state."""
        self.current_wave_data = None
        self.current_group_idx = 0
        self.spawn_idx_in_group = 0
        self.inter_group_delay_timer = 0.0
        self.time_since_last_spawn = 0.0
        self.wave_prep_timer = 0.0

    def update(self, dt: float, enemies_list: list[Enemy]) -> bool:
        """Update spawning. Returns True if wave complete (all spawned and defeated)."""
        if self.current_wave_data is None:
            return True

        # Handle preparation time
        if self.wave_prep_timer > 0:
            self.wave_prep_timer -= dt
            return False

        # Handle inter-group delay
        if self.inter_group_delay_timer > 0:
            self.inter_group_delay_timer -= dt
            if self.inter_group_delay_timer < 0:
                self.inter_group_delay_timer = 0
            return False

        # Spawn enemies
        enemy_groups = self.current_wave_data.get("enemy_groups", [])

        if self.current_group_idx < len(enemy_groups):
            group = enemy_groups[self.current_group_idx]
            enemies_to_spawn = group["enemies_to_spawn"]
            spawn_delay = group.get(
                "inter_enemy_spawn_delay_ms", DEFAULT_INTER_ENEMY_SPAWN_DELAY_MS
            )

            if self.spawn_idx_in_group < len(enemies_to_spawn):
                self.time_since_last_spawn += dt

                if self.time_since_last_spawn >= spawn_delay:
                    # Spawn next enemy
                    enemy = enemies_to_spawn[self.spawn_idx_in_group]
                    enemy.all_enemies = enemies_list
                    enemy.enemies_ref = enemies_list
                    enemies_list.append(enemy)

                    # Emit enemy spawned event
                    if self.events:
                        self.events.emit(
                            GameEvent.ENEMY_SPAWNED,
                            EnemySpawnedEvent(enemy=enemy),
                        )

                    self.spawn_idx_in_group += 1
                    self.time_since_last_spawn = 0
            else:
                # Group complete, move to next
                self.current_group_idx += 1
                self.spawn_idx_in_group = 0
                self.inter_group_delay_timer = group["delay_after_group"] * 1000.0

        # Check if wave is complete
        all_spawned = self.current_group_idx >= len(enemy_groups)
        all_dead = len(enemies_list) == 0

        return all_spawned and all_dead

    @property
    def is_spawning(self) -> bool:
        """Check if still spawning enemies."""
        if self.current_wave_data is None:
            return False

        enemy_groups = self.current_wave_data.get("enemy_groups", [])
        return self.current_group_idx < len(enemy_groups)
