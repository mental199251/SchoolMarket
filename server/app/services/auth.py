from datetime import datetime, timedelta, timezone
import re

import bcrypt
import jwt
from flask import current_app

from app.repositories import users as user_repository


USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,32}$")
PROFILE_FIELDS = {"nickname", "contact", "campus", "avatar_url"}
FORBIDDEN_USER_FIELDS = {"role", "status", "password_hash", "username_key", "_id"}


class AuthError(Exception):
    def __init__(self, error_code, message, status_code=400):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.status_code = status_code


def validate_no_forbidden_fields(payload):
    forbidden = sorted(FORBIDDEN_USER_FIELDS.intersection(payload))
    if forbidden:
        raise AuthError(
            "VALIDATION_ERROR",
            f"不允许提交权限字段：{', '.join(forbidden)}",
            400,
        )


def validate_username(username):
    if not isinstance(username, str) or not USERNAME_RE.match(username.strip()):
        raise AuthError(
            "VALIDATION_ERROR",
            "账号需为 3-32 位字母、数字或下划线",
            400,
        )
    return username.strip()


def validate_password(password, field_name="password"):
    min_length = current_app.config["PASSWORD_MIN_LENGTH"]
    if not isinstance(password, str) or len(password) < min_length:
        raise AuthError(
            "VALIDATION_ERROR",
            f"{field_name} 至少需要 {min_length} 位",
            400,
        )
    return password


def extract_profile(payload):
    profile = {}
    for field in PROFILE_FIELDS:
        if field in payload:
            value = payload.get(field) or ""
            if not isinstance(value, str):
                raise AuthError("VALIDATION_ERROR", "资料字段必须为字符串", 400)
            if len(value) > 120:
                raise AuthError("VALIDATION_ERROR", "资料字段长度不能超过 120 位", 400)
            profile[field] = value
    return profile


def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password, password_hash):
    if not password_hash:
        return False
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def _jwt_secret():
    return current_app.config["JWT_SECRET_KEY"]


def create_access_token(user, expires_delta=None):
    now = datetime.now(timezone.utc)
    expires_delta = expires_delta or timedelta(
        seconds=current_app.config["JWT_EXPIRES_SECONDS"]
    )
    expires_at = now + expires_delta
    payload = {
        "sub": str(user["_id"]),
        "role": user.get("role", "user"),
        "iat": now,
        "exp": expires_at,
    }
    token = jwt.encode(payload, _jwt_secret(), algorithm="HS256")
    return token, expires_at.isoformat()


def decode_access_token(token):
    try:
        return jwt.decode(token, _jwt_secret(), algorithms=["HS256"])
    except jwt.ExpiredSignatureError as exc:
        raise AuthError("TOKEN_EXPIRED", "登录已过期，请重新登录", 401) from exc
    except jwt.InvalidTokenError as exc:
        raise AuthError("AUTH_REQUIRED", "登录状态无效，请重新登录", 401) from exc


def build_auth_payload(user):
    token, expires_at = create_access_token(user)
    return {
        "token": token,
        "expires_at": expires_at,
        "user": user_repository.serialize_user(user),
    }
