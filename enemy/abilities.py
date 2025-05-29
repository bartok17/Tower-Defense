import pygame as pg
import enemy.abstractEnemyAbilities as aea

class Abilities:
    def __init__(self):
        self.abilities = []


    def add_ability(self, ability_name):
        abilities_dict = {
            "magic_resistant": aea.MagicResistantAbility(),
            "ranged": aea.RangedAbility(),
            "fast": aea.FastAbility(),
            "tank": aea.TankAbility(),
            "summoner1": aea.SummonerAbility(4, "6"),
            "healer": aea.HealerAbility(5),
            "boss": aea.Boss(),
            "invisible": aea.invisibleAbility(),
        }
        if ability_name in abilities_dict:
            self.abilities.append(abilities_dict[ability_name])  

    def apply_all(self, enemy):
        for ability in enemy.abilities.abilities:
            ability.apply(enemy)

    def update_all(self, enemy, clock_tick):
        for ability in self.abilities:
            ability.on_update(enemy, clock_tick)
