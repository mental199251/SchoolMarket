# 部署与备份说明

本文档用于 M8 交付阶段的本地演示、局域网联调和数据备份。

## 1. 环境要求

- Node.js 20
- Python 3.11 或 3.12
- MongoDB 7.x
- MongoDB Database Tools（用于 `mongodump` / `mongorestore`）
- Ollama（需要 AI 发布助手时安装）

## 2. 环境变量

从项目根目录复制示例配置：

```bash
cp .env.example .env
```

关键配置：

```env
MONGO_URI=mongodb://127.0.0.1:27017/?directConnection=true
MONGO_DB_NAME=school_market

OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=gpt-oss:120b-cloud
```

H5 和微信小程序前端请求地址在 `frontend/.env.development` 中配置：

```env
VITE_API_BASE_URL=http://127.0.0.1:5001
```

真机或微信开发者工具访问局域网后端时，将 `127.0.0.1` 改为运行 Flask 的电脑局域网 IP。

## 3. 初始化与启动

安装依赖：

```bash
cd frontend
npm ci

cd ../server
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

启动 MongoDB 后初始化演示数据：

```bash
cd server
source .venv/bin/activate
python scripts/seed_data.py
```

V3 答辩或完整演示建议使用真实演示数据脚本，它会读取仓库内的 `server/fixtures/v3_demo_data.json`，再写入用户、商家、12 个带图片商品、交易、消息、公告、操作日志和 AI 调用日志：

```bash
python scripts/seed_v3_demo.py
```

生成的商品图片保存到 `server/uploads/images/`，数据库中保存 `/uploads/images/...` 访问路径。

启动后端：

```bash
python run.py
```

检查：

```bash
curl http://127.0.0.1:5001/health
curl http://127.0.0.1:5001/ready
```

启动 H5：

```bash
cd frontend
npm run dev:h5
```

微信小程序构建：

```bash
cd frontend
npm run dev:mp-weixin
```

然后在微信开发者工具中导入 `frontend/dist/dev/mp-weixin`。

## 4. AI 启用

后端通过本机 Ollama HTTP API 调用模型。使用 Ollama Cloud 模型时，项目不保存 API key，登录态由 Ollama 管理：

```bash
ollama signin
ollama serve
```

登录应用后检查：

```bash
GET /api/v1/ai/status
```

若 `service_available=true`、`cloud_model=true`、`ready=true`，说明后端可通过 Ollama 使用 cloud 模型。

## 5. 数据备份与恢复

备份前确认 MongoDB 正在运行，并且 `.env` 中的 `MONGO_URI` 和 `MONGO_DB_NAME` 指向目标库。

```bash
cd server
source .venv/bin/activate
python scripts/backup_database.py
```

默认输出到 `server/backups/`，该目录不会提交到 Git。

恢复示例：

```bash
mongorestore --uri "$MONGO_URI" --gzip --drop server/backups/school_market-YYYYMMDDTHHMMSSZ/school_market
```

恢复到生产或答辩环境前，先确认目标库是否允许 `--drop` 清空已有集合。
