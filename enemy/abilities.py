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
            "summoner": aea.SummonerAbility(1, "enemy"),
            "healer": aea.HealerAbility(10),
            "boss": aea.Boss(),
            "invisible": aea.invisibleAbility(5),
        }
        if ability_name in self.abilities:
            self.abilities.append(abilities_dict[ability_name])
    def apply_all(self, enemy):
        for ability in enemy.abilities.abilities:
            ability.apply(enemy)

    def update_all(self, enemy):
        for ability in enemy.abilities.abilities:
            ability.update(enemy)
