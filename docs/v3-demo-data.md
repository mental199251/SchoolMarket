# V3 演示数据说明

V3 增加一套可重复执行的真实演示数据脚本，用于把用户、商家、商品、图片、交易、消息、公告、操作日志和 AI 调用日志写入 MongoDB。商品图片由脚本生成 PNG 文件，路径写入商品 `images` 字段，H5 和微信小程序通过后端 `/uploads/images/...` 地址加载。

演示数据本体已作为 JSON fixture 提交到仓库：`server/fixtures/v3_demo_data.json`。`server/scripts/seed_v3_demo.py` 会优先读取这份 fixture，再写入当前配置的 MongoDB。

## 初始化命令

先确认 MongoDB 已启动，并且 `.env` 中的 `MONGO_URI`、`MONGO_DB_NAME` 指向要写入的数据库。

```bash
cd server
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/seed_v3_demo.py
```

脚本可重复执行：用户和商品会按账号、卖家和标题更新；V3 交易、消息、公告、日志会按 `seed_tag=v3_demo` 清理后重新写入。生成的图片位于 `server/uploads/images/`，该目录不提交到 Git。

## 账号

| 账号 | 密码 | 角色 | 状态 | 说明 |
| --- | --- | --- | --- | --- |
| `user_a` | `Password123` | 普通用户 | 启用 | 普通买家演示 |
| `user_b` | `Password123` | 普通用户 | 启用 | 普通买家演示 |
| `seller_books` | `Password123` | 普通用户 | 启用 | 教材资料商家 |
| `seller_digital` | `Password123` | 普通用户 | 启用 | 数码商品商家 |
| `seller_life` | `Password123` | 普通用户 | 启用 | 生活用品商家 |
| `seller_sports` | `Password123` | 普通用户 | 启用 | 运动器材商家 |
| `buyer_lina` | `Password123` | 普通用户 | 启用 | 交易流程买家 |
| `buyer_tao` | `Password123` | 普通用户 | 启用 | 交易流程买家 |
| `admin` | `Admin12345` | 管理员 | 启用 | 后台治理账号 |
| `blocked_user` | `Password123` | 普通用户 | 禁用 | 管理端状态演示 |

## 商品覆盖

每个分类写入 3 个商品，共 12 个商品：

| 分类 | 商品 |
| --- | --- |
| 教材资料 | 计算机网络第 8 版教材、考研英语真题套装、线性代数辅导讲义 |
| 电子产品 | iPad Air 5 64G、Sony WH-1000XM4 耳机、罗技 K380 蓝牙键盘 |
| 生活用品 | 宿舍床上小桌板、小熊电煮锅 1.2L、桌面收纳抽屉三层 |
| 运动器材 | Yonex 入门羽毛球拍、加厚防滑瑜伽垫、山地车骑行头盔 |

V3 还会补充 4 条不同状态的交易，覆盖 `pending`、`confirmed`、`completed`、`cancelled`，并生成对应站内消息。
