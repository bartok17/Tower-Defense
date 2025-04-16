import pygame as pg

class Abilities:
    def __init__(self):
        self.abilities = {
            "magic_resistant": False,
            "ranged": False,
            "boss": False,
            "fast": False,
            "slow": False,
            "healer": False,
            "tank": False,
            "summoner": False,
        }


    def add_ability(self, ability_name):
        if ability_name in self.abilities:
            self.abilities[ability_name] = True

