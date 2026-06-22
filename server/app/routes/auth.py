from flask import Blueprint, g, request

from app.middleware.auth import require_auth
from app.repositories import users as user_repository
from app.services.auth import (
    AuthError,
    build_auth_payload,
    extract_profile,
    hash_password,
    validate_no_forbidden_fields,
    validate_password,
    validate_username,
    verify_password,
)
from app.utils.response import error_response, success_response


auth_bp = Blueprint("auth", __name__)


def _json_payload():
    return request.get_json(silent=True) or {}


def _auth_error(error):
    return error_response(error.error_code, error.message, error.status_code)


@auth_bp.post("/register")
def register():
    payload = _json_payload()
    try:
        validate_no_forbidden_fields(payload)
        username = validate_username(payload.get("username"))
        password = validate_password(payload.get("password"))
        profile = extract_profile(payload)
        user = user_repository.create_user(
            username=username,
            password_hash=hash_password(password),
            profile=profile,
        )
    except user_repository.DuplicateAccountError:
        return error_response("DUPLICATE_ACCOUNT", "账号已存在", 409)
    except AuthError as error:
        return _auth_error(error)

    return success_response(
        data=build_auth_payload(user),
        message="注册成功",
        status_code=201,
    )


@auth_bp.post("/login")
def login():
    payload = _json_payload()
    try:
        username = validate_username(payload.get("username"))
        password = payload.get("password")
        if not isinstance(password, str) or not password:
            raise AuthError("VALIDATION_ERROR", "请输入密码", 400)
    except AuthError as error:
        return _auth_error(error)

    user = user_repository.find_user_by_username(username)
    if not user or not verify_password(password, user.get("password_hash")):
        return error_response("INVALID_CREDENTIALS", "账号或密码错误", 401)
    if user.get("status") != "active":
        return error_response("USER_DISABLED", "账号已被禁用", 403)

    user_repository.mark_login(str(user["_id"]))
    return success_response(data=build_auth_payload(user), message="登录成功")


@auth_bp.post("/logout")
@require_auth
def logout():
    return success_response(data={"logged_out": True}, message="已退出登录")


@auth_bp.put("/password")
@require_auth
def change_password():
    payload = _json_payload()
    current_password = payload.get("current_password")
    new_password = payload.get("new_password")

    try:
        if not isinstance(current_password, str) or not current_password:
            raise AuthError("VALIDATION_ERROR", "请输入当前密码", 400)
        validate_password(new_password, "新密码")
    except AuthError as error:
        return _auth_error(error)

    if not verify_password(current_password, g.current_user.get("password_hash")):
        return error_response("INVALID_CREDENTIALS", "当前密码错误", 401)

    user_repository.update_password_hash(str(g.current_user["_id"]), hash_password(new_password))
    return success_response(data={"changed": True}, message="密码已更新")
