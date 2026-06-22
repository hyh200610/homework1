import random
from character import AllCharacterManager

class chouka:
    def __init__(self, name="default", baodi=0, dabaodi=0):
        self.name = name
        self.baodi = baodi
        self.dabaodi = dabaodi
        # 初始化角色管理器
        self.char_manager = AllCharacterManager()
        # 加载角色列表
        self._load_characters()
    
    def _load_characters(self):
        # 从角色管理器获取角色列表（包含完整信息）
        self.star6_chars = []
        self.star5_chars = []
        self.star4_chars = []
        
        star6_pool = self.char_manager.get_pool_by_star(6)
        if star6_pool:
            self.star6_chars = star6_pool.characters
        
        star5_pool = self.char_manager.get_pool_by_star(5)
        if star5_pool:
            self.star5_chars = star5_pool.characters
        
        star4_pool = self.char_manager.get_pool_by_star(4)
        if star4_pool:
            self.star4_chars = star4_pool.characters
    
    def set_up(self, up="庄方宜"):
        self.up = up
        # 找到UP角色的完整信息
        self.up_char = next((c for c in self.star6_chars if c.name == up), None)
    
    def set_other6(self, other6=None):
        if other6 is None:
            # 使用默认的6星列表（排除UP角色）
            self.other6 = [c for c in self.star6_chars if c.name != self.up]
        else:
            self.other6 = other6
    
    def set_other5(self, other5=None):
        if other5 is None:
            self.other5 = self.star5_chars.copy()
        else:
            self.other5 = other5
    
    def set_other4(self, other4=None):
        if other4 is None:
            self.other4 = self.star4_chars.copy()
        else:
            self.other4 = other4
    
    def _get_char_info(self, char):
        """获取角色信息字典"""
        return {
            "name": char.name,
            "star": char.star,
            "image_id": char.image_id,
            "image_url": f"http://localhost:8888/static/images/characterWebp/{char.image_id}.webp"
        }
    
    def choujiang(self, times): 
        result = []
        for i in range(times):
            who = random.randint(1, 1000)
            char = None
            
            # 调试日志
            print(f"=== 第{i+1}抽 ===")
            print(f"当前状态: baodi={self.baodi}, dabaodi={self.dabaodi}")
            
            # 先检查保底机制
            if self.dabaodi == 80:
                print("触发6星大保底")
                if random.randint(0, 1) == 0:
                    char = random.choice(self.other6)
                else:
                    char = self.up_char if self.up_char else random.choice(self.star6_chars)
                self.dabaodi = 0
                self.baodi = 0
            elif self.baodi >= 9:
                print("触发5星保底（连续9次4星）")
                if who <= 8:
                    print("  -> 保底出6星")
                    if random.randint(0, 1) == 0:
                        char = random.choice(self.other6)
                    else:
                        char = self.up_char if self.up_char else random.choice(self.star6_chars)
                    self.dabaodi = 0
                else:
                    print("  -> 保底出5星")
                    char = random.choice(self.other5)
                    self.dabaodi = self.dabaodi + 1
                self.baodi = 0
            elif who <= 8 + max(0, (self.dabaodi - 65)) * 50 and who >= 1:
                print("正常出6星")
                if random.randint(0, 1) == 0:
                    char = random.choice(self.other6)
                else:
                    char = self.up_char if self.up_char else random.choice(self.star6_chars)
                self.baodi = 0
                self.dabaodi = 0
            elif who <= 80 + max(0, (self.dabaodi - 65)) * 50 and who > 8 + max(0, (self.dabaodi - 65)) * 50:
                print("正常出5星")
                char = random.choice(self.other5)
                self.baodi = 0 
                self.dabaodi = self.dabaodi + 1
            else:
                if self.baodi < 9:
                    print(f"出4星, baodi={self.baodi} -> {self.baodi+1}")
                    char = random.choice(self.other4)   
                    self.baodi = self.baodi + 1
                    self.dabaodi = self.dabaodi + 1
                else:
                    print(f"ERROR: baodi={self.baodi} >= 9 但没有触发保底!")
            
            if char:
                result.append(self._get_char_info(char))
                print(f"抽到: {char.name} ({char.star}星)")
            else:
                print("ERROR: 没有抽到任何角色!")
        
        return result