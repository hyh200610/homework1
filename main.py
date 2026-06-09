from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from bijia import bijia
from chouka import chouka
from weapon import all_weapons
import uvicorn
import json
import os


app = FastAPI()

# 初始化武器系统
# 创建武器字典（名称: {类型, 稀有度}）
weapons_data = {
    "铁剑": {"type": "剑", "rarity": "1"},
    "钢剑": {"type": "剑", "rarity": "2"},
    "精钢剑": {"type": "剑", "rarity": "3"},
    "烈焰剑": {"type": "剑", "rarity": "4"},
    "神圣之剑": {"type": "剑", "rarity": "5"},
    "木弓": {"type": "弓", "rarity": "1"},
    "猎弓": {"type": "弓", "rarity": "2"},
    "长弓": {"type": "弓", "rarity": "3"},
    "精灵弓": {"type": "弓", "rarity": "4"},
    "星辰弓": {"type": "弓", "rarity": "5"},
    "短枪": {"type": "枪", "rarity": "1"},
    "长枪": {"type": "枪", "rarity": "2"},
    "龙枪": {"type": "枪", "rarity": "3"},
    "雷霆枪": {"type": "枪", "rarity": "4"},
    "破魔枪": {"type": "枪", "rarity": "5"},
}

# 创建武器实例
weapon_system = all_weapons(weapons_data)

# 添加CORS中间件，允许Vue前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8888", "http://127.0.0.1:8888"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 首页菜单
@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <h1>小助手网页版</h1>
    <p><a href="/bijia">商品比价</a></p>
    <p><a href="/chouka">抽奖</a></p>
    """

# ==================== 比价 ====================
@app.get("/bijia", response_class=HTMLResponse)
def bijia_form():
    return """
    <form method=post action=/bijia_calc>
        商品1名称：<input name=a_name><br>
        商品1总价：<input name=a_price type=number step="0.01"><br>
        商品1单位：<input name=a_per type=number step="0.01"><br><br>

        商品2名称：<input name=b_name><br>
        商品2总价：<input name=b_price type=number step="0.01"><br>
        商品2单位：<input name=b_per type=number step="0.01"><br><br>

        <button type=submit>计算</button>
    </form>
    """

@app.post("/bijia_calc", response_class=HTMLResponse)
def bijia_calc(
    a_name: str = Form(...),
    a_price: float = Form(...),  # 👈 修复
    a_per: float = Form(...),    # 👈 修复
    b_name: str = Form(...),
    b_price: float = Form(...),  # 👈 修复
    b_per: float = Form(...)     # 👈 修复
):
    a = bijia(a_name, a_price, a_per)
    b = bijia(b_name, b_price, b_per)
    res = bijia.compare(a, b)
    # 添加Cache-Control头，防止浏览器缓存
    html_content = f"<h3>{res}</h3>"
    return HTMLResponse(content=html_content, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

# ==================== 用户管理 ====================
@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    """用户登录"""
    if not os.path.exists("usrinf.json"):
        return JSONResponse({"success": False, "message": "用户数据文件不存在"})
    
    try:
        with open("usrinf.json", "r", encoding="utf-8") as f:
            file_content = f.read().strip()
            if not file_content:  # 文件为空
                return JSONResponse({"success": False, "message": "用户数据文件为空"})
            data = json.loads(file_content)
    except json.JSONDecodeError:
        return JSONResponse({"success": False, "message": "用户数据文件格式错误"})
    
    if username not in data:
        return JSONResponse({"success": False, "message": "用户不存在"})
    
    if data[username]["password"] != password:
        return JSONResponse({"success": False, "message": "密码错误"})
    
    return JSONResponse({
        "success": True, 
        "message": "登录成功",
        "user": {
            "username": username,
            "baodi": data[username]["baodi"],
            "dabaodi": data[username]["dabaodi"]
        }
    })

@app.post("/register")
def register(username: str = Form(...), password: str = Form(...)):
    """用户注册"""
    if os.path.exists("usrinf.json"):
        with open("usrinf.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}
    
    if username in data:
        return JSONResponse({"success": False, "message": "用户名已存在"})
    
    # 创建新用户
    new_user = {
        "password": password,
        "baodi": 0,
        "dabaodi": 0
    }
    data[username] = new_user
    
    with open("usrinf.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    return JSONResponse({
        "success": True, 
        "message": "注册成功",
        "user": {
            "username": username,
            "baodi": 0,
            "dabaodi": 0
        }
    })



@app.get("/baodi/{username}")
def get_baodi(username: str):
    """查询用户保底信息"""
    if not os.path.exists("usrinf.json"):
        return JSONResponse({"success": False, "message": "用户数据文件不存在"})
    
    try:
        with open("usrinf.json", "r", encoding="utf-8") as f:
            file_content = f.read().strip()
            if not file_content:  # 文件为空
                return JSONResponse({"success": False, "message": "用户数据文件为空"})
            data = json.loads(file_content)
    except json.JSONDecodeError:
        return JSONResponse({"success": False, "message": "用户数据文件格式错误"})
    
    if username not in data:
        return JSONResponse({"success": False, "message": "用户不存在"})
    
    return JSONResponse({
        "success": True,
        "baodi": data[username]["baodi"],
        "dabaodi": data[username]["dabaodi"]
    })

# ==================== 武器刮刮乐 ====================
@app.get("/scratch/status")
def get_scratch_status():
    """获取刮刮乐状态"""
    total_cards = len(weapons_data)
    used_cards = len(weapon_system.static_used)
    remaining_cards = total_cards - used_cards
    
    return JSONResponse({
        "success": True,
        "total_cards": total_cards,
        "remaining_cards": remaining_cards,
        "scratched_count": used_cards
    })

@app.post("/scratch/play")
def scratch_play():
    """刮开一张卡片"""
    global weapon_system
    
    # 检查是否还有剩余卡片
    remaining = len(weapons_data) - len(weapon_system.static_used)
    if remaining <= 0:
        return JSONResponse({"success": False, "message": "没有剩余卡片了！"})
    
    # 使用 get_r_weapon 获取随机武器
    weapon_name = weapon_system.get_r_weapon()
    weapon_info = weapons_data[weapon_name]
    
    remaining_after = len(weapons_data) - len(weapon_system.static_used)
    
    return JSONResponse({
        "success": True,
        "message": f"恭喜获得: {weapon_name}",
        "prize": {
            "name": weapon_name,
            "weapon_type": weapon_info["type"],
            "rarity": weapon_info["rarity"]
        },
        "remaining_cards": remaining_after
    })

@app.post("/scratch/reset")
def scratch_reset():
    """重置刮刮乐"""
    global weapon_system
    weapon_system.reset()
    
    return JSONResponse({
        "success": True,
        "message": "刮刮乐已重置",
        "total_cards": len(weapons_data)
    })

# ==================== 抽奖 ====================
@app.get("/chouka", response_class=HTMLResponse)
def chouka_form():
    return """
    <form method=post action=/chouka_do>
        抽奖次数：<input name=times type=number><br><br>
        <button type=submit>开始抽奖</button>
    </form>
    """

@app.post("/chouka_do", response_class=HTMLResponse)
def chouka_do(times: int = Form(...), username: str = Form(None)):
    # 如果有用户登录，加载用户的保底计数
    if username and os.path.exists("usrinf.json"):
        try:
            with open("usrinf.json", "r", encoding="utf-8") as f:
                file_content = f.read().strip()
                if file_content:
                    data = json.loads(file_content)
                else:
                    data = {}
        except json.JSONDecodeError:
            data = {}
        
        if username in data:
            # 使用用户的保底计数初始化抽卡器
            c = chouka(username, data[username]["baodi"], data[username]["dabaodi"])
        else:
            c = chouka()
    else:
        c = chouka()
    
    c.set_up()
    c.set_other6()
    c.set_other5()
    c.set_other4()
    result = c.choujiang(times)
    
    # 如果有用户登录，保存抽卡后的保底计数
    if username:
        if os.path.exists("usrinf.json"):
            try:
                with open("usrinf.json", "r", encoding="utf-8") as f:
                    file_content = f.read().strip()
                    if file_content:
                        data = json.loads(file_content)
                    else:
                        data = {}
            except json.JSONDecodeError:
                data = {}
            
            # 更新用户的保底计数
            if username in data:
                data[username]["baodi"] = c.baodi
                data[username]["dabaodi"] = c.dabaodi
            else:
                # 用户不存在，创建新用户
                data[username] = {
                    "password": "",  # 密码为空，因为这里是通过抽卡创建的
                    "baodi": c.baodi,
                    "dabaodi": c.dabaodi
                }
            
            with open("usrinf.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
    
    # 列表每个元素换行显示，添加样式
    html = """
    <style>
        .star-6 {
            color: #e53e3e;
            font-weight: bold;
            font-size: 28px;
        }
        .star-5 {
            color: #f6e05e;
            font-weight: bold;
            font-size: 22px;
        }
        .star-4 {
            color: #805ad5;
            font-size: 16px;
        }
    </style>
    <h3>抽奖结果：</h3>
    """
    for item in result:
        # 根据星星数量确定样式类
        if "******" in item:
            style_class = "star-6"
        elif "*****" in item:
            style_class = "star-5"
        else:
            style_class = "star-4"
        
        html += f"<div class='{style_class}'>{item}</div>"

    return html

# 直接 python main.py 启动
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8888, reload=True)