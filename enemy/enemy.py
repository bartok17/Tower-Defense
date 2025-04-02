import pygame as pg

class Enemy:
    def __init__(self, waypoints):
        #Movement
        self.waypoints = waypoints  
        self.curr_waypoint = 0      
        self.pos = pg.Vector2(waypoints[0]) 
        self.speed = 2            
        #Health and damage reduction multipliers
        self.health = 300
        self.max_health = 300
        self.armor = 1
        self.magic_resistance = 1
        #Attack
        self.attack_type = "s" #s-standard, r-ranged, m-magic
        self.damage_multiplier = 1
        self.damage = 10 * self.damage_multiplier
        self.attack_speed = 1.0
        self.attack_cooldown = 0
        self.attack_range = 50


    def update(self):
        if self.curr_waypoint + 1 < len(self.waypoints):
            next_target = pg.Vector2(self.waypoints[self.curr_waypoint + 1])
            direction = (next_target - self.pos).normalize()
            self.pos += direction * self.speed
            if self.pos.distance_to(next_target) < self.speed:
                self.pos = next_target
                self.curr_waypoint += 1
                
    def draw(self, map_surface):
        r = 255 * (1 - self.health/self.max_health)
        g = 255 * (self.health/self.max_health)
        b = 0
        pg.draw.circle(map_surface, (r, g, b), (int(self.pos.x), int(self.pos.y)), 10)

    def take_damage(self, value):
        self.health -= value
        if self.health <= 0:
            self.health = 0

    def is_dead(self):
        return self.health <= 0