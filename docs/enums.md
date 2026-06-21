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

