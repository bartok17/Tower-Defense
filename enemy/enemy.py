import time
import pygame as pg
import math 
import enemy.abstractEnemyAbilities as aea 
from enemy.abilities import Abilities
import constants as con
_enemy_font = None

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

        self.is_invisible = False
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
        self.disabled_abilities = {"active": False, "timer": 0.0, "expires_in": 0.0}
        self._pre_rendered_shape = None 
        self._render_shape() 

    def _render_shape(self):
        # Pre-render the enemy's shape onto a Surface for efficient drawing.
        r, g, b = self.color
        draw_alpha = 255
        if self.has_ability(aea.invisibleAbility):
            draw_alpha = 60

        self._pre_rendered_shape = pg.Surface((self.radius * 2, self.radius * 2), pg.SRCALPHA)
        self._pre_rendered_shape.fill((0,0,0,0))

        if self.shape == "circle":
            pg.draw.circle(self._pre_rendered_shape, (r, g, b, draw_alpha), (self.radius, self.radius), self.radius)
        elif self.shape == "square":
            pg.draw.rect(self._pre_rendered_shape, (r, g, b, draw_alpha), (0, 0, self.radius * 2, self.radius * 2))
        elif self.shape == "triangle":
            points = [
                (self.radius, 0),
                (0, self.radius * 2),
                (self.radius * 2, self.radius * 2)
            ]
            pg.draw.polygon(self._pre_rendered_shape, (r, g, b, draw_alpha), points)
        elif self.shape == "hexagon":
            points = []
            for i in range(6):
                angle_rad = i * math.pi / 3
                x = self.radius + self.radius * math.cos(angle_rad)
                y = self.radius + self.radius * math.sin(angle_rad)
                points.append((x, y))
            pg.draw.polygon(self._pre_rendered_shape, (r, g, b, draw_alpha), points)
        elif self.shape == "glitch_hex":
            glitch_values = [-2, 1.5, -1, 2.5, -0.5, 0.8]
            points = []
            for i in range(6):
                angle_rad = i * math.pi / 3
                glitch = glitch_values[i % len(glitch_values)]
                x = self.radius + (self.radius + glitch) * math.cos(angle_rad)
                y = self.radius + (self.radius + glitch) * math.sin(angle_rad)
                points.append((x, y))
            pg.draw.polygon(self._pre_rendered_shape, (r, g, b, draw_alpha), points, width=2)

    def update(self, clock_tick=0): 
        # Move towards the next waypoint if not at the end.
        if self.curr_waypoint + 1 < len(self.waypoints):
            next_target = pg.Vector2(self.waypoints[self.curr_waypoint + 1])
            direction = (next_target - self.pos).normalize()
            self.pos += direction * self.speed * (clock_tick / 20.0)
            if self.pos.distance_to(next_target) < self.speed * (clock_tick / 20.0):
                self.pos = next_target
                self.curr_waypoint += 1
        
        if self.abilities:
            self.abilities.update_all(self, clock_tick)
        
        # Update floating texts (e.g., damage numbers).
        for ft in self.special_texts[:]:
            ft["lifetime"] -= clock_tick / 1000.0
            ft["pos"].y -= 0.2 
            if ft["lifetime"] <= 0:
                self.special_texts.remove(ft)
        if self.disabled_abilities["active"]:
            self.disabled_abilities["timer"] += clock_tick
            if self.disabled_abilities["timer"] >= self.disabled_abilities["expires_in"] * 1000:
                self.disabled_abilities["active"] = False
                self.disabled_abilities["timer"] = 0.0

    def draw(self, map_surface):
        # Draw the enemy and any floating texts.
        if self._pre_rendered_shape:
            map_surface.blit(self._pre_rendered_shape, (self.pos.x - self.radius, self.pos.y - self.radius))
        
        global _enemy_font 
        if _enemy_font is None: 
            _enemy_font = pg.font.Font(None, 24)

        for ft in self.special_texts:
            alpha = int(255 * (ft["lifetime"] / 1.0)) 
            surface = _enemy_font.render(ft["text"], True, ft["color"])
            surface.set_alpha(alpha)
            map_surface.blit(surface, (ft["pos"].x, ft["pos"].y - 20))
        if self.has_ability(aea.BossAbility):
            bar_width = 600
            bar_height = 25
            bar_x = (con.SCREEN_WIDTH - bar_width) // 2
            bar_y = 20
            pg.draw.rect(map_surface, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            hp_perc = self.health / self.max_health
            pg.draw.rect(map_surface, (255, 0, 255), (bar_x, bar_y, bar_width * hp_perc, bar_height))
            boss_font = pg.font.Font(None, 32)
            text_surface = boss_font.render("BOSS - 404", True, (255, 255, 255))
            map_surface.blit(text_surface, (bar_x + 10, bar_y - 28))

    def take_damage(self, value, damage_type="physical"):
        # Apply damage after reductions from armor or magic resistance.
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
        return self.health <= 0

    def distance_to_end(self):
        # Return the remaining distance to the last waypoint.
        total_distance = 0
        current_position = self.pos
        for i in range(self.curr_waypoint + 1, len(self.waypoints)):
            next_waypoint = pg.Vector2(self.waypoints[i])
            total_distance += current_position.distance_to(next_waypoint)
            current_position = next_waypoint
        return total_distance

    def has_finished(self):
        # True if the enemy has reached the final waypoint.
        return self.curr_waypoint >= len(self.waypoints) - 1

    def add_incoming_damage(self, amount):
        self.incoming_damage += amount

    def remove_incoming_damage(self, amount):
        self.incoming_damage -= amount
        if self.incoming_damage < 0:
            self.incoming_damage = 0

    def get_effective_health(self):
        # Health after accounting for incoming damage.
        return self.health - self.incoming_damage
        
    def has_ability(self, ability_type):
        # Check if the enemy has a specific ability.
        return any(isinstance(a, ability_type) for a in self.abilities.abilities)
