import pygame as pg
class ResourcesManager:
    def __init__(self):
        self.resources = {
            "gold": 300,
            "wood": 330,
            "metal": 330
        }

    def add(self, resource, amount):
        if resource in self.resources:
            self.resources[resource] += amount
    def spend(self, cost_dict):
        if self.can_afford(cost_dict):
            for res, amt in cost_dict.items():
                self.resources[res] -= amt
            return True
        return False
    def can_afford(self, cost_dict):
        return all(self.resources.get(r, 0) >= amount for r, amount in cost_dict.items())

    def get_resource(self, resource):
        return self.resources.get(resource, 0)
    
    def draw_resources(self, surface):
        font = pg.font.SysFont(None, 30)
        y = 100
        for resource, amount in self.resources.items():
            text = font.render(f"{resource.capitalize()}: {amount}", True, (255, 255, 0))
            surface.blit(text, (10, y))
            y += 30
