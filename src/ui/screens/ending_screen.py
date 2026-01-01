"""
Ending screen - Victory or Game Over.

Shown after a level ends with options to continue.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from ...config import GAME_HEIGHT, GAME_WIDTH
from ..components.button import Button
from .base_screen import BaseScreen

if TYPE_CHECKING:
    from ...core.game import GameContext, GameEngine


class EndingScreen(BaseScreen):
    """
    Screen shown after level completion (win or lose).
    """

    def __init__(
        self,
        context: GameContext,
        engine: GameEngine,
        game_won: bool = False,
        next_level_available: bool = False,
    ) -> None:
        super().__init__(context)
        self.engine = engine
        self.game_won = game_won
        self.next_level_available = next_level_available

        self.font = pg.font.Font(None, 74)

        # Create buttons
        self._create_buttons()

    def _create_buttons(self) -> None:
        """Create buttons based on game state."""
        button_width = 220
        button_height = 50
        button_spacing = 20

        num_buttons = 3 if (self.game_won and self.next_level_available) else 2
        total_height = num_buttons * button_height + (num_buttons - 1) * button_spacing
        button_y_start = (GAME_HEIGHT // 2) - (total_height // 2) + 70

        current_y = button_y_start

        # Next level button (if won and available)
        self.next_level_button = None
        if self.game_won and self.next_level_available:
            self.next_level_button = Button(
                GAME_WIDTH // 2 - button_width // 2,
                current_y,
                None,
                text="Next Level",
                text_color=(255, 255, 255),
                font_size=30,
                width=button_width,
                height=button_height,
                color=(0, 150, 50),
            )
            current_y += button_height + button_spacing

        # Replay/Try again button
        play_text = "Replay Level" if self.game_won else "Try Again"
        self.play_again_button = Button(
            GAME_WIDTH // 2 - button_width // 2,
            current_y,
            None,
            text=play_text,
            text_color=(255, 255, 255),
            font_size=30,
            width=button_width,
            height=button_height,
            color=(0, 100, 150),
        )
        current_y += button_height + button_spacing

        # Main menu button
        self.main_menu_button = Button(
            GAME_WIDTH // 2 - button_width // 2,
            current_y,
            None,
            text="Level Select",
            text_color=(255, 255, 255),
            font_size=30,
            width=button_width,
            height=button_height,
            color=(150, 100, 0),
        )

    def handle_event(self, event: pg.event.Event) -> None:
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos

            if self.next_level_button and self.next_level_button.is_clicked(mouse_pos):
                self._go_to_next_level()

            elif self.play_again_button.is_clicked(mouse_pos):
                self._replay_level()

            elif self.main_menu_button.is_clicked(mouse_pos):
                self._go_to_level_select()

    def _go_to_next_level(self) -> None:
        """Navigate to next level."""
        levels = self.context.levels_config
        current_config = self.context.current_level_config

        if current_config is None:
            self._go_to_level_select()
            return

        # Find current level index
        current_idx = -1
        for i, lc in enumerate(levels):
            if lc["id"] == current_config["id"]:
                current_idx = i
                break

        if current_idx != -1 and current_idx + 1 < len(levels):
            self.context.current_level_config = levels[current_idx + 1]
            from .game_screen import GameScreen

            self.engine.replace_screen(GameScreen(self.context, self.engine))
        else:
            self._go_to_level_select()

    def _replay_level(self) -> None:
        """Replay the current level."""
        from .game_screen import GameScreen

        self.engine.replace_screen(GameScreen(self.context, self.engine))

    def _go_to_level_select(self) -> None:
        """Return to level select screen."""
        from .level_select import LevelSelectScreen

        self.engine.replace_screen(LevelSelectScreen(self.context, self.engine))

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pg.Surface) -> None:
        surface.fill((30, 30, 30))

        # Title
        if self.game_won:
            title = self.font.render("Victory!", True, (0, 255, 0))
        else:
            title = self.font.render("Game Over", True, (255, 0, 0))

        title_rect = title.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 - 100))
        surface.blit(title, title_rect)

        # Buttons
        if self.next_level_button:
            self.next_level_button.draw(surface)
        self.play_again_button.draw(surface)
        self.main_menu_button.draw(surface)
