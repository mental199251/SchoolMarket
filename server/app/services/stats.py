from datetime import datetime, timedelta, timezone
import re


DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DEFAULT_DAYS = 30
MAX_DAYS = 365
MAX_LIMIT = 50


class StatsError(Exception):
    def __init__(self, error_code, message, status_code=400):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.status_code = status_code


def _parse_date(value, end_of_day=False):
    if not isinstance(value, str) or not DATE_RE.match(value.strip()):
        raise StatsError("VALIDATION_ERROR", "日期格式需为 YYYY-MM-DD", 400)

    hour = 23 if end_of_day else 0
    minute = 59 if end_of_day else 0
    second = 59 if end_of_day else 0
    microsecond = 999999 if end_of_day else 0
    year, month, day = [int(part) for part in value.split("-")]
    return datetime(
        year,
        month,
        day,
        hour,
        minute,
        second,
        microsecond,
        tzinfo=timezone.utc,
    )


def _parse_days(args):
    try:
        days = int(args.get("days", DEFAULT_DAYS))
    except (TypeError, ValueError):
        raise StatsError("VALIDATION_ERROR", "统计天数无效", 400)
    if days < 1 or days > MAX_DAYS:
        raise StatsError("VALIDATION_ERROR", f"统计天数需在 1-{MAX_DAYS} 天内", 400)
    return days


def parse_stats_filters(args):
    start_value = (args.get("start_date") or "").strip()
    end_value = (args.get("end_date") or "").strip()

    if start_value or end_value:
        if not start_value or not end_value:
            raise StatsError("VALIDATION_ERROR", "请同时提供开始日期和结束日期", 400)
        start_at = _parse_date(start_value)
        end_at = _parse_date(end_value, end_of_day=True)
        if start_at > end_at:
            raise StatsError("VALIDATION_ERROR", "开始日期不能晚于结束日期", 400)
        if end_at - start_at > timedelta(days=MAX_DAYS):
            raise StatsError("VALIDATION_ERROR", f"统计范围不能超过 {MAX_DAYS} 天", 400)
        days = (end_at.date() - start_at.date()).days + 1
    else:
        days = _parse_days(args)
        end_at = datetime.now(timezone.utc)
        start_at = end_at - timedelta(days=days)

    return {
        "start_at": start_at.isoformat(),
        "end_at": end_at.isoformat(),
        "start_date": start_at.date().isoformat(),
        "end_date": end_at.date().isoformat(),
        "days": days,
    }


def parse_stats_limit(args, default=10):
    try:
        limit = int(args.get("limit", default))
    except (TypeError, ValueError):
        raise StatsError("VALIDATION_ERROR", "结果数量无效", 400)
    if limit < 1 or limit > MAX_LIMIT:
        raise StatsError("VALIDATION_ERROR", f"结果数量需在 1-{MAX_LIMIT} 之间", 400)
    return limit
