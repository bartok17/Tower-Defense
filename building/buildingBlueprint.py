import pygame as pg

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

    def draw_ghost(self, surface, resource_manager, road_segments):
        mouse_pos = pg.mouse.get_pos()
        ghost_x = mouse_pos[0] - self.width // 2
        ghost_y = mouse_pos[1] - self.height // 2
        ghost_image = self.image.copy()
        ghost_image.set_alpha(150)  # Semi-transparent
        surface.blit(ghost_image, (ghost_x, ghost_y))

