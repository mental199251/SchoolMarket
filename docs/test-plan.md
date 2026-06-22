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
