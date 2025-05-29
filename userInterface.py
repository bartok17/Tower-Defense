import pygame as pg
import constants as con
from Button import Button
class UserInterface:
    def __init__(self, font=None):
        self.font = pg.font.Font(font, 36)
        self.small_font = pg.font.Font(font, 24)
        self.hud = IconHUD(con.ICON_PATHS, font=font)
        self.build_panel_open = False
        self.ability_buttons = []
        self.toggle_button = Button(
        x=0, y=0, image=None,
        text="<", font_size=24, text_color=(255,255,255),
        width=30, height=30, color=(50,50,50))
        self.pause_button = Button(
        x=10,
        y=con.SCREEN_HEIGHT - 50, 
        image=None,
        text="II", font_size=22, text_color=(0, 0, 0),
        width=30, height=30, color=(255, 255, 0)
        )
    def draw_resources(self, screen, resources: dict, wave_index=None, total_waves=None):
        if wave_index is not None and total_waves is not None:
            resources["wave"] = f"{wave_index + 1}/{total_waves}"
        self.hud.draw_hud(screen, resources)

    def draw_button_column(self, screen, buttons, start_x, start_y):
        for i, btn in enumerate(buttons):
            btn.rect.topleft = (start_x, start_y + i * 60)
            btn.draw(screen)


    def draw_build_panel(self, screen, factory_buttons, tower_buttons):
        screen_width = screen.get_width()
        panel_width = 180
        base_panel_x = screen_width - panel_width

        slide_offset = 0 if self.build_panel_open else panel_width
        actual_panel_x = base_panel_x + slide_offset

        panel_rect = pg.Rect(actual_panel_x, 0, panel_width, screen.get_height())
        s = pg.Surface((panel_rect.width, panel_rect.height), pg.SRCALPHA)
        s.fill((30, 30, 30, 180))
        screen.blit(s, panel_rect.topleft)

        if self.build_panel_open:
            self.hud.draw_button_grid(screen, {
                "factories": factory_buttons,
                "towers": tower_buttons
            }, base_x=actual_panel_x + 10)
        if self.build_panel_open and hasattr(self, "ability_buttons"):
            self.draw_ability_grid(screen, actual_panel_x + 10, screen.get_height() - 120)
        self.toggle_button.draw(screen)

    def handle_panel_toggle(self, event, screen_width, screen_height):
        btn_x = screen_width - 30
        btn_y = screen_height // 2 - 15
        self.toggle_button.rect.topleft = (btn_x, btn_y)

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.toggle_button.is_clicked(pg.mouse.get_pos()):
                self.build_panel_open = not self.build_panel_open
                self.toggle_button.text = "<" if self.build_panel_open else ">"
    def draw_pause_button(self, screen):
        self.pause_button.draw(screen)
        if self.pause_button.rect.collidepoint(pg.mouse.get_pos()):
            tip = self.small_font.render("Pause (Esc)", True, (255, 255, 255))
            screen.blit(tip, (self.pause_button.rect.right + 8, self.pause_button.rect.centery - tip.get_height() // 2))
    def is_pause_button_clicked(self, mouse_pos): return self.pause_button.is_clicked(mouse_pos)
    def draw_ability_grid(self, screen, base_x, base_y, button_size=(80, 40), spacing=10, cols=2):
        for i, btn in enumerate(self.ability_buttons):
            col = i % cols
            row = i // cols
            x = base_x + col * (button_size[0] + spacing)
            y = base_y + row * (button_size[1] + spacing)
            btn.rect.topleft = (x, y)
            btn.draw(screen)
    def get_clicked_ability(self, mouse_pos):
        for btn in self.ability_buttons:
            if btn.is_clicked(mouse_pos):
                return btn.text.lower()
        return None
class IconHUD:
    def __init__(self, icon_paths: dict, font=None):
        self.font = pg.font.Font(font, 28)
        self.padding = 8
        self.icon_size = 32
        self.item_spacing = 10
        self.icon_spacing = 6
        self.bg_color = (10, 10, 10)
        self.border_color = (255, 255, 255)
        self.text_color = (255, 255, 255)

        self.icons = {}
        for key, path in icon_paths.items():
            img = pg.image.load(path).convert_alpha()
            img = pg.transform.scale(img, (self.icon_size, self.icon_size))
            self.icons[key] = img


    def draw_bar_item(self, screen, x, y, icon_key, value):
        icon = self.icons.get(icon_key)
        text_surf = self.font.render(str(value), True, self.text_color)

        width = self.icon_size + self.icon_spacing + text_surf.get_width() + 2 * self.padding
        height = max(self.icon_size, text_surf.get_height()) + 2 * self.padding

        box_rect = pg.Rect(x, y, width, height)
        pg.draw.rect(screen, self.bg_color, box_rect, border_radius=8)
        pg.draw.rect(screen, self.border_color, box_rect, 2, border_radius=8)

        if icon:
            screen.blit(icon, (x + self.padding, y + self.padding))
        screen.blit(text_surf, (x + self.padding + self.icon_size + self.icon_spacing, y + self.padding))

        return width + self.item_spacing
    def draw_button_grid(self, screen, button_groups: dict, base_x, start_y=50, spacing=70, base_icon_size=(40, 40)):
        for col_idx, (label, buttons) in enumerate(button_groups.items()):
            col_x = base_x + col_idx * (base_icon_size[0] + 20) 
            for row_idx, btn in enumerate(buttons):
                x = col_x
                y = start_y + row_idx * spacing
                is_hovered = btn.rect.collidepoint(pg.mouse.get_pos())
                if not hasattr(btn, "hover_progress"):
                    btn.hover_progress = 0.0
                    btn.hover_speed = 0.08
                if is_hovered:
                    label_text = self.font.render(btn.label, True, (255, 255, 255))
                    label_rect = label_text.get_rect(center=(btn.rect.centerx, btn.rect.bottom + 12))
                    screen.blit(label_text, label_rect)
                else:
                    btn.hover_progress = max(0.0, btn.hover_progress - btn.hover_speed)
                scale = 1.0 + 0.15 * btn.hover_progress
                scaled_w = int(base_icon_size[0] * scale)
                scaled_h = int(base_icon_size[1] * scale)
                icon = pg.transform.smoothscale(btn.image, (scaled_w, scaled_h))
                icon_x = x + (base_icon_size[0] - scaled_w) // 2
                icon_y = y + (base_icon_size[1] - scaled_h) // 2
                screen.blit(icon, (icon_x, icon_y))
                btn.rect = pg.Rect(icon_x, icon_y, scaled_w, scaled_h)



    def draw_hud(self, screen, values: dict, start_pos=(10, 10)):
        x, y = start_pos
        for key in values:
            used_width = self.draw_bar_item(screen, x, y, key, values[key])
            x += used_width
