"""
Main game screen.

The primary gameplay screen where tower defense action happens.
This is now a thin UI layer that delegates game logic to GameWorld.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pygame as pg

from ...config import GAME_HEIGHT, GAME_WIDTH
from ...config.paths import ASSETS_DIR, DATA_DIR
from ...core.event_manager import (
    EventManager,
    GameEvent,
    TowerBuiltEvent,
    FactoryBuiltEvent,
    WaveStartedEvent,
)
from ...core.game_world import GamePhase, GameWorld, GameWorldConfig
from ...systems import BuildingBlueprint, BuildManager
from ..components.button import Button
from ..ui_manager import UIManager
from .base_screen import BaseScreen

if TYPE_CHECKING:
    from ...core.game import GameContext, GameEngine


class GameScreen(BaseScreen):
    """
    Main gameplay screen.

    This screen is responsible for:
    - Rendering the game world
    - Handling user input and translating to game actions
    - Managing UI elements (buttons, panels, HUD)
    """

    def __init__(self, context: GameContext, engine: GameEngine) -> None:
        super().__init__(context)
        self.engine = engine

        # Ensure level config exists
        if context.current_level_config is None:
            raise ValueError("No level config set in context")
        self.level_config: dict = context.current_level_config

        # Create game world (contains all game logic)
        self.world = GameWorld(
            GameWorldConfig(
                level_config=self.level_config,
                events=None,  # GameWorld creates its own EventManager
            )
        )

        # Keep reference to events for UI subscriptions
        self.events = self.world.events

        # UI state
        self.is_paused = False
        self.selected_blueprint: BuildingBlueprint | None = None

        # Load UI assets
        self._load_ui_assets()

        # UI manager
        self.ui = UIManager()
        self._setup_ui()

        # Debug toggles
        self.show_fps = False
        self.show_roads = False
        self.show_tower_ranges = False

        # Pause menu
        self._setup_pause_menu()
        self._setup_speed_controls()

        # Subscribe to events for UI updates
        self._setup_event_subscriptions()

    def _setup_event_subscriptions(self) -> None:
        """Set up event subscriptions for UI updates."""
        self.events.subscribe(GameEvent.TOWER_BUILT, self._on_tower_built)
        self.events.subscribe(GameEvent.FACTORY_BUILT, self._on_factory_built)
        self.events.subscribe(GameEvent.WAVE_STARTED, self._on_wave_started)
        self.events.subscribe(GameEvent.GAME_OVER, self._on_game_over)

    def _on_tower_built(self, data: TowerBuiltEvent) -> None:
        """Handle tower built - update UI."""
        # Future: Play sound, show notification
        pass

    def _on_factory_built(self, data: FactoryBuiltEvent) -> None:
        """Handle factory built - update UI."""
        # Future: Play sound, show notification
        pass

    def _on_wave_started(self, data: WaveStartedEvent) -> None:
        """Handle wave started - update UI."""
        # Future: Play sound, show wave announcement
        pass

    def _on_game_over(self, data) -> None:
        """Handle game over - transition to ending screen."""
        won = data.won if data else False

        # Unlock next level if won
        if won:
            self._unlock_next_level()

        # Check for next level
        next_available = self._check_next_level_available()

        from .ending_screen import EndingScreen

        self.engine.replace_screen(
            EndingScreen(
                self.context, self.engine, game_won=won, next_level_available=next_available
            )
        )

    def on_exit(self) -> None:
        """Clean up when leaving this screen."""
        self.events.clear()

    def _load_ui_assets(self) -> None:
        """Load UI-specific assets."""
        # Map image (needed for rendering)
        map_path = ASSETS_DIR / self.level_config["map_image_path"]
        self.map_img = pg.image.load(str(map_path)).convert_alpha()

        # Load building blueprints for UI
        self._load_building_blueprints()

    def _load_building_blueprints(self) -> None:
        """Load building blueprints and create UI buttons."""
        # Factory icons
        factory_metal_img = pg.image.load(
            str(ASSETS_DIR / "factory_metal_icon.png")
        ).convert_alpha()
        factory_wood_img = pg.image.load(
            str(ASSETS_DIR / "factory_wood_icon.png")
        ).convert_alpha()

        # Tower icons
        tower_basic_img = pg.image.load(str(ASSETS_DIR / "tower_basic_icon.png")).convert_alpha()
        tower_cannon_img = pg.image.load(str(ASSETS_DIR / "tower_cannon_icon.png")).convert_alpha()
        tower_flame_img = pg.image.load(str(ASSETS_DIR / "tower_flame_icon.png")).convert_alpha()
        tower_rapid_img = pg.image.load(str(ASSETS_DIR / "tower_rapid_icon.png")).convert_alpha()
        tower_sniper_img = pg.image.load(str(ASSETS_DIR / "tower_sniper_icon.png")).convert_alpha()

        # Factory blueprints
        self.factory_blueprints = [
            BuildingBlueprint(
                "Metal Factory",
                factory_metal_img,
                {"gold": 50},
                40,
                40,
                self.world.build_manager.build_factory,
                resource="metal",
                payout_per_wave=10,
            ),
            BuildingBlueprint(
                "Wood Factory",
                factory_wood_img,
                {"gold": 35},
                40,
                40,
                self.world.build_manager.build_factory,
                resource="wood",
                payout_per_wave=15,
            ),
        ]

        # All tower blueprints
        all_towers = [
            {"name": "Tower - basic", "image": tower_basic_img, "cost": {"gold": 50}, "type": "basic"},
            {"name": "Tower - cannon", "image": tower_cannon_img, "cost": {"gold": 150, "wood": 70, "metal": 20}, "type": "cannon"},
            {"name": "Tower - flame", "image": tower_flame_img, "cost": {"gold": 200, "wood": 90}, "type": "flame"},
            {"name": "Tower - rapid", "image": tower_rapid_img, "cost": {"gold": 150, "wood": 10}, "type": "rapid"},
            {"name": "Tower - sniper", "image": tower_sniper_img, "cost": {"gold": 200, "metal": 15}, "type": "sniper"},
        ]

        # Filter by level config
        available_types = self.level_config.get("available_towers", [t["type"] for t in all_towers])

        self.tower_blueprints = []
        for data in all_towers:
            if data["type"] in available_types:
                cost_dict: dict[str, int] = data["cost"]  # type: ignore[assignment]
                self.tower_blueprints.append(
                    BuildingBlueprint(
                        str(data["name"]),
                        data["image"],  # type: ignore[arg-type]
                        cost_dict,
                        40,
                        40,
                        self.world.build_manager.build_tower,
                        tower_type=str(data["type"]),
                    )
                )

        # Upgrade blueprint
        self.upgrade_blueprint = None
        if self.level_config.get("are_upgrades_enabled", False):
            self.upgrade_blueprint = BuildingBlueprint(
                "Tower Upgrade",
                tower_basic_img,
                {"gold": 150, "wood": 50},
                40,
                40,
                self.world.build_manager.upgrade_tower,
                tower_type=None,
            )
            self.tower_blueprints.append(self.upgrade_blueprint)

        # Create buttons
        self.factory_buttons = [
            Button(0, 0, bp.image, bp.name, width=bp.width, height=bp.height)
            for bp in self.factory_blueprints
        ]
        self.tower_buttons = [
            Button(0, 0, bp.image, bp.name, width=bp.width, height=bp.height)
            for bp in self.tower_blueprints
        ]

    def _setup_ui(self) -> None:
        """Set up UI elements."""
        # Start wave button
        self.start_wave_button = Button(
            GAME_WIDTH // 2 - 100,
            GAME_HEIGHT - 70,
            None,
            text="Start Wave",
            text_color=(255, 255, 255),
            font_size=28,
            width=200,
            height=40,
            color=(0, 150, 0),
        )

        # Ability buttons (if enabled)
        if self.level_config.get("are_abilities_enabled", True):
            self.ui.ability_buttons = [
                Button(0, 0, None, text="Fireball", text_color=(255, 255, 255), font_size=20, width=90, height=40, color=(180, 0, 0)),
                Button(0, 0, None, text="Scanner", text_color=(255, 255, 255), font_size=20, width=90, height=40, color=(0, 120, 180)),
                Button(0, 0, None, text="Disruptor", text_color=(0, 0, 0), font_size=20, width=90, height=40, color=(255, 255, 0)),
                Button(0, 0, None, text="Glue", text_color=(255, 255, 255), font_size=20, width=90, height=40, color=(100, 100, 255)),
            ]

    def _setup_pause_menu(self) -> None:
        """Set up pause menu elements."""
        self.pause_font = pg.font.Font(None, 50)
        self.pause_text = self.pause_font.render("Paused", True, (200, 200, 200))
        self.pause_text_rect = self.pause_text.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 - 100))

        self.resume_button = Button(GAME_WIDTH // 2 - 100, GAME_HEIGHT // 2 - 30, None, text="Resume", text_color=(255, 255, 255), font_size=30, width=200, height=50, color=(0, 180, 0))
        self.restart_button = Button(GAME_WIDTH // 2 - 100, GAME_HEIGHT // 2 + 30, None, text="Restart Level", text_color=(255, 255, 255), font_size=30, width=200, height=50, color=(180, 180, 0))
        self.quit_button = Button(GAME_WIDTH // 2 - 100, GAME_HEIGHT // 2 + 90, None, text="Quit to Menu", text_color=(255, 255, 255), font_size=30, width=200, height=50, color=(180, 0, 0))

        self.pause_overlay = pg.Surface((GAME_WIDTH, GAME_HEIGHT), pg.SRCALPHA)
        self.pause_overlay.fill((0, 0, 0, 128))

    def _setup_speed_controls(self) -> None:
        """Set up game speed control buttons."""
        margin = 20
        btn_w, btn_h = 50, 40

        self.slow_button = Button(GAME_WIDTH - (btn_w * 2 + 60 + margin * 3), GAME_HEIGHT - btn_h - margin, None, text="<<", text_color=(255, 255, 255), font_size=28, width=btn_w, height=btn_h, color=(80, 80, 80))
        self.fast_button = Button(GAME_WIDTH - (btn_w + margin), GAME_HEIGHT - btn_h - margin, None, text=">>", text_color=(255, 255, 255), font_size=28, width=btn_w, height=btn_h, color=(80, 80, 80))
        self.speed_font = pg.font.Font(None, 28)

    # -------------------------------------------------------------------------
    # Event Handling (Input -> Game Actions)
    # -------------------------------------------------------------------------

    def handle_event(self, event: pg.event.Event) -> None:
        """Handle pygame events."""
        if not self.is_paused:
            self.ui.handle_panel_toggle(event, GAME_WIDTH, GAME_HEIGHT)

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos

            # Speed controls (always active)
            if self.slow_button.is_clicked(mouse_pos):
                self.world.set_game_speed(self.world.game_speed / 2)
                return
            if self.fast_button.is_clicked(mouse_pos):
                self.world.set_game_speed(self.world.game_speed * 2)
                return

            if self.is_paused:
                self._handle_pause_click(mouse_pos)
            else:
                self._handle_game_click(mouse_pos)

        elif event.type == pg.KEYDOWN:
            self._handle_keydown(event)

    def _handle_pause_click(self, mouse_pos: tuple[int, int]) -> None:
        """Handle clicks while paused."""
        if self.resume_button.is_clicked(mouse_pos):
            self.is_paused = False
            self.events.emit(GameEvent.GAME_RESUMED, None)
        elif self.restart_button.is_clicked(mouse_pos):
            self.engine.replace_screen(GameScreen(self.context, self.engine))
        elif self.quit_button.is_clicked(mouse_pos):
            from .level_select import LevelSelectScreen
            self.engine.replace_screen(LevelSelectScreen(self.context, self.engine))

    def _handle_game_click(self, mouse_pos: tuple[int, int]) -> None:
        """Handle clicks during gameplay."""
        # Pause button
        if self.ui.is_pause_button_clicked(mouse_pos):
            self.is_paused = True
            self.selected_blueprint = None
            self.world.player_abilities.deselect()
            return

        # Ability buttons (if enabled)
        if self.world.abilities_enabled:
            clicked_ability = self.ui.get_clicked_ability(mouse_pos)
            if clicked_ability:
                if self.world.player_abilities.can_use(clicked_ability, self.world.resources):
                    self.world.player_abilities.select(clicked_ability)
                    self.selected_blueprint = None
                return

        # If ability is selected, use it
        if self.world.player_abilities.selected_ability:
            if self.world.use_ability(self.world.player_abilities.selected_ability, mouse_pos):
                return
            self.world.player_abilities.deselect()
            return

        # Start wave button
        if not self.world.is_wave_active and self.world.current_wave < self.world.total_waves:
            if self.start_wave_button.is_clicked(mouse_pos):
                self.world.start_wave()
                self.selected_blueprint = None
                return

        # Factory buttons
        for idx, btn in enumerate(self.factory_buttons):
            if btn.is_clicked(mouse_pos):
                self.selected_blueprint = self.factory_blueprints[idx]
                return

        # Tower buttons
        for idx, btn in enumerate(self.tower_buttons):
            if btn.is_clicked(mouse_pos):
                self.selected_blueprint = self.tower_blueprints[idx]
                return

        # Build placement
        if self.selected_blueprint:
            if self.world.try_build(mouse_pos, self.selected_blueprint):
                self.selected_blueprint = None

    def _handle_keydown(self, event: pg.event.Event) -> None:
        """Handle keyboard input."""
        if event.key == pg.K_ESCAPE:
            if self.selected_blueprint:
                self.selected_blueprint = None
            elif self.world.player_abilities.selected_ability:
                self.world.player_abilities.deselect()
            else:
                self.is_paused = not self.is_paused
                if self.is_paused:
                    self.events.emit(GameEvent.GAME_PAUSED, None)
                else:
                    self.events.emit(GameEvent.GAME_RESUMED, None)

        if not self.is_paused:
            if event.key == pg.K_f:
                self.show_fps = not self.show_fps
            elif event.key == pg.K_r:
                self.show_roads = not self.show_roads
            elif event.key == pg.K_v:
                self.show_tower_ranges = not self.show_tower_ranges

    # -------------------------------------------------------------------------
    # Update
    # -------------------------------------------------------------------------

    def update(self, dt: float) -> None:
        """Update game state."""
        if self.is_paused:
            return

        # Delegate all game logic to GameWorld
        self.world.update(dt)

    # -------------------------------------------------------------------------
    # Rendering
    # -------------------------------------------------------------------------

    def render(self, surface: pg.Surface) -> None:
        """Render the game."""
        # Background
        surface.fill("black")
        surface.blit(self.map_img, (0, 0))

        # Debug: roads
        if self.show_roads:
            for _name, road in self.world.waypoints.items():
                pg.draw.lines(surface, "red", False, road, 2)

        # HUD
        self.ui.draw_resources(
            surface,
            self.world.resources.resources,
            wave_index=self.world.current_wave,
            total_waves=self.world.total_waves,
        )

        # Build panel
        self.ui.draw_build_panel(surface, self.factory_buttons, self.tower_buttons, mouse_pos=self.context.mouse_pos)

        # Factories
        self.world.build_manager.draw_factories(surface)

        # Towers
        self.world.build_manager.draw_towers(surface, self.show_tower_ranges)

        # Enemies
        for enemy in self.world.enemies:
            enemy.draw(surface)

        # Projectiles
        for proj in self.world.projectiles:
            proj.draw(surface)

        # Player ability effects
        if self.world.abilities_enabled:
            self.world.player_abilities.draw(surface)

        # Ghost preview
        if self.selected_blueprint:
            self.selected_blueprint.draw_ghost(
                surface, self.world.resources, self.world.road_segments, self.world.build_manager,
                mouse_pos=self.context.mouse_pos
            )

        # Ability targeting preview
        if self.world.abilities_enabled and self.world.player_abilities.selected_ability:
            self.world.player_abilities.draw_targeting(surface, mouse_pos=self.context.mouse_pos)

        # Start wave button
        if not self.world.is_wave_active and self.world.current_wave < self.world.total_waves:
            self.start_wave_button.text = f"Start Wave {self.world.current_wave + 1}"
            self.start_wave_button.draw(surface)

        # FPS
        if self.show_fps:
            fps_font = pg.font.Font(None, 30)
            fps_text = fps_font.render(f"FPS: {self.context.clock.get_fps():.2f}", True, (255, 255, 255))
            surface.blit(fps_text, (10, surface.get_height() - 30))

        # Pause button
        self.ui.draw_pause_button(surface, mouse_pos=self.context.mouse_pos)

        # Pause overlay
        if self.is_paused:
            surface.blit(self.pause_overlay, (0, 0))
            surface.blit(self.pause_text, self.pause_text_rect)
            self.resume_button.draw(surface)
            self.restart_button.draw(surface)
            self.quit_button.draw(surface)

        # Speed controls
        self.slow_button.draw(surface)
        self.fast_button.draw(surface)
        speed_text = self.speed_font.render(f"{self.world.game_speed:.2f}x", True, (255, 255, 255))
        surface.blit(speed_text, (GAME_WIDTH - 130, GAME_HEIGHT - 52))

    # -------------------------------------------------------------------------
    # Level Management
    # -------------------------------------------------------------------------

    def _unlock_next_level(self) -> None:
        """Unlock the next level."""
        levels = self.context.levels_config
        current_id = self.level_config["id"]

        for i, lc in enumerate(levels):
            if lc["id"] == current_id:
                if i + 1 < len(levels):
                    levels[i + 1]["unlocked"] = True
                    self._save_levels_config()
                break

    def _check_next_level_available(self) -> bool:
        """Check if there's a next level."""
        levels = self.context.levels_config
        current_id = self.level_config["id"]

        for i, lc in enumerate(levels):
            if lc["id"] == current_id:
                return i + 1 < len(levels)
        return False

    def _save_levels_config(self) -> None:
        """Save levels config to file."""
        config_path = DATA_DIR / "levels_config.json"
        try:
            with open(config_path, "w") as f:
                json.dump(self.context.levels_config, f, indent=4)
        except Exception as e:
            print(f"Error saving levels config: {e}")
