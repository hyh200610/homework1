import os
import json

class usrinf:
    def __init__(self, usrname: str, password: str):
        self.name = usrname
        self.password = password
        self.baodi = 0       # 保底
        self.dabaodi = 0     # 大保底

    # 累加保底次数
    def record(self, baodi, dabaodi):
        self.baodi += baodi
        self.dabaodi += dabaodi

    # 封装：查询保底信息 函数
    def query_baodi(self):
        print("===== 保底查询结果 =====")
        print(f"当前保底计数：{self.baodi}")
        print(f"当前大保底计数：{self.dabaodi}")
        return self.baodi, self.dabaodi


# 保存用户数据到json 单独抽成函数
def save_user_data(user_obj, username):
    # 读取现有数据
    with open("usrinf.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    # 更新当前用户数据
    data[username] = user_obj.__dict__
    # 写回文件
    with open("usrinf.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# 输入账号密码
usrname = input("请输入用户名：")
password = input("请输入密码：")

# 文件不存在则初始化空字典
if not os.path.exists("usrinf.json"):
    data = {}
else:
    with open("usrinf.json", "r", encoding="utf-8") as f:
        data = json.load(f)

# 用户已存在
if usrname in data:
    if password != data[usrname]["password"]:
        print("密码错误")
        exit()
    else:
        print("登录成功")
        # 加载用户数据到对象
        user = usrinf(usrname, password)
        user.__dict__ = data[usrname]

        # 调用封装好的查询函数
        user.query_baodi()

        # 示例：累加一次保底，然后保存
        # user.record(1, 0)
        # save_user_data(user, usrname)
        exit()

# 用户不存在 注册
else:
    print("用户名不存在，是否自动注册？(y/n)")
    if input() != "y":
        print("注册取消")
        exit()
    else:
        new_user = usrinf(usrname, password)
        data[usrname] = new_user.__dict__
        with open("usrinf.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("注册成功！")
        # 注册完也可以直接查
        new_user.query_baodi()
        exit()