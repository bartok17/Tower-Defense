import time
import pygame as pg
import enemy.abstractEnemyAbilities as aea

class Abilities:
    def __init__(self):
        self.abilities_dict = {
            "magic_resistant": aea.MagicResistantAbility(),
            "ranged": aea.RangedAbility(),
            "fast": aea.FastAbility(),
            "tank": aea.TankAbility(),
            "summoner1": aea.SummonerAbility(4, "6"),
            "summoner2": aea.SummonerAbility(1, "8", cooldown=5.3),
            "healer": aea.HealerAbility(5),
            "invisible": aea.invisibleAbility(),
            "inispeed": aea.DashAbility(4.0, 10.0, 10.0),
            "dash": aea.DashAbility(4.0, 1.0, 3.0),
            "boss": aea.BossAbility()
        }
        self.abilities = []


    def add_ability(self, ability_name):

        if ability_name in self.abilities_dict:
            self.abilities.append(self.abilities_dict[ability_name])  

    def apply_all(self, enemy):
        for ability in enemy.abilities.abilities:
            ability.apply(enemy)

    def update_all(self, enemy, clock_tick):
        if hasattr(enemy, "disabled_abilities") and enemy.disabled_abilities.get("active", False):
            if time.time() > enemy.disabled_abilities["expires_at"]:
                enemy.disabled_abilities["active"] = False
            else: return 
        for ability in self.abilities:
            ability.on_update(enemy, clock_tick)

    def remove_ability(self, name: str):
        self.abilities = [a for a in self.abilities if getattr(a, "name", None) != name]