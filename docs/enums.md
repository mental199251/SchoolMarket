# 状态枚举

状态值由后端服务层维护。前端只负责展示和触发动作，不得直接指定任意目标状态。

## 用户

- 角色：`user`、`admin`
- 状态：`active`、`disabled`

买家和卖家不是账号角色。同一普通用户可以购买他人商品，也可以发布自己的商品。

## 商品

- `draft`：草稿
- `pending_review`：待审核
- `available`：可交易
- `off_shelf`：已下架
- `rejected`：审核拒绝
- `sold`：已成交

第一版设置 `PRODUCT_REVIEW_ENABLED=false`，正式提交后直接进入 `available`。

成色：

- `new`：全新
- `like_new`：几乎全新
- `good`：轻微使用
- `fair`：明显使用

第一版分类：

- `books`：教材资料
- `electronics`：电子产品
- `daily`：生活用品
- `sports`：运动器材

## 交易请求

- `pending`：等待卖家处理
- `confirmed`：卖家已确认
- `cancelled`：交易已取消
- `completed`：线下交易已完成

主要流转：

```text
pending -> confirmed -> completed
pending -> cancelled
```

交易完成时必须同步将商品更新为 `sold`。

## 消息

- 类型：`trade`
- 已读状态：`is_read=true`、`is_read=false`

当前交易消息标题：

- `收到新的购买请求`
- `购买请求已确认`
- `交易请求已取消`
- `交易已完成`

## 公告

- `published`：已发布，公开公告列表可见
- `hidden`：已隐藏，仅管理员后台可见

## 操作日志

目标类型：

- `user`
- `product`
- `announcement`

动作：

- `user_status_update`：管理员禁用或恢复用户
- `product_status_update`：管理员更新商品状态
- `product_delete`：管理员删除商品
- `announcement_create`：管理员创建公告
- `announcement_update`：管理员更新公告
- `announcement_delete`：管理员隐藏公告
