import pygame as pg
import random

def generate_offset_path(original_path_tuples: list, offset_distance: float) -> list:
    """
    Generates a new path by offsetting each point of the original path
    perpendicular to the path segments.
    """
    if not original_path_tuples or len(original_path_tuples) < 2:
        return [pg.math.Vector2(p) for p in original_path_tuples]

    original_path = [pg.math.Vector2(p) for p in original_path_tuples]
    offset_path = []

    for i in range(len(original_path)):
        p_i = original_path[i]
        perpendicular = pg.math.Vector2(0, 0)

        if i == 0:
            # First point: use direction to next point
            if len(original_path) > 1:
                p_next = original_path[i+1]
                direction = (p_next - p_i)
                if direction.length_squared() > 0:
                    direction = direction.normalize()
                    perpendicular = pg.math.Vector2(-direction.y, direction.x)
        elif i == len(original_path) - 1:
            # Last point: use direction from previous point
            p_prev = original_path[i-1]
            direction = (p_i - p_prev)
            if direction.length_squared() > 0:
                direction = direction.normalize()
                perpendicular = pg.math.Vector2(-direction.y, direction.x)
        else:
            # Intermediate point: handle corners and collinear cases
            p_prev = original_path[i-1]
            p_next = original_path[i+1]

            v_in = p_i - p_prev
            v_out = p_next - p_i

            if v_in.length_squared() == 0 and v_out.length_squared() == 0:
                offset_path.append(p_i)
                continue
            elif v_in.length_squared() == 0:
                if v_out.length_squared() > 0:
                    direction = v_out.normalize()
                    perpendicular = pg.math.Vector2(-direction.y, direction.x)
            elif v_out.length_squared() == 0:
                if v_in.length_squared() > 0:
                    direction = v_in.normalize()
                    perpendicular = pg.math.Vector2(-direction.y, direction.x)
            else:
                norm_v_in = v_in.normalize()
                norm_v_out = v_out.normalize()

                if abs(norm_v_in.dot(norm_v_out) - 1.0) < 1e-6:
                    # Collinear, same direction
                    perpendicular = pg.math.Vector2(-norm_v_in.y, norm_v_in.x)
                elif abs(norm_v_in.dot(norm_v_out) + 1.0) < 1e-6:
                    # Collinear, 180 degree turn
                    perpendicular = pg.math.Vector2(-norm_v_in.y, norm_v_in.x)
                else:
                    # Corner: use angle bisector
                    tangent_bisector = (norm_v_in + norm_v_out)
                    if tangent_bisector.length_squared() < 1e-8:
                        perpendicular = pg.math.Vector2(-norm_v_in.y, norm_v_in.x)
                    else:
                        tangent_bisector = tangent_bisector.normalize()
                        perpendicular = pg.math.Vector2(-tangent_bisector.y, tangent_bisector.x)
        
        offset_point = p_i + perpendicular * offset_distance
        offset_path.append(offset_point)

    return offset_path