# -*- coding: utf-8 -*-
"""澳门文旅导航平台 - Flask 后端 API

接口一览：
  POST /api/auth/register      注册（姓名、邮箱、密码、兴趣标签）
  POST /api/auth/login         登录 → 返回 JWT
  GET  /api/auth/me            当前用户信息（需登录）
  GET  /api/attractions        景点列表（支持 q 关键词、category 分类、分页）
  GET  /api/attractions/<id>   景点详情
  POST /api/routes/plan        按兴趣标签+时间预算生成路线（需登录）
  GET  /api/routes             我保存的路线（需登录）
  POST /api/routes             保存路线（需登录）
"""
import datetime
import math
import re
from functools import wraps

import jwt
from flask import Flask, g, jsonify, request
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db, init_db

app = Flask(__name__)
app.config["SECRET_KEY"] = "macau-tourism-dev-secret"  # 生产环境应改为环境变量
TOKEN_TTL_HOURS = 24

CORS(app)  # 允许 Vite 开发服务器跨域

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ---------------- 工具 ----------------

def make_token(user_id):
    payload = {
        "uid": user_id,
        "exp": datetime_now() + datetime_timedelta(hours=TOKEN_TTL_HOURS),
    }
    return jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")


def datetime_now():
    return datetime.datetime.now(datetime.timezone.utc)


def datetime_timedelta(**kw):
    return datetime.timedelta(**kw)


def auth_required(fn):
    """JWT 校验装饰器：从 Authorization: Bearer <token> 解析用户"""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "未登录或登录已过期"}), 401
        try:
            payload = jwt.decode(auth[7:], app.config["SECRET_KEY"], algorithms=["HS256"])
        except jwt.PyJWTError:
            return jsonify({"error": "凭证无效，请重新登录"}), 401
        g.user_id = payload["uid"]
        return fn(*args, **kwargs)

    return wrapper


def row_to_dict(row):
    return {k: row[k] for k in row.keys()}


def haversine_km(lat1, lng1, lat2, lng2):
    """两点间球面距离（公里）"""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


# ---------------- 认证 ----------------

@app.post("/api/auth/register")
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    interests = ",".join(data.get("interests") or [])

    if not name or not email or not password:
        return jsonify({"error": "姓名、邮箱、密码均为必填"}), 400
    if not EMAIL_RE.match(email):
        return jsonify({"error": "邮箱格式不正确"}), 400
    if len(password) < 6:
        return jsonify({"error": "密码至少 6 位"}), 400

    conn = get_db()
    exists = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if exists:
        conn.close()
        return jsonify({"error": "该邮箱已注册"}), 409

    cur = conn.execute(
        "INSERT INTO users (name, email, password_hash, interests) VALUES (?,?,?,?)",
        (name, email, generate_password_hash(password), interests),
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()

    return jsonify({
        "token": make_token(user_id),
        "user": {"id": user_id, "name": name, "email": email,
                 "interests": interests.split(",") if interests else []},
    }), 201


@app.post("/api/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "邮箱或密码错误"}), 401

    return jsonify({
        "token": make_token(user["id"]),
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "interests": user["interests"].split(",") if user["interests"] else [],
        },
    })


@app.get("/api/auth/me")
@auth_required
def me():
    conn = get_db()
    user = conn.execute(
        "SELECT id, name, email, interests FROM users WHERE id = ?", (g.user_id,)
    ).fetchone()
    conn.close()
    if not user:
        return jsonify({"error": "用户不存在"}), 404
    d = row_to_dict(user)
    d["interests"] = d["interests"].split(",") if d["interests"] else []
    return jsonify(d)


# ---------------- 景点 ----------------

@app.get("/api/attractions")
def list_attractions():
    q = (request.args.get("q") or "").strip()
    category = (request.args.get("category") or "").strip()
    page = max(int(request.args.get("page", 1) or 1), 1)
    per_page = min(max(int(request.args.get("per_page", 9) or 9), 1), 50)

    where, params = [], []
    if q:
        where.append("(name LIKE ? OR brief LIKE ?)")
        params += [f"%{q}%", f"%{q}%"]
    if category:
        where.append("category = ?")
        params.append(category)
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    conn = get_db()
    total = conn.execute(
        f"SELECT COUNT(*) AS c FROM attractions {where_sql}", params
    ).fetchone()["c"]
    rows = conn.execute(
        f"""SELECT id, name, category, brief, lat, lng, rating, image
            FROM attractions {where_sql}
            ORDER BY rating DESC LIMIT ? OFFSET ?""",
        params + [per_page, (page - 1) * per_page],
    ).fetchall()
    conn.close()

    return jsonify({
        "total": total,
        "page": page,
        "per_page": per_page,
        "items": [row_to_dict(r) for r in rows],
    })


@app.get("/api/attractions/<int:attraction_id>")
def attraction_detail(attraction_id):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM attractions WHERE id = ?", (attraction_id,)
    ).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "景点不存在"}), 404
    return jsonify(row_to_dict(row))


# ---------------- 路线规划 ----------------

@app.post("/api/routes/plan")
@auth_required
def plan_route():
    """按兴趣标签 + 时间预算生成游览路线（贪心最近邻排序）"""
    data = request.get_json(silent=True) or {}
    interests = data.get("interests") or []           # 例: ["历史", "美食"]
    time_budget = int(data.get("time_budget", 240))   # 分钟
    start_lat = float(data.get("lat", 22.1935))       # 默认从议事亭前地出发
    start_lng = float(data.get("lng", 113.5395))

    conn = get_db()
    if interests:
        marks = ",".join("?" for _ in interests)
        rows = conn.execute(
            f"SELECT * FROM attractions WHERE category IN ({marks})", interests
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM attractions").fetchall()
    conn.close()

    candidates = [row_to_dict(r) for r in rows]

    # 贪心最近邻：从起点开始不断选最近的下一个景点，直到时间预算用完
    route, remaining = [], candidates[:]
    cur_lat, cur_lng, time_used, total_km = start_lat, start_lng, 0, 0.0
    while remaining:
        nxt = min(remaining, key=lambda a: haversine_km(cur_lat, cur_lng, a["lat"], a["lng"]))
        leg_km = haversine_km(cur_lat, cur_lng, nxt["lat"], nxt["lng"])
        travel_min = max(round(leg_km / 4.5 * 60), 5)  # 步行按 4.5km/h 估
        cost = travel_min + nxt["duration_min"]
        if route and time_used + cost > time_budget:
            break
        route.append({
            "id": nxt["id"], "name": nxt["name"], "category": nxt["category"],
            "lat": nxt["lat"], "lng": nxt["lng"], "rating": nxt["rating"],
            "duration_min": nxt["duration_min"], "brief": nxt["brief"],
            "image": nxt["image"], "leg_km": round(leg_km, 2), "travel_min": travel_min,
        })
        time_used += cost
        total_km += leg_km
        cur_lat, cur_lng = nxt["lat"], nxt["lng"]
        remaining.remove(nxt)

    return jsonify({
        "start": {"lat": start_lat, "lng": start_lng},
        "stops": route,
        "total_distance_km": round(total_km, 2),
        "total_minutes": time_used,
    })


@app.get("/api/routes")
@auth_required
def my_routes():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM saved_routes WHERE user_id = ? ORDER BY id DESC", (g.user_id,)
    ).fetchall()
    conn.close()
    return jsonify([row_to_dict(r) for r in rows])


@app.post("/api/routes")
@auth_required
def save_route():
    import json as _json
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "我的路线").strip()
    stops = data.get("stops") or []
    if not stops:
        return jsonify({"error": "路线不能为空"}), 400
    conn = get_db()
    cur = conn.execute(
        """INSERT INTO saved_routes (user_id, name, stops, total_distance_km, total_minutes)
           VALUES (?,?,?,?,?)""",
        (g.user_id, name, _json.dumps(stops, ensure_ascii=False),
         data.get("total_distance_km", 0), data.get("total_minutes", 0)),
    )
    conn.commit()
    route_id = cur.lastrowid
    conn.close()
    return jsonify({"id": route_id, "name": name}), 201


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5001, debug=True)
