"""
Tower Defense Game - Main Entry Point

A pygame tower defense game with multiple levels, tower types,
enemy abilities, and resource management.
"""

import json
import sys

import pygame as pg

from .config import DEFAULT_LEVELS_CONFIG, FPS
from .config.settings import GAME_WIDTH, GAME_HEIGHT, WINDOW_SCALE_FACTOR
from .config.paths import ASSETS_DIR, DATA_DIR
from .core import GameContext, GameEngine
from .ui.screens import MainMenuScreen


def load_levels_config() -> list[dict]:
    """Load levels configuration from file."""
    config_path = DATA_DIR / "levels_config.json"

    if config_path.exists():
        try:
            with open(config_path) as f:
                data: list[dict] = json.load(f)
                return data
        except (OSError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load levels config: {e}")
            print("Using default configuration.")

    return DEFAULT_LEVELS_CONFIG


def calculate_window_size() -> tuple[int, int]:
    """Calculate optimal window size based on screen resolution."""
    # Get display info before creating window
    display_info = pg.display.Info()
    screen_w = display_info.current_w
    screen_h = display_info.current_h
    
    # Calculate window size as percentage of screen height (keeping aspect ratio 1:1)
    target_size = int(screen_h * WINDOW_SCALE_FACTOR)
    
    # Ensure it fits on screen with some margin
    max_size = min(screen_w - 100, screen_h - 100)
    window_size = min(target_size, max_size)
    
    return window_size, window_size


def main() -> int:
    """Main entry point."""
    # Initialize pygame
    pg.init()
    pg.mixer.init()

    # Calculate window size based on display
    window_width, window_height = calculate_window_size()
    
    # Create display (actual window)
    screen = pg.display.set_mode((window_width, window_height), pg.RESIZABLE)
    pg.display.set_caption("Tower Defense")

    # Create virtual surface for game rendering (fixed internal resolution)
    game_surface = pg.Surface((GAME_WIDTH, GAME_HEIGHT))
    
    # Calculate initial scale factor
    scale = min(window_width / GAME_WIDTH, window_height / GAME_HEIGHT)

    # Set icon
    icon_path = ASSETS_DIR / "icon.png"
    if icon_path.exists():
        icon = pg.image.load(str(icon_path))
        pg.display.set_icon(icon)

    # Create clock
    clock = pg.time.Clock()

    # Load config
    levels_config = load_levels_config()

    # Create context and engine (pass game_surface instead of screen)
    context = GameContext(
        screen=game_surface, 
        clock=clock, 
        levels_config=levels_config,
        scale=scale
    )

    engine = GameEngine(context)

    # Start with main menu
    engine.push_screen(MainMenuScreen(context, engine))

    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.VIDEORESIZE:
                # Window was resized - update scale
                window_width, window_height = event.w, event.h
                scale = min(window_width / GAME_WIDTH, window_height / GAME_HEIGHT)
                context.scale = scale
            elif event.type == pg.MOUSEMOTION:
                # Transform mouse position to game coordinates
                transformed_event = transform_mouse_event(event, scale, window_width, window_height)
                context.mouse_pos = transformed_event.pos  # Update context for render-time access
                engine.handle_event(transformed_event)
            elif event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP):
                # Transform mouse position to game coordinates
                transformed_event = transform_mouse_event(event, scale, window_width, window_height)
                context.mouse_pos = transformed_event.pos  # Update context for render-time access
                engine.handle_event(transformed_event)
            else:
                engine.handle_event(event)

        # Calculate delta time
        dt = clock.tick(FPS) / 1000.0  # seconds

        # Update current screen
        engine.update(dt)

        # Render current screen to game surface
        engine.render(game_surface)

        # Scale game surface to window
        render_scaled(screen, game_surface, window_width, window_height, scale)

        # Flip display
        pg.display.flip()

        # Check if engine wants to quit
        if not engine.is_running():
            running = False

    # Cleanup
    pg.quit()
    return 0


def transform_mouse_event(event: pg.event.Event, scale: float, window_w: int, window_h: int) -> pg.event.Event:
    """Transform mouse event coordinates from window space to game space."""
    # Calculate offset for centered rendering
    scaled_w = int(GAME_WIDTH * scale)
    scaled_h = int(GAME_HEIGHT * scale)
    offset_x = (window_w - scaled_w) // 2
    offset_y = (window_h - scaled_h) // 2
    
    # Transform position
    window_x, window_y = event.pos
    game_x = int((window_x - offset_x) / scale)
    game_y = int((window_y - offset_y) / scale)
    
    # Clamp to game bounds
    game_x = max(0, min(game_x, GAME_WIDTH - 1))
    game_y = max(0, min(game_y, GAME_HEIGHT - 1))
    
    # Create new event with transformed position
    if event.type == pg.MOUSEMOTION:
        # Transform rel as well
        rel_x = int(event.rel[0] / scale)
        rel_y = int(event.rel[1] / scale)
        return pg.event.Event(event.type, pos=(game_x, game_y), rel=(rel_x, rel_y), buttons=event.buttons)
    else:
        # MOUSEBUTTONDOWN/UP
        return pg.event.Event(event.type, pos=(game_x, game_y), button=event.button)


def render_scaled(screen: pg.Surface, game_surface: pg.Surface, window_w: int, window_h: int, scale: float) -> None:
    """Render game surface scaled to fit the window, centered."""
    # Clear screen with black
    screen.fill((0, 0, 0))
    
    # Calculate scaled size
    scaled_w = int(GAME_WIDTH * scale)
    scaled_h = int(GAME_HEIGHT * scale)
    
    # Scale the game surface
    scaled_surface = pg.transform.smoothscale(game_surface, (scaled_w, scaled_h))
    
    # Center it on screen
    offset_x = (window_w - scaled_w) // 2
    offset_y = (window_h - scaled_h) // 2
    
    screen.blit(scaled_surface, (offset_x, offset_y))


if __name__ == "__main__":
    sys.exit(main())
