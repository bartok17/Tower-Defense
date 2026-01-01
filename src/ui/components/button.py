"""
Button UI component.

Reusable button for menus and gameplay.
"""

from __future__ import annotations

import pygame as pg


class Button:
    """A clickable UI button with image or text."""

    def __init__(
        self,
        x: int,
        y: int,
        image: pg.Surface | None,
        label: str | None = None,
        text: str = "",
        text_color: tuple[int, int, int] = (0, 0, 0),
        font_size: int = 24,
        font_name: str | None = None,
        width: int | None = None,
        height: int | None = None,
        color: tuple[int, int, int] = (200, 200, 200),
        click_and_hold: bool = False,
    ) -> None:
        self.x = x
        self.y = y
        self.click_and_hold = click_and_hold
        self.clicked = False
        self.hover_progress = 0.0
        self.hover_speed = 0.1
        self.label = label
        self.text = text

        # Create button surface
        if image:
            self.image = image
            if width is not None and height is not None:
                self.image = pg.transform.scale(self.image, (width, height))
        else:
            # Create text button
            if width is None or height is None:
                if text:
                    if not pg.font.get_init():
                        pg.font.init()
                    temp_font = pg.font.Font(font_name, font_size)
                    text_render = temp_font.render(text, True, text_color)
                    if width is None:
                        width = text_render.get_width() + 20
                    if height is None:
                        height = text_render.get_height() + 10
                else:
                    raise ValueError("Button without image needs width/height or text")

            self.image = pg.Surface((width, height))
            self.image.fill(color)

            if text:
                if not pg.font.get_init():
                    pg.font.init()
                font = pg.font.Font(font_name, font_size)
                text_surface = font.render(text, True, text_color)
                text_rect = text_surface.get_rect(center=(width // 2, height // 2))
                self.image.blit(text_surface, text_rect)

        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self, surface: pg.Surface, mouse_pos: tuple[int, int] | None = None) -> bool:
        """Draw button and return True if clicked this frame."""
        action = False
        pos = mouse_pos if mouse_pos is not None else pg.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pg.mouse.get_pressed()[0]:
                if not self.clicked:
                    action = True
                    if self.click_and_hold:
                        self.clicked = True

        if not pg.mouse.get_pressed()[0]:
            self.clicked = False

        surface.blit(self.image, self.rect)
        return action

    def is_clicked(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)

    def update_hover(self, is_hovered: bool) -> None:
        if is_hovered:
            self.hover_progress = min(1.0, self.hover_progress + self.hover_speed)
        else:
            self.hover_progress = max(0.0, self.hover_progress - self.hover_speed)
