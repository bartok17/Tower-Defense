"""
Economy system - Resource management.

Handles player resources like gold, wood, metal, and health.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.event_manager import EventManager


class ResourcesManager:
    """Manages player resources (gold, wood, metal, health)."""

    def __init__(
        self,
        initial_gold: int = 100,
        initial_wood: int = 50,
        initial_metal: int = 25,
        initial_health: int = 100,
        events: "EventManager | None" = None,
    ) -> None:
        self.resources: dict[str, int] = {
            "health": initial_health,
            "gold": initial_gold,
            "wood": initial_wood,
            "metal": initial_metal,
        }
        self.events: "EventManager | None" = events

    def _emit_change(self, resource_type: str, old_value: int, new_value: int) -> None:
        """Emit a resource change event if events are configured."""
        if self.events:
            from ..core.event_manager import GameEvent, ResourceChangedEvent

            self.events.emit(
                GameEvent.RESOURCE_CHANGED,
                ResourceChangedEvent(
                    resource_type=resource_type,
                    old_value=old_value,
                    new_value=new_value,
                    change=new_value - old_value,
                ),
            )

    def get_resource(self, resource_type: str) -> int:
        return self.resources.get(resource_type, 0)

    def add_resource(self, resource_type: str, amount: int) -> None:
        if resource_type in self.resources:
            old_value = self.resources[resource_type]
            self.resources[resource_type] += amount
            self._emit_change(resource_type, old_value, self.resources[resource_type])

    def spend_resource(self, resource_type: str, amount: int) -> bool:
        """Spend resource if available. Returns True if spent."""
        if resource_type not in self.resources:
            return False

        if self.resources[resource_type] >= amount:
            old_value = self.resources[resource_type]
            self.resources[resource_type] -= amount
            self._emit_change(resource_type, old_value, self.resources[resource_type])
            return True

        # Emit insufficient event
        if self.events:
            from ..core.event_manager import GameEvent, ResourceInsufficientEvent

            self.events.emit(
                GameEvent.RESOURCE_INSUFFICIENT,
                ResourceInsufficientEvent(
                    resource_type=resource_type,
                    required=amount,
                    available=self.resources[resource_type],
                ),
            )

        return False

    def can_afford(self, costs: dict[str, int]) -> bool:
        for resource_type, amount in costs.items():
            if self.get_resource(resource_type) < amount:
                return False
        return True

    def spend_multiple(self, costs: dict[str, int]) -> bool:
        """Spend multiple resources atomically. Returns True if all spent."""
        if not self.can_afford(costs):
            return False

        for resource_type, amount in costs.items():
            self.spend_resource(resource_type, amount)

        return True

    @property
    def health(self) -> int:
        return self.resources.get("health", 0)

    @property
    def gold(self) -> int:
        return self.resources.get("gold", 0)

    @property
    def wood(self) -> int:
        return self.resources.get("wood", 0)

    @property
    def metal(self) -> int:
        return self.resources.get("metal", 0)

    def is_dead(self) -> bool:
        return self.health <= 0
