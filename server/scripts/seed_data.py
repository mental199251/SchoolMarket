from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from app.repositories.categories import upsert_default_categories
from app.repositories.products import serialize_product, upsert_sample_product
from app.repositories.users import find_user_by_username, serialize_user, upsert_seed_user
from app.services.auth import hash_password


SEED_USERS = [
    {
        "username": "user_a",
        "password": "Password123",
        "role": "user",
        "profile": {"nickname": "普通用户 A", "campus": "东校区"},
    },
    {
        "username": "user_b",
        "password": "Password123",
        "role": "user",
        "profile": {"nickname": "普通用户 B", "campus": "西校区"},
    },
    {
        "username": "admin",
        "password": "Admin12345",
        "role": "admin",
        "profile": {"nickname": "管理员"},
    },
]


SAMPLE_PRODUCTS = [
    {
        "owner": "user_a",
        "title": "高等数学教材",
        "description": "同济版教材，附少量课堂笔记。",
        "price_cents": 2800,
        "category_key": "books",
        "category_name": "教材资料",
        "condition": "good",
    },
    {
        "owner": "user_a",
        "title": "蓝牙耳机",
        "description": "续航正常，配件齐全。",
        "price_cents": 9900,
        "category_key": "electronics",
        "category_name": "电子产品",
        "condition": "like_new",
    },
    {
        "owner": "user_b",
        "title": "宿舍收纳盒",
        "description": "透明三层收纳盒，适合桌面整理。",
        "price_cents": 1800,
        "category_key": "daily",
        "category_name": "生活用品",
        "condition": "fair",
    },
    {
        "owner": "user_b",
        "title": "羽毛球拍",
        "description": "轻量球拍一支，适合入门练习。",
        "price_cents": 4500,
        "category_key": "sports",
        "category_name": "运动器材",
        "condition": "good",
    },
]


def main():
    app = create_app()
    with app.app_context():
        upsert_default_categories()
        print("seeded categories")

        for seed in SEED_USERS:
            user = upsert_seed_user(
                username=seed["username"],
                password_hash=hash_password(seed["password"]),
                role=seed["role"],
                profile=seed["profile"],
            )
            public = serialize_user(user)
            print(f"seeded {public['username']} / {seed['password']} ({public['role']})")

        for seed in SAMPLE_PRODUCTS:
            owner = find_user_by_username(seed["owner"])
            product = upsert_sample_product(str(owner["_id"]), seed)
            public_product = serialize_product(product)
            print(f"seeded product {public_product['title']} ({public_product['category_name']})")


if __name__ == "__main__":
    main()
