from pathlib import Path
import hashlib
import re
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from PIL import Image, ImageDraw, ImageFont

from app import create_app
from app.repositories import ai_generation_logs as ai_log_repository
from app.repositories import announcements as announcement_repository
from app.repositories import messages as message_repository
from app.repositories import operation_logs as operation_log_repository
from app.repositories import products as product_repository
from app.repositories import trades as trade_repository
from app.repositories.categories import upsert_default_categories
from app.repositories.users import find_user_by_username, serialize_user, upsert_seed_user, utc_now_iso
from app.services.auth import hash_password


SEED_TAG = "v3_demo"
DEFAULT_PASSWORD = "Password123"


V3_USERS = [
    {
        "username": "user_a",
        "password": DEFAULT_PASSWORD,
        "role": "user",
        "status": "active",
        "profile": {
            "nickname": "普通用户 A",
            "contact": "user_a@school.example",
            "campus": "东校区",
        },
    },
    {
        "username": "user_b",
        "password": DEFAULT_PASSWORD,
        "role": "user",
        "status": "active",
        "profile": {
            "nickname": "普通用户 B",
            "contact": "user_b@school.example",
            "campus": "西校区",
        },
    },
    {
        "username": "seller_books",
        "password": DEFAULT_PASSWORD,
        "role": "user",
        "status": "active",
        "profile": {
            "nickname": "书香小铺",
            "contact": "books@school.example",
            "campus": "图书馆北门",
        },
    },
    {
        "username": "seller_digital",
        "password": DEFAULT_PASSWORD,
        "role": "user",
        "status": "active",
        "profile": {
            "nickname": "数码社团",
            "contact": "digital@school.example",
            "campus": "信息楼",
        },
    },
    {
        "username": "seller_life",
        "password": DEFAULT_PASSWORD,
        "role": "user",
        "status": "active",
        "profile": {
            "nickname": "宿舍好物站",
            "contact": "life@school.example",
            "campus": "南区宿舍",
        },
    },
    {
        "username": "seller_sports",
        "password": DEFAULT_PASSWORD,
        "role": "user",
        "status": "active",
        "profile": {
            "nickname": "运动补给摊",
            "contact": "sports@school.example",
            "campus": "体育馆",
        },
    },
    {
        "username": "buyer_lina",
        "password": DEFAULT_PASSWORD,
        "role": "user",
        "status": "active",
        "profile": {
            "nickname": "林娜",
            "contact": "lina@school.example",
            "campus": "东校区",
        },
    },
    {
        "username": "buyer_tao",
        "password": DEFAULT_PASSWORD,
        "role": "user",
        "status": "active",
        "profile": {
            "nickname": "阿涛",
            "contact": "tao@school.example",
            "campus": "西校区",
        },
    },
    {
        "username": "admin",
        "password": "Admin12345",
        "role": "admin",
        "status": "active",
        "profile": {
            "nickname": "管理员",
            "contact": "admin@school.example",
            "campus": "平台后台",
        },
    },
    {
        "username": "blocked_user",
        "password": DEFAULT_PASSWORD,
        "role": "user",
        "status": "disabled",
        "profile": {
            "nickname": "违规测试号",
            "contact": "blocked@school.example",
            "campus": "北区宿舍",
        },
    },
]


V3_PRODUCTS = [
    {
        "owner": "seller_books",
        "title": "计算机网络第 8 版教材",
        "description": "九成新，重点章节有少量荧光笔标注，适合计算机网络课程复习。",
        "price_cents": 3200,
        "category_key": "books",
        "category_name": "教材资料",
        "condition": "good",
        "palette": ("#BDEEE3", "#EAF8FF", "#2A7C6B"),
    },
    {
        "owner": "seller_books",
        "title": "考研英语真题套装",
        "description": "近十年真题，答案册完整，部分年份已做铅笔痕迹，可擦除。",
        "price_cents": 2600,
        "category_key": "books",
        "category_name": "教材资料",
        "condition": "like_new",
        "palette": ("#FFE1B8", "#FFF7EA", "#9A5B17"),
    },
    {
        "owner": "seller_books",
        "title": "线性代数辅导讲义",
        "description": "课堂配套讲义，含常考题型整理，封面轻微磨损。",
        "price_cents": 1800,
        "category_key": "books",
        "category_name": "教材资料",
        "condition": "fair",
        "status": "off_shelf",
        "palette": ("#D9E8FF", "#F7FBFF", "#3264A8"),
    },
    {
        "owner": "seller_digital",
        "title": "iPad Air 5 64G",
        "description": "蓝色 64G，屏幕无划痕，附保护壳和充电线，适合记笔记。",
        "price_cents": 265000,
        "category_key": "electronics",
        "category_name": "电子产品",
        "condition": "like_new",
        "palette": ("#C9E7FF", "#F2FAFF", "#1F6FA8"),
    },
    {
        "owner": "seller_digital",
        "title": "Sony WH-1000XM4 耳机",
        "description": "降噪正常，耳罩干净，续航稳定，适合图书馆自习。",
        "price_cents": 92000,
        "category_key": "electronics",
        "category_name": "电子产品",
        "condition": "good",
        "palette": ("#D8D6FF", "#F7F5FF", "#5A4AA8"),
    },
    {
        "owner": "seller_digital",
        "title": "罗技 K380 蓝牙键盘",
        "description": "多设备切换正常，按键回弹好，附两节新电池。",
        "price_cents": 9500,
        "category_key": "electronics",
        "category_name": "电子产品",
        "condition": "good",
        "palette": ("#D8F6E8", "#F7FFFB", "#1A7A5C"),
    },
    {
        "owner": "seller_life",
        "title": "宿舍床上小桌板",
        "description": "折叠稳定，桌面干净，适合床上学习或放电脑。",
        "price_cents": 2500,
        "category_key": "daily",
        "category_name": "生活用品",
        "condition": "good",
        "palette": ("#FFE2C7", "#FFF8F0", "#A8652B"),
    },
    {
        "owner": "seller_life",
        "title": "小熊电煮锅 1.2L",
        "description": "宿舍早餐煮面小锅，功能正常，内胆已清洁，建议自提验货。",
        "price_cents": 5800,
        "category_key": "daily",
        "category_name": "生活用品",
        "condition": "good",
        "palette": ("#FFD9DF", "#FFF7F9", "#A83A52"),
    },
    {
        "owner": "seller_life",
        "title": "桌面收纳抽屉三层",
        "description": "透明三层抽屉，能放文具、数据线和护肤小样。",
        "price_cents": 2200,
        "category_key": "daily",
        "category_name": "生活用品",
        "condition": "like_new",
        "palette": ("#D9F4FF", "#F2FBFF", "#287A96"),
    },
    {
        "owner": "seller_sports",
        "title": "Yonex 入门羽毛球拍",
        "description": "轻量球拍一支，线还比较紧，适合体育课和入门练习。",
        "price_cents": 6800,
        "category_key": "sports",
        "category_name": "运动器材",
        "condition": "good",
        "palette": ("#D7F7C8", "#F7FFF2", "#3E7E2B"),
    },
    {
        "owner": "seller_sports",
        "title": "加厚防滑瑜伽垫",
        "description": "墨绿色加厚款，使用次数少，送绑带，适合宿舍拉伸。",
        "price_cents": 3000,
        "category_key": "sports",
        "category_name": "运动器材",
        "condition": "like_new",
        "palette": ("#CDEFE0", "#F3FFF8", "#246B55"),
    },
    {
        "owner": "seller_sports",
        "title": "山地车骑行头盔",
        "description": "M 码，调节扣正常，适合校园骑行和周末短途。",
        "price_cents": 4500,
        "category_key": "sports",
        "category_name": "运动器材",
        "condition": "good",
        "palette": ("#FFE8AE", "#FFF9E8", "#926B14"),
    },
]


V3_ANNOUNCEMENTS = [
    {
        "title": "V3 演示数据已上线",
        "content": "本次演示库包含真实账号、每类商品、图片、交易、消息和 AI 日志，可直接用于答辩走查。",
        "status": "published",
    },
    {
        "title": "线下交易提醒",
        "content": "建议在校园公共区域当面验货，贵重数码商品请确认序列号、配件和电池状态。",
        "status": "published",
    },
    {
        "title": "图片展示优化说明",
        "content": "V3 商品已补充本地 PNG 图片，H5 与微信小程序均可通过后端静态地址加载。",
        "status": "published",
    },
]


def _font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if path and Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def _slug(value):
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    if cleaned:
        return cleaned
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:10]


def _draw_gradient(draw, width, height, start, end):
    start_rgb = tuple(int(start[i : i + 2], 16) for i in (1, 3, 5))
    end_rgb = tuple(int(end[i : i + 2], 16) for i in (1, 3, 5))
    for y in range(height):
        ratio = y / max(1, height - 1)
        color = tuple(round(start_rgb[i] * (1 - ratio) + end_rgb[i] * ratio) for i in range(3))
        draw.line([(0, y), (width, y)], fill=color)


def _wrap_text(draw, text, font, max_width):
    lines = []
    current = ""
    for char in text:
        probe = f"{current}{char}"
        bbox = draw.textbbox((0, 0), probe, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = probe
        else:
            if current:
                lines.append(current)
            current = char
    if current:
        lines.append(current)
    return lines[:3]


def _draw_product_illustration(draw, product, ink, primary):
    title = product["title"]
    category = product["category_key"]
    accent = "#FFFFFF"
    muted = "#6D817A"

    if category == "books":
        for index, offset in enumerate([0, 46, 92]):
            y = 308 + offset
            color = [accent, primary, "#FFF2CF"][index]
            draw.rounded_rectangle((765, y, 1010, y + 56), radius=18, fill=color, outline=ink, width=5)
            draw.line((810, y + 14, 970, y + 14), fill=ink, width=4)
            draw.line((810, y + 36, 940, y + 36), fill=muted, width=3)
        return

    if "iPad" in title:
        draw.rounded_rectangle((770, 270, 1035, 475), radius=30, fill=accent, outline=ink, width=8)
        draw.rounded_rectangle((795, 295, 1010, 445), radius=18, fill=primary)
        draw.ellipse((890, 452, 916, 478), fill=ink)
        return

    if "耳机" in title:
        draw.arc((770, 250, 1030, 490), start=205, end=335, fill=ink, width=16)
        draw.rounded_rectangle((750, 365, 825, 495), radius=34, fill=accent, outline=ink, width=8)
        draw.rounded_rectangle((975, 365, 1050, 495), radius=34, fill=accent, outline=ink, width=8)
        draw.line((815, 455, 880, 490), fill=ink, width=9)
        draw.line((985, 455, 920, 490), fill=ink, width=9)
        return

    if "键盘" in title:
        draw.rounded_rectangle((735, 305, 1055, 485), radius=34, fill=accent, outline=ink, width=8)
        for row in range(3):
            for col in range(6):
                x = 770 + col * 44
                y = 340 + row * 38
                draw.rounded_rectangle((x, y, x + 28, y + 24), radius=8, fill=primary)
        draw.rounded_rectangle((820, 452, 970, 472), radius=8, fill=primary)
        return

    if "桌板" in title:
        draw.rounded_rectangle((760, 330, 1040, 405), radius=22, fill=accent, outline=ink, width=7)
        draw.line((805, 405, 775, 515), fill=ink, width=9)
        draw.line((995, 405, 1025, 515), fill=ink, width=9)
        draw.rounded_rectangle((840, 260, 960, 325), radius=18, fill=primary, outline=ink, width=5)
        return

    if "电煮锅" in title:
        draw.rounded_rectangle((790, 350, 1010, 505), radius=42, fill=accent, outline=ink, width=8)
        draw.rounded_rectangle((830, 305, 970, 360), radius=22, fill=primary, outline=ink, width=6)
        draw.arc((750, 380, 840, 470), start=90, end=270, fill=ink, width=8)
        draw.arc((960, 380, 1050, 470), start=270, end=90, fill=ink, width=8)
        return

    if "收纳" in title:
        draw.rounded_rectangle((795, 285, 1015, 520), radius=30, fill=accent, outline=ink, width=8)
        for y in [320, 390, 460]:
            draw.rounded_rectangle((825, y, 985, y + 46), radius=16, fill=primary)
            draw.ellipse((895, y + 15, 916, y + 36), fill=ink)
        return

    if "球拍" in title:
        draw.ellipse((760, 245, 955, 440), fill=accent, outline=ink, width=8)
        for x in [805, 850, 895]:
            draw.line((x, 270, x, 415), fill=primary, width=4)
        for y in [295, 340, 385]:
            draw.line((785, y, 930, y), fill=primary, width=4)
        draw.line((920, 410, 1040, 530), fill=ink, width=14)
        return

    if "瑜伽垫" in title:
        draw.rounded_rectangle((765, 365, 1035, 470), radius=50, fill=primary, outline=ink, width=7)
        draw.ellipse((745, 355, 855, 480), fill=accent, outline=ink, width=7)
        draw.ellipse((780, 390, 825, 445), fill=primary, outline=ink, width=5)
        draw.line((920, 345, 920, 490), fill=ink, width=6)
        return

    if "头盔" in title:
        draw.pieslice((770, 270, 1040, 540), start=180, end=360, fill=accent, outline=ink, width=8)
        draw.rounded_rectangle((795, 390, 1005, 505), radius=34, fill=primary, outline=ink, width=7)
        draw.line((815, 430, 990, 430), fill=ink, width=7)
        return

    draw.rounded_rectangle((790, 300, 1020, 500), radius=44, fill=accent, outline=ink, width=8)
    draw.ellipse((860, 340, 950, 430), fill=primary)


def _create_product_image(upload_dir, product):
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"v3-{_slug(product['category_key'])}-{_slug(product['title'])}.png"
    target = upload_dir / filename
    if target.exists():
        return f"/uploads/images/{filename}"

    width, height = 1200, 900
    image = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(image)
    primary, surface, ink = product["palette"]
    _draw_gradient(draw, width, height, surface, primary)

    draw.ellipse((780, -120, 1160, 260), fill="#FFFFFF")
    draw.ellipse((900, 80, 1320, 520), fill=primary)
    draw.rounded_rectangle((80, 90, 1120, 810), radius=80, fill=(255, 255, 255), outline="#FFFFFF", width=8)
    draw.rounded_rectangle((120, 130, 1080, 770), radius=64, fill=surface)
    draw.ellipse((150, 500, 380, 730), fill=primary)
    draw.rounded_rectangle((730, 510, 1030, 690), radius=50, fill="#FFFFFF")
    _draw_product_illustration(draw, product, ink, primary)

    category_font = _font(34, bold=True)
    title_font = _font(66, bold=True)
    meta_font = _font(34)
    price_font = _font(54, bold=True)

    draw.rounded_rectangle((150, 165, 360, 225), radius=30, fill="#FFFFFF")
    draw.text((178, 174), product["category_name"], fill=ink, font=category_font)

    y = 310
    for line in _wrap_text(draw, product["title"], title_font, 720):
        draw.text((150, y), line, fill=ink, font=title_font)
        y += 82

    condition_map = {
        "new": "全新",
        "like_new": "几乎全新",
        "good": "轻微使用",
        "fair": "明显使用",
    }
    meta = f"{condition_map.get(product['condition'], product['condition'])} / 校园自提"
    draw.text((150, 645), meta, fill="#51645E", font=meta_font)
    draw.text((770, 570), f"¥{product['price_cents'] / 100:.0f}", fill="#C95F36", font=price_font)

    image.save(target, format="PNG", optimize=True)
    return f"/uploads/images/{filename}"


def _collection(name):
    from flask import current_app

    return current_app.extensions["mongo"].db[name]


def _cleanup_seeded_records():
    for name in [
        "trade_requests",
        "messages",
        "operation_logs",
        "ai_generation_logs",
        "announcements",
    ]:
        _collection(name).delete_many({"seed_tag": SEED_TAG})


def _tag(collection_name, document_id):
    _collection(collection_name).update_one({"_id": document_id}, {"$set": {"seed_tag": SEED_TAG}})


def _seed_users():
    users = {}
    for seed in V3_USERS:
        user = upsert_seed_user(
            username=seed["username"],
            password_hash=hash_password(seed["password"]),
            role=seed["role"],
            status=seed["status"],
            profile=seed["profile"],
        )
        _tag("users", user["_id"])
        users[seed["username"]] = user
        public = serialize_user(user)
        print(f"seeded user {public['username']} / {seed['password']} ({public['role']}, {public['status']})")
    return users


def _seed_products(upload_dir):
    products = {}
    for seed in V3_PRODUCTS:
        image_url = _create_product_image(upload_dir, seed)
        owner = find_user_by_username(seed["owner"])
        product = product_repository.upsert_sample_product(
            str(owner["_id"]),
            {
                **seed,
                "images": [image_url],
            },
        )
        _tag("products", product["_id"])
        products[seed["title"]] = product
        print(f"seeded product {seed['category_name']} / {seed['title']} / {image_url}")
    return products


def _set_trade_status(trade, status, completed_by=None):
    if status == "pending":
        return trade
    if status in {"confirmed", "completed"}:
        trade = trade_repository.confirm_trade(str(trade["_id"]))
    if status == "completed":
        product_repository.mark_product_sold(str(trade["product_id"]))
        trade = trade_repository.complete_trade(str(trade["_id"]), str(completed_by))
    if status == "cancelled":
        trade = trade_repository.cancel_trade(str(trade["_id"]))
    return trade


def _seed_trades_and_messages(products, users):
    trade_specs = [
        ("buyer_lina", "Sony WH-1000XM4 耳机", "pending", "想今天傍晚在图书馆门口看一下耳机。"),
        ("buyer_tao", "罗技 K380 蓝牙键盘", "confirmed", "键盘还在吗？我可以今晚自提。"),
        ("user_b", "iPad Air 5 64G", "completed", "iPad 可以带保护壳一起吗？"),
        ("user_a", "加厚防滑瑜伽垫", "cancelled", "临时不需要了，抱歉。"),
    ]
    trades = []
    for buyer_username, product_title, status, message in trade_specs:
        buyer = users[buyer_username]
        product = products[product_title]
        trade = trade_repository.create_trade(str(buyer["_id"]), product, message=f"[V3] {message}")
        trade = _set_trade_status(trade, status, completed_by=buyer["_id"])
        _tag("trade_requests", trade["_id"])
        trades.append(trade)
        print(f"seeded trade {product_title} -> {buyer_username} ({trade['status']})")

        seller_id = str(product["owner_id"])
        buyer_id = str(buyer["_id"])
        seller_message = message_repository.create_message(
            seller_id,
            "trade",
            f"收到购买请求：{product_title}",
            f"{users[buyer_username]['nickname']} 对该商品发起了购买请求。",
            related_type="trade",
            related_id=str(trade["_id"]),
        )
        buyer_message = message_repository.create_message(
            buyer_id,
            "trade",
            f"交易状态：{product_title}",
            f"当前交易状态为 {trade['status']}，请按页面提示继续处理。",
            related_type="trade",
            related_id=str(trade["_id"]),
        )
        _tag("messages", seller_message["_id"])
        _tag("messages", buyer_message["_id"])
    return trades


def _seed_announcements_and_logs(users, products):
    admin = users["admin"]
    for data in V3_ANNOUNCEMENTS:
        announcement = announcement_repository.create_announcement(data, str(admin["_id"]))
        _tag("announcements", announcement["_id"])
        print(f"seeded announcement {data['title']}")

    for action, target_type, target_id, details in [
        (
            "product_status_update",
            "product",
            str(products["线性代数辅导讲义"]["_id"]),
            {"from_status": "available", "to_status": "off_shelf", "reason": "V3 演示下架商品"},
        ),
        (
            "user_status_update",
            "user",
            str(users["blocked_user"]["_id"]),
            {"from_status": "active", "to_status": "disabled", "reason": "V3 演示禁用账号"},
        ),
    ]:
        log = operation_log_repository.create_log(str(admin["_id"]), action, target_type, target_id, details)
        _tag("operation_logs", log["_id"])
        print(f"seeded operation log {action}")


def _seed_ai_logs(users):
    specs = [
        (
            "seller_books",
            "title",
            "计算机网络教材 / 教材资料 / 轻微使用",
            "计算机网络教材九成新 | 计网第8版带标注 | 校园自提计网教材",
            "success",
            None,
        ),
        (
            "seller_digital",
            "description",
            "iPad Air 5 / 电子产品 / 几乎全新",
            "蓝色 iPad Air 5，屏幕无划痕，适合课堂笔记，支持校园内当面验货。",
            "success",
            None,
        ),
        (
            "seller_life",
            "title",
            "电煮锅 / 生活用品",
            "",
            "failed",
            "AI_UNAVAILABLE",
        ),
    ]
    for username, generation_type, prompt, response, status, error_code in specs:
        log = ai_log_repository.create_log(
            str(users[username]["_id"]),
            generation_type,
            "gpt-oss:120b-cloud",
            status,
            prompt_summary=prompt,
            response_summary=response,
            duration_ms=860 if status == "success" else 0,
            error_code=error_code,
            error_message="V3 演示：Ollama 暂不可用" if error_code else "",
        )
        _tag("ai_generation_logs", log["_id"])
        print(f"seeded ai log {username} / {generation_type} / {status}")


def seed_v3_demo():
    from flask import current_app

    upsert_default_categories()
    _cleanup_seeded_records()

    upload_dir = Path(current_app.config["UPLOAD_FOLDER"]) / "images"
    users = _seed_users()
    products = _seed_products(upload_dir)
    trades = _seed_trades_and_messages(products, users)
    _seed_announcements_and_logs(users, products)
    _seed_ai_logs(users)

    summary = {
        "users": len(V3_USERS),
        "products": len(V3_PRODUCTS),
        "trades": len(trades),
        "announcements": len(V3_ANNOUNCEMENTS),
        "images_dir": str(upload_dir),
        "seeded_at": utc_now_iso(),
    }
    print(f"V3 demo seed complete: {summary}")
    return summary


def main():
    app = create_app()
    with app.app_context():
        seed_v3_demo()


if __name__ == "__main__":
    main()
