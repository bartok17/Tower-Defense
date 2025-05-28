import json
import pygame as pg
import constants as con
import os

# Ensure data directory exists
os.makedirs(con.DATA_DIR, exist_ok=True)

def save_lists_to_json(filename, **lists):
    with open(filename, 'w') as f:
        json.dump(lists, f)

def load_lists_from_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

if __name__ == "__main__":
    mapName = "map2"

    list1 = [(725,0),(725,585),(415,585),(0,1000)]
    list2 = [(725,0),(725,585),(970,1000)]

    pg.init()
    screen = pg.display.set_mode((con.SCREEN_WIDTH, con.SCREEN_HEIGHT))
    pg.display.set_caption("Waypoint Creator")

    current_road = []
    all_roads = []
    map_img_path = os.path.join(con.ASSETS_DIR, mapName + ".png")
    map_img = pg.image.load(map_img_path).convert_alpha()

    save_path = os.path.join(con.DATA_DIR, mapName + "_waypoints.json")
    
    try:
        loaded_lists = load_lists_from_json(save_path)
        all_roads = [loaded_lists[key] for key in sorted(loaded_lists.keys())]
    except FileNotFoundError:
        print(f"No existing waypoints file found for {mapName}. Starting fresh.")

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                pos = pg.mouse.get_pos()
                last_point = current_road[-1] if current_road else None
                if last_point:
                    # Snap to axis or edge if close
                    if abs(pos[0] - last_point[0]) < 10:
                        pos = (last_point[0], pos[1])
                    if abs(pos[1] - last_point[1]) < 10:
                        pos = (pos[0], last_point[1])
                    if pos[0] < 10:
                        pos = (0, pos[1])
                    elif pos[0] > con.SCREEN_WIDTH - 10:
                        pos = (con.SCREEN_WIDTH, pos[1])
                    if pos[1] < 10:
                        pos = (pos[0], 0)
                    elif pos[1] > con.SCREEN_HEIGHT - 10:
                        pos = (pos[0], con.SCREEN_HEIGHT)
                    if abs(pos[0] - last_point[0]) < 10 and abs(pos[1] - last_point[1]) < 10:
                        continue
                current_road.append(pos)
                print(f"Added point: {pos}")
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_BACKSPACE and pg.key.get_mods() & pg.KMOD_CTRL:
                    if all_roads:
                        all_roads.pop()  # Remove last road
                elif event.key == pg.K_BACKSPACE and pg.key.get_mods() & pg.KMOD_SHIFT:
                    all_roads = []
                    current_road = []  # Clear all
                elif event.key == pg.K_BACKSPACE:
                    if current_road:
                        current_road.pop()  # Remove last point
                elif event.key == pg.K_RETURN:
                    if current_road:
                        all_roads.append(current_road)
                        current_road = []  # Commit current road
                elif event.key == pg.K_s:
                    road_dict = {f"road{i+1}": road for i, road in enumerate(all_roads)}
                    save_lists_to_json(save_path, **road_dict)
                    print("Waypoints saved.")

        screen.fill(con.WHITE)
        screen.blit(map_img, (0, 0))
        for road in all_roads:
            if len(road) > 1:
                pg.draw.lines(screen, con.RED, False, road, 3)
            for point in road:
                pg.draw.circle(screen, con.RED, point, 5)
        if len(current_road) > 1:
            pg.draw.lines(screen, con.RED, False, current_road, 3)
        for point in current_road:
            pg.draw.circle(screen, con.RED, point, 5)

        pg.display.flip()

    pg.quit()

    loaded_lists = load_lists_from_json(save_path)
    print(loaded_lists)
