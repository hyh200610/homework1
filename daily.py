import random
class dailynew:
    def __init__(self,name,all_weapons):
        self.name = name
        self.all_weapons = all_weapons
    def refresh_your_store(self):
        for i in range(4):
            weapon = random.choice(self.all_weapons)
            print(weapon)
        

