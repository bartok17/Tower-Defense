import pygame as pg

class Enemy:
    def __init__(self, waypoints):
        #Movement
        self.waypoints = waypoints  
        self.curr_waypoint = 0      
        self.pos = pg.Vector2(waypoints[0]) 
        self.speed = 2            
        #Health
        self.health = 100
        self.max_health = 100
        #Attack
        self.damage = 10
        self.attack_speed = 1.0
        self.attack_cooldown = 0
        self.attack_range = 50


    def update(self):
        if self.curr_waypoint + 1 < len(self.waypoints):
            next_target = pg.Vector2(self.waypoints[self.curr_waypoint + 1])
            direction = (next_target - self.pos).normalize()
            self.pos += direction * self.speed

    def draw(self, map_surface):
        r = 255 * (1 - self.health/self.max_health)
        g = 255 * (self.health/self.max_health)
        b = 0
        pg.draw.circle(map_surface, (r, g, b), (int(self.pos.x), int(self.pos.y)), 10)

    def take_damage(self, value):
        self.hp -= value
        if self.hp <= 0:
            self.hp = 0

    def is_dead(self):
        return self.hp > 0