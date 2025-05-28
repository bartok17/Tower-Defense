import pygame as pg

class ResourcesManager:
    def __init__(self, initial_gold=100, initial_wood=50, initial_metal=25, initial_health=100):
        self.resources = {
            "health": initial_health,
            "gold": initial_gold,
            "wood": initial_wood,
            "metal": initial_metal
            
        }
        self.font = pg.font.Font(None, 36)

    def get_resource(self, resource_type):
        return self.resources.get(resource_type, 0)

    def add_resource(self, resource_type, amount):
        if resource_type in self.resources:
            self.resources[resource_type] += amount

    def spend_resource(self, resource_type, amount):
        if resource_type in self.resources:
            if self.resources[resource_type] >= amount:
                self.resources[resource_type] -= amount
                return True
            else:
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

