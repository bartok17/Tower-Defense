import time
import pygame as pg
from economy.resourcesManager import ResourcesManager


class PlayerAbilities:
    def __init__(self):
        self.selected_skill = None
        self.costs = {
            "fireball": {"gold": 70},
            "scanner": {"gold": 30, "metal": 15, "wood": 15},
            "disruptor" : {"gold": 100, "metal": 30, "wood": 30},
            "glue": {"gold": 10, "wood": 50}
        }
        self.active_effects = {
            "scanner": {
                "active": False,
                "start_time": 0,
                "duration": 5.0
            },
            "glue": {
                "active": False,
                "start_time": 0,
                "duration": 5.0,
                "pos": None
            },
        }
        self.pos = None
        self.last_target_pos = None
        self.recent_strike_timer = 0

    def can_use(self, name, resources_manager):
        return resources_manager.can_afford(self.costs.get(name, {}))

    def use(self, name, resources_manager, pos=None, enemies=None):
        if pos is None:
            self.selected_skill = name
            return False  
        if not self.can_use(name, resources_manager):
            return False
        resources_manager.spend_multiple(self.costs[name])
        if name == "fireball":
            self.fireball(pos, enemies)
        elif name == "scanner":
            self.activate_scanner()
        elif name == "disruptor":
            self.activate_disruptor(pos, enemies)
        elif name == "glue":
            self.activate_glue(pos)
        self.selected_skill = None
        
        return True


    def fireball(self, pos, enemies):
        self.last_target_pos = pg.Vector2(pos)
        self.recent_strike_timer = 0.5
        radius = 80
        damage = 100
        for e in enemies:
            if e.pos.distance_to(pg.Vector2(pos)) <= radius:
                e.take_damage(damage)

    def activate_scanner(self):
        self.active_effects["scanner"]["active"] = True
        self.active_effects["scanner"]["start_time"] = time.time()
        self.pos = pg.Vector2(pg.mouse.get_pos())
    def activate_glue(self, pos):
        self.active_effects["glue"]["active"] = True
        self.active_effects["glue"]["start_time"] = time.time()
        self.active_effects["glue"]["pos"] = pg.Vector2(pos)

    def activate_disruptor(self, pos, enemies):
        radius = 120
        duration = 10.0
        center = pg.Vector2(pos)

        for enemy in enemies:
            if enemy.pos.distance_to(center) <= radius:
                enemy.disabled_abilities = {
                    "active": True,
                    "expires_at": time.time() + duration
                }
                if hasattr(enemy, 'special_texts'):
                    enemy.special_texts.append({
                        "text": "Silenced!",
                        "pos": enemy.pos.copy(),
                        "lifetime": 1.0,
                        "color": (255, 255, 0)
                    })
        self.last_target_pos = center
        self.active_effects["disruptor"] = {
            "active": True,
            "start_time": time.time(),
            "duration": duration
        }

    def update(self, enemies, tick):
        if self.recent_strike_timer > 0:
            self.recent_strike_timer -= tick
            if self.recent_strike_timer < 0:
                self.recent_strike_timer = 0
                self.last_target_pos = None
        scanner = self.active_effects["scanner"]
        if scanner["active"] and self.pos:
            now = time.time()
            if now - scanner["start_time"] > scanner["duration"]:
                scanner["active"] = False
                self.pos = None
            else:
                scanner_radius = 150
                for e in enemies:
                    if getattr(e, "is_invisible", False):
                        if pg.Vector2(e.pos).distance_to(self.pos) <= scanner_radius:
                            e.abilities.remove_ability("invisible")
                            e.is_invisible = False
        dis = self.active_effects.get("disruptor", {})
        if dis.get("active", False):
            if time.time() - dis["start_time"] > dis["duration"]:
                dis["active"] = False
                self.last_target_pos = None
        glue = self.active_effects["glue"]
        if glue["active"] and glue["pos"]:
            now = time.time()
            if now - glue["start_time"] > glue["duration"]:
                glue["active"] = False
                glue["pos"] = None
            else:
                radius = 100
                for e in enemies:
                    if e.pos.distance_to(glue["pos"]) <= radius and not hasattr(e, "was_glued"):
                        e.speed *= 0.70
                        e.was_glued = True
                        if hasattr(e, "special_texts"):
                            e.special_texts.append({
                                "text": "Slowed",
                                "pos": e.pos.copy(),
                                "lifetime": 1.0,
                                "color": (100, 150, 255)
                            })


    def draw(self, screen):
        if self.last_target_pos and self.recent_strike_timer > 0:
            radius = 80
            color = (255, 50, 0)
            pg.draw.circle(screen, color, (int(self.last_target_pos.x), int(self.last_target_pos.y)), radius, 3)
        if self.active_effects["scanner"]["active"] and self.pos:
            radius = 150
            alpha = 80  
            overlay = pg.Surface((radius * 2, radius * 2), pg.SRCALPHA)
            pg.draw.circle(overlay, (0, 200, 0, alpha), (radius, radius), radius, 3)
            screen.blit(overlay, (self.pos.x - radius, self.pos.y - radius))
        if self.active_effects.get("disruptor", {}).get("active", False) and self.last_target_pos:
            radius = 120
            alpha = 90
            overlay = pg.Surface((radius * 2, radius * 2), pg.SRCALPHA)
            pg.draw.circle(overlay, (255, 255, 0, alpha), (radius, radius), radius, 3)
            screen.blit(overlay, (self.last_target_pos.x - radius, self.last_target_pos.y - radius))
        if self.active_effects.get("glue", {}).get("active", False) and self.active_effects.get("glue", {}).get("pos"):
            radius = 100
            alpha = 60
            overlay = pg.Surface((radius * 2, radius * 2), pg.SRCALPHA)
            pg.draw.circle(overlay, (120, 120, 255, alpha), (radius, radius), radius, 3)
            screen.blit(overlay, (self.active_effects.get("glue", {})["pos"].x - radius, self.active_effects.get("glue", {})["pos"].y - radius))