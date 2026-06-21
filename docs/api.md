# API 契约

## 基础约定

- 业务接口统一使用 `/api/v1` 前缀。
- 健康检查使用根路径 `/health` 和 `/ready`。
- JSON 请求使用 `Content-Type: application/json`。
- 受保护接口使用 `Authorization: Bearer <token>`。
- 时间字段使用带时区的 ISO 8601 字符串。

## 统一响应

成功：

```json
{
  "success": true,
  "data": {},
  "message": "success",
  "error_code": null
}
```

失败：

```json
{
  "success": false,
  "data": null,
  "message": "面向用户的错误说明",
  "error_code": "ERROR_CODE"
}
```

分页接口的 `data` 固定为：

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20
}
```

## 健康检查

### GET /health

只检查 Flask 进程，不访问 MongoDB 或 Ollama。Flask 正常时返回 HTTP 200。

### GET /ready

检查 MongoDB 连接。MongoDB 可用时返回 HTTP 200，不可用时返回 HTTP 503 和 `DATABASE_UNAVAILABLE`。Ollama 不属于核心就绪条件。

## 通用错误码

| HTTP | 错误码 | 含义 |
| --- | --- | --- |
| 400 | `VALIDATION_ERROR` | 请求字段无效 |
| 401 | `AUTH_REQUIRED` / `TOKEN_EXPIRED` | 未登录或令牌失效 |
| 403 | `FORBIDDEN` / `USER_DISABLED` | 越权或账号禁用 |
| 404 | `NOT_FOUND` | 资源不存在 |
| 405 | `METHOD_NOT_ALLOWED` | 请求方法不支持 |
| 409 | `PRODUCT_UNAVAILABLE` / `DUPLICATE_TRADE_REQUEST` | 业务状态冲突 |
| 500 | `INTERNAL_ERROR` | 未分类服务端错误 |
| 503 | `DATABASE_UNAVAILABLE` / `AI_UNAVAILABLE` | 外部依赖不可用 |

