"""Core game engine module."""

from .event_manager import (
    AbilityReadyEvent,
    AbilityUsedEvent,
    EnemyKilledEvent,
    EnemyReachedEndEvent,
    EnemySpawnedEvent,
    EventManager,
    FactoryBuiltEvent,
    FactoryProducedEvent,
    GameEvent,
    GameOverEvent,
    ResourceChangedEvent,
    ResourceInsufficientEvent,
    TowerBuiltEvent,
    TowerSoldEvent,
    TowerUpgradedEvent,
    WaveCompletedEvent,
    WaveStartedEvent,
)
from .game import GameContext, GameEngine
from .game_state import GameState
from .game_world import GamePhase, GameWorld, GameWorldConfig, WaveRewards

__all__ = [
    "GameState",
    "EventManager",
    "GameEvent",
    "GameEngine",
    "GameContext",
    # Game world
    "GameWorld",
    "GameWorldConfig",
    "GamePhase",
    "WaveRewards",
    # Event data classes
    "TowerBuiltEvent",
    "TowerUpgradedEvent",
    "TowerSoldEvent",
    "EnemySpawnedEvent",
    "EnemyKilledEvent",
    "EnemyReachedEndEvent",
    "WaveStartedEvent",
    "WaveCompletedEvent",
    "ResourceChangedEvent",
    "ResourceInsufficientEvent",
    "GameOverEvent",
    "AbilityUsedEvent",
    "AbilityReadyEvent",
    "FactoryBuiltEvent",
    "FactoryProducedEvent",
]
