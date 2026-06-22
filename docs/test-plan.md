# 测试计划

## M0/M1 自动化测试

- `/health` 返回 HTTP 200 和统一响应。
- `/health` 不依赖 MongoDB。
- `/ready` 在 MongoDB可用时返回 HTTP 200。
- `/ready` 在 MongoDB不可用时返回 HTTP 503 和 `DATABASE_UNAVAILABLE`。
- 404、405 使用统一错误响应。
- 单元测试不要求本机 MongoDB，通过替换 ping 行为覆盖就绪和失败场景。

## M0/M1 构建检查

```bash
cd frontend
npm ci
npm run build:h5
npm run build:mp-weixin
```

## M0/M1 手工验收

1. 启动 MongoDB 和 Flask。
2. 在微信开发者工具打开首页。
3. 确认 Flask 状态为正常，MongoDB 状态为就绪。
4. 停止 MongoDB 后重新检查。
5. 确认 `/health` 仍正常，`/ready` 显示数据库不可用。
6. 停止 Flask，确认前端显示网络错误并可以重试。

## M2 自动化测试

- 注册成功后返回 token、过期时间和用户摘要。
- 登录成功后返回标准登录态。
- `GET /api/v1/users/me` 可读取当前用户最新资料。
- `PUT /api/v1/users/me` 可修改昵称、联系方式、校区和头像 URL。
- `PUT /api/v1/auth/password` 校验当前密码并更新密码哈希。
- `POST /api/v1/auth/logout` 返回统一成功响应。
- 重复账号返回 `DUPLICATE_ACCOUNT`。
- 错误密码返回 `INVALID_CREDENTIALS`。
- 缺失 token 返回 `AUTH_REQUIRED`。
- 过期 token 返回 `TOKEN_EXPIRED`。
- 禁用账号持有旧 token 时返回 `USER_DISABLED`。
- 普通用户提交 `role`、`status` 等权限字段返回 `VALIDATION_ERROR`。

## M2 手工验收

1. 启动 MongoDB 和 Flask。
2. 执行 `python scripts/seed_users.py` 初始化 `user_a`、`user_b` 和 `admin`。
3. 打开前端首页，进入登录 / 注册。
4. 注册新账号，确认自动进入个人中心。
5. 退出后使用新账号重新登录。
6. 编辑昵称、联系方式和校区，确认个人中心同步展示。
7. 修改密码，确认旧密码登录失败、新密码登录成功。
8. 使用重复账号注册，确认页面展示账号已存在。

## M3 自动化测试

- `GET /api/v1/categories` 返回教材资料、电子产品、生活用品和运动器材分类。
- `POST /api/v1/products` 登录后可发布商品。
- `GET /api/v1/products` 支持关键词、分类、成色、价格和排序筛选，默认只返回 `available`。
- `GET /api/v1/products/{id}` 可查看公开商品，非公开商品仅所有者可见。
- `PUT /api/v1/products/{id}` 只能由所有者编辑，非所有者返回 `FORBIDDEN`。
- `PUT /api/v1/products/{id}/status` 支持下架和恢复。
- `DELETE /api/v1/products/{id}` 只能由所有者删除。
- 已售商品不能编辑、下架或删除，返回 `PRODUCT_UNAVAILABLE`。
- `POST /api/v1/uploads/images` 校验登录态、扩展名、MIME、文件内容、数量和大小。

## M3 手工验收

1. 启动 MongoDB 和 Flask。
2. 执行 `python scripts/seed_data.py` 初始化分类、账号和示例商品。
3. 打开首页，确认能看到最新商品。
4. 进入商品列表，按关键词、分类、成色和排序筛选。
5. 使用 `user_a` 登录，发布一个带图片的新商品。
6. 使用 `user_b` 登录，确认能搜索并查看 `user_a` 发布的商品详情。
7. 切回 `user_a`，进入我的商品，编辑、下架、恢复该商品。
8. 确认 `user_b` 无法编辑 `user_a` 的商品。

## M4 自动化测试

- `POST /api/v1/trades` 可对 `available` 商品发起购买请求。
- 自购返回 `FORBIDDEN`。
- 同一买家对同一商品重复有效请求返回 `DUPLICATE_TRADE_REQUEST`。
- `GET /api/v1/trades/my-buy` 返回当前买家的请求。
- `GET /api/v1/trades/my-sell` 返回当前卖家的请求。
- 非卖家确认返回 `FORBIDDEN`。
- 非参与者取消或完成返回 `FORBIDDEN`。
- 卖家可将 `pending` 确认为 `confirmed`。
- 买家或卖家可将 `pending` 取消为 `cancelled`。
- 买家或卖家可将 `confirmed` 完成为 `completed`，商品同步变为 `sold`。
- 对已取消或已完成交易重复操作返回 HTTP 409，并带回最新交易状态。
- 下架、已售或不存在商品不能发起交易。

## M4 手工验收

1. 启动 MongoDB 和 Flask。
2. 执行 `python scripts/seed_data.py` 初始化分类、账号和示例商品。
3. 使用 `user_a` 发布或确认已有一个 `available` 商品。
4. 使用 `user_b` 打开商品详情并发起购买。
5. 在 `user_b` 的“我的购买”中确认请求为待处理。
6. 切换到 `user_a`，在“收到的请求”中确认该请求。
7. 任一参与者标记线下交易完成。
8. 回到商品详情，确认商品状态为已成交，公开列表不再展示该商品。
9. 验证自购、重复请求、非卖家确认、非参与者完成和重复完成会被拒绝。

## M5 自动化测试

- 交易创建后卖家收到“新的购买请求”站内消息。
- 卖家确认后买家收到“购买请求已确认”站内消息。
- 交易完成后买家和卖家收到完成消息。
- 交易取消后非操作者收到取消消息。
- `GET /api/v1/messages` 返回未读数量，单条已读和全部已读接口可更新状态。
- 普通用户调用 `/api/v1/admin/*` 返回 `FORBIDDEN`。
- 管理员可查询用户、禁用和恢复普通用户。
- 普通用户被禁用后，旧 token 访问受保护接口立即返回 `USER_DISABLED`。
- 管理员可治理商品状态，商品治理操作写入日志。
- 管理员可创建、更新和隐藏公告，公开公告接口只返回 `published`。
- 管理员日志查询返回操作者、目标、动作、时间和详情。

## M5 手工验收

1. 启动 MongoDB 和 Flask。
2. 执行 `python scripts/seed_data.py` 初始化分类、账号、管理员和示例商品。
3. 使用 `user_b` 对 `user_a` 的可交易商品发起购买请求。
4. 切换到 `user_a`，进入消息中心，确认出现新的购买请求消息并可标记已读。
5. 在“收到的请求”确认交易，再切回 `user_b`，确认消息中心收到确认消息。
6. 完成交易后，买卖双方消息中心都能看到完成消息。
7. 使用 `admin / Admin12345` 登录，进入用户管理，禁用 `user_b`。
8. 使用 `user_b` 的旧登录态访问个人中心或消息中心，确认返回账号已禁用。
9. 管理员恢复 `user_b`，并在商品治理中下架或删除一个商品。
10. 管理员创建一条已发布公告，回到首页确认公告可见；隐藏后首页不再展示。
11. 进入操作日志，确认用户状态、商品治理和公告维护操作都有记录。

## M6 自动化测试

- 普通用户调用 `/api/v1/stats/*` 返回 `FORBIDDEN`。
- 管理员可查询 `/api/v1/stats/overview`，返回用户、商品、交易总量和状态分布。
- 概览统计包含范围内发布量、交易请求量、成交量和成交率。
- `/api/v1/stats/categories` 使用商品聚合返回分类发布量、可交易量、下架量和成交量。
- `/api/v1/stats/users` 返回活跃用户排行，包含发布、买入请求、收到请求、完成交易和活跃分。
- `days`、`start_date`、`end_date` 和 `limit` 参数非法时返回 `VALIDATION_ERROR`。

## M6 手工验收

1. 启动 MongoDB 和 Flask。
2. 执行 `python scripts/seed_data.py` 初始化分类、账号、管理员和示例商品。
3. 使用 `user_a` 发布至少两个不同分类商品。
4. 使用 `user_b` 发起购买请求，并完成其中一笔交易。
5. 使用 `admin / Admin12345` 登录，进入后台统计。
6. 切换近 7 天、近 30 天和近 90 天，确认卡片和图表刷新。
7. 核对发布量、交易请求量、成交量和分类排行与测试数据一致。
8. 确认普通用户无法打开统计页面，也无法直接调用统计接口。
