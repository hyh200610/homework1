from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from chouka import chouka
from weapon import AllWeaponManager
import uvicorn
import json
import os


app = FastAPI(title="小助手API", version="1.0.0")

# 添加CORS中间件，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 初始化武器系统
weapon_manager = AllWeaponManager()

# 构建武器数据映射（用于兼容旧接口）
weapons_data = {}
for weapon in weapon_manager.all_weapon_list:
    weapons_data[weapon.name] = {
        "type": weapon.type,
        "rarity": str(weapon.star),
        "star": weapon.star,
        "image_id": weapon.image_id
    }

# 存储当前四个刮刮乐卡片
current_cards = []

# ==================== 统一响应格式 ====================
def success_response(data=None, message="操作成功"):
    """成功响应格式"""
    return JSONResponse({
        "code": 200,
        "success": True,
        "message": message,
        "data": data
    })

def error_response(code=400, message="操作失败", data=None):
    """错误响应格式"""
    return JSONResponse({
        "code": code,
        "success": False,
        "message": message,
        "data": data
    }, status_code=code)

# ==================== 健康检查 ====================
@app.get("/health", summary="健康检查")
def health_check():
    """检查API服务状态"""
    return success_response({"status": "ok"}, "服务运行正常")



# ==================== 用户管理 API ====================
@app.post("/api/user/login", summary="用户登录")
def login(username: str = Form(...), password: str = Form(...)):
    """用户登录验证"""
    if not os.path.exists("usrinf.json"):
        return error_response(404, "用户数据文件不存在")
    
    try:
        with open("usrinf.json", "r", encoding="utf-8") as f:
            file_content = f.read().strip()
            if not file_content:
                return error_response(400, "用户数据文件为空")
            data = json.loads(file_content)
    except json.JSONDecodeError:
        return error_response(500, "用户数据文件格式错误")
    
    if username not in data:
        return error_response(404, "用户不存在")
    
    if data[username]["password"] != password:
        return error_response(401, "密码错误")
    
    return success_response({
        "user": {
            "username": username,
            "baodi": data[username]["baodi"],
            "dabaodi": data[username]["dabaodi"]
        }
    }, "登录成功")

@app.post("/api/user/register", summary="用户注册")
def register(username: str = Form(...), password: str = Form(...)):
    """用户注册"""
    if os.path.exists("usrinf.json"):
        try:
            with open("usrinf.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            return error_response(500, "用户数据文件格式错误")
    else:
        data = {}
    
    if username in data:
        return error_response(400, "用户名已存在")
    
    # 创建新用户
    new_user = {
        "password": password,
        "baodi": 0,
        "dabaodi": 0
    }
    data[username] = new_user
    
    try:
        with open("usrinf.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        return error_response(500, f"保存用户数据失败: {str(e)}")
    
    return success_response({
        "user": {
            "username": username,
            "baodi": 0,
            "dabaodi": 0
        }
    }, "注册成功")


@app.get("/api/user/baodi/{username}", summary="查询用户保底信息")
def get_baodi(username: str):
    """查询用户的抽卡保底信息"""
    if not os.path.exists("usrinf.json"):
        return error_response(404, "用户数据文件不存在")
    
    try:
        with open("usrinf.json", "r", encoding="utf-8") as f:
            file_content = f.read().strip()
            if not file_content:
                return error_response(400, "用户数据文件为空")
            data = json.loads(file_content)
    except json.JSONDecodeError:
        return error_response(500, "用户数据文件格式错误")
    
    if username not in data:
        return error_response(404, "用户不存在")
    
    return success_response({
        "baodi": data[username]["baodi"],
        "dabaodi": data[username]["dabaodi"]
    })

# ==================== 抽奖 API ====================
@app.post("/api/chouka/do", summary="执行抽奖")
def chouka_do(times: int = Form(...), username: str = Form(None)):
    """执行抽奖，支持指定用户记录保底"""
    try:
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
            else:
                data = {}
            
            # 更新用户的保底计数
            if username in data:
                data[username]["baodi"] = c.baodi
                data[username]["dabaodi"] = c.dabaodi
            else:
                # 用户不存在，创建新用户
                data[username] = {
                    "password": "",
                    "baodi": c.baodi,
                    "dabaodi": c.dabaodi
                }
            
            try:
                with open("usrinf.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
            except Exception as e:
                return error_response(500, f"保存用户保底信息失败: {str(e)}")
        
        # 统计结果
        stats = {
            "total": times,
            "star_6": sum(1 for item in result if "******" in item),
            "star_5": sum(1 for item in result if "*****" in item and "******" not in item),
            "star_4": sum(1 for item in result if "****" in item and "*****" not in item)
        }
        
        return success_response({
            "results": result,
            "statistics": stats,
            "baodi_info": {
                "current_baodi": c.baodi,
                "current_dabaodi": c.dabaodi
            } if username else None
        }, f"抽奖完成，共获得 {stats['star_6']} 个6星, {stats['star_5']} 个5星, {stats['star_4']} 个4星")
        
    except Exception as e:
        return error_response(500, f"抽奖失败: {str(e)}")

# ==================== 武器刮刮乐 API ====================
@app.get("/api/scratch/status", summary="获取刮刮乐状态")
def get_scratch_status():
    """获取刮刮乐系统状态"""
    total_cards = len(weapons_data)
    # 计算所有池子已使用的武器总数
    used_cards = sum(len(pool.static_used) for pool in weapon_manager.pools.values())
    remaining_cards = total_cards - used_cards
    
    return success_response({
        "total_cards": total_cards,
        "remaining_cards": remaining_cards,
        "scratched_count": used_cards,
        "current_cards_count": len(current_cards)
    })

@app.post("/api/scratch/play", summary="刮一张卡片")
def scratch_play():
    """随机刮开一张卡片"""
    try:
        # 检查是否还有剩余卡片
        remaining = len(weapons_data) - sum(len(pool.static_used) for pool in weapon_manager.pools.values())
        if remaining <= 0:
            return error_response(400, "没有剩余卡片了！")
        
        # 使用 random_get_all_type_weapon 获取随机武器
        weapon = weapon_manager.random_get_all_type_weapon()
        if not weapon:
            return error_response(400, "没有剩余卡片了！")
        
        remaining_after = len(weapons_data) - sum(len(pool.static_used) for pool in weapon_manager.pools.values())
        
        return success_response({
            "prize": {
                "name": weapon.name,
                "weapon_type": weapon.type,
                "rarity": str(weapon.star),
                "star": weapon.star,
                "image_id": weapon.image_id
            },
            "remaining_cards": remaining_after
        }, f"恭喜获得: {weapon.name}")
        
    except Exception as e:
        return error_response(500, f"刮卡片失败: {str(e)}")

@app.post("/api/scratch/reset", summary="重置刮刮乐")
def scratch_reset():
    """重置所有刮刮乐卡片"""
    try:
        weapon_manager.reset_all_pool()
        
        return success_response({
            "total_cards": len(weapons_data)
        }, "刮刮乐已重置")
        
    except Exception as e:
        return error_response(500, f"重置失败: {str(e)}")

# ==================== 新版四个刮刮乐 API ====================
@app.post("/api/scratch/new/init", summary="初始化四个刮刮乐卡片")
def init_new_scratch():
    """初始化四个刮刮乐卡片"""
    try:
        global current_cards
        
        # 检查是否还有足够的卡片
        remaining = len(weapons_data) - sum(len(pool.static_used) for pool in weapon_manager.pools.values())
        if remaining < 4:
            return error_response(400, f"剩余卡片不足4张，仅剩{remaining}张！")
        
        # 生成四个随机武器
        current_cards = []
        for _ in range(4):
            weapon = weapon_manager.random_get_all_type_weapon()
            if not weapon:
                return error_response(400, "生成卡片失败，没有剩余卡片了！")
            current_cards.append({
                "id": _ + 1,
                "name": weapon.name,
                "weapon_type": weapon.type,
                "rarity": str(weapon.star),
                "star": weapon.star,
                "image_id": weapon.image_id,
                "revealed": False
            })
        
        return success_response({
            "cards": current_cards
        }, "四个刮刮乐卡片已准备就绪！")
        
    except Exception as e:
        return error_response(500, f"初始化失败: {str(e)}")

@app.post("/api/scratch/new/reveal/{card_id}", summary="揭开指定卡片")
def reveal_card(card_id: int):
    """揭开指定ID的卡片"""
    try:
        global current_cards
        
        if not current_cards:
            return error_response(400, "请先初始化刮刮乐卡片！")
        
        if card_id < 1 or card_id > 4:
            return error_response(400, "无效的卡片ID！")
        
        card = current_cards[card_id - 1]
        if card["revealed"]:
            return error_response(400, "该卡片已被揭开！")
        
        card["revealed"] = True
        
        return success_response({
            "card": card,
            "all_revealed": all(c["revealed"] for c in current_cards)
        }, f"揭开卡片{card_id}：{card['name']}")
        
    except Exception as e:
        return error_response(500, f"揭开卡片失败: {str(e)}")

@app.post("/api/scratch/new/reset", summary="完全重置刮刮乐")
def reset_new_scratch():
    """完全重置刮刮乐系统"""
    try:
        global current_cards
        weapon_manager.reset_all_pool()
        current_cards = []
        
        return success_response({
            "total_cards": len(weapons_data)
        }, "刮刮乐已完全重置")
        
    except Exception as e:
        return error_response(500, f"重置失败: {str(e)}")

# 直接 python main_api.py 启动
if __name__ == "__main__":
    uvicorn.run("main_api:app", host="127.0.0.1", port=8888, reload=True)
