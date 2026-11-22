# -*- coding: utf-8 -*-
"""SQLite 数据库初始化与种子数据"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tourism.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _img(prompt):
    """生成配图 URL（text_to_image 服务）"""
    from urllib.parse import quote
    return ("https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image"
            f"?prompt={quote(prompt)}&image_size=landscape_4_3")


# 澳门真实景点种子数据：(名称, 分类, 简介, 历史介绍, 开放时间, 纬度, 经度, 评分, 建议游览分钟, 门票)
SEED_ATTRACTIONS = [
    ("大三巴牌坊", "历史", "澳门标志性建筑，圣保禄教堂前壁遗址，世界文化遗产。",
     "建于1602年，原为圣保禄学院天主之母教堂，1835年大火后仅存前壁，因形似中国传统牌坊而得名'大三巴'，是中西文化交融的见证。",
     "全天开放", 22.1975, 113.5408, 4.8, 60, "免费",
     "Ruins of St. Paul Macau, iconic stone facade landmark, travel photography"),
    ("议事亭前地", "历史", "澳门市中心广场，黑白碎石波浪纹地面与葡式建筑群。",
     "自16世纪以来一直是澳门的政治与商业心脏，周围环绕民政总署大楼、仁慈堂等历史建筑，2005年列入世界文化遗产。",
     "全天开放", 22.1935, 113.5395, 4.6, 45, "免费",
     "Senado Square Macau, wave pattern mosaic pavement, Portuguese colonial buildings"),
    ("妈阁庙", "文化", "澳门最古老的庙宇，供奉妈祖，澳门葡文名'Macau'即源于此。",
     "始建于明弘治元年（1488年），是澳门三大古刹之首。相传葡萄牙人登陆时询问地名，渔民答'妈阁'，遂成Macau。",
     "07:00-18:00", 22.1861, 113.5311, 4.5, 50, "免费",
     "A-Ma Temple Macau, ancient Chinese temple with incense coils, cultural heritage"),
    ("澳门旅游塔", "摄影", "338米高观光塔，可俯瞰澳门全景，设有蹦极跳等极限项目。",
     "2001年建成，是全球第十高独立式观光塔。塔顶观景台可360度环视澳门半岛、氹仔、路环及珠海横琴。",
     "10:00-21:00", 22.1797, 113.5367, 4.7, 90, "约MOP 165",
     "Macau Tower at dusk, modern observation tower skyline, aerial city view"),
    ("官也街", "美食", "氹仔著名手信美食街，聚集杏仁饼、葡挞、猪扒包等特色小吃。",
     "这条仅115米长的小街是氹仔旧城区的美食核心，莫义记榴莲雪糕、安德鲁饼店葡挞、大利来记猪扒包均发迹于此。",
     "10:00-22:00", 22.1536, 113.5576, 4.6, 60, "免费",
     "Rua do Cunha Macau food street, pastel shops, Portuguese egg tart pastry"),
    ("龙环葡韵", "文化", "五幢薄荷绿葡式住宅博物馆，展现土生葡人生活风貌。",
     "建于1921年，原为氹仔葡籍官员官邸，现为住宅式博物馆，'龙环'是氹仔旧称，'葡韵'指葡萄牙风情。",
     "10:00-19:00（周一休馆）", 22.1531, 113.5557, 4.4, 40, "免费",
     "Taipa Houses Museum Macau, mint green Portuguese colonial houses, lotus pond"),
    ("路环岛", "摄影", "澳门最后的渔村风情，彩色小屋、安德鲁蛋挞总店与黑沙滩。",
     "路环保留了大片未被赌场化的原始风貌，圣方济各教堂前的蛋挞店是葡挞发源地，黑沙海滩以独特黑色海沙闻名。",
     "全天开放", 22.1167, 113.5519, 4.5, 120, "免费",
     "Coloane Village Macau, colorful fishing village, Chapel of St Francis Xavier"),
    ("澳门博物馆", "文化", "坐落大炮台内，系统展示澳门四百年中西交融史。",
     "1998年开馆，三层展厅分别以澳门早期历史、民间艺术传统和当代风貌为主题，是了解澳门前世今生的最佳起点。",
     "10:00-18:00（周一休馆）", 22.1972, 113.5414, 4.3, 80, "MOP 15",
     "Macau Museum interior, cultural exhibition hall, historical artifacts"),
    ("东望洋灯塔", "摄影", "中国海岸第一座现代灯塔，澳门半岛制高点。",
     "建于1864年，1871年正式启用，灯塔与圣母雪地殿教堂、松山炮台构成东望洋炮台建筑群，台风季悬挂风球的传统延续至今。",
     "09:00-18:00", 22.1967, 113.5497, 4.4, 50, "免费",
     "Guia Lighthouse Macau, white and yellow lighthouse on hilltop, sunset view"),
    ("哪吒庙", "历史", "大三巴旁的中式小庙，体现中西宗教比邻共存的奇景。",
     "建于1888年，相传澳门瘟疫期间民众建庙供奉哪吒以镇疫，与一旁的教堂遗址形成'一墙之隔、两教并存'的独特景观。",
     "08:00-17:00", 22.1978, 113.5402, 4.1, 20, "免费",
     "Na Tcha Temple Macau, small traditional Chinese temple, incense and red lanterns"),
    ("福隆新街", "美食", "百年红窗门老街，如今变身文创美食街区。",
     "曾是澳门最繁华的'花街'，整齐的中式骑楼配红色门窗极具辨识度，如今聚集添发碗仔翅、佛笑楼等老字号食肆。",
     "11:00-23:00", 22.1920, 113.5383, 4.2, 40, "免费",
     "Rua da Felicidade Macau, red shutter windows old street, Chinese shophouses"),
    ("郑家大屋", "历史", "近代思想家郑观应故居，岭南风格大宅院落。",
     "建于1881年，是澳门现存最大的民居建筑群，郑观应在此写下影响中国近代化进程的《盛世危言》。",
     "10:00-18:00（周三休馆）", 22.1886, 113.5356, 4.3, 45, "免费",
     "Mandarin's House Macau, traditional Lingnan courtyard residence, grey brick architecture"),
]


def init_db():
    """建表并写入种子数据（幂等：已有数据则跳过种子写入）"""
    conn = get_db()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        interests TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS attractions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        brief TEXT NOT NULL,
        history TEXT DEFAULT '',
        open_hours TEXT DEFAULT '',
        lat REAL NOT NULL,
        lng REAL NOT NULL,
        rating REAL DEFAULT 0,
        duration_min INTEGER DEFAULT 60,
        ticket TEXT DEFAULT '免费',
        image TEXT DEFAULT ''
    );

    CREATE TABLE IF NOT EXISTS saved_routes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id),
        name TEXT NOT NULL,
        stops TEXT NOT NULL,
        total_distance_km REAL DEFAULT 0,
        total_minutes INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    count = cur.execute("SELECT COUNT(*) AS c FROM attractions").fetchone()["c"]
    if count == 0:
        rows = [
            (name, cat, brief, history, hours, lat, lng, rating, dur, ticket, _img(prompt))
            for (name, cat, brief, history, hours, lat, lng, rating, dur, ticket, prompt)
            in SEED_ATTRACTIONS
        ]
        cur.executemany(
            """INSERT INTO attractions
               (name, category, brief, history, open_hours, lat, lng, rating, duration_min, ticket, image)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            rows,
        )
        print(f"已写入 {len(rows)} 条景点种子数据")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"数据库初始化完成: {DB_PATH}")
