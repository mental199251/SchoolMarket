# 校淘空间

“校淘空间”是面向校园师生的二手交易平台。前端使用 uni-app、Vue 3 和 Vite，后端使用 Flask，数据存储使用 MongoDB。

## 当前进度

- M0：工程基线与协作规范
- M1：前后端健康检查链路
- M2：账号注册登录、JWT 鉴权、个人资料和密码修改
- M3：商品浏览、发布、编辑、下架、图片上传和我的商品
- M4：购买请求、卖家确认/取消和交易完成状态机
- M5：站内消息、管理员用户/商品/公告治理和操作日志
- M6：管理端概览、热门分类和活跃用户统计报表
- M7：Ollama 商品标题和描述建议、AI 调用日志和失败降级
- M8：系统回归测试、重复操作保护、备份脚本和答辩交付文档
- V2：前端 UI 重构，提供可爱、轻盈、灵动的 H5/微信小程序视觉体验

## 环境要求

- Node.js 20
- Python 3.11 或 3.12
- MongoDB 7.x
- MongoDB Database Tools（备份恢复需要）
- 微信开发者工具
- Ollama（AI 功能需要）

## 初始化

```bash
cp .env.example .env

cd frontend
npm ci

cd ../server
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## 启动后端

```bash
cd server
source .venv/bin/activate
python run.py
```

默认监听 `0.0.0.0:5001`：

- `GET /health`：仅检查 Flask 服务
- `GET /ready`：检查 Flask 和 MongoDB

初始化 M2 演示账号：

```bash
cd server
source .venv/bin/activate
python scripts/seed_users.py
```

初始化 M3 分类、演示账号和示例商品：

```bash
cd server
source .venv/bin/activate
python scripts/seed_data.py
```

默认账号：

| 账号 | 密码 | 角色 |
| --- | --- | --- |
| `user_a` | `Password123` | 普通用户 |
| `user_b` | `Password123` | 普通用户 |
| `admin` | `Admin12345` | 管理员 |

## AI 模型启用

AI 发布助手通过后端访问本机 Ollama HTTP API。默认配置使用 Ollama Cloud 模型，不需要在项目中配置 API key；在运行后端的机器上安装 Ollama 后执行：

```bash
ollama signin
ollama serve
```

`.env` 中保持：

```env
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=gpt-oss:120b-cloud
```

登录应用后可通过 `GET /api/v1/ai/status` 检查 Ollama 服务和模型配置。若改用完全本地模型，将 `OLLAMA_MODEL` 改为已拉取的本地模型名即可。

## 数据备份

安装 MongoDB Database Tools 后执行：

```bash
cd server
source .venv/bin/activate
python scripts/backup_database.py
```

默认备份到 `server/backups/`，该目录不会提交到 Git。恢复命令见 [部署与备份说明](docs/deployment.md)。

## 启动前端

H5：

```bash
cd frontend
npm run dev:h5
```

微信小程序：

```bash
cd frontend
npm run dev:mp-weixin
```

然后在微信开发者工具中导入 `frontend/dist/dev/mp-weixin`。

前端通过 `frontend/.env.development` 中的 `VITE_API_BASE_URL` 访问后端。真机调试时不能使用 `127.0.0.1`，需要改为运行 Flask 的电脑局域网地址。

## 测试与构建

```bash
cd server
source .venv/bin/activate
pytest

cd ../frontend
npm run build:h5
npm run build:mp-weixin
```

更多约定参见：

- [开发环境](docs/development.md)
- [部署与备份说明](docs/deployment.md)
- [API 契约](docs/api.md)
- [状态枚举](docs/enums.md)
- [测试计划](docs/test-plan.md)
- [M8 测试报告](docs/m8-test-report.md)
- [答辩演示脚本](docs/demo-script.md)
- [V2 UI 设计说明](docs/v2-ui-design.md)
- [完整开发计划](docs/development-plan.md)
