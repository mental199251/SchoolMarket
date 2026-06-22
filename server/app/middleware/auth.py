from functools import wraps

from flask import g, request

from app.repositories.users import find_user_by_id
from app.services.auth import AuthError, decode_access_token
from app.utils.response import error_response


def _auth_error_response(error):
    return error_response(
        error_code=error.error_code,
        message=error.message,
        status_code=error.status_code,
    )


def require_auth(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return _auth_error_response(
                AuthError("AUTH_REQUIRED", "请先登录后再操作", 401)
            )

        token = header.removeprefix("Bearer ").strip()
        if not token:
            return _auth_error_response(
                AuthError("AUTH_REQUIRED", "请先登录后再操作", 401)
            )

        try:
            payload = decode_access_token(token)
        except AuthError as error:
            return _auth_error_response(error)

        user = find_user_by_id(payload.get("sub"))
        if not user:
            return _auth_error_response(
                AuthError("AUTH_REQUIRED", "登录用户不存在，请重新登录", 401)
            )
        if user.get("status") != "active":
            return _auth_error_response(
                AuthError("USER_DISABLED", "账号已被禁用", 403)
            )

        g.current_user = user
        return view(*args, **kwargs)

    return wrapped


def require_admin(view):
    @require_auth
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.current_user.get("role") != "admin":
            return _auth_error_response(AuthError("FORBIDDEN", "没有权限执行该操作", 403))
        return view(*args, **kwargs)

    return wrapped
