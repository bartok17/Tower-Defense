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
        new_tower = create_tower(position, blueprint.name.lstrip("Tower - "))  
        towers.append(new_tower)
        building_rects.append(pg.Rect(position[0], position[1], blueprint.width, blueprint.height))
        return True
    return False
def can_build_at(position, blueprint, resource_manager, road, road_thickness=100):
    candidate = pg.Rect(position[0], position[1], blueprint.width, blueprint.height)
    for rect in building_rects:
        if candidate.colliderect(rect): return False
    for (start, end) in road:
        dist = point_to_segment_distance(candidate[0], candidate[1], start[0], start[1], end[0], end[1], )
        if dist < road_thickness // 2:
            return False
    if not resource_manager.can_afford(blueprint.cost): return False
    return True

def try_build(position, blueprint, resource_manager, road):
    if can_build_at(position, blueprint, resource_manager, road):
        if blueprint.function(position, blueprint, resource_manager):
            candidate = pg.Rect(position[0], position[1], blueprint.width, blueprint.height)
            building_rects.append(candidate)
            return True
    return False

def generate_road_segments(waypoints):
    road = []
    for name, points in waypoints.items():
        for i in range(len(points) - 1):
            start = points[i]
            end = points[i + 1]
            road.append((start, end))
    return road

def point_to_segment_distance(px, py, x1, y1, x2, y2):
    p = pg.Vector2(px, py)
    a = pg.Vector2(x1, y1)
    b = pg.Vector2(x2, y2)

    ab = b - a
    ap = p - a
    ab_len_sq = ab.length_squared()

    if ab_len_sq == 0:
        return p.distance_to(a)
    u = ap.dot(ab) / ab_len_sq
    if u < 0:
        closest = a
    elif u > 1:
        closest = b
    else:
        closest = a + u * ab
    return p.distance_to(closest)

def draw_factories(screen):
    for factory in factories:
        factory.draw(screen)

def update_factories(time, resource_manager):
    for factory in factories:
        factory.update(time, resource_manager)