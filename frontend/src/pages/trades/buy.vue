<template>
  <view class="page">
    <view class="header">
      <text class="eyebrow">BUYER</text>
      <text class="title">我的购买</text>
      <button class="nav-button" @click="goProducts">继续逛逛</button>
    </view>

    <picker :range="statusNames" :value="statusIndex" @change="onStatusChange">
      <view class="select">{{ selectedStatusName }}</view>
    </picker>

    <view v-if="loading && trades.length === 0" class="empty">正在加载购买请求</view>
    <view v-else-if="trades.length === 0" class="empty">暂无购买请求</view>

    <view v-for="trade in trades" :key="trade.id" class="trade-card">
      <view class="trade-main" @click="goProduct(trade.product_id)">
        <image
          v-if="trade.product?.images && trade.product.images.length"
          class="trade-image"
          mode="aspectFill"
          :src="assetUrl(trade.product.images[0])"
        />
        <view v-else class="image-placeholder">
          <text>校</text>
        </view>
        <view class="trade-copy">
          <text class="trade-title">{{ trade.product?.title || '商品已不可用' }}</text>
          <text class="trade-meta">卖家：{{ trade.seller?.nickname || trade.seller?.username || '-' }}</text>
          <view class="trade-bottom">
            <text :class="['status', `status-${trade.status}`]">{{ tradeStatusLabel(trade.status) }}</text>
            <text class="price">{{ formatPrice(trade.product?.price_cents) }}</text>
          </view>
        </view>
      </view>

      <view class="actions">
        <view v-if="trade.status === 'pending'" class="action-button" @click="runAction(trade, 'cancel')">
          取消请求
        </view>
        <view v-if="trade.status === 'confirmed'" class="action-button primary" @click="runAction(trade, 'complete')">
          标记完成
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { cancelTrade, completeTrade, getMyBuyTrades } from '../../api'
import { getAuthToken } from '../../utils/auth'
import {
  assetUrl,
  formatPrice,
  tradeStatusLabel,
  tradeStatusOptions,
} from '../../utils/product'

export default {
  data() {
    return {
      loading: false,
      trades: [],
      filters: {
        page: 1,
        page_size: 50,
        status: '',
      },
    }
  },
  computed: {
    statusNames() {
      return tradeStatusOptions.map((item) => item.label)
    },
    statusIndex() {
      return Math.max(0, tradeStatusOptions.findIndex((item) => item.value === this.filters.status))
    },
    selectedStatusName() {
      return tradeStatusOptions[this.statusIndex]?.label || '全部状态'
    },
  },
  onLoad() {
    if (!getAuthToken()) {
      uni.redirectTo({ url: '/pages/auth/login' })
      return
    }
    this.fetchTrades()
  },
  onPullDownRefresh() {
    this.fetchTrades().finally(() => uni.stopPullDownRefresh())
  },
  methods: {
    assetUrl,
    formatPrice,
    tradeStatusLabel,
    async fetchTrades() {
      this.loading = true
      try {
        const data = await getMyBuyTrades(this.filters)
        this.trades = data.items
      } finally {
        this.loading = false
      }
    },
    onStatusChange(event) {
      const index = Number(event.detail.value)
      this.filters.status = tradeStatusOptions[index]?.value || ''
      this.fetchTrades()
    },
    goProducts() {
      uni.navigateTo({ url: '/pages/products/list' })
    },
    goProduct(id) {
      uni.navigateTo({ url: `/pages/products/detail?id=${id}` })
    },
    runAction(trade, action) {
      const config = {
        cancel: {
          title: '确认取消请求？',
          request: () => cancelTrade(trade.id),
          toast: '已取消',
        },
        complete: {
          title: '确认线下交易已完成？',
          request: () => completeTrade(trade.id),
          toast: '已完成',
        },
      }[action]

      uni.showModal({
        title: config.title,
        success: async (result) => {
          if (!result.confirm) return
          await config.request()
          uni.showToast({ title: config.toast, icon: 'success' })
          this.fetchTrades()
        },
      })
    },
  },
}
</script>

<style>
page {
  background: #f2f5f3;
}

.page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 42rpx 28rpx 64rpx;
  color: #17221e;
}

.header {
  display: flex;
  flex-direction: column;
  margin-bottom: 24rpx;
}

.eyebrow {
  margin-bottom: 8rpx;
  color: #367c6c;
  font-size: 22rpx;
  font-weight: 700;
}

.title {
  font-size: 50rpx;
  font-weight: 700;
}

.nav-button {
  margin-top: 24rpx;
  border-radius: 18rpx;
  background: #173f36;
  color: #fff;
  font-size: 28rpx;
}

.select {
  height: 74rpx;
  box-sizing: border-box;
  margin-bottom: 22rpx;
  padding: 0 20rpx;
  border: 1rpx solid #dbe3df;
  border-radius: 16rpx;
  background: #fff;
  color: #43504b;
  font-size: 26rpx;
  line-height: 74rpx;
}

.empty {
  padding: 100rpx 0;
  color: #75817c;
  font-size: 28rpx;
  text-align: center;
}

.trade-card {
  margin-bottom: 18rpx;
  padding: 20rpx;
  border: 1rpx solid #e3e9e6;
  border-radius: 22rpx;
  background: #fff;
}

.trade-main {
  display: flex;
  align-items: center;
}

.trade-image,
.image-placeholder {
  width: 132rpx;
  height: 132rpx;
  margin-right: 18rpx;
  border-radius: 18rpx;
}

.image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ddf5eb;
  color: #25715f;
  font-size: 42rpx;
  font-weight: 700;
}

.trade-copy {
  display: flex;
  flex: 1;
  min-width: 0;
  flex-direction: column;
}

.trade-title {
  font-size: 30rpx;
  font-weight: 700;
  line-height: 1.35;
}

.trade-meta {
  margin-top: 8rpx;
  color: #75817c;
  font-size: 24rpx;
}

.trade-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
  margin-top: 12rpx;
}

.status {
  padding: 8rpx 14rpx;
  border-radius: 999rpx;
  background: #fff3d9;
  color: #94651e;
  font-size: 22rpx;
}

.status-confirmed {
  background: #e4f0fd;
  color: #356c9e;
}

.status-completed {
  background: #ddf5eb;
  color: #25715f;
}

.status-cancelled {
  background: #f0f2f1;
  color: #69746f;
}

.price {
  color: #b6533d;
  font-size: 30rpx;
  font-weight: 700;
}

.actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14rpx;
  margin-top: 18rpx;
}

.action-button {
  height: 64rpx;
  border-radius: 16rpx;
  background: #eef4f1;
  color: #24594e;
  font-size: 25rpx;
  font-weight: 600;
  line-height: 64rpx;
  text-align: center;
}

.action-button.primary {
  background: #173f36;
  color: #fff;
}
</style>
