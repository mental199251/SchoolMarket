from bson import ObjectId
from bson.errors import InvalidId


USER_STATUSES = {"active", "disabled"}
PRODUCT_STATUSES = {"available", "off_shelf", "sold"}
ANNOUNCEMENT_STATUSES = {"published", "hidden"}


class AdminError(Exception):
    def __init__(self, error_code, message, status_code=400):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.status_code = status_code


def parse_pagination(args):
    try:
        page = max(1, int(args.get("page", 1)))
        page_size = min(50, max(1, int(args.get("page_size", 20))))
    except (TypeError, ValueError):
        raise AdminError("VALIDATION_ERROR", "分页参数无效", 400)
    return page, page_size


def parse_user_filters(args):
    page, page_size = parse_pagination(args)
    role = (args.get("role") or "").strip()
    status = (args.get("status") or "").strip()
    if role and role not in {"user", "admin"}:
        raise AdminError("VALIDATION_ERROR", "角色无效", 400)
    if status and status not in USER_STATUSES:
        raise AdminError("VALIDATION_ERROR", "用户状态无效", 400)
    return {
        "page": page,
        "page_size": page_size,
        "keyword": (args.get("keyword") or "").strip(),
        "role": role,
        "status": status,
    }


def parse_admin_product_filters(args):
    page, page_size = parse_pagination(args)
    status = (args.get("status") or "").strip()
    if status and status not in PRODUCT_STATUSES:
        raise AdminError("VALIDATION_ERROR", "商品状态无效", 400)
    return {
        "page": page,
        "page_size": page_size,
        "keyword": (args.get("keyword") or "").strip(),
        "status": status,
        "category_key": (args.get("category_key") or "").strip(),
        "include_deleted": (args.get("include_deleted") or "").lower() == "true",
    }


def parse_log_filters(args):
    page, page_size = parse_pagination(args)
    operator_id = (args.get("operator_id") or "").strip()
    if operator_id:
        try:
            ObjectId(operator_id)
        except (InvalidId, TypeError):
            raise AdminError("VALIDATION_ERROR", "操作者无效", 400)
    return {
        "page": page,
        "page_size": page_size,
        "action": (args.get("action") or "").strip(),
        "target_type": (args.get("target_type") or "").strip(),
        "operator_id": operator_id,
    }


def validate_user_status(status):
    if status not in USER_STATUSES:
        raise AdminError("VALIDATION_ERROR", "用户状态无效", 400)
    return status


def validate_product_status(status):
    if status not in PRODUCT_STATUSES:
        raise AdminError("VALIDATION_ERROR", "商品状态无效", 400)
    return status


def validate_announcement_payload(payload):
    title = payload.get("title")
    content = payload.get("content", "")
    status = payload.get("status", "published")
    if not isinstance(title, str) or not title.strip():
        raise AdminError("VALIDATION_ERROR", "公告标题不能为空", 400)
    if len(title.strip()) > 80:
        raise AdminError("VALIDATION_ERROR", "公告标题不能超过 80 位", 400)
    if not isinstance(content, str):
        raise AdminError("VALIDATION_ERROR", "公告内容必须为字符串", 400)
    if len(content) > 2000:
        raise AdminError("VALIDATION_ERROR", "公告内容不能超过 2000 位", 400)
    if status not in ANNOUNCEMENT_STATUSES:
        raise AdminError("VALIDATION_ERROR", "公告状态无效", 400)
    return {
        "title": title.strip(),
        "content": content.strip(),
        "status": status,
    }


def parse_announcement_filters(args, include_hidden=False):
    page, page_size = parse_pagination(args)
    status = (args.get("status") or "").strip()
    if status and status not in ANNOUNCEMENT_STATUSES:
        raise AdminError("VALIDATION_ERROR", "公告状态无效", 400)
    return {
        "page": page,
        "page_size": page_size,
        "status": status,
        "include_hidden": include_hidden,
    }
