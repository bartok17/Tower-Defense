"""
Waypoint loading utilities.
"""

import json
from pathlib import Path


def load_waypoints(filepath: str | Path) -> dict[str, list[tuple[int, int]]]:
    """
    Load waypoints from a JSON file.

    Args:
        filepath: Path to the waypoints JSON file.

    Returns:
        Dictionary mapping path names to lists of coordinate tuples.
    """
    filepath = Path(filepath)

    with open(filepath) as f:
        data = json.load(f)

    waypoints: dict[str, list[tuple[int, int]]] = {}

    for name, points in data.items():
        waypoints[name] = [tuple(p) for p in points]

    return waypoints


def save_waypoints(waypoints: dict[str, list[tuple[int, int]]], filepath: str | Path) -> None:
    """
    Save waypoints to a JSON file.

    Args:
        waypoints: Dictionary mapping path names to coordinate lists.
        filepath: Path to save the JSON file.
    """
    filepath = Path(filepath)

    data = {name: [list(p) for p in points] for name, points in waypoints.items()}

    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)
