"""
Event manager for game communication.

This module provides a publish-subscribe (pub/sub) event system for loose coupling
between game components. Systems can emit events without knowing who listens,
and listeners can react to events without direct dependencies on emitters.

Usage:
    # Create event manager
    events = EventManager()

    # Subscribe to events
    def on_enemy_killed(data: EnemyKilledEvent):
        print(f"Enemy killed! +{data.gold_reward} gold")

    events.subscribe(GameEvent.ENEMY_KILLED, on_enemy_killed)

    # Emit events
    events.emit(GameEvent.ENEMY_KILLED, EnemyKilledEvent(enemy=some_enemy, gold_reward=50))

    # Cleanup
    events.unsubscribe(GameEvent.ENEMY_KILLED, on_enemy_killed)
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# Event Data Classes - These define the exact structure of event data
@dataclass
class TowerBuiltEvent:
    """Data for TOWER_BUILT event."""

    tower: Any
    position: tuple[int, int]
    tower_type: str


@dataclass
class TowerUpgradedEvent:
    """Data for TOWER_UPGRADED event."""

    tower: Any
    position: tuple[int, int]
    old_type: str
    new_type: str


@dataclass
class TowerSoldEvent:
    """Data for TOWER_SOLD event."""

    position: tuple[int, int]
    refund_amount: int


@dataclass
class EnemySpawnedEvent:
    """Data for ENEMY_SPAWNED event."""

    enemy: Any


@dataclass
class EnemyKilledEvent:
    """Data for ENEMY_KILLED event."""

    enemy: Any
    gold_reward: int


@dataclass
class EnemyReachedEndEvent:
    """Data for ENEMY_REACHED_END event."""

    enemy: Any
    damage: int


@dataclass
class WaveStartedEvent:
    """Data for WAVE_STARTED event."""

    wave_index: int
    wave_data: dict[str, Any]


@dataclass
class WaveCompletedEvent:
    """Data for WAVE_COMPLETED event."""

    wave_index: int
    rewards: dict[str, int]


@dataclass
class ResourceChangedEvent:
    """Data for RESOURCE_CHANGED event."""

    resource_type: str
    old_value: int
    new_value: int
    change: int


@dataclass
class ResourceInsufficientEvent:
    """Data for RESOURCE_INSUFFICIENT event."""

    resource_type: str
    required: int
    available: int


@dataclass
class GameOverEvent:
    """Data for GAME_OVER event."""

    won: bool


@dataclass
class AbilityUsedEvent:
    """Data for ABILITY_USED event."""

    ability_name: str
    position: tuple[int, int]
    cost: dict[str, int]


@dataclass
class AbilityReadyEvent:
    """Data for ABILITY_READY event."""

    ability_name: str


@dataclass
class FactoryBuiltEvent:
    """Data for FACTORY_BUILT event."""

    factory: Any
    position: tuple[int, int]
    resource_type: str | None


@dataclass
class FactoryProducedEvent:
    """Data for FACTORY_PRODUCED event."""

    factory: Any
    resource_type: str
    amount: int


class GameEvent(Enum):
    """All game events that can be emitted and subscribed to."""

    # Tower events
    TOWER_BUILT = auto()
    TOWER_UPGRADED = auto()
    TOWER_SOLD = auto()

    # Enemy events
    ENEMY_SPAWNED = auto()
    ENEMY_KILLED = auto()
    ENEMY_REACHED_END = auto()

    # Wave events
    WAVE_STARTED = auto()
    WAVE_COMPLETED = auto()
    ALL_WAVES_COMPLETED = auto()

    # Resource events
    RESOURCE_CHANGED = auto()
    RESOURCE_INSUFFICIENT = auto()

    # Game flow events
    GAME_PAUSED = auto()
    GAME_RESUMED = auto()
    GAME_OVER = auto()
    GAME_WON = auto()

    # Ability events
    ABILITY_USED = auto()
    ABILITY_READY = auto()

    # Factory events
    FACTORY_BUILT = auto()
    FACTORY_PRODUCED = auto()


# Type alias for event callbacks - now receives a dataclass
EventCallback = Callable[[Any], None]


class EventManager:
    """
    Central event bus for game-wide pub/sub communication.
    """

    def __init__(self) -> None:
        self._listeners: dict[GameEvent, list[EventCallback]] = defaultdict(list)

    def subscribe(self, event: GameEvent, callback: EventCallback) -> None:
        """
        Subscribe a callback to an event.
        """
        if callback not in self._listeners[event]:
            self._listeners[event].append(callback)

    def unsubscribe(self, event: GameEvent, callback: EventCallback) -> None:
        """
        Unsubscribe a callback from an event.
        """
        if callback in self._listeners[event]:
            self._listeners[event].remove(callback)

    def emit(self, event: GameEvent, data: Any) -> None:
        """
        Emit an event to all subscribers.

        Args:
            event: The event type to emit
            data: Event data (should be an appropriate event dataclass)
        """
        for callback in self._listeners[event]:
            try:
                callback(data)
            except Exception as e:
                print(f"Error in event handler for {event}: {e}")

    def clear(self) -> None:
        """Remove all event subscriptions."""
        self._listeners.clear()

    def clear_event(self, event: GameEvent) -> None:
        """Remove all subscriptions for a specific event."""
        self._listeners[event].clear()

    def subscriber_count(self, event: GameEvent) -> int:
        """Get the number of subscribers for an event."""
        return len(self._listeners[event])
