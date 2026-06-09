import numpy as np
import random
class all_weapons():
    static_used = []
    def __init__(self,weapons={}):
        self.weapons = weapons
    def get_r_weapon(self):
        weapon_keys = list(self.weapons.keys())
        weapon = random.choice(weapon_keys)
        while weapon in self.static_used:
            weapon = random.choice(weapon_keys)
        self.static_used.append(weapon)
        return weapon
    def reset(self):
        self.static_used = []    