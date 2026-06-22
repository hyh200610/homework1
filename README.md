# 抽卡模拟器

一个基于 FastAPI 和 Vue.js 的抽卡模拟器应用，支持角色抽卡和武器刮刮乐功能。

## 功能特性

### 🎰 角色抽卡
- **单抽**：消耗1抽，全屏展示抽卡结果，渐变动画效果
- **十连抽**：消耗10抽，2行5列网格布局展示，从左到右依次显示
- **保底机制**：
  - 5星保底：连续9次4星后，第10次必定出5星或6星（8%概率出6星）
  - 6星大保底：累计80抽必定出6星
  - 概率提升：65抽后6星概率每抽提升5%
- **保底计数显示**：实时显示当前保底进度

### 🎁 武器刮刮乐
- 每日商店风格刮刮乐
- 4个槽位同时展示
- 翻开特效：先展示品质底色，再渐变出武器图片
- 刮完后可全部重置

## 技术栈

### 后端
- Python 3.10+
- FastAPI
- JSON 数据存储

### 前端
- Vue 3
- Vite
- CSS3 动画

## 项目结构

```
homework1/
├── main_api.py          # 后端API入口
├── chouka.py            # 抽卡模块
├── character.py         # 角色管理模块
├── characters.json      # 角色数据
├── usrinf.json          # 用户数据（运行时自动生成）
├── static/              # 静态资源
│   └── images/          # 角色图片
├── weapons/             # 武器刮刮乐模块
└── frontend/            # 前端项目
    ├── src/
    │   ├── App.vue      # 主应用组件
    │   └── main.js      # 入口文件
    └── package.json
```

## 安装和运行

### 1. 安装依赖

```bash
# 后端依赖
pip install fastapi uvicorn python-multipart

# 前端依赖
cd frontend
npm install
```

### 2. 运行后端

```bash
cd homework1
uvicorn main_api:app --host 0.0.0.0 --port 8888 --reload
```

### 3. 运行前端

```bash
cd frontend
npm run dev
```

### 4. 访问应用

打开浏览器访问 http://localhost:5173

## API 接口

### 用户接口
- `POST /api/user/login` - 用户登录
- `POST /api/user/register` - 用户注册

### 抽卡接口
- `POST /api/chouka/do` - 执行抽卡

### 刮刮乐接口
- `POST /api/scratch/reset` - 重置刮刮乐
- `POST /api/scratch/do` - 执行刮刮
- `GET /api/scratch/status` - 获取刮刮乐状态

## 抽卡概率

| 星级 | 基础概率 | 特殊规则 |
|------|---------|---------|
| 6星 | 0.8% | 65抽后每抽+5%，80抽必出 |
| 5星 | 7.2% | 连续9次4星后必出（含6星概率） |
| 4星 | 92% | 常规掉落 |

## 角色数据

角色数据存储在 `characters.json` 中，包含：
- 6星角色：13个
- 5星角色：9个  
- 4星角色：5个

图片文件需放置在 `static/images/characterWebp/` 目录下。

## 开发说明

### 添加新角色
1. 在 `characters.json` 中添加角色信息
2. 将角色图片放入 `static/images/characterWebp/` 目录
3. 重启后端服务

### 自定义抽卡概率
修改 `chouka.py` 中的概率参数即可调整抽卡概率。

## 许可证

MIT License
