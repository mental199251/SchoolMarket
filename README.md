# 校淘空间

“校淘空间”是面向校园师生的二手交易平台。前端使用 uni-app、Vue 3 和 Vite，后端使用 Flask，数据存储使用 MongoDB。

## 当前进度

- M0：工程基线与协作规范
- M1：前后端健康检查链路

注册、商品、交易、管理和 AI 功能将在后续里程碑实现。

## 环境要求

- Node.js 20
- Python 3.11 或 3.12
- MongoDB 7.x
- 微信开发者工具
- Ollama（M7 才需要）

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
- [API 契约](docs/api.md)
- [状态枚举](docs/enums.md)
- [测试计划](docs/test-plan.md)
- [完整开发计划](docs/development-plan.md)

