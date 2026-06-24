from http.client import HTTPConnection, HTTPSConnection
import json
from time import perf_counter
from urllib.parse import urlparse

from flask import current_app

from app.repositories import ai_generation_logs as log_repository


GENERATION_TYPES = {"title", "description"}


class AIError(Exception):
    def __init__(self, error_code, message, status_code=400):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.status_code = status_code


class AIUnavailable(AIError):
    def __init__(self, message="AI 服务暂不可用，请稍后重试"):
        super().__init__("AI_UNAVAILABLE", message, 503)


def _clean_text(value, field_name, min_length=0, max_length=500):
    if value in (None, "") and min_length == 0:
        return ""
    if not isinstance(value, str):
        raise AIError("VALIDATION_ERROR", f"{field_name}必须为字符串", 400)
    cleaned = value.strip()
    if len(cleaned) < min_length:
        raise AIError("VALIDATION_ERROR", f"{field_name}不能为空", 400)
    if len(cleaned) > max_length:
        raise AIError("VALIDATION_ERROR", f"{field_name}长度不能超过 {max_length} 位", 400)
    return cleaned


def _parse_price(value):
    if value in (None, ""):
        return ""
    if isinstance(value, bool):
        raise AIError("VALIDATION_ERROR", "价格格式无效", 400)
    try:
        cents = int(value)
    except (TypeError, ValueError):
        raise AIError("VALIDATION_ERROR", "价格格式无效", 400)
    if cents < 0 or cents > 1_000_000_00:
        raise AIError("VALIDATION_ERROR", "价格格式无效", 400)
    return f"{cents / 100:.2f} 元"


def _payload_context(payload):
    return {
        "title": _clean_text(payload.get("title", ""), "标题", max_length=80),
        "description": _clean_text(payload.get("description", ""), "描述", max_length=800),
        "category_name": _clean_text(payload.get("category_name", ""), "分类", max_length=40),
        "condition": _clean_text(payload.get("condition", ""), "成色", max_length=20),
        "price": _parse_price(payload.get("price_cents")),
    }


def validate_title_payload(payload):
    context = _payload_context(payload)
    if len(context["description"]) < 4:
        raise AIError("VALIDATION_ERROR", "请先填写至少 4 个字的描述", 400)
    return context


def validate_description_payload(payload):
    context = _payload_context(payload)
    if len(context["title"]) < 2:
        raise AIError("VALIDATION_ERROR", "请先填写至少 2 个字的标题", 400)
    return context


def _summary(context):
    parts = [
        context.get("title") or "",
        context.get("category_name") or "",
        context.get("condition") or "",
        context.get("price") or "",
        context.get("description") or "",
    ]
    return " / ".join(part for part in parts if part)[:240]


def _title_prompt(context):
    return f"""你是校园二手交易平台的发布助手。请基于用户已提供的信息生成商品标题候选。
要求：
- 只依据已给信息，不虚构品牌、型号、配件、成色或交易地点。
- 面向校园二手场景，真实、简洁、自然。
- 输出 JSON，格式必须是 {{"candidates":["标题1","标题2","标题3"]}}。
- 每个标题不超过 24 个中文字符。

已知信息：
分类：{context['category_name'] or '未填写'}
成色：{context['condition'] or '未填写'}
价格：{context['price'] or '未填写'}
描述：{context['description']}
"""


def _description_prompt(context):
    return f"""你是校园二手交易平台的发布助手。请基于用户已提供的信息生成商品描述候选。
要求：
- 只依据已给信息，不虚构品牌、型号、配件、购买时间、保修或交易地点。
- 面向校园二手场景，描述真实、简洁，可包含使用情况和线下交付提醒。
- 输出 JSON，格式必须是 {{"candidates":["描述1","描述2","描述3"]}}。
- 每个描述不超过 180 个中文字符。

已知信息：
标题：{context['title']}
分类：{context['category_name'] or '未填写'}
成色：{context['condition'] or '未填写'}
价格：{context['price'] or '未填写'}
现有描述：{context['description'] or '未填写'}
"""


def _ollama_endpoint():
    base_url = current_app.config["OLLAMA_BASE_URL"].rstrip("/")
    if base_url.endswith("/api"):
        return base_url
    return f"{base_url}/api"


def _is_cloud_model():
    model = current_app.config["OLLAMA_MODEL"]
    return model.endswith("-cloud") or model.endswith(":cloud")


def _setup_hint():
    if _is_cloud_model():
        return "后端机器需安装 Ollama，执行 ollama signin，并保持 ollama serve 运行。"
    return "后端机器需安装 Ollama，执行 ollama pull <模型名>，并保持 ollama serve 运行。"


def _request_ollama(method, path, payload=None):
    endpoint = f"{_ollama_endpoint()}{path}"
    parsed = urlparse(endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise AIUnavailable("AI 服务地址配置无效")

    connection_cls = HTTPSConnection if parsed.scheme == "https" else HTTPConnection
    port = parsed.port
    host = parsed.hostname
    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"

    body = None
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    connect_timeout = current_app.config["OLLAMA_CONNECT_TIMEOUT_SECONDS"]
    response_timeout = current_app.config["OLLAMA_RESPONSE_TIMEOUT_SECONDS"]

    connection = connection_cls(host, port=port, timeout=connect_timeout)
    try:
        connection.connect()
        if connection.sock:
            connection.sock.settimeout(response_timeout)
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        raw = response.read().decode("utf-8")
    except OSError as exc:
        raise AIUnavailable(f"无法连接 Ollama。{_setup_hint()}") from exc
    finally:
        connection.close()

    if response.status < 200 or response.status >= 300:
        upstream_message = ""
        try:
            error_payload = json.loads(raw)
            if isinstance(error_payload, dict):
                upstream_message = str(error_payload.get("error") or "").strip()
        except json.JSONDecodeError:
            pass

        if _is_cloud_model() and response.status in {401, 403}:
            raise AIUnavailable("Ollama Cloud 未登录或无权限，请在后端机器执行 ollama signin")
        if response.status == 410:
            message = upstream_message or "当前模型已被 Ollama Cloud 下线"
            raise AIUnavailable(f"Ollama 模型已下线：{message}")
        if response.status == 404:
            raise AIUnavailable(f"Ollama 模型不可用，请确认模型 {current_app.config['OLLAMA_MODEL']} 可访问")
        if upstream_message:
            raise AIUnavailable(f"Ollama 返回异常：{upstream_message}")
        raise AIUnavailable(f"Ollama 返回异常状态：{response.status}")

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AIUnavailable("Ollama 返回格式无效") from exc


def _post_ollama_generate(prompt):
    payload = _request_ollama(
        "POST",
        "/generate",
        {
            "model": current_app.config["OLLAMA_MODEL"],
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.35},
        },
    )
    text = payload.get("response")
    if not isinstance(text, str) or not text.strip():
        raise AIUnavailable("Ollama 未返回有效内容")
    return text


def get_ai_status():
    model = current_app.config["OLLAMA_MODEL"]
    data = {
        "base_url": current_app.config["OLLAMA_BASE_URL"],
        "model": model,
        "cloud_model": _is_cloud_model(),
        "service_available": False,
        "model_listed": False,
        "ready": False,
        "setup_hint": _setup_hint(),
        "error_code": None,
        "message": "",
    }
    try:
        tags = _request_ollama("GET", "/tags")
    except AIError as error:
        data["error_code"] = error.error_code
        data["message"] = error.message
        return data

    models = tags.get("models", [])
    listed_names = {
        item.get("name") or item.get("model")
        for item in models
        if isinstance(item, dict)
    }
    data["service_available"] = True
    data["model_listed"] = model in listed_names
    data["ready"] = data["model_listed"] or data["cloud_model"]
    data["message"] = "Ollama 服务可访问"
    if data["cloud_model"] and not data["model_listed"]:
        data["message"] = "Ollama 服务可访问；cloud 模型会在生成时使用本机登录状态访问"
    return data


def _extract_json_object(text):
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.removeprefix("json").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        try:
            return json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError:
            return None


def _normalize_candidates(text, max_length):
    parsed = _extract_json_object(text)
    raw_candidates = parsed.get("candidates") if isinstance(parsed, dict) else None
    if not isinstance(raw_candidates, list):
        raw_candidates = [line.strip("- 0123456789.、") for line in text.splitlines()]

    candidates = []
    seen = set()
    for item in raw_candidates:
        if not isinstance(item, str):
            continue
        candidate = " ".join(item.strip().split())
        if not candidate or len(candidate) > max_length or candidate in seen:
            continue
        seen.add(candidate)
        candidates.append(candidate)
        if len(candidates) >= 3:
            break
    if not candidates:
        raise AIUnavailable("AI 未生成可用候选")
    return candidates


def _log_result(user_id, generation_type, status, prompt_summary, candidates, duration_ms, error=None):
    return log_repository.create_log(
        user_id,
        generation_type,
        current_app.config["OLLAMA_MODEL"],
        status,
        prompt_summary=prompt_summary,
        response_summary=" | ".join(candidates)[:240] if candidates else "",
        duration_ms=duration_ms,
        error_code=getattr(error, "error_code", None),
        error_message=getattr(error, "message", str(error) if error else ""),
    )


def _generate(user_id, generation_type, context, prompt, max_length):
    started = perf_counter()
    prompt_summary = _summary(context)
    try:
        text = _post_ollama_generate(prompt)
        candidates = _normalize_candidates(text, max_length)
    except AIError as error:
        duration_ms = round((perf_counter() - started) * 1000)
        _log_result(user_id, generation_type, "failed", prompt_summary, [], duration_ms, error)
        raise
    except Exception as exc:
        duration_ms = round((perf_counter() - started) * 1000)
        error = AIUnavailable("AI 生成失败，请稍后重试")
        _log_result(user_id, generation_type, "failed", prompt_summary, [], duration_ms, error)
        raise error from exc

    duration_ms = round((perf_counter() - started) * 1000)
    log = _log_result(user_id, generation_type, "success", prompt_summary, candidates, duration_ms)
    return {
        "candidates": candidates,
        "model": current_app.config["OLLAMA_MODEL"],
        "duration_ms": duration_ms,
        "log_id": str(log["_id"]),
    }


def generate_titles(user_id, payload):
    context = validate_title_payload(payload)
    return _generate(user_id, "title", context, _title_prompt(context), 60)


def generate_descriptions(user_id, payload):
    context = validate_description_payload(payload)
    return _generate(user_id, "description", context, _description_prompt(context), 500)
