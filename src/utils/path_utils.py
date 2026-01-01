"""
Path generation utilities.
"""

import math
from collections.abc import Sequence


def generate_offset_path(
    original_path: Sequence[tuple[int, int]], offset: float
) -> list[tuple[int, int]]:
    """
    Generate a path offset from the original by a perpendicular distance.

    Creates a parallel path by offsetting each point perpendicular to the
    direction of travel. Positive offset goes left, negative goes right.

    Args:
        original_path: List of (x, y) waypoints.
        offset: Perpendicular offset distance (positive = left, negative = right).

    Returns:
        New path with offset applied to each point.
    """
    if len(original_path) < 2:
        return list(original_path)

    offset_path: list[tuple[int, int]] = []

    for i, (x, y) in enumerate(original_path):
        # Use float for intermediate calculations
        dx: float
        dy: float
        # Calculate direction vector
        if i == 0:
            # First point: use direction to next point
            dx = original_path[i + 1][0] - x
            dy = original_path[i + 1][1] - y
        elif i == len(original_path) - 1:
            # Last point: use direction from previous point
            dx = x - original_path[i - 1][0]
            dy = y - original_path[i - 1][1]
        else:
            # Middle points: average of incoming and outgoing directions
            dx_in = x - original_path[i - 1][0]
            dy_in = y - original_path[i - 1][1]
            dx_out = original_path[i + 1][0] - x
            dy_out = original_path[i + 1][1] - y
            dx = (dx_in + dx_out) / 2
            dy = (dy_in + dy_out) / 2

        # Normalize direction
        length = math.sqrt(dx * dx + dy * dy)
        if length > 0:
            dx /= length
            dy /= length

        # Perpendicular vector (rotated 90 degrees)
        perp_x = -dy
        perp_y = dx

        # Apply offset
        new_x = int(x + perp_x * offset)
        new_y = int(y + perp_y * offset)

        offset_path.append((new_x, new_y))

    return offset_path


def path_length(path: Sequence[tuple[int, int]]) -> float:
    """
    Calculate total length of a path.

    Args:
        path: List of (x, y) waypoints.

    Returns:
        Total distance along the path.
    """
    total = 0.0
    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]
        total += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return total


def point_on_path(path: Sequence[tuple[int, int]], distance: float) -> tuple[float, float]:
    """
    Get position at a certain distance along a path.

    Args:
        path: List of (x, y) waypoints.
        distance: Distance along the path.

    Returns:
        Interpolated (x, y) position.
    """
    if distance <= 0:
        return float(path[0][0]), float(path[0][1])

    traveled = 0.0

    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]

        segment_length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        if traveled + segment_length >= distance:
            # Interpolate within this segment
            remaining = distance - traveled
            t = remaining / segment_length if segment_length > 0 else 0
            return x1 + t * (x2 - x1), y1 + t * (y2 - y1)

        traveled += segment_length

    # Past end of path
    return float(path[-1][0]), float(path[-1][1])
