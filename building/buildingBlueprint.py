import pygame as pg

class BuildingBlueprint:
    def __init__(self, name, image, cost, width, height, function, resource):
        self.name = name
        self.image = image
        self.cost = cost
        self.width = width
        self.height = height
        self.function = function
        self.resource = resource  
    def draw_ghost(self, screen, resource_manager, road_rects):
        mouse_pos = pg.mouse.get_pos()
        import building.buildManager as bm 
        can_build = bm.can_build_at(mouse_pos, self, resource_manager, road_rects)
        ghost_img = self.image.copy()
        if can_build:
            ghost_img.fill((0, 255, 0, 100), special_flags=pg.BLEND_RGBA_MULT)
        else:
            ghost_img.fill((255, 0, 0, 100), special_flags=pg.BLEND_RGBA_MULT)
        screen.blit(ghost_img, (mouse_pos[0] - self.width // 2, mouse_pos[1] - self.height // 2))