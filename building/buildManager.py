import pygame as pg
from economy.resourcesFactory import Factory
#import Tower pewnie jakis

factories = []
towers = []
building_rects = []

def build_factory(position, blueprint, resource_manager):
    cost = blueprint.cost
    if resource_manager.can_afford(cost):
        resource_manager.spend(cost)
        new_factory = Factory(position, blueprint.resource, 5, 500)
        factories.append(new_factory)
        building_rects.append(pg.Rect(position[0], position[1], blueprint.width, blueprint.height))
        return True
    return False
# def build_tower(position, resource_manager)...
def can_build_at(position, blueprint, resource_manager, road_rects):
    candidate = pg.Rect(position[0], position[1], blueprint.width, blueprint.height)
    for rect in building_rects:
        if candidate.colliderect(rect): return False
    for road in road_rects:
        if candidate.colliderect(road): return False
    if not resource_manager.can_afford(blueprint.cost): return False
    return True

def try_build(position, blueprint, resource_manager, road_rects):
    if can_build_at(position, blueprint, resource_manager, road_rects):
        if blueprint.function(position, blueprint, resource_manager):
            candidate = pg.Rect(position[0], position[1], blueprint.width, blueprint.height)
            building_rects.append(candidate)
            print(f"Built {blueprint.name} at {position}")
            return True
    return False




def draw_factories(screen):
    for factory in factories:
        factory.draw(screen)

def update_factories(time, resource_manager):
    for factory in factories:
        factory.update(time, resource_manager)