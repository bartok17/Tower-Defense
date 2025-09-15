import pygame as pg
from . import buildManager as bm


class BuildingBlueprint:
    def __init__(self, name, image, cost, width, height, build_function, resource=None, tower_type=None, payout_per_wave=None):
        self.name = name
        self.image = image  # Pygame Surface
        self.cost = cost  # Dict: {"gold": 100, ...}
        self.width = width
        self.height = height
        self.build_function = build_function
        self.resource = resource
        self.tower_type = tower_type
        self.payout_per_wave = payout_per_wave
        self.font = pg.font.Font(None, 24)

    def draw_ghost(self, screen, resources_manager, road_segments):
        mouse_x, mouse_y = pg.mouse.get_pos()
        x = mouse_x - self.width // 2
        y = mouse_y - self.height // 2

        # Check if building can be placed at this position
        can_build = bm.can_build_at((x, y), self, resources_manager, road_segments)
        
        color = (0, 200, 0, 100) if can_build else (200, 0, 0, 100)
        overlay = pg.Surface((self.width, self.height), pg.SRCALPHA)
        overlay.fill(color)
        screen.blit(overlay, (x, y))

        ghost_image = pg.transform.scale(self.image, (self.width, self.height)).copy()
        ghost_image.set_alpha(120)
        screen.blit(ghost_image, (x, y))

        # Draw cost below the ghost image
        cost_texts = []
        for resource, amount in self.cost.items():
            cost_texts.append(f"{resource.capitalize()}: {amount}")
        
        cost_surface_y_offset = y + self.height + 5

        for i, text_line in enumerate(cost_texts):
            resource_name = list(self.cost.keys())[i]
            required_amount = self.cost[resource_name]
            text_color = (255, 255, 255)
            if not resources_manager.can_afford({resource_name: required_amount}):
                text_color = (255, 100, 100)

            cost_line_surface = self.font.render(text_line, True, text_color)
            cost_line_rect = cost_line_surface.get_rect(midtop=(mouse_x, cost_surface_y_offset + i * (self.font.get_height() + 2)))
            screen.blit(cost_line_surface, cost_line_rect)
