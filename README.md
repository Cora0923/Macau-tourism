# 澳门文旅导航平台

面向赴澳游客的一站式文旅导航平台。支持 JWT 身份登录认证、景点信息浏览与检索、基于兴趣标签和时间预算的智能路线规划，并在地图上可视化游览路线。

## 技术栈

| 层级 | 技术 |
| ---- | ---- |
| 前端 | Vue 3 + Vite + Vue Router + Axios + Leaflet（OpenStreetMap） |
| 后端 | Flask + Flask-CORS + PyJWT |
| 数据库 | SQLite（轻量化存储用户、景点、保存的路线） |

## 项目结构

```
macau-tourism/
├── backend/
│   ├── app.py            # Flask API：认证 / 景点 / 路线规划
│   ├── database.py       # SQLite 建表 + 12 条澳门真实景点种子数据
│   ├── requirements.txt
│   └── tourism.db        # 初始化后自动生成
└── frontend/
    ├── src/
    │   ├── api.js        # axios 实例（JWT 拦截器、401 统一处理）
    │   ├── router/       # 路由与登录守卫
    │   └── views/        # 登录注册 / 景点列表 / 景点详情 / 路线规划 / 我的路线
    └── vite.config.js    # 开发代理 /api → http://127.0.0.1:5001
```

## 快速开始

### 1. 启动后端（端口 5001）

```bash
cd backend
pip install -r requirements.txt
python database.py     # 首次运行：建表并写入种子数据
python app.py          # 监听 http://127.0.0.1:5001
```

> 注意：macOS 的 5000 端口被 AirPlay 占用，因此后端固定使用 5001。

### 2. 启动前端（端口 5173，被占用时自动顺延）

```bash
cd frontend
npm install
npm run dev
```

浏览器打开终端提示的地址（如 `http://localhost:5173/`）。

### 演示账号

```
邮箱：t@t.com
密码：123456
```

## 核心功能

- **JWT 登录认证**：注册 / 登录签发 JWT（24 小时有效），前端 axios 拦截器自动携带，路由守卫保护需登录页面。
- **景点信息展示**：12 个澳门真实景点（大三巴、议事亭前地、官也街等），支持关键词搜索、分类筛选（历史 / 美食 / 文化 / 摄影）、分页浏览与详情页历史介绍。
- **路线规划**：选择兴趣标签与时间预算（半天 / 一天 / 两天），后端以贪心最近邻算法从议事亭前地出发生成游览顺序，前端在 Leaflet 地图上绘制编号标记与路线折线，支持保存路线并在「我的路线」中回看。

## API 一览

| 方法 | 路径 | 说明 |
| ---- | ---- | ---- |
| POST | `/api/auth/register` | 注册（姓名、邮箱、密码、兴趣标签） |
| POST | `/api/auth/login` | 登录，返回 JWT |
| GET | `/api/auth/me` | 当前用户信息（需登录） |
| GET | `/api/attractions` | 景点列表（`q` 关键词、`category` 分类、分页） |
| GET | `/api/attractions/<id>` | 景点详情 |
| POST | `/api/routes/plan` | 生成路线（兴趣 + 时间预算，需登录） |
| GET / POST | `/api/routes` | 查询 / 保存我的路线（需登录） |
