import json
from math import inf
import random
class EnemyAbility:
    def apply(self, enemy, clock_tick=0):
        pass

    def on_update(self, enemy, clock_tick=0):
        pass

class FastAbility(EnemyAbility):
    def apply(self, enemy):
        enemy.speed += 1

class MagicResistantAbility(EnemyAbility):
    def apply(self, enemy):
        enemy.magic_resistance = inf

class RangedAbility(EnemyAbility):
    def apply(self, enemy):
        enemy.attack_range += 50
class Boss(EnemyAbility):
    pass #Implementation needed

import pygame as pg

class HealerAbility(EnemyAbility):
    def __init__(self, heal_amount, range=150, cooldown=3.0):
        self.heal_amount = heal_amount
        self.range = range
        self.cooldown = cooldown  
        self.timer = 0.0  

    def on_update(self, enemy, clock_tick):
        self.timer += clock_tick / 1000.0 
        if self.timer < self.cooldown:
            return

        self.timer = 0.0
        if not hasattr(enemy, 'pos') or not hasattr(enemy, 'all_enemies'):
            return

        nearby = [
            e for e in enemy.all_enemies
            if not e.is_dead() and e != enemy and e.health < e.max_health
            and enemy.pos.distance_to(e.pos) <= self.range
        ]
        if not nearby:
            return

        target = min(nearby, key=lambda e: e.health / e.max_health)
        target.health = min(target.max_health, target.health + self.heal_amount)
        if hasattr(target, 'special_texts'):
            target.special_texts.append({
                "text": f"+{self.heal_amount}",
                "pos": target.pos.copy(),
                "lifetime": 1.0, 
                "color": (0, 255, 0)
            })

class TankAbility(EnemyAbility):
    def apply(self, enemy):
        enemy.armor += 4
        enemy.max_health *= 2
        enemy.health *= 2
        enemy.speed -= 0.5

class SummonerAbility(EnemyAbility):
    def __init__(self, summon_count, summon_type, cooldown=5.0):
        self.summon_count = summon_count
        self.summon_type = summon_type
        self.cooldown = cooldown
        self.timer = 0.0

    def on_update(self, enemy, clock_tick):
        from enemy.enemy import Enemy
        self.timer += clock_tick / 1000.0
        if self.timer < self.cooldown:
            return

        self.timer = 0.0

        if not hasattr(enemy, "all_enemies"):
            return
        with open("data/enemyTemplates.json") as f:
            templates = json.load(f)
        template = templates[self.summon_type]
        for _ in range(self.summon_count):
            start = pg.Vector2(enemy.pos)
            loop = [
                start,
                start + pg.Vector2(30, 0).rotate(random.uniform(0, 360)),
                start + pg.Vector2(30, 0).rotate(random.uniform(0, 360)),
                start + pg.Vector2(30, 0).rotate(random.uniform(0, 360)),
                start  # powrót
            ]
            if enemy.curr_waypoint + 1 < len(enemy.waypoints):
                resume_path = enemy.waypoints[enemy.curr_waypoint + 1:]
            else: resume_path = []
            path = loop + [pg.Vector2(p) for p in resume_path]
            new_enemy = Enemy(path, template)
            new_enemy.all_enemies = enemy.all_enemies
            enemy.all_enemies.append(new_enemy)

            enemy.special_texts.append({
                "text": "Summon!",
                "pos": enemy.pos.copy(),
                "lifetime": 1.0,
                "color": (150, 150, 255)
            })



class invisibleAbility(EnemyAbility):
    def apply(self, enemy):
        enemy.is_invisible = True

