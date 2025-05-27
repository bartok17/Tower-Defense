SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
FPS = 60



WHITE = (255, 255, 255)
RED = (255, 0, 0)


DATA_DIR = "data"
ASSETS_DIR = "assets"

LEVELS_CONFIG = [
    {
        "id": "level1",
        "name": "Beggining",
        "map_image_path": "map1.png",
        "waypoints_path": "map1_waypoints.json",
        "waves_path": "waves_level1.json", 
        "thumbnail_path": "level1_thumb.png", 
        "unlocked": True,
        "start_gold": 200,  
        "start_wood": 100, 
        "start_metal": 50,   
    },
    {
        "id": "level2",
        "name": "hexagon valley",
        "map_image_path": "map1.png", 
        "waypoints_path": "map2_waypoints.json", 
        "waves_path": "waves_level2.json",
        "thumbnail_path": "level2_thumb.png",
        "unlocked": False, 
        "start_gold": 150,  
        "start_wood": 75,   
        "start_metal": 25,   
    },
]