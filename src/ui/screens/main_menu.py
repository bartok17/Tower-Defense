"""
Main menu screen.

The first screen players see with Start Game and Quit options.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from ...config import GAME_HEIGHT, GAME_WIDTH
from ..components.button import Button
from .base_screen import BaseScreen

if TYPE_CHECKING:
    from ...core.game import GameContext, GameEngine


class MainMenuScreen(BaseScreen):
    """
    Main menu screen with title and navigation buttons.
    """

    def __init__(self, context: GameContext, engine: GameEngine) -> None:
        super().__init__(context)
        self.engine = engine

        # Fonts
        self.title_font = pg.font.Font(None, 74)
        self.button_font = pg.font.Font(None, 50)

        # Title
        self.title_text = self.title_font.render("Tower Defense Game", True, (200, 200, 200))
        self.title_rect = self.title_text.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 4))

        # Buttons
        self.start_button = Button(
            GAME_WIDTH // 2 - 150,
            GAME_HEIGHT // 2 - 50,
            None,
            text="Start Game",
            text_color=(255, 255, 255),
            font_size=40,
            width=300,
            height=60,
            color=(0, 180, 0),
        )
        self.quit_button = Button(
            GAME_WIDTH // 2 - 150,
            GAME_HEIGHT // 2 + 40,
            None,
            text="Quit",
            text_color=(255, 255, 255),
            font_size=40,
            width=300,
            height=60,
            color=(180, 0, 0),
        )

    def handle_event(self, event: pg.event.Event) -> None:
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos

            if self.start_button.is_clicked(mouse_pos):
                from .level_select import LevelSelectScreen

                self.engine.replace_screen(LevelSelectScreen(self.context, self.engine))

            elif self.quit_button.is_clicked(mouse_pos):
                self.engine.request_quit()

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pg.Surface) -> None:
        surface.fill((30, 30, 30))
        surface.blit(self.title_text, self.title_rect)
        self.start_button.draw(surface)
        self.quit_button.draw(surface)
