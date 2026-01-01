"""
HUD (Heads-Up Display) component.

Displays resources and game info with icons.
"""

from __future__ import annotations

import pygame as pg

from ...config.paths import ICON_PATHS


class IconHUD:
    """
    Displays game information with icons.

    Shows health, gold, wood, metal, wave counter, etc.
    """

    def __init__(self, icon_paths: dict[str, str] | None = None, font: str | None = None) -> None:
        """
        Initialize the HUD.

        Args:
            icon_paths: Dictionary of resource name to icon path.
            font: Font name (None for default).
        """
        self.font = pg.font.Font(font, 28)
        self.padding = 8
        self.icon_size = 32
        self.item_spacing = 10
        self.icon_spacing = 6

        self.bg_color = (10, 10, 10)
        self.border_color = (255, 255, 255)
        self.text_color = (255, 255, 255)

        # Load icons
        self.icons: dict[str, pg.Surface] = {}
        paths = icon_paths or ICON_PATHS

        for key, path in paths.items():
            try:
                img = pg.image.load(path).convert_alpha()
                img = pg.transform.scale(img, (self.icon_size, self.icon_size))
                self.icons[key] = img
            except Exception as e:
                print(f"Warning: Could not load icon '{key}': {e}")

    def draw_bar_item(
        self, screen: pg.Surface, x: int, y: int, icon_key: str, value: str | int
    ) -> int:
        """
        Draw a single HUD item with icon and value.

        Args:
            screen: Surface to draw on.
            x: X position.
            y: Y position.
            icon_key: Key for icon in icons dict.
            value: Value to display.

        Returns:
            Width of the drawn item (for positioning next item).
        """
        icon = self.icons.get(icon_key)
        text_surf = self.font.render(str(value), True, self.text_color)

        width = self.icon_size + self.icon_spacing + text_surf.get_width() + 2 * self.padding
        height = max(self.icon_size, text_surf.get_height()) + 2 * self.padding

        # Draw background box
        box_rect = pg.Rect(x, y, width, height)
        pg.draw.rect(screen, self.bg_color, box_rect, border_radius=8)
        pg.draw.rect(screen, self.border_color, box_rect, 2, border_radius=8)

        # Draw icon
        if icon:
            screen.blit(icon, (x + self.padding, y + self.padding))

        # Draw text
        screen.blit(
            text_surf, (x + self.padding + self.icon_size + self.icon_spacing, y + self.padding)
        )

        return width + self.item_spacing

    def draw_hud(
        self,
        screen: pg.Surface,
        values: dict[str, int | str],
        start_pos: tuple[int, int] = (10, 10),
    ) -> None:
        """
        Draw the full HUD bar.

        Args:
            screen: Surface to draw on.
            values: Dictionary of resource name to value.
            start_pos: Starting position (x, y).
        """
        x, y = start_pos

        # Display order
        order = ["health", "gold", "wood", "metal", "wave"]

        for key in order:
            if key in values:
                width = self.draw_bar_item(screen, x, y, key, values[key])
                x += width

    def draw_button_grid(
        self,
        screen: pg.Surface,
        button_groups: dict[str, list],
        base_x: int,
        start_y: int = 50,
        spacing: int = 70,
        base_icon_size: tuple[int, int] = (40, 40),
        mouse_pos: tuple[int, int] | None = None,
    ) -> None:
        """
        Draw a grid of buttons with hover effects.

        Args:
            screen: Surface to draw on.
            button_groups: Dictionary of group name to button list.
            base_x: Base X position.
            start_y: Starting Y position.
            spacing: Vertical spacing between buttons.
            base_icon_size: Base size for icons.
            mouse_pos: Mouse position for hover detection.
        """
        current_mouse = mouse_pos if mouse_pos is not None else pg.mouse.get_pos()

        for col_idx, (_label, buttons) in enumerate(button_groups.items()):
            col_x = base_x + col_idx * (base_icon_size[0] + 20)

            for row_idx, btn in enumerate(buttons):
                x = col_x
                y = start_y + row_idx * spacing

                # Handle hover animation
                is_hovered = btn.rect.collidepoint(current_mouse)

                if not hasattr(btn, "hover_progress"):
                    btn.hover_progress = 0.0
                    btn.hover_speed = 0.08

                if is_hovered:
                    btn.hover_progress = min(1.0, btn.hover_progress + btn.hover_speed)

                    # Show label
                    if btn.label:
                        label_text = self.font.render(btn.label, True, (255, 255, 255))
                        label_rect = label_text.get_rect(
                            center=(btn.rect.centerx, btn.rect.bottom + 12)
                        )
                        screen.blit(label_text, label_rect)
                else:
                    btn.hover_progress = max(0.0, btn.hover_progress - btn.hover_speed)

                # Scale based on hover
                scale = 1.0 + 0.15 * btn.hover_progress
                scaled_w = int(base_icon_size[0] * scale)
                scaled_h = int(base_icon_size[1] * scale)

                # Draw scaled icon
                icon = pg.transform.smoothscale(btn.image, (scaled_w, scaled_h))
                icon_x = x + (base_icon_size[0] - scaled_w) // 2
                icon_y = y + (base_icon_size[1] - scaled_h) // 2

                screen.blit(icon, (icon_x, icon_y))
                btn.rect = pg.Rect(icon_x, icon_y, scaled_w, scaled_h)
