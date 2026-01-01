"""
Level selection screen.

Allows players to choose which level to play.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from ...config import GAME_HEIGHT, GAME_WIDTH
from ..components.button import Button
from .base_screen import BaseScreen

if TYPE_CHECKING:
    from ...core.game import GameContext, GameEngine


class LevelSelectScreen(BaseScreen):
    """
    Screen for selecting which level to play.
    """

    def __init__(self, context: GameContext, engine: GameEngine) -> None:
        super().__init__(context)
        self.engine = engine

        # Fonts
        self.title_font = pg.font.Font(None, 60)

        # Title
        self.title_text = self.title_font.render("Select Level", True, (200, 200, 200))
        self.title_rect = self.title_text.get_rect(center=(GAME_WIDTH // 2, 70))

        # Create level buttons
        self._create_level_buttons()

        # Back button
        self.back_button = Button(
            50,
            GAME_HEIGHT - 70,
            None,
            text="Back",
            text_color=(255, 255, 255),
            font_size=30,
            width=100,
            height=40,
            color=(150, 150, 0),
        )

    def _create_level_buttons(self) -> None:
        """Create buttons for each level."""
        self.level_buttons: list[dict] = []

        button_height = 50
        button_spacing = 20
        start_y = 150

        for i, level_config in enumerate(self.context.levels_config):
            if level_config["unlocked"]:
                text = level_config["name"]
                color = (0, 150, 150)
            else:
                text = f"{level_config['name']} (Locked)"
                color = (100, 100, 100)

            button = Button(
                GAME_WIDTH // 2 - 200,
                start_y + i * (button_height + button_spacing),
                None,
                text=text,
                text_color=(255, 255, 255),
                font_size=30,
                width=400,
                height=button_height,
                color=color,
            )

            self.level_buttons.append(
                {"button": button, "config": level_config, "unlocked": level_config["unlocked"]}
            )

    def handle_event(self, event: pg.event.Event) -> None:
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos

            # Check back button
            if self.back_button.is_clicked(mouse_pos):
                from .main_menu import MainMenuScreen

                self.engine.replace_screen(MainMenuScreen(self.context, self.engine))
                return

            # Check level buttons
            for item in self.level_buttons:
                if item["unlocked"] and item["button"].is_clicked(mouse_pos):
                    self.context.current_level_config = item["config"]
                    from .game_screen import GameScreen

                    self.engine.replace_screen(GameScreen(self.context, self.engine))
                    return

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pg.Surface) -> None:
        surface.fill((40, 40, 40))
        surface.blit(self.title_text, self.title_rect)

        for item in self.level_buttons:
            item["button"].draw(surface)

        self.back_button.draw(surface)

    def refresh_buttons(self) -> None:
        """Refresh buttons when levels may have been unlocked."""
        self._create_level_buttons()
