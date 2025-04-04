from enemy.enemy import Enemy
import pygame as pg

class EnemyRanged(Enemy):
    def __init__(self, waypoints):
        super().__init__(waypoints)
        #Attack
        self.attack_type = "r"
        self.damage_multiplier = 1.5
        self.attack_range = 100 

