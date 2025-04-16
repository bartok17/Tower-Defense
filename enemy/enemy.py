import pygame as pg

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
        for ability in template.get("abilities", []):
            self.abilities.add_ability(ability)

        self.color = tuple(template.get("color", [255, 255, 255]))
        self.radius = template.get("radius", 10)



    def update(self):
        if self.curr_waypoint + 1 < len(self.waypoints):
            next_target = pg.Vector2(self.waypoints[self.curr_waypoint + 1])
            direction = (next_target - self.pos).normalize()
            self.pos += direction * self.speed
            if self.pos.distance_to(next_target) < self.speed:
                self.pos = next_target
                self.curr_waypoint += 1
                
    def draw(self, map_surface):
        r, g, b = self.color
        pg.draw.circle(map_surface, (r, g, b), (int(self.pos.x), int(self.pos.y)), self.radius)

    def take_damage(self, value):
        self.health -= value
        if self.health <= 0:
            self.health = 0

    def is_dead(self):
        return self.health <= 0
    
    def check_abilities(self, ability):
        pass

