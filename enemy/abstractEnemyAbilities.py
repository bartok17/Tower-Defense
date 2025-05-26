from math import inf


class EnemyAbility:
    def apply(self, enemy):
        pass

    def on_update(self, enemy):
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

class HealerAbility(EnemyAbility):
    def __init__(self, heal_amount):
        self.heal_amount = heal_amount
    #Implementation needed

class TankAbility(EnemyAbility):
    def apply(self, enemy):
        enemy.armor += 4
        enemy.max_health *= 2
        enemy.health *= 2
        enemy.speed -= 0.5

class SummonerAbility(EnemyAbility):
    def __init__(self, summon_count, summon_type):
        self.summon_type = summon_type
        self.summon_count = summon_count
    #Implementation needed

class invisibleAbility(EnemyAbility):
    def __init__(self, duration):
        self.duration = duration
    #Implementation needed
