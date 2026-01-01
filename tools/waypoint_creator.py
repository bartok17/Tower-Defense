"""
Waypoint Creator Tool.

Controls:
    - Click: Add waypoint (snaps to axis/edge if close)
    - Backspace: Remove last point
    - Ctrl+Backspace: Remove last road
    - Shift+Backspace: Clear all
    - Enter: Commit current road
    - S: Save to file
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pygame as pg

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from src.config.colors import RED, WHITE
from src.config.paths import ASSETS_DIR, DATA_DIR
from src.config.settings import SCREEN_HEIGHT, SCREEN_WIDTH

# Tool settings
SNAP_THRESHOLD = 10
EDGE_THRESHOLD = 10
POINT_RADIUS = 5
LINE_WIDTH = 3


def save_waypoints(filepath: Path, roads: list[list[tuple[int, int]]]) -> None:
    """Save roads to JSON file."""
    road_dict = {f"road{i + 1}": road for i, road in enumerate(roads)}
    with open(filepath, "w") as f:
        json.dump(road_dict, f, indent=2)


def load_waypoints(filepath: Path) -> list[list[tuple[int, int]]]:
    """Load roads from JSON file."""
    try:
        with open(filepath) as f:
            data = json.load(f)
        return [data[key] for key in sorted(data.keys())]
    except FileNotFoundError:
        return []


def snap_point(
    pos: tuple[int, int], last_point: tuple[int, int] | None
) -> tuple[int, int]:
    """Snap point to axis alignment or screen edges."""
    x, y = pos

    if last_point:
        lx, ly = last_point
        # Snap to axis alignment
        if abs(x - lx) < SNAP_THRESHOLD:
            x = lx
        if abs(y - ly) < SNAP_THRESHOLD:
            y = ly

    # Snap to edges
    if x < EDGE_THRESHOLD:
        x = 0
    elif x > SCREEN_WIDTH - EDGE_THRESHOLD:
        x = SCREEN_WIDTH
    if y < EDGE_THRESHOLD:
        y = 0
    elif y > SCREEN_HEIGHT - EDGE_THRESHOLD:
        y = SCREEN_HEIGHT

    return (x, y)


def is_duplicate_point(pos: tuple[int, int], last_point: tuple[int, int] | None) -> bool:
    """Check if point is too close to the last point."""
    if not last_point:
        return False
    return abs(pos[0] - last_point[0]) < SNAP_THRESHOLD and abs(pos[1] - last_point[1]) < SNAP_THRESHOLD


def draw_roads(
    screen: pg.Surface,
    roads: list[list[tuple[int, int]]],
    current_road: list[tuple[int, int]],
) -> None:
    """Draw all roads and current road being edited."""
    # Draw completed roads
    for road in roads:
        if len(road) > 1:
            pg.draw.lines(screen, RED, False, road, LINE_WIDTH)
        for point in road:
            pg.draw.circle(screen, RED, point, POINT_RADIUS)

    # Draw current road
    if len(current_road) > 1:
        pg.draw.lines(screen, RED, False, current_road, LINE_WIDTH)
    for point in current_road:
        pg.draw.circle(screen, RED, point, POINT_RADIUS)


def main() -> None:
    """Run the waypoint creator tool."""
    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("Waypoint Creator")
    clock = pg.time.Clock()

    # Get map name from user or default
    map_name = input("Enter map name (e.g., map1): ").strip() or "map1"

    # Load map image
    map_img_path = ASSETS_DIR / f"{map_name}.png"
    if not map_img_path.exists():
        print(f"Error: Map image not found at {map_img_path}")
        pg.quit()
        return

    map_img = pg.image.load(str(map_img_path)).convert_alpha()

    # Load or initialize waypoints
    save_path = DATA_DIR / f"{map_name}_waypoints.json"
    all_roads = load_waypoints(save_path)
    current_road: list[tuple[int, int]] = []

    if all_roads:
        print(f"Loaded {len(all_roads)} existing roads from {save_path}")
    else:
        print(f"No existing waypoints for {map_name}. Starting fresh.")

    print("\nControls:")
    print("  Click: Add waypoint")
    print("  Backspace: Remove last point")
    print("  Ctrl+Backspace: Remove last road")
    print("  Shift+Backspace: Clear all")
    print("  Enter: Commit current road")
    print("  S: Save to file")
    print("  ESC/Close: Quit")

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                pos = pg.mouse.get_pos()
                last_point = current_road[-1] if current_road else None

                pos = snap_point(pos, last_point)

                if not is_duplicate_point(pos, last_point):
                    current_road.append(pos)
                    print(f"Added point: {pos}")

            elif event.type == pg.KEYDOWN:
                mods = pg.key.get_mods()

                if event.key == pg.K_ESCAPE:
                    running = False

                elif event.key == pg.K_BACKSPACE:
                    if mods & pg.KMOD_CTRL:
                        if all_roads:
                            removed = all_roads.pop()
                            print(f"Removed road with {len(removed)} points")
                    elif mods & pg.KMOD_SHIFT:
                        all_roads.clear()
                        current_road.clear()
                        print("Cleared all roads")
                    elif current_road:
                        removed = current_road.pop()
                        print(f"Removed point: {removed}")

                elif event.key == pg.K_RETURN:
                    if current_road:
                        all_roads.append(current_road)
                        print(f"Committed road with {len(current_road)} points")
                        current_road = []

                elif event.key == pg.K_s:
                    # Include current road if not empty
                    roads_to_save = all_roads + ([current_road] if current_road else [])
                    save_waypoints(save_path, roads_to_save)
                    print(f"Saved {len(roads_to_save)} roads to {save_path}")

        # Draw
        screen.fill(WHITE)
        screen.blit(map_img, (0, 0))
        draw_roads(screen, all_roads, current_road)
        pg.display.flip()
        clock.tick(60)

    pg.quit()

    # Print final data
    if all_roads or current_road:
        final_roads = all_roads + ([current_road] if current_road else [])
        print(f"\nFinal waypoints ({len(final_roads)} roads):")
        for i, road in enumerate(final_roads):
            print(f"  road{i + 1}: {road}")


if __name__ == "__main__":
    main()
