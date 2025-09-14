import pygame as pg
from scripts.economy.resourcesFactory import Factory
from Tower import create_tower

factories = []
towers = []
building_rects = []

def build_factory(position, blueprint, resource_manager):
    # Build a factory if resources are sufficient
    cost = blueprint.cost
    if resource_manager.can_afford(cost):
        for resource_name, amount in cost.items():
            if not resource_manager.spend_resource(resource_name, amount):
                print(f"Error: Failed to spend {amount} of {resource_name} for factory.")
                return False
        
        payout_rate = blueprint.payout_per_wave if hasattr(blueprint, 'payout_per_wave') and blueprint.payout_per_wave is not None else 0

        new_factory = Factory(position, blueprint.resource, payout_rate, image_path=None)
        new_factory.image = pg.transform.scale(blueprint.image, (blueprint.width, blueprint.height))
        factories.append(new_factory)
        building_rects.append(pg.Rect(position[0], position[1], blueprint.width, blueprint.height))
        return True
    return False

def build_tower(position, blueprint, resource_manager):
    # Build a tower if resources are sufficient
    cost = blueprint.cost
    if resource_manager.can_afford(cost):
        for resource_name, amount in cost.items():
            if not resource_manager.spend_resource(resource_name, amount):
                print(f"Error: Failed to spend {amount} of {resource_name} for tower.")
                return False
        
        tower_type_name = blueprint.name.replace("Tower - ", "").lower()
        adjusted_pos = (position[0] + blueprint.width // 2, position[1] + blueprint.height // 2)
        new_tower = create_tower(adjusted_pos, tower_type_name)
        if tower_type_name == "sniper":
            new_tower.can_see_invisible = True
        towers.append(new_tower)
        building_rects.append(pg.Rect(position[0], position[1], blueprint.width, blueprint.height))
        return True
    return False

def upgrade_tower(position, blueprint, resource_manager):
    # Upgrade a tower at the given position if possible
    from Tower import TOWER_PRESETS, create_tower

    cost = blueprint.cost
    if not resource_manager.can_afford(cost):
        return False

    for i, tower in enumerate(towers):
        tower_rect = pg.Rect(int(tower.pos.x - blueprint.width // 2), int(tower.pos.y - blueprint.height // 2), blueprint.width, blueprint.height)
        build_rect = pg.Rect(position[0], position[1], blueprint.width, blueprint.height)
        if tower_rect.colliderect(build_rect):
            current_type = getattr(tower.stats, "preset_name", None)
            if not current_type:
                continue

            next_type = f"{current_type} 2"
            if next_type not in TOWER_PRESETS:
                return False

            for resource_name, amount in cost.items():
                if not resource_manager.spend_resource(resource_name, amount):
                    return False

            new_tower = create_tower((int(tower.pos.x), int(tower.pos.y)), next_type)
            towers[i] = new_tower
            return True
    return False

def can_build_at(position, blueprint, resource_manager, road_segments, road_thickness=100):
    # Check if a building can be placed at the position
    candidate_rect = pg.Rect(position[0], position[1], blueprint.width, blueprint.height)
    
    for existing_rect in building_rects:
        if candidate_rect.colliderect(existing_rect):
            return False

    for (start_point, end_point) in road_segments:
        center_x = candidate_rect.centerx
        center_y = candidate_rect.centery
        dist_to_road = point_to_segment_distance(center_x, center_y, start_point[0], start_point[1], end_point[0], end_point[1])
        if dist_to_road < (blueprint.width / 2 + road_thickness / 2):
            return False

    if not resource_manager.can_afford(blueprint.cost):
        return False

    return True

def try_build(mouse_pos, blueprint, resource_manager, road_segments):
    # Attempt to build at mouse position using blueprint
    build_pos_tuple = mouse_pos

    if can_build_at(build_pos_tuple, blueprint, resource_manager, road_segments):
        if hasattr(blueprint, 'build_function') and callable(blueprint.build_function):
            if blueprint.build_function(build_pos_tuple, blueprint, resource_manager):
                return True
            else:
                print(f"Build function for {blueprint.name} failed.")
                return False
        else:
            print(f"Error: Blueprint '{blueprint.name}' has no valid build_function attribute or it's not callable.")
            return False
    return False

def generate_road_segments(waypoints_dict):
    # Convert waypoints to road segments
    all_segments = []
    for path_name, points_list in waypoints_dict.items():
        for i in range(len(points_list) - 1):
            start_point = points_list[i]
            end_point = points_list[i+1]
            all_segments.append((start_point, end_point))
    return all_segments

def point_to_segment_distance(px, py, x1, y1, x2, y2):
    # Distance from point (px, py) to segment (x1, y1)-(x2, y2)
    line_vec = pg.Vector2(x2 - x1, y2 - y1)
    point_vec = pg.Vector2(px - x1, py - y1)
    line_len_sq = line_vec.length_squared()
    if line_len_sq == 0:
        return point_vec.length()
    
    t = max(0, min(1, line_vec.dot(point_vec) / line_len_sq))
    closest_point_on_segment = pg.Vector2(x1, y1) + t * line_vec
    return closest_point_on_segment.distance_to(pg.Vector2(px, py))

def draw_factories(screen):
    # Draw all factories
    for factory in factories:
        factory.draw(screen)

def update_factories(delta_time, resource_manager):
    # Update all factories
    for factory in factories:
        factory.update(delta_time, resource_manager)

def reset_build_state():
    # Clear all build state lists
    global factories, towers, building_rects
    factories.clear()
    towers.clear()
    building_rects.clear()
