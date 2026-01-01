"""
Base screen abstract class.

All game screens inherit from this to provide consistent interface.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pygame as pg

if TYPE_CHECKING:
    from ...core.game import GameContext


class BaseScreen(ABC):
    """
    Abstract base class for all game screens.

    Provides the interface for handling events, updating, and rendering.
    """

    def __init__(self, context: "GameContext") -> None:
        """
        Initialize the screen.

        Args:
            context: Shared game context.
        """
        self.context = context

    @abstractmethod
    def handle_event(self, event: pg.event.Event) -> None:
        """
        Handle a pygame event.

        Args:
            event: The event to process.
        """
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """
        Update the screen logic.

        Args:
            dt: Delta time in seconds since last update.
        """
        pass

    @abstractmethod
    def render(self, surface: pg.Surface) -> None:
        """
        Render the screen.

        Args:
            surface: Surface to render to.
        """
        pass

    def on_enter(self) -> None:
        """Called when screen becomes active."""
        pass

    def on_exit(self) -> None:
        """Called when screen is being removed."""
        pass

    def on_pause(self) -> None:
        """Called when another screen is pushed on top."""
        pass

    def on_resume(self) -> None:
        """Called when screen becomes active again after being paused."""
        pass
