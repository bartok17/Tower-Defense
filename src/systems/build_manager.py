"""
Build manager system.

Handles building placement, validation, and management.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pygame as pg

from ..core.event_manager import EventManager, FactoryBuiltEvent, GameEvent, TowerBuiltEvent, TowerUpgradedEvent
from ..entities import Factory, Tower, create_tower

if TYPE_CHECKING:
    from .economy_system import ResourcesManager


@dataclass
class BuildingBlueprint:
    """Blueprint for a buildable structure."""

    name: str
    image: pg.Surface
    cost: dict[str, int]
    width: int
    height: int
    build_function: Callable | None = None
    resource: str | None = None  # For factories
    tower_type: str | None = None  # For towers
    payout_per_wave: int | None = None  # For factories

    _font: pg.font.Font | None = None

    @property
    def font(self) -> pg.font.Font:
        if self._font is None:
            self._font = pg.font.Font(None, 24)
        return self._font

    def draw_ghost(
        self,
        screen: pg.Surface,
        resources_manager: ResourcesManager,
        road_segments: list[tuple[tuple[int, int], tuple[int, int]]],
        build_manager: BuildManager,
        mouse_pos: tuple[int, int] | None = None,
    ) -> None:
        if mouse_pos is None:
            mouse_x, mouse_y = pg.mouse.get_pos()
        else:
            mouse_x, mouse_y = mouse_pos
        x = mouse_x - self.width // 2
        y = mouse_y - self.height // 2

        can_build = build_manager.can_build_at((x, y), self, resources_manager, road_segments)

        # Draw colored overlay
        color = (0, 200, 0, 100) if can_build else (200, 0, 0, 100)
        overlay = pg.Surface((self.width, self.height), pg.SRCALPHA)
        overlay.fill(color)
        screen.blit(overlay, (x, y))

        # Draw ghost image
        ghost_image = pg.transform.scale(self.image, (self.width, self.height)).copy()
        ghost_image.set_alpha(120)
        screen.blit(ghost_image, (x, y))

        # Draw cost text
        cost_y = y + self.height + 5
        for i, (resource, amount) in enumerate(self.cost.items()):
            text_color = (255, 255, 255)
            if not resources_manager.can_afford({resource: amount}):
                text_color = (255, 100, 100)

            text = f"{resource.capitalize()}: {amount}"
            text_surface = self.font.render(text, True, text_color)
            text_rect = text_surface.get_rect(
                midtop=(mouse_x, cost_y + i * (self.font.get_height() + 2))
            )
            screen.blit(text_surface, text_rect)


class BuildManager:
    """Manages building placement and tracking."""

    def __init__(self, events: EventManager | None = None) -> None:
        self.towers: list[Tower] = []
        self.factories: list[Factory] = []
        self.building_rects: list[pg.Rect] = []
        self.events = events

    def reset(self) -> None:
        self.towers.clear()
        self.factories.clear()
        self.building_rects.clear()

    def build_factory(
        self, position: tuple[int, int], blueprint: BuildingBlueprint, resources: ResourcesManager
    ) -> bool:
        """Build a factory at position. Returns True if successful."""
        if not resources.can_afford(blueprint.cost):
            return False

        # Spend resources
        for resource_name, amount in blueprint.cost.items():
            if not resources.spend_resource(resource_name, amount):
                print(f"Error: Failed to spend {amount} of {resource_name}")
                return False

        # Create factory
        payout = blueprint.payout_per_wave or 0
        new_factory = Factory(position, blueprint.resource or "gold", payout)
        new_factory.image = pg.transform.scale(blueprint.image, (blueprint.width, blueprint.height))

        self.factories.append(new_factory)
        self.building_rects.append(
            pg.Rect(position[0], position[1], blueprint.width, blueprint.height)
        )

        # Emit event
        if self.events:
            self.events.emit(
                GameEvent.FACTORY_BUILT,
                FactoryBuiltEvent(
                    factory=new_factory,
                    position=position,
                    resource_type=blueprint.resource,
                ),
            )

        return True

    def build_tower(
        self, position: tuple[int, int], blueprint: BuildingBlueprint, resources: ResourcesManager
    ) -> bool:
        """Build a tower at position. Returns True if successful."""
        if not resources.can_afford(blueprint.cost):
            return False

        # Spend resources
        for resource_name, amount in blueprint.cost.items():
            if not resources.spend_resource(resource_name, amount):
                print(f"Error: Failed to spend {amount} of {resource_name}")
                return False

        # Create tower
        tower_type = blueprint.name.replace("Tower - ", "").lower()
        adjusted_pos = (position[0] + blueprint.width // 2, position[1] + blueprint.height // 2)

        new_tower = create_tower(adjusted_pos, tower_type)
        if tower_type == "sniper":
            new_tower.can_see_invisible = True

        self.towers.append(new_tower)
        self.building_rects.append(
            pg.Rect(position[0], position[1], blueprint.width, blueprint.height)
        )

        # Emit event
        if self.events:
            self.events.emit(
                GameEvent.TOWER_BUILT,
                TowerBuiltEvent(
                    tower=new_tower,
                    position=adjusted_pos,
                    tower_type=tower_type,
                ),
            )

        return True

    def upgrade_tower(
        self, position: tuple[int, int], blueprint: BuildingBlueprint, resources: ResourcesManager
    ) -> bool:
        from ..entities.tower import get_tower_presets

        if not resources.can_afford(blueprint.cost):
            return False

        presets = get_tower_presets()

        # Find tower at position
        for i, tower in enumerate(self.towers):
            tower_rect = pg.Rect(
                int(tower.pos.x - blueprint.width // 2),
                int(tower.pos.y - blueprint.height // 2),
                blueprint.width,
                blueprint.height,
            )
            build_rect = pg.Rect(position[0], position[1], blueprint.width, blueprint.height)

            if tower_rect.colliderect(build_rect):
                current_type = tower.stats.preset_name
                if not current_type:
                    continue

                # Check for upgrade path
                next_type = f"{current_type} 2"
                if next_type not in presets:
                    return False

                # Spend resources
                for resource_name, amount in blueprint.cost.items():
                    if not resources.spend_resource(resource_name, amount):
                        return False

                # Create upgraded tower
                old_type = current_type
                new_tower = create_tower((int(tower.pos.x), int(tower.pos.y)), next_type)
                self.towers[i] = new_tower

                # Emit event
                if self.events:
                    self.events.emit(
                        GameEvent.TOWER_UPGRADED,
                        TowerUpgradedEvent(
                            tower=new_tower,
                            position=(int(tower.pos.x), int(tower.pos.y)),
                            old_type=old_type,
                            new_type=next_type,
                        ),
                    )

                return True

        return False

    def can_build_at(
        self,
        position: tuple[int, int],
        blueprint: BuildingBlueprint,
        resources: ResourcesManager,
        road_segments: list[tuple[tuple[int, int], tuple[int, int]]],
        road_thickness: int = 100,
    ) -> bool:
        """Check if a building can be placed at position."""
        candidate_rect = pg.Rect(position[0], position[1], blueprint.width, blueprint.height)

        # Check collision with existing buildings
        for existing_rect in self.building_rects:
            if candidate_rect.colliderect(existing_rect):
                return False

        # Check distance from roads
        center_x = candidate_rect.centerx
        center_y = candidate_rect.centery

        for start, end in road_segments:
            dist = self._point_to_segment_distance(
                center_x, center_y, start[0], start[1], end[0], end[1]
            )
            if dist < (blueprint.width / 2 + road_thickness / 2):
                return False

        # Check affordability
        if not resources.can_afford(blueprint.cost):
            return False

        return True

    def try_build(
        self,
        mouse_pos: tuple[int, int],
        blueprint: BuildingBlueprint,
        resources: ResourcesManager,
        road_segments: list[tuple[tuple[int, int], tuple[int, int]]],
    ) -> bool:
        """Attempt to build at mouse position. Returns True if successful."""
        if not self.can_build_at(mouse_pos, blueprint, resources, road_segments):
            return False

        if blueprint.build_function and callable(blueprint.build_function):
            result: bool = blueprint.build_function(mouse_pos, blueprint, resources)
            return result

        print(f"Error: Blueprint '{blueprint.name}' has no valid build_function")
        return False

    def draw_factories(self, surface: pg.Surface) -> None:
        """Draw all factories."""
        for factory in self.factories:
            factory.draw(surface)

    def draw_towers(self, surface: pg.Surface, show_range: bool = False) -> None:
        """Draw all towers."""
        for tower in self.towers:
            tower.draw(surface, show_range)

    def update_factories(self, dt: float, resources: ResourcesManager) -> None:
        """Update all factories."""
        for factory in self.factories:
            factory.update(dt)

    def update_towers(self, dt: float, enemies: list, projectiles: list) -> None:
        """Update all towers."""
        for tower in self.towers:
            tower.update(dt)
            tower.attack(enemies, projectiles)

    def give_factory_payouts(self, resources: ResourcesManager) -> None:
        """Give end-of-wave payouts from all factories."""
        for factory in self.factories:
            resource_type, amount = factory.get_wave_payout()
            resources.add_resource(resource_type, amount)

    @staticmethod
    def generate_road_segments(
        waypoints_dict: dict[str, list[tuple[int, int]]]
    ) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        """Convert waypoints to road segments."""
        segments = []
        for points in waypoints_dict.values():
            for i in range(len(points) - 1):
                segments.append((points[i], points[i + 1]))
        return segments

    @staticmethod
    def _point_to_segment_distance(
        px: float, py: float, x1: float, y1: float, x2: float, y2: float
    ) -> float:
        """Calculate distance from point to line segment."""
        line_vec = pg.Vector2(x2 - x1, y2 - y1)
        point_vec = pg.Vector2(px - x1, py - y1)

        line_len_sq = line_vec.length_squared()
        if line_len_sq == 0:
            return point_vec.length()

        t = max(0, min(1, line_vec.dot(point_vec) / line_len_sq))
        closest = pg.Vector2(x1, y1) + t * line_vec

        return closest.distance_to(pg.Vector2(px, py))
