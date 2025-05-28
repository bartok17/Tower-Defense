import pygame as pg
import building.buildManager as bm
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

    def draw_ghost(self, screen, resources_manager, road_segments):
        mouse_x, mouse_y = pg.mouse.get_pos()
        x = mouse_x - self.width // 2
        y = mouse_y - self.height // 2
        can_build = bm.can_build_at((mouse_x, mouse_y), self, resources_manager, road_segments)
        color = (0, 200, 0, 100) if can_build else (200, 0, 0, 100)
        overlay = pg.Surface((self.width, self.height), pg.SRCALPHA)
        overlay.fill(color)
        screen.blit(overlay, (x, y))
        ghost_image = pg.transform.scale(self.image, (self.width, self.height)).copy()
        ghost_image.set_alpha(120)  
        screen.blit(ghost_image, (x, y))
        print("Ghost center at:", mouse_x, mouse_y)




