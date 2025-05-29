import pygame as pg
import math
from enemy.abilities import Abilities

class Enemy:
    def __init__(self, waypoints, template):
        self.id = int(template.get("id", 1))
        self.waypoints = waypoints
        self.curr_waypoint = 0
        self.pos = pg.Vector2(waypoints[0])

        self.speed = template.get("speed", 1.0)
        self.health = template.get("health", 300)
        self.max_health = self.health
        self.armor = template.get("armor", 1)
        self.magic_resistance = template.get("magic_resistance", 1)

        self.attack_range = template.get("attack_range", 50)
        self.attack_speed = template.get("attack_speed", 1.0)
        self.attack_cooldown = 0
        self.damage_multiplier = 1
        self.damage = template.get("damage", 10)

        self.abilities = Abilities()
        for name in template.get("abilities", []):
            self.abilities.add_ability(name)
        self.abilities.apply_all(self)

        self.color = tuple(template.get("color", [255, 255, 255]))
        self.radius = template.get("radius", 10)
        self.shape = template.get("shape", "circle")
        self.incoming_damage = 0
        self.gold_reward = template.get("gold_reward", 5)

    def update(self):
        # Move towards the next waypoint
        if self.curr_waypoint + 1 < len(self.waypoints):
            next_target = pg.Vector2(self.waypoints[self.curr_waypoint + 1])
            direction = (next_target - self.pos).normalize()
            self.pos += direction * self.speed
            if self.pos.distance_to(next_target) < self.speed:
                self.pos = next_target
                self.curr_waypoint += 1

    def draw(self, map_surface):
        # Draw the enemy based on its shape
        r, g, b = self.color
        if self.shape == "circle":
            pg.draw.circle(map_surface, (r, g, b), (int(self.pos.x), int(self.pos.y)), self.radius)
        elif self.shape == "square":
            rect = pg.Rect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2, self.radius * 2)
            pg.draw.rect(map_surface, (r, g, b), rect)
        elif self.shape == "triangle":
            points = [
                (self.pos.x, self.pos.y - self.radius),
                (self.pos.x - self.radius, self.pos.y + self.radius),
                (self.pos.x + self.radius, self.pos.y + self.radius)
            ]
            pg.draw.polygon(map_surface, (r, g, b), points)
            angle_offset = math.pi / 6
            points = [
                (
                    self.pos.x + self.radius * math.cos(angle_offset + i * math.pi / 3),
                    self.pos.y + self.radius * math.sin(angle_offset + i * math.pi / 3)
                )
                for i in range(6)
            ]
            pg.draw.polygon(map_surface, (r, g, b), points)
            pg.draw.polygon(map_surface, (r, g, b), points)

    def take_damage(self, value, damage_type="physical"):
        # Apply damage after resistances
        if damage_type == "magic":
            value -= self.magic_resistance
        elif damage_type == "physical":
            value -= self.armor
        if value < 0:
            value = 0
        self.health -= value
        if self.health <= 0:
            self.health = 0

    def is_dead(self):
        # Check if enemy is dead
        return self.health <= 0

    def distance_to_end(self):
        # Calculate distance to the last waypoint
        total_distance = 0
        current_position = self.pos
        for i in range(self.curr_waypoint + 1, len(self.waypoints)):
            next_waypoint = pg.Vector2(self.waypoints[i])
            total_distance += current_position.distance_to(next_waypoint)
            current_position = next_waypoint
        return total_distance

    def has_finished(self):
        # Check if enemy reached the last waypoint
        return self.curr_waypoint >= len(self.waypoints) - 1

    def add_incoming_damage(self, amount):
        # Track incoming damage
        self.incoming_damage += amount

    def remove_incoming_damage(self, amount):
        # Remove tracked incoming damage
        self.incoming_damage -= amount
        if self.incoming_damage < 0:
            self.incoming_damage = 0

    def get_effective_health(self):
        # Health after accounting for incoming damage
        return self.health - self.incoming_damage
