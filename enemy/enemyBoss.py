from enemy.enemy import Enemy
import pygame as pg

class EnemyBoss(Enemy):
    def __init__(self, waypoints):
        super().__init__(waypoints)

