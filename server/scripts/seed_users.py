from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from app.repositories.users import serialize_user, upsert_seed_user
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


def main():
    app = create_app()
    with app.app_context():
        for seed in SEED_USERS:
            user = upsert_seed_user(
                username=seed["username"],
                password_hash=hash_password(seed["password"]),
                role=seed["role"],
                profile=seed["profile"],
            )
            public_user = serialize_user(user)
            print(
                f"{public_user['username']} / {seed['password']} "
                f"({public_user['role']})"
            )


if __name__ == "__main__":
    main()
