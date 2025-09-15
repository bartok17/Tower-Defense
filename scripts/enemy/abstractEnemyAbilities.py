import json
from math import inf
import random
import os
from .. import constants as root_project_constants
from .. import constants as con
import pygame as pg

_loaded_enemy_templates = None

def _get_enemy_templates():
    global _loaded_enemy_templates
    if _loaded_enemy_templates is None:
        file_path = os.path.join(root_project_constants.DATA_DIR, "enemyTemplates.json")
        try:
            with open(file_path) as f:
                _loaded_enemy_templates = json.load(f)
        except FileNotFoundError:
            print(f"ERROR: Could not find enemyTemplates.json at {file_path}")
            _loaded_enemy_templates = {}
        except json.JSONDecodeError:
            print(f"ERROR: Could not decode enemyTemplates.json at {file_path}")
            _loaded_enemy_templates = {}
    return _loaded_enemy_templates

class EnemyAbility:
    def apply(self, enemy, clock_tick=0):
        pass

    def on_update(self, enemy, clock_tick=0):
        if getattr(enemy, "disabled_abilities", {}).get("active", False):
            return  


class FastAbility(EnemyAbility):
    def apply(self, enemy):
        enemy.speed += 1

class MagicResistantAbility(EnemyAbility):
    def apply(self, enemy):
        enemy.magic_resistance = inf

class RangedAbility(EnemyAbility):
    def apply(self, enemy):
        enemy.attack_range += 50

class HealerAbility(EnemyAbility):
    def __init__(self, heal_amount, range=150, cooldown=3.0):
        self.heal_amount = heal_amount
        self.range = range
        self.cooldown = cooldown  
        self.timer = 0.0  

    def on_update(self, enemy, clock_tick):
        if getattr(enemy, "disabled_abilities", {}).get("active", False):
            return  

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

        # Heal the most injured nearby ally (lowest health ratio)
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
    def __init__(self, summon_count, summon_type_id, cooldown=5.0):
        self.summon_count = summon_count
        self.summon_type_id = str(summon_type_id)
        self.cooldown = cooldown
        self.timer = 0.0

    def on_update(self, enemy, clock_tick):
        if getattr(enemy, "disabled_abilities", {}).get("active", False):
            return  
        from scripts.enemy.enemy import Enemy
        self.timer += clock_tick / 1000.0
        if self.timer < self.cooldown:
            return

        self.timer = 0.0

        if not hasattr(enemy, "all_enemies"):
            return
        
        templates = _get_enemy_templates()
        template = templates.get(self.summon_type_id)
        if not template:
            print(f"Warning: SummonerAbility could not find template for ID {self.summon_type_id}")
            return

        for _ in range(self.summon_count):
            start = pg.Vector2(enemy.pos)
            # Create a short loop path before resuming normal path
            loop = [
                start,
                start + pg.Vector2(30, 0).rotate(random.uniform(0, 360)),
                start + pg.Vector2(30, 0).rotate(random.uniform(0, 360)),
                start + pg.Vector2(30, 0).rotate(random.uniform(0, 360)),
                start 
            ]
            if enemy.curr_waypoint + 1 < len(enemy.waypoints):
                resume_path = enemy.waypoints[enemy.curr_waypoint + 1:]
            else:
                resume_path = []
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
    def __init__(self):
        self.name = "invisible"
    def apply(self, enemy):
        enemy.is_invisible = True

class BossAbility(EnemyAbility):
    def __init__(self):
        self.name = "boss"
        self.stage = 1
        self.phase_timer = 0
        self.phase_cooldown = 5.0
        self.glitch_spawn_timer = 0
        self.active_glitches = []
        
    def apply(self, enemy):
        enemy.abilities.add_ability("invisible")
        enemy.is_invisible = True
    def on_update(self, enemy, clock_tick):
        clock_tick = clock_tick / 1000.0
        if enemy.health < (enemy.max_health * 0.8): 
            enemy.abilities.remove_ability("invisible")
            enemy.is_invisible = False
            self.stage = 2
        if enemy.health < (enemy.max_health * 0.6):
            self.stage = 20
        if self.stage>1:
            clock_tick = clock_tick 
            self.phase(enemy, clock_tick)
            self.glitch_spawn_timer += clock_tick
            if self.glitch_spawn_timer >= 0.15:  
                self.glitch_spawn_timer = 0
                self.glitch()
        for glitch in self.active_glitches[:]:
            glitch["time"] -= clock_tick
            if glitch["time"] <= 0:
                self.active_glitches.remove(glitch)
    def phase(self, enemy, clock_tick):
        
        self.phase_timer += clock_tick
        if self.phase_timer >= self.phase_cooldown:
            self.phase_timer = 0
            self.phase_cooldown = random.randint(1, 3)
            if enemy.curr_waypoint > 0:
                enemy.curr_waypoint -= 1
                enemy.pos = pg.Vector2(enemy.waypoints[enemy.curr_waypoint])
                self.summon_nearby(enemy, count=7)

    def glitch(self):
        for i in range(self.stage * 3): 
            glitch = {
                "pos": pg.Vector2(random.randint(0, root_project_constants.SCREEN_WIDTH), random.randint(0, root_project_constants.SCREEN_HEIGHT)),
                "size": random.randint(10, 40),
                "color": random.choice([(255, 0, 255), (0, 255, 255), (150, 0, 255)]),
                "time": 0.3  
            }
            self.active_glitches.append(glitch)

    def summon_nearby(self, enemy, count=7, radius=40):
        from scripts.enemy.enemy import Enemy
        import os, json
        template_path = os.path.join(con.DATA_DIR, "enemyTemplates.json")
        with open(template_path, "r") as f:
            templates = json.load(f)
        template = templates.get("1") 
        for _ in range(count):
            start = pg.Vector2(enemy.pos)
            loop = [
                start,
                start + pg.Vector2(radius, 0).rotate(random.uniform(0, 360)),
                start + pg.Vector2(radius, 0).rotate(random.uniform(0, 360)),
                start + pg.Vector2(radius, 0).rotate(random.uniform(0, 360)),
                start
            ]
            if enemy.curr_waypoint + 1 < len(enemy.waypoints):
                resume_path = enemy.waypoints[enemy.curr_waypoint + 1:]
            else:
                resume_path = []

            path = loop + [pg.Vector2(p) for p in resume_path]
            new_enemy = Enemy(path, template)
            new_enemy.all_enemies = enemy.all_enemies
            enemy.all_enemies.append(new_enemy)

            enemy.special_texts.append({
                "text": "PHASE SUMMON",
                "pos": enemy.pos.copy(),
                "lifetime": 1.0,
                "color": (200, 100, 255)
            })

class DashAbility(EnemyAbility):
    def __init__(self, speed_multiplier=2.0, dash_duration=1.0, cooldown=5.0):
        self.speed_multiplier = speed_multiplier
        self.dash_duration = dash_duration
        self.cooldown = cooldown
        self.timer = 0.0
        self.dashing = False
        self.dash_timer = 0.0

    def apply(self, enemy):
        self.original_speed = getattr(enemy, "speed", 1.0)

    def on_update(self, enemy, clock_tick):
        if getattr(enemy, "disabled_abilities", {}).get("active", False):
            return

        dt = clock_tick / 1000.0
        self.timer += dt

        if self.dashing:
            self.dash_timer += dt
            if self.dash_timer >= self.dash_duration:
                enemy.speed = self.original_speed
                self.dashing = False
                self.dash_timer = 0.0
        elif self.timer >= self.cooldown:
            self.original_speed = getattr(enemy, "speed", 1.0)
            enemy.speed = self.original_speed * self.speed_multiplier
            self.dashing = True
            self.dash_timer = 0.0
            self.timer = 0.0
            if hasattr(enemy, "special_texts"):
                enemy.special_texts.append({
                    "text": "DASH!",
                    "pos": enemy.pos.copy(),
                    "lifetime": 0.7,
                    "color": (255, 200, 50)
                })
