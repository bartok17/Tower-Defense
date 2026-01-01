"""
Main game engine that orchestrates the game loop and screens.

This is the central coordinator that manages screen transitions,
the main loop, and high-level game state.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from ..config import FPS
from ..config.settings import GAME_WIDTH, GAME_HEIGHT
from .event_manager import EventManager

if TYPE_CHECKING:
    from ..ui.screens.base_screen import BaseScreen


class GameContext:
    """Shared context passed to all screens."""

    def __init__(
        self,
        screen: pg.Surface | None = None,
        clock: pg.time.Clock | None = None,
        levels_config: list[dict] | None = None,
        display: pg.Surface | None = None,  # Alias for screen
        scale: float = 1.0,  # Scale factor for mouse coordinate transformation
    ):
        self.display = screen or display
        self.clock = clock or pg.time.Clock()
        self.events = EventManager()
        self.levels_config: list[dict] = levels_config or []
        self.current_level_config: dict | None = None
        self.scale = scale  # Current window scale factor
        self._mouse_pos: tuple[int, int] = (0, 0)  # Transformed mouse position in game coordinates

    @property
    def mouse_pos(self) -> tuple[int, int]:
        """Get the current mouse position in game coordinates (transformed for scaling)."""
        return self._mouse_pos

    @mouse_pos.setter
    def mouse_pos(self, pos: tuple[int, int]) -> None:
        """Set the transformed mouse position."""
        self._mouse_pos = pos

    @property
    def screen_size(self) -> tuple[int, int]:
        """Returns the internal game resolution."""
        return (GAME_WIDTH, GAME_HEIGHT)


class GameEngine:
    """Main game engine managing the game loop and screen stack."""

    def __init__(self, context: GameContext | None = None) -> None:
        if context is None:
            pg.init()

            self._display = pg.display.set_mode(
                (GAME_WIDTH, GAME_HEIGHT), pg.SCALED | pg.RESIZABLE
            )
            pg.display.set_caption("Tower Defense")

            self._clock = pg.time.Clock()
            self.context = GameContext(screen=self._display, clock=self._clock)
        else:
            self._display = context.display
            self._clock = context.clock
            self.context = context

        self._running = True
        self._screen_stack: list[BaseScreen] = []

    @property
    def current_screen(self) -> BaseScreen | None:
        return self._screen_stack[-1] if self._screen_stack else None

    def push_screen(self, screen: BaseScreen) -> None:
        """Push a new screen onto the stack, pausing current."""
        if self._screen_stack:
            self._screen_stack[-1].on_pause()

        self._screen_stack.append(screen)
        screen.on_enter()

    def pop_screen(self) -> BaseScreen | None:
        if not self._screen_stack:
            return None

        screen = self._screen_stack.pop()
        screen.on_exit()

        if self._screen_stack:
            self._screen_stack[-1].on_resume()

        return screen

    def replace_screen(self, screen: BaseScreen) -> None:
        self.pop_screen()
        self.push_screen(screen)

    def clear_screens(self) -> None:
        while self._screen_stack:
            self.pop_screen()

    def request_quit(self) -> None:
        self._running = False

    def is_running(self) -> bool:
        return self._running and bool(self._screen_stack)

    def handle_event(self, event: pg.event.Event) -> None:
        if self.current_screen:
            self.current_screen.handle_event(event)

    def update(self, dt: float) -> None:
        if self.current_screen:
            self.current_screen.update(dt)

    def render(self, surface: pg.Surface) -> None:
        if self.current_screen:
            self.current_screen.render(surface)

    def run(self) -> None:
        self._running = True

        while self._running and self._screen_stack:
            # Calculate delta time
            dt = self._clock.tick(FPS) / 1000.0

            # Process events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self._running = False
                elif self.current_screen:
                    self.current_screen.handle_event(event)

            # Update current screen
            if self.current_screen:
                self.current_screen.update(dt)
                self.current_screen.render(self._display)

            pg.display.flip()

        self.shutdown()

    def shutdown(self) -> None:
        self.clear_screens()
        pg.quit()
