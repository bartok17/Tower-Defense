import pygame as pg

class ResourcesManager:
    def __init__(self, initial_gold=100, initial_wood=50, initial_metal=25, initial_health=100):
        self.resources = {
            "gold": initial_gold,
            "wood": initial_wood,
            "metal": initial_metal,
            "health": initial_health
        }
        self.font = pg.font.Font(None, 36)

    def get_resource(self, resource_type):
        return self.resources.get(resource_type, 0)

    def add_resource(self, resource_type, amount):
        if resource_type in self.resources:
            self.resources[resource_type] += amount
        else:
            print(f"Warning: Tried to add to unknown resource type: {resource_type}")

    def spend_resource(self, resource_type, amount):
        if resource_type in self.resources:
            if self.resources[resource_type] >= amount:
                self.resources[resource_type] -= amount
                return True
            else:
                return False
        else:
            print(f"Warning: Tried to spend unknown resource type: {resource_type}")
            return False

    def can_afford(self, costs: dict):
        for resource_type, amount in costs.items():
            if self.get_resource(resource_type) < amount:
                return False
        return True

    def spend_multiple(self, costs: dict):
        if self.can_afford(costs):
            for resource_type, amount in costs.items():
                self.spend_resource(resource_type, amount)
            return True
        return False

    def draw_resources(self, screen):
        y_offset = 10
        spacing = 30
        display_order = [
            ("gold", (255, 215, 0)),
            ("wood", (139, 69, 19)),
            ("metal", (169, 169, 169)),
            ("health", (255, 0, 0))
        ]
        for i, (resource_type, color) in enumerate(display_order):
            text = f"{resource_type.capitalize()}: {self.resources.get(resource_type, 0)}"
            text_surface = self.font.render(text, True, color)
            screen.blit(text_surface, (10, y_offset + i * spacing))
