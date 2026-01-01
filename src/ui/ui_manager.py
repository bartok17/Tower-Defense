"""
UI Manager - Coordinates all UI elements.

Handles the build panel, HUD, and other UI components.
"""

from __future__ import annotations

import pygame as pg

from ..config.settings import GAME_HEIGHT
from ..config.paths import ICON_PATHS
from .components.button import Button
from .components.hud import IconHUD


class UIManager:
    """Manages all in-game UI elements (HUD, build panel, abilities)."""

    def __init__(self, font: str | None = None) -> None:
        self.font = pg.font.Font(font, 36)
        self.small_font = pg.font.Font(font, 24)

        self.hud = IconHUD(ICON_PATHS, font=font)

        # Build panel state
        self.build_panel_open = False
        self.ability_buttons: list[Button] = []

        # Toggle button for build panel
        self.toggle_button = Button(
            x=0,
            y=0,
            image=None,
            text="<",
            font_size=24,
            text_color=(255, 255, 255),
            width=30,
            height=30,
            color=(50, 50, 50),
        )

        # Pause button
        self.pause_button = Button(
            x=10,
            y=GAME_HEIGHT - 50,
            image=None,
            text="II",
            font_size=22,
            text_color=(0, 0, 0),
            width=30,
            height=30,
            color=(255, 255, 0),
        )

    def draw_resources(
        self,
        screen: pg.Surface,
        resources: dict[str, int],
        wave_index: int | None = None,
        total_waves: int | None = None,
    ) -> None:
        values: dict[str, int | str] = dict(resources)
        if wave_index is not None and total_waves is not None:
            values["wave"] = f"{wave_index + 1}/{total_waves}"

        self.hud.draw_hud(screen, values)

    def draw_build_panel(
        self, screen: pg.Surface, factory_buttons: list[Button], tower_buttons: list[Button],
        mouse_pos: tuple[int, int] | None = None
    ) -> None:
        screen_width = screen.get_width()
        panel_width = 180
        base_panel_x = screen_width - panel_width

        # Slide offset
        slide_offset = 0 if self.build_panel_open else panel_width
        actual_panel_x = base_panel_x + slide_offset

        # Draw panel background
        panel_rect = pg.Rect(actual_panel_x, 0, panel_width, screen.get_height())
        panel_surface = pg.Surface((panel_rect.width, panel_rect.height), pg.SRCALPHA)
        panel_surface.fill((30, 30, 30, 180))
        screen.blit(panel_surface, panel_rect.topleft)

        # Draw button grid if open
        if self.build_panel_open:
            self.hud.draw_button_grid(
                screen,
                {"factories": factory_buttons, "towers": tower_buttons},
                base_x=actual_panel_x + 10,
                mouse_pos=mouse_pos,
            )

            # Draw ability grid
            if self.ability_buttons:
                self.draw_ability_grid(screen, actual_panel_x + 10, screen.get_height() - 120, mouse_pos=mouse_pos)

        # Draw toggle button
        self.toggle_button.draw(screen, mouse_pos=mouse_pos)

    def draw_ability_grid(
        self,
        screen: pg.Surface,
        base_x: int,
        base_y: int,
        button_size: tuple[int, int] = (80, 40),
        spacing: int = 10,
        cols: int = 2,
        mouse_pos: tuple[int, int] | None = None,
    ) -> None:
        for i, btn in enumerate(self.ability_buttons):
            col = i % cols
            row = i // cols
            x = base_x + col * (button_size[0] + spacing)
            y = base_y + row * (button_size[1] + spacing)
            btn.rect.topleft = (x, y)
            btn.draw(screen, mouse_pos=mouse_pos)

    def handle_panel_toggle(
        self, event: pg.event.Event, screen_width: int, screen_height: int
    ) -> None:
        # Position toggle button
        btn_x = screen_width - 30
        btn_y = screen_height // 2 - 15
        self.toggle_button.rect.topleft = (btn_x, btn_y)

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.toggle_button.is_clicked(event.pos):
                self.build_panel_open = not self.build_panel_open
                self.toggle_button.text = ">" if self.build_panel_open else "<"

    def draw_pause_button(self, screen: pg.Surface, mouse_pos: tuple[int, int] | None = None) -> None:
        self.pause_button.draw(screen)

        if mouse_pos and self.pause_button.rect.collidepoint(mouse_pos):
            tip = self.small_font.render("Pause (Esc)", True, (255, 255, 255))
            screen.blit(
                tip,
                (
                    self.pause_button.rect.right + 8,
                    self.pause_button.rect.centery - tip.get_height() // 2,
                ),
            )

    def is_pause_button_clicked(self, mouse_pos: tuple[int, int]) -> bool:
        return self.pause_button.is_clicked(mouse_pos)

    def get_clicked_ability(self, mouse_pos: tuple[int, int]) -> str | None:
        for btn in self.ability_buttons:
            if btn.is_clicked(mouse_pos):
                return btn.text.lower()
        return None
