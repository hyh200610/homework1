import random
import json

# 角色类
class Character:
    def __init__(self, name, star, image_id):
        self.name = name
        self.star = star
        self.image_id = image_id

# 角色池子类
class CharacterPool:
    def __init__(self, character_list=None):
        self.characters = []
        self.static_used = []
        if character_list is not None:
            self.characters = character_list

    def get_r_character(self):
        if not self.characters:
            return None
        while True:
            target_char = random.choice(self.characters)
            if target_char not in self.static_used:
                self.static_used.append(target_char)
                return target_char

    def reset(self):
        self.static_used = []

# 全局角色管理器
class AllCharacterManager:
    def __init__(self):
        self.pools = {}
        self.all_character_list = []
        self.load_all_characters()

    def load_all_characters(self):
        try:
            with open("characters.json", "r", encoding="utf-8") as f:
                json_data = json.load(f)
        except FileNotFoundError:
            print("错误：characters.json 文件不存在")
            return
        except json.JSONDecodeError:
            print("错误：characters.json json格式损坏")
            return
        except Exception as e:
            print(f"读取文件异常: {str(e)}")
            return

        # 按星级分类
        for pool_name, char_raw_list in json_data.items():
            star_type = pool_name.replace("charpool_", "")
            temp_char_objs = []
            for raw in char_raw_list:
                image_raw = raw.get("image", "")
                image_id = image_raw.split(".")[0] if image_raw else raw["name"]
                c = Character(
                    name=raw["name"],
                    star=int(raw["star"]),
                    image_id=image_id
                )
                temp_char_objs.append(c)
                self.all_character_list.append(c)
            self.pools[star_type] = CharacterPool(temp_char_objs)

    # 获取指定星级的角色池
    def get_pool_by_star(self, star):
        return self.pools.get(str(star))

    # 随机获取指定星级的角色
    def random_get_by_star(self, star):
        pool = self.get_pool_by_star(star)
        if pool:
            return pool.get_r_character()
        return None

    # 随机获取任意角色
    def random_get_any(self):
        if not self.pools:
            return None
        target_pool = random.choice(list(self.pools.values()))
        return target_pool.get_r_character()

    # 重置所有池子
    def reset_all_pool(self):
        for pool in self.pools.values():
            pool.reset()

# 工具函数
def load_character_raw_json():
    try:
        with open("characters.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# 使用示例
if __name__ == "__main__":
    character_manager = AllCharacterManager()
    
    # 获取6星角色池
    star6_pool = character_manager.get_pool_by_star(6)
    if star6_pool:
        c = star6_pool.get_r_character()
        print(f"抽到6星角色：{c.name}，元素：{c.element}")
    
    # 获取5星角色池
    star5_pool = character_manager.get_pool_by_star(5)
    if star5_pool:
        c = star5_pool.get_r_character()
        print(f"抽到5星角色：{c.name}，元素：{c.element}")
    
    # 获取4星角色池
    star4_pool = character_manager.get_pool_by_star(4)
    if star4_pool:
        c = star4_pool.get_r_character()
        print(f"抽到4星角色：{c.name}，元素：{c.element}")
    
    # 重置所有池子
    character_manager.reset_all_pool()