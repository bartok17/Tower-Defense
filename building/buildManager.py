import pygame as pg
from economy.resourcesFactory import Factory
from Tower import create_tower

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
def build_tower(position, blueprint, resource_manager):
    cost = blueprint.cost
    if resource_manager.can_afford(cost):
        resource_manager.spend(cost)
        new_tower = create_tower(position, "basic")  # na razie tylko ten typ
        towers.append(new_tower)
        building_rects.append(pg.Rect(position[0], position[1], blueprint.width, blueprint.height))
        return True
    return False
def can_build_at(position, blueprint, resource_manager, road_segments, road_thickness=20):
    candidate = pg.Rect(position[0], position[1], blueprint.width, blueprint.height)
    for rect in building_rects:
        if candidate.colliderect(rect): return False
    for (start, end) in road_segments:
        dist = point_to_segment_distance(candidate[0], candidate[1], start[0], start[1], end[0], end[1], )
        if dist < road_thickness // 2:
            return False
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

def generate_road_segments(waypoints):
    road_segments = []
    for name, points in waypoints.items():
        for i in range(len(points) - 1):
            start = points[i]
            end = points[i + 1]
            road_segments.append((start, end))
    return road_segments

def point_to_segment_distance(px, py, x1, y1, x2, y2):
    line_mag = ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5
    if line_mag == 0:
        return ((px - x1)**2 + (py - y1)**2) ** 0.5

    u = ((px - x1)*(x2 - x1) + (py - y1)*(y2 - y1)) / (line_mag**2)

    if u < 0:
        closest_x = x1
        closest_y = y1
    elif u > 1:
        closest_x = x2
        closest_y = y2
    else:
        closest_x = x1 + u * (x2 - x1)
        closest_y = y1 + u * (y2 - y1)

    dx = px - closest_x
    dy = py - closest_y
    return (dx**2 + dy**2) ** 0.5

def draw_factories(screen):
    for factory in factories:
        factory.draw(screen)

def update_factories(time, resource_manager):
    for factory in factories:
        factory.update(time, resource_manager)