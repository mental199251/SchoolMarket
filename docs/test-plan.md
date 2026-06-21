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

