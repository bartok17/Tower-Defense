"""
Factory entity.
"""

from __future__ import annotations

import pygame as pg

from .base_entity import BaseEntity


class Factory(BaseEntity):
    """
    A resource-producing factory building.

    Produces a set amount of a specific resource at the end of each wave.
    """

    def __init__(
        self,
        pos: tuple[int, int],
        resource_type: str,
        production_rate: int,
        image: pg.Surface | None = None,
    ) -> None:
        """Create a factory that produces resources at end of wave."""
        super().__init__(pos)

        self.resource_type = resource_type
        self.production_rate = production_rate

        # Visual
        if image is not None:
            self.image = image
        else:
            self.image = pg.Surface((40, 40))
            self.image.fill((100, 100, 100))

        self._width = self.image.get_width()
        self._height = self.image.get_height()

    @property
    def rect(self) -> pg.Rect:
        """Get the factory's bounding rectangle."""
        return pg.Rect(self._pos.x, self._pos.y, self._width, self._height)

    def get_wave_payout(self) -> tuple[str, int]:
        """Get (resource_type, amount) for end of wave."""
        return self.resource_type, self.production_rate

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pg.Surface) -> None:
        """Draw the factory."""
        x, y = int(self._pos.x), int(self._pos.y)

        # Draw image
        surface.blit(self.image, (x, y))

        # Draw border
        pg.draw.rect(
            surface, (255, 255, 255), (x, y, self._width, self._height), width=2, border_radius=4
        )
