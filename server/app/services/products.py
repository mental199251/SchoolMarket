from app.repositories import categories as category_repository


CONDITIONS = {"new", "like_new", "good", "fair"}
PRODUCT_STATUSES = {"available", "off_shelf", "sold"}
SORT_OPTIONS = {"newest", "price_asc", "price_desc"}


class ProductError(Exception):
    def __init__(self, error_code, message, status_code=400):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.status_code = status_code


def _clean_text(value, field_name, min_length=0, max_length=120):
    if not isinstance(value, str):
        raise ProductError("VALIDATION_ERROR", f"{field_name}必须为字符串", 400)
    cleaned = value.strip()
    if len(cleaned) < min_length:
        raise ProductError("VALIDATION_ERROR", f"{field_name}不能为空", 400)
    if len(cleaned) > max_length:
        raise ProductError("VALIDATION_ERROR", f"{field_name}长度不能超过 {max_length} 位", 400)
    return cleaned


def _parse_price_cents(value):
    if isinstance(value, bool):
        raise ProductError("VALIDATION_ERROR", "价格格式无效", 400)
    try:
        price_cents = int(value)
    except (TypeError, ValueError):
        raise ProductError("VALIDATION_ERROR", "价格格式无效", 400)
    if price_cents <= 0 or price_cents > 1_000_000_00:
        raise ProductError("VALIDATION_ERROR", "价格需大于 0 且不超过 100 万元", 400)
    return price_cents


def _parse_images(value):
    if value in (None, ""):
        return []
    if not isinstance(value, list):
        raise ProductError("VALIDATION_ERROR", "图片字段必须为数组", 400)
    if len(value) > 9:
        raise ProductError("VALIDATION_ERROR", "最多上传 9 张图片", 400)
    images = []
    for url in value:
        cleaned = _clean_text(url, "图片 URL", min_length=1, max_length=300)
        images.append(cleaned)
    return images


def validate_product_payload(payload):
    title = _clean_text(payload.get("title"), "标题", min_length=2, max_length=80)
    description = _clean_text(
        payload.get("description", ""),
        "描述",
        min_length=0,
        max_length=2000,
    )
    category_key = _clean_text(payload.get("category_key"), "分类", min_length=1, max_length=40)
    category = category_repository.find_category_by_key(category_key)
    if not category:
        raise ProductError("VALIDATION_ERROR", "分类不存在或已停用", 400)

    condition = _clean_text(payload.get("condition"), "成色", min_length=1, max_length=20)
    if condition not in CONDITIONS:
        raise ProductError("VALIDATION_ERROR", "成色值无效", 400)

    return {
        "title": title,
        "description": description,
        "price_cents": _parse_price_cents(payload.get("price_cents")),
        "category_key": category_key,
        "category_name": category["name"],
        "condition": condition,
        "images": _parse_images(payload.get("images")),
    }


def parse_product_filters(args):
    try:
        page = max(1, int(args.get("page", 1)))
        page_size = min(50, max(1, int(args.get("page_size", 20))))
    except (TypeError, ValueError):
        raise ProductError("VALIDATION_ERROR", "分页参数无效", 400)

    filters = {
        "page": page,
        "page_size": page_size,
        "keyword": (args.get("keyword") or "").strip(),
        "category_key": (args.get("category_key") or "").strip(),
        "condition": (args.get("condition") or "").strip(),
        "sort": (args.get("sort") or "newest").strip(),
        "status": (args.get("status") or "").strip(),
    }

    if filters["condition"] and filters["condition"] not in CONDITIONS:
        raise ProductError("VALIDATION_ERROR", "成色值无效", 400)
    if filters["sort"] not in SORT_OPTIONS:
        raise ProductError("VALIDATION_ERROR", "排序值无效", 400)
    if filters["status"] and filters["status"] not in PRODUCT_STATUSES:
        raise ProductError("VALIDATION_ERROR", "商品状态无效", 400)

    for source, target in (
        ("min_price_cents", "min_price_cents"),
        ("max_price_cents", "max_price_cents"),
    ):
        raw = args.get(source)
        if raw in (None, ""):
            filters[target] = None
            continue
        try:
            filters[target] = int(raw)
        except (TypeError, ValueError):
            raise ProductError("VALIDATION_ERROR", "价格筛选参数无效", 400)

    if filters["category_key"] and not category_repository.find_category_by_key(filters["category_key"]):
        raise ProductError("VALIDATION_ERROR", "分类不存在或已停用", 400)

    return filters


def ensure_owner(product, user):
    if str(product["owner_id"]) != str(user["_id"]):
        raise ProductError("FORBIDDEN", "只能操作自己的商品", 403)


def ensure_editable(product):
    if product.get("status") == "sold":
        raise ProductError("PRODUCT_UNAVAILABLE", "已售商品不能编辑", 409)


def resolve_target_status(product, payload):
    target = (payload.get("status") or payload.get("action") or "").strip()
    action_map = {
        "off_shelf": "off_shelf",
        "restore": "available",
        "available": "available",
    }
    if target not in action_map:
        raise ProductError("VALIDATION_ERROR", "状态操作无效", 400)
    target_status = action_map[target]

    current_status = product.get("status")
    if current_status == "sold":
        raise ProductError("PRODUCT_UNAVAILABLE", "已售商品不能变更状态", 409)
    if target_status == current_status:
        return target_status
    if target_status == "available" and current_status != "off_shelf":
        raise ProductError("PRODUCT_UNAVAILABLE", "只有已下架商品可以恢复", 409)
    if target_status == "off_shelf" and current_status != "available":
        raise ProductError("PRODUCT_UNAVAILABLE", "只有可交易商品可以下架", 409)
    return target_status
