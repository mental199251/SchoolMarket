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

## 商品与图片

### 分类对象

```json
{
  "id": "66f000000000000000000010",
  "key": "books",
  "name": "教材资料",
  "sort_order": 10,
  "is_active": true
}
```

### 商品对象

```json
{
  "id": "66f000000000000000000020",
  "owner_id": "66f000000000000000000001",
  "owner": {
    "id": "66f000000000000000000001",
    "username": "user_a",
    "nickname": "普通用户 A",
    "campus": "东校区"
  },
  "title": "高等数学教材",
  "description": "同济版教材，附少量课堂笔记。",
  "price_cents": 2800,
  "category_key": "books",
  "category_name": "教材资料",
  "condition": "good",
  "images": ["/uploads/images/example.png"],
  "status": "available",
  "created_at": "2026-06-22T10:00:00+00:00",
  "updated_at": "2026-06-22T10:00:00+00:00"
}
```

### GET /api/v1/categories

返回启用的商品分类。

成功：

```json
{
  "items": []
}
```

### POST /api/v1/uploads/images

受保护接口。使用 `multipart/form-data` 上传图片，字段名为 `images` 或 `file`。一次最多 9 张，单张默认不超过 5MB，仅支持 JPG、PNG、GIF 和 WEBP。

成功：HTTP 201。

```json
{
  "urls": ["/uploads/images/1f2a3b.png"]
}
```

### POST /api/v1/products

受保护接口。发布商品，状态直接进入 `available`。

请求：

```json
{
  "title": "高等数学教材",
  "description": "八成新，附课堂笔记",
  "price_cents": 2800,
  "category_key": "books",
  "condition": "good",
  "images": []
}
```

成功：HTTP 201，返回商品对象。

### GET /api/v1/products

公开商品列表默认只返回 `available` 且未删除商品。

查询参数：

| 参数 | 说明 |
| --- | --- |
| `page` / `page_size` | 分页，`page_size` 最大 50 |
| `keyword` | 标题或描述关键词 |
| `category_key` | 分类 |
| `condition` | 成色 |
| `min_price_cents` / `max_price_cents` | 价格区间，单位分 |
| `sort` | `newest`、`price_asc`、`price_desc` |
| `mine=true` | 受保护查询，返回当前用户自己的商品 |
| `status` | 与 `mine=true` 一起使用，筛选自己的商品状态 |

成功返回分页对象。

### GET /api/v1/products/{id}

公开接口。`available` 商品所有人可见；非公开状态只有商品所有者携带 token 时可见，否则返回 `NOT_FOUND`。

### PUT /api/v1/products/{id}

受保护接口。只有商品所有者可编辑，已售商品不可编辑。

请求字段与发布商品一致。成功返回更新后的商品对象。

### DELETE /api/v1/products/{id}

受保护接口。只有商品所有者可删除，已售商品不可删除。当前版本为软删除，公开列表和详情不再返回。

成功：

```json
{
  "deleted": true
}
```

### PUT /api/v1/products/{id}/status

受保护接口。只有商品所有者可操作。

请求：

```json
{
  "action": "off_shelf"
}
```

`action` 支持：

- `off_shelf`：可交易商品下架。
- `restore`：已下架商品恢复为可交易。

已售商品返回 `PRODUCT_UNAVAILABLE`。
