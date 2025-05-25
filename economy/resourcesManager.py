import pygame as pg

class ResourcesManager:
    def __init__(self):
        self.resources = {
            "gold": 2000,
            "metal": 500,
            "wood": 500,
            "health": 1000
        }
        if pg.font.get_init():
            self.font = pg.font.Font(None, 28)
        else:
            pg.font.init()
            self.font = pg.font.Font(None, 28)

    def get_resource(self, name):
        return self.resources.get(name, 0)

    def spend_resource(self, name, amount):
        if self.resources.get(name, 0) >= amount:
            self.resources[name] -= amount
            return True
        return False

    def can_afford(self, costs: dict):
        # Check if all required resources are available
        for resource_name, cost_amount in costs.items():
            if self.get_resource(resource_name) < cost_amount:
                return False
        return True

    def add_resource(self, name, amount):
        if name in self.resources:
            self.resources[name] += amount

    def draw_resources(self, surface):
        y_offset = 10
        for resource_name, value in self.resources.items():
            text = f"{resource_name.capitalize()}: {value}"
            text_surface = self.font.render(text, True, (255, 255, 255))
            surface.blit(text_surface, (10, y_offset))
            y_offset += 30
