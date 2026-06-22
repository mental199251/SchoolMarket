# M8 测试报告

测试日期：2026-06-22

## 1. 覆盖范围

- 后端认证、用户资料、商品、上传、交易状态机、消息、管理员、统计和 AI 接口。
- M8 主流程：用户 A 发布商品，用户 B 发起购买，卖家确认，买家完成交易，商品变为已售。
- 安全与边界：权限字段注入、上传伪造类型、上传大小限制、重复购买、重复完成、AI 非法返回。
- 前端：请求封装、发布页校验、AI 候选采用、交易操作重复点击保护、H5 和微信小程序构建。
- 交付：初始化脚本、备份脚本、部署说明和答辩演示脚本。

## 2. 自动化测试

运行命令：

```bash
cd server
python3 -m pytest
```

重点新增：

- `tests/test_m8_acceptance.py::test_m8_full_acceptance_journey_and_state_conflicts`
- `tests/test_m8_acceptance.py::test_m8_upload_security_rejects_spoofed_and_oversized_files`
- `tests/test_m8_acceptance.py::test_m8_ai_invalid_response_is_logged_as_failure`

通过标准：

- 所有测试用例通过。
- 所有错误响应保持统一信封：`success`、`data`、`message`、`error_code`。
- 状态冲突返回 409，并带回最新交易状态。

本次结果：

- `python3 -m pytest`：34 passed。

## 3. 构建验证

H5：

```bash
cd frontend
npm run build:h5
```

微信小程序：

```bash
cd frontend
npm run build:mp-weixin
```

通过标准：

- 构建命令成功结束。
- 微信小程序产物生成在 `frontend/dist/build/mp-weixin`。
- 开发者工具导入后按 `docs/demo-script.md` 执行人工回归。

本次结果：

- `npm run build:h5`：通过。
- `npm run build:mp-weixin`：通过。

## 4. 手工回归清单

- 注册、登录、退出、资料修改和密码修改。
- 商品列表搜索、筛选、分页、详情、发布、编辑、下架、恢复和删除。
- 图片上传成功、伪造图片失败、超大图片失败。
- 买家发起购买，卖家确认，任一参与者完成交易。
- 取消、重复请求、重复完成、越权确认和已售商品购买冲突。
- 管理员用户治理、商品治理、公告、日志和统计。
- Ollama Cloud 可用时生成标题和描述；停止 Ollama 时保留表单并提示失败。
- MongoDB 不可用时 `/ready` 返回 `DATABASE_UNAVAILABLE`。

## 5. 已知环境说明

- 单元测试使用 `mongomock`，不要求本机安装 MongoDB。
- 完整 H5/微信开发者工具演示需要真实 MongoDB 或可用的测试 MongoDB。
- Ollama Cloud 模型需要在后端机器执行 `ollama signin`，项目不保存 API key。
