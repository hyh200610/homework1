import json
import os

# 读取wea.json
with open('wea.json', 'r', encoding='utf-8') as f:
    weapons_data = json.load(f)

# 获取静态目录中的图片文件
static_images_dir = 'static/images/weapons'
existing_images = set()
for filename in os.listdir(static_images_dir):
    if filename.endswith('.png'):
        existing_images.add(filename.lower())

# 收集所有武器及其图片
all_weapons = []
for pool_name, weapons in weapons_data.items():
    for weapon in weapons:
        image_name = weapon.get('image', '')
        all_weapons.append({
            'name': weapon['name'],
            'type': weapon['type'],
            'star': weapon['star'],
            'image': image_name
        })

# 找出没有对应图片的武器
missing_weapons = []
for weapon in all_weapons:
    image_name = weapon['image']
    # 处理图片名中的空格问题
    image_name_clean = image_name.strip().lower()
    if not image_name_clean:
        missing_weapons.append(weapon)
    elif image_name_clean not in existing_images:
        missing_weapons.append(weapon)

print(f"总武器数: {len(all_weapons)}")
print(f"静态目录图片数: {len(existing_images)}")
print(f"缺失图片的武器数: {len(missing_weapons)}")
print("\n=== 缺失图片的武器列表 ===")
for weapon in missing_weapons:
    print(f"  [{weapon['star']}星] {weapon['name']} ({weapon['type']}) - 图片: {weapon['image']}")

# 生成未实装类JSON
unused_data = {
    "unused": missing_weapons
}

with open('unused.json', 'w', encoding='utf-8') as f:
    json.dump(unused_data, f, ensure_ascii=False, indent=2)

print(f"\n已将{len(missing_weapons)}个未实装武器写入 unused.json")
