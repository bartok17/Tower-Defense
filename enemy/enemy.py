import pygame as pg
import enemy.abstractEnemyAbilities as aea
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
        self.special_texts = []
        self.incoming_damage = 0
        self.gold_reward = template.get("gold_reward", 5)

    def update(self, clock_tick=0):
        if self.curr_waypoint + 1 < len(self.waypoints):
            next_target = pg.Vector2(self.waypoints[self.curr_waypoint + 1])
            direction = (next_target - self.pos).normalize()
            self.pos += direction * self.speed
            if self.pos.distance_to(next_target) < self.speed:
                self.pos = next_target
                self.curr_waypoint += 1
        if self.abilities:
            self.abilities.update_all(self, clock_tick)
        for ft in self.special_texts[:]:
            ft["lifetime"] -= clock_tick / 1000.0
            ft["pos"].y -= 0.2 
            if ft["lifetime"] <= 0: self.special_texts.remove(ft)

    def draw(self, map_surface):
        r, g, b = self.color
        draw_alpha = 255
        if self.has_ability(aea.invisibleAbility):
            draw_alpha = 60

        shape_surface = pg.Surface((self.radius * 2, self.radius * 2), pg.SRCALPHA)
        if self.shape == "circle":
            pg.draw.circle(shape_surface, (r, g, b, draw_alpha), (self.radius, self.radius), self.radius)
        elif self.shape == "square":
            pg.draw.rect(shape_surface, (r, g, b, draw_alpha), (0, 0, self.radius * 2, self.radius * 2))
        elif self.shape == "triangle":
            points = [
                (self.radius, 0),
                (0, self.radius * 2),
                (self.radius * 2, self.radius * 2)
            ]
            pg.draw.polygon(shape_surface, (r, g, b, draw_alpha), points)
        map_surface.blit(shape_surface, (self.pos.x - self.radius, self.pos.y - self.radius))
        font = pg.font.Font(None, 24)
        for ft in self.special_texts:
            alpha = int(255 * (ft["lifetime"] / 1.0))
            surface = font.render(ft["text"], True, ft["color"])
            surface.set_alpha(alpha)
            map_surface.blit(surface, (ft["pos"].x, ft["pos"].y - 20))

    def take_damage(self, value):
        self.health -= value
        if self.health <= 0:
            self.health = 0

    def is_dead(self):
        return self.health <= 0

    def distance_to_end(self):
        total_distance = 0
        current_position = self.pos
        for i in range(self.curr_waypoint + 1, len(self.waypoints)):
            next_waypoint = pg.Vector2(self.waypoints[i])
            total_distance += current_position.distance_to(next_waypoint)
            current_position = next_waypoint
        return total_distance

    def has_finished(self):
        return self.curr_waypoint >= len(self.waypoints) - 1

    def add_incoming_damage(self, amount):
        self.incoming_damage += amount

    def remove_incoming_damage(self, amount):
        self.incoming_damage -= amount
        if self.incoming_damage < 0:
            self.incoming_damage = 0

    def get_effective_health(self):
        # Health after accounting for incoming damage
        return self.health - self.incoming_damage
    def has_ability(self, ability_type):
        return any(isinstance(a, ability_type) for a in self.abilities.abilities)