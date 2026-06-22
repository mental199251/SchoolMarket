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

## 交易请求

### 交易对象

```json
{
  "id": "66f000000000000000000030",
  "product_id": "66f000000000000000000020",
  "buyer_id": "66f000000000000000000002",
  "seller_id": "66f000000000000000000001",
  "product": {},
  "buyer": {},
  "seller": {},
  "status": "pending",
  "message": "想买这个",
  "created_at": "2026-06-22T10:00:00+00:00",
  "updated_at": "2026-06-22T10:00:00+00:00",
  "confirmed_at": null,
  "cancelled_at": null,
  "completed_at": null,
  "completed_by": null
}
```

状态流转：

```text
pending -> confirmed -> completed
pending -> cancelled
```

### POST /api/v1/trades

受保护接口。买家对可交易商品发起购买请求。

请求：

```json
{
  "product_id": "66f000000000000000000020",
  "message": "想买这个，今晚可以线下交易"
}
```

成功：HTTP 201，返回交易对象。

失败：

- `FORBIDDEN`：购买自己发布的商品。
- `PRODUCT_UNAVAILABLE`：商品不存在、已售、下架或状态不可购买。
- `DUPLICATE_TRADE_REQUEST`：同一买家对同一商品已有 `pending` 或 `confirmed` 请求。

### GET /api/v1/trades/my-buy

受保护接口。返回当前用户作为买家的交易请求。

查询参数：

| 参数 | 说明 |
| --- | --- |
| `page` / `page_size` | 分页，`page_size` 最大 50 |
| `status` | `pending`、`confirmed`、`cancelled`、`completed` |

### GET /api/v1/trades/my-sell

受保护接口。返回当前用户作为卖家的交易请求。查询参数同 `my-buy`。

### PUT /api/v1/trades/{id}/confirm

受保护接口。只有卖家可以确认 `pending` 请求。

成功返回更新后的交易对象，状态为 `confirmed`。

### PUT /api/v1/trades/{id}/cancel

受保护接口。买家或卖家可以取消 `pending` 请求。

成功返回更新后的交易对象，状态为 `cancelled`。

### PUT /api/v1/trades/{id}/complete

受保护接口。买家或卖家可以将 `confirmed` 请求标记为线下完成。完成时商品同步更新为 `sold`。

状态已变化或商品已不可完成时返回 HTTP 409，并在 `data.trade` 中返回最新交易状态。

## 消息与公告

交易创建、确认、取消和完成成功后会自动生成站内消息。消息对象：

```json
{
  "id": "66f000000000000000000040",
  "user_id": "66f000000000000000000001",
  "type": "trade",
  "title": "收到新的购买请求",
  "content": "普通用户 B 想购买「高等数学教材」。",
  "related_type": "trade",
  "related_id": "66f000000000000000000030",
  "is_read": false,
  "created_at": "2026-06-22T10:00:00+00:00",
  "read_at": null
}
```

### GET /api/v1/messages

受保护接口。返回当前用户消息分页，并额外返回 `unread_count`。

查询参数：

| 参数 | 说明 |
| --- | --- |
| `page` / `page_size` | 分页，`page_size` 最大 50 |
| `read` | `true` 或 `false`，筛选已读/未读 |
| `type` | 消息类型，当前为 `trade` |

### PUT /api/v1/messages/{id}/read

受保护接口。将当前用户的一条消息标记为已读，返回更新后的消息对象。

### PUT /api/v1/messages/read-all

受保护接口。将当前用户全部未读消息标记为已读。

成功：

```json
{
  "updated": 2
}
```

### GET /api/v1/announcements

公开接口。返回 `published` 公告分页。

公告对象：

```json
{
  "id": "66f000000000000000000050",
  "title": "线下交易提醒",
  "content": "请在校园公共区域完成线下交易。",
  "status": "published",
  "created_by": "66f000000000000000000003",
  "created_at": "2026-06-22T10:00:00+00:00",
  "updated_at": "2026-06-22T10:00:00+00:00"
}
```

## 管理员治理

以下接口均要求管理员 token。普通用户调用返回 `FORBIDDEN`；禁用用户即使持有管理员旧 token 也返回 `USER_DISABLED`。

### GET /api/v1/admin/users

查询用户分页。

查询参数：

| 参数 | 说明 |
| --- | --- |
| `page` / `page_size` | 分页，`page_size` 最大 50 |
| `keyword` | 账号或昵称关键词 |
| `role` | `user`、`admin` |
| `status` | `active`、`disabled` |

### PUT /api/v1/admin/users/{id}/status

禁用或恢复用户，并写入操作日志。

请求：

```json
{
  "status": "disabled"
}
```

### GET /api/v1/admin/products

查询商品治理列表。

查询参数：

| 参数 | 说明 |
| --- | --- |
| `page` / `page_size` | 分页，`page_size` 最大 50 |
| `keyword` | 标题或描述关键词 |
| `status` | `available`、`off_shelf`、`sold` |
| `category_key` | 分类 |
| `include_deleted=true` | 是否包含软删除商品 |

### PUT /api/v1/admin/products/{id}/status

管理员直接更新商品状态，并写入操作日志。

请求：

```json
{
  "status": "off_shelf"
}
```

### DELETE /api/v1/admin/products/{id}

管理员软删除商品，并写入操作日志。成功返回 `{ "deleted": true }`。

### GET /api/v1/admin/announcements

查询公告分页，默认包含隐藏公告，可用 `status=published|hidden` 筛选。

### POST /api/v1/admin/announcements

创建公告，并写入操作日志。成功 HTTP 201。

请求：

```json
{
  "title": "线下交易提醒",
  "content": "请在校园公共区域完成线下交易。",
  "status": "published"
}
```

### PUT /api/v1/admin/announcements/{id}

更新公告标题、内容和状态，并写入操作日志。请求字段同创建公告。

### DELETE /api/v1/admin/announcements/{id}

隐藏公告，并写入操作日志。成功返回 `{ "deleted": true }`。

### GET /api/v1/admin/logs

查询管理员操作日志。

查询参数：

| 参数 | 说明 |
| --- | --- |
| `page` / `page_size` | 分页，`page_size` 最大 50 |
| `action` | 例如 `user_status_update`、`product_status_update` |
| `target_type` | `user`、`product`、`announcement` |
| `operator_id` | 管理员用户 id |

日志对象：

```json
{
  "id": "66f000000000000000000060",
  "operator_id": "66f000000000000000000003",
  "operator": {
    "id": "66f000000000000000000003",
    "username": "admin",
    "nickname": "管理员",
    "role": "admin"
  },
  "action": "product_status_update",
  "target_type": "product",
  "target_id": "66f000000000000000000020",
  "details": {
    "status": "off_shelf",
    "title": "高等数学教材"
  },
  "created_at": "2026-06-22T10:00:00+00:00"
}
```

## 统计报表

以下接口均要求管理员 token。统计接口支持统一范围参数：

| 参数 | 说明 |
| --- | --- |
| `days` | 最近 N 天，默认 30，范围 1-365 |
| `start_date` / `end_date` | 固定日期范围，格式 `YYYY-MM-DD`，需同时提供 |
| `limit` | 排行接口返回数量，默认 10，范围 1-50 |

如果同时提供日期范围和 `days`，优先使用 `start_date` / `end_date`。

### GET /api/v1/stats/overview

返回平台概览、状态分布和范围信息。

```json
{
  "range": {
    "start_date": "2026-05-23",
    "end_date": "2026-06-22",
    "days": 30
  },
  "totals": {
    "users_total": 3,
    "new_users": 2,
    "products_total": 8,
    "published_products": 4,
    "trades_total": 5,
    "created_trades": 3,
    "completed_trades": 1,
    "completion_rate": 33.3
  },
  "status": {
    "users": {
      "active": 3,
      "disabled": 0
    },
    "products": {
      "available": 6,
      "off_shelf": 1,
      "sold": 1
    },
    "trades": {
      "pending": 1,
      "confirmed": 1,
      "cancelled": 1,
      "completed": 2
    }
  }
}
```

### GET /api/v1/stats/categories

按分类返回发布量和商品状态分布，按发布量降序。

```json
{
  "range": {
    "start_date": "2026-05-23",
    "end_date": "2026-06-22",
    "days": 30
  },
  "items": [
    {
      "category_key": "books",
      "category_name": "教材资料",
      "published_count": 3,
      "available_count": 2,
      "off_shelf_count": 0,
      "sold_count": 1
    }
  ],
  "limit": 10
}
```

### GET /api/v1/stats/users

返回活跃用户排行。活跃分由发布、成交、买入请求和收到请求综合计算，用于排序，不作为业务结算依据。

```json
{
  "range": {
    "start_date": "2026-05-23",
    "end_date": "2026-06-22",
    "days": 30
  },
  "items": [
    {
      "user": {
        "id": "66f000000000000000000001",
        "username": "user_a",
        "nickname": "普通用户 A",
        "role": "user",
        "status": "active",
        "campus": "东校区"
      },
      "published_count": 2,
      "buy_request_count": 0,
      "received_request_count": 2,
      "completed_count": 1,
      "activity_score": 11
    }
  ],
  "limit": 10
}
```

## AI 辅助发布

AI 接口均要求登录。后端调用 Ollama 的 `/api/generate` 非流式接口，只返回候选内容，不直接创建或修改商品。Ollama 地址、模型和超时从环境变量读取：

- `OLLAMA_BASE_URL`
- `OLLAMA_MODEL`
- `OLLAMA_CONNECT_TIMEOUT_SECONDS`
- `OLLAMA_RESPONSE_TIMEOUT_SECONDS`

Ollama 未启动、超时、非 2xx 响应或返回内容无法解析时，接口返回 HTTP 503 和 `AI_UNAVAILABLE`。前端保留原表单内容，用户仍可手工发布。

### POST /api/v1/ai/title

根据商品描述、分类、成色和价格生成标题候选。

请求：

```json
{
  "description": "同济版高等数学教材，八成新，附少量课堂笔记",
  "category_name": "教材资料",
  "condition": "good",
  "price_cents": 2800
}
```

成功：

```json
{
  "candidates": [
    "高数教材带笔记",
    "同济高数二手教材",
    "课堂笔记高数教材"
  ],
  "model": "qwen2.5:7b",
  "duration_ms": 1234,
  "log_id": "66f000000000000000000070"
}
```

### POST /api/v1/ai/description

根据标题、分类、成色、价格和现有描述生成描述候选。

请求：

```json
{
  "title": "高等数学教材",
  "category_name": "教材资料",
  "condition": "good",
  "price_cents": 2800,
  "description": "有课堂笔记"
}
```

成功响应字段同标题建议。

### AI 调用日志

每次成功或失败的 AI 调用都会写入 `ai_generation_logs`，字段包括：

```json
{
  "user_id": "66f000000000000000000001",
  "generation_type": "title",
  "model": "qwen2.5:7b",
  "status": "success",
  "prompt_summary": "教材资料 / good / 28.00 元 / 同济版高等数学教材...",
  "response_summary": "高数教材带笔记 | 同济高数二手教材",
  "duration_ms": 1234,
  "error_code": null,
  "error_message": "",
  "created_at": "2026-06-22T10:00:00+00:00"
}
```
