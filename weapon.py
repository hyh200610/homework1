import random
import json

# 规范大驼峰类名
class Weapon:
    def __init__(self, name, weapon_type, star, image_id):
        self.name = name
        self.type = weapon_type
        self.star = star
        self.image_id = image_id

class WeaponPool:
    # 修复可变参数陷阱，默认值设None，内部再加载
    def __init__(self, weapon_list=None):
        self.weapons = []
        self.static_used = []
        if weapon_list is not None:
            self.weapons = weapon_list

    def get_r_weapon(self):
        if not self.weapons:
            return None
        # 循环抽取未使用武器
        while True:
            target_weapon = random.choice(self.weapons)
            if target_weapon not in self.static_used:
                self.static_used.append(target_weapon)
                return target_weapon

    def reset(self):
        # 清空已抽取记录
        self.static_used = []

# 全局武器管理器，一次性解析wea.json拆分所有分类池子
class AllWeaponManager:
    def __init__(self):
        self.pools = {}
        self.all_weapon_list = []
        self.load_all_weapon()

    def load_all_weapon(self):
        try:
            with open("wea.json", "r", encoding="utf-8") as f:
                json_data = json.load(f)
        except FileNotFoundError:
            print("错误：wea.json 文件不存在")
            return
        except json.JSONDecodeError:
            print("错误：wea.json json格式损坏")
            return
        except Exception as e:
            print(f"读取文件异常: {str(e)}")
            return

        # 遍历每个武器分类池子
        for pool_name, weapon_raw_list in json_data.items():
            weapon_type = pool_name.replace("weapool_", "")
            temp_weapon_objs = []
            for raw in weapon_raw_list:
                # 实例化Weapon对象存入列表
                w = Weapon(
                    name=raw["name"],
                    weapon_type=raw["type"],
                    star=raw["star"],
                    image_id=raw["image"].split(".")[0]
                )
                temp_weapon_objs.append(w)
                self.all_weapon_list.append(w)
            # 创建对应类型的武器池子
            self.pools[weapon_type] = WeaponPool(temp_weapon_objs)

    # 全局随机抽取任意类型武器
    def random_get_all_type_weapon(self):
        if not self.pools:
            return None
        target_pool = random.choice(list(self.pools.values()))
        return target_pool.get_r_weapon()

    # 一键重置所有池子抽取记录
    def reset_all_pool(self):
        for pool in self.pools.values():
            pool.reset()

# 工具函数单独分离，不参与类默认参数
def load_weapon_raw_json():
    try:
        with open("wea.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# 使用示例
if __name__ == "__main__":
    # 初始化全局武器管理器，自动加载所有池子
    weapon_manager = AllWeaponManager()
    # 获取单手剑池子
    one_hand_pool = weapon_manager.pools["单手剑"]
    # 随机抽一把单手剑
    w = one_hand_pool.get_r_weapon()
    print(f"抽到武器：{w.name}，星级：{w.star}，图片ID：{w.image_id}")
    # 重置所有池子
    weapon_manager.reset_all_pool()