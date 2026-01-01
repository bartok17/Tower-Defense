"""
Base entity class for all game objects.
"""

from abc import ABC, abstractmethod

import pygame as pg


class BaseEntity(ABC):
    """Abstract base class for all game entities."""

    def __init__(self, pos: tuple[int, int]) -> None:
        self._pos = pg.Vector2(pos)

    @property
    def pos(self) -> pg.Vector2:
        return self._pos

    @pos.setter
    def pos(self, value: tuple[int, int] | pg.Vector2) -> None:
        self._pos = pg.Vector2(value)

    @property
    def x(self) -> float:
        return self._pos.x

    @property
    def y(self) -> float:
        return self._pos.y

    @abstractmethod
    def update(self, dt: float) -> None:
        pass

    @abstractmethod
    def draw(self, surface: pg.Surface) -> None:
        pass

    def distance_to(self, other: "BaseEntity | pg.Vector2 | tuple[int, int]") -> float:
        if isinstance(other, BaseEntity):
            return self._pos.distance_to(other.pos)
        return self._pos.distance_to(pg.Vector2(other))


class DummyEntity(BaseEntity):
    """A placeholder entity for testing or as a target."""

    def __init__(self, pos: tuple[int, int], health: int = 1000) -> None:
        super().__init__(pos)
        self.health = health
        self.max_health = health
        self._healthbar_length = 40
        self._healthbar_height = 5

    def take_damage(self, amount: int) -> None:
        """Reduce health by damage amount."""
        self.health = max(0, self.health - amount)

    def is_dead(self) -> bool:
        """Check if entity has no health remaining."""
        return self.health <= 0

    def update(self, dt: float) -> None:
        """Update the dummy entity (no-op)."""
        pass

    def draw(self, surface: pg.Surface) -> None:
        """Draw the dummy entity with health bar."""
        # Draw entity circle
        pg.draw.circle(surface, (255, 255, 0), (int(self._pos.x), int(self._pos.y)), 20)

        # Draw health bar background
        bar_x = self._pos.x - 20
        bar_y = self._pos.y - 30
        pg.draw.rect(
            surface, (255, 0, 0), (bar_x, bar_y, self._healthbar_length, self._healthbar_height)
        )

        # Draw health bar fill
        health_ratio = self.health / self.max_health
        pg.draw.rect(
            surface,
            (0, 255, 0),
            (bar_x, bar_y, self._healthbar_length * health_ratio, self._healthbar_height),
        )
