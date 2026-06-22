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
| 401 | `AUTH_REQUIRED` / `TOKEN_EXPIRED` / `INVALID_CREDENTIALS` | 未登录、令牌失效或账号密码错误 |
| 403 | `FORBIDDEN` / `USER_DISABLED` | 越权或账号禁用 |
| 404 | `NOT_FOUND` | 资源不存在 |
| 405 | `METHOD_NOT_ALLOWED` | 请求方法不支持 |
| 409 | `DUPLICATE_ACCOUNT` / `PRODUCT_UNAVAILABLE` / `DUPLICATE_TRADE_REQUEST` | 业务状态冲突 |
| 500 | `INTERNAL_ERROR` | 未分类服务端错误 |
| 503 | `DATABASE_UNAVAILABLE` / `AI_UNAVAILABLE` | 外部依赖不可用 |

## 认证与用户资料

### 用户对象

```json
{
  "id": "66f000000000000000000001",
  "username": "user_a",
  "role": "user",
  "status": "active",
  "nickname": "普通用户 A",
  "contact": "user_a@example.com",
  "campus": "东校区",
  "avatar_url": "",
  "created_at": "2026-06-22T10:00:00+00:00",
  "updated_at": "2026-06-22T10:00:00+00:00"
}
```

普通用户提交的 `role`、`status`、`password_hash`、`username_key`、`_id` 会被拒绝并返回 `VALIDATION_ERROR`。

### POST /api/v1/auth/register

注册普通用户并直接返回登录态。

请求：

```json
{
  "username": "alice",
  "password": "Password123",
  "nickname": "Alice",
  "contact": "alice@example.com",
  "campus": "东校区",
  "avatar_url": ""
}
```

成功：HTTP 201。

```json
{
  "token": "<jwt>",
  "expires_at": "2026-06-29T10:00:00+00:00",
  "user": {}
}
```

失败：

- `VALIDATION_ERROR`：账号格式、密码长度或资料字段无效。
- `DUPLICATE_ACCOUNT`：账号已存在。

### POST /api/v1/auth/login

请求：

```json
{
  "username": "alice",
  "password": "Password123"
}
```

成功返回与注册相同的登录态。

失败：

- `INVALID_CREDENTIALS`：账号或密码错误。
- `USER_DISABLED`：账号已禁用。

### POST /api/v1/auth/logout

受保护接口。当前版本 JWT 不做服务端黑名单，前端收到成功后清理本地登录态。

成功：

```json
{
  "logged_out": true
}
```

### PUT /api/v1/auth/password

受保护接口。

请求：

```json
{
  "current_password": "Password123",
  "new_password": "NewPassword123"
}
```

成功：

```json
{
  "changed": true
}
```

失败：

- `INVALID_CREDENTIALS`：当前密码错误。
- `VALIDATION_ERROR`：新密码不符合长度要求。

### GET /api/v1/users/me

受保护接口。返回当前 token 对应的最新用户资料；若用户已被禁用，即使 token 未过期也返回 `USER_DISABLED`。

### PUT /api/v1/users/me

受保护接口。只允许更新资料字段。

请求：

```json
{
  "nickname": "Alice",
  "contact": "alice@example.com",
  "campus": "东校区",
  "avatar_url": ""
}
```

成功返回更新后的用户对象。
