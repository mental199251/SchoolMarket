<template>
  <view class="page">
    <view class="hero">
      <text class="eyebrow">SCHOOL MARKET</text>
      <text class="title">校淘空间</text>
      <text class="subtitle">校园二手好物流转</text>
    </view>

    <view class="status-card">
      <view>
        <text class="status-label">系统状态</text>
        <text class="status-value">{{ overallLabel }}</text>
      </view>
      <view :class="['status-dot', `dot-${overallState}`]"></view>
    </view>

    <view class="quick-grid">
      <button class="quick-button primary" @click="goProducts">浏览商品</button>
      <button class="quick-button" @click="goPublish">发布商品</button>
      <button class="quick-button" @click="goMyProducts">我的商品</button>
      <button class="quick-button" @click="goMessages">消息中心</button>
      <button class="quick-button" @click="goBuyTrades">我的购买</button>
      <button class="quick-button" @click="goSellTrades">收到请求</button>
      <button class="quick-button" @click="goProfile">
        {{ currentUser ? '个人中心' : '登录 / 注册' }}
      </button>
    </view>

    <view v-if="isAdmin" class="admin-panel">
      <text class="panel-title">后台管理</text>
      <view class="admin-grid">
        <button class="admin-button" @click="goAdminUsers">用户</button>
        <button class="admin-button" @click="goAdminProducts">商品</button>
        <button class="admin-button" @click="goAdminAnnouncements">公告</button>
        <button class="admin-button" @click="goAdminLogs">日志</button>
        <button class="admin-button" @click="goAdminStats">统计</button>
      </view>
    </view>

    <view class="section-heading">
      <text class="section-title">公告</text>
      <text class="section-link" @click="loadAnnouncements">刷新</text>
    </view>

    <view v-if="loadingAnnouncements" class="empty compact">正在加载公告</view>
    <view v-else-if="announcements.length === 0" class="empty compact">暂无公告</view>
    <view v-for="item in announcements" :key="item.id" class="announcement-card">
      <text class="announcement-title">{{ item.title }}</text>
      <text class="announcement-content">{{ item.content || '暂无内容' }}</text>
    </view>

    <view class="section-heading">
      <text class="section-title">最新商品</text>
      <text class="section-link" @click="goProducts">查看全部</text>
    </view>

    <view v-if="loadingProducts" class="empty">正在加载商品</view>
    <view v-else-if="products.length === 0" class="empty">暂无商品</view>

    <view v-for="product in products" :key="product.id" class="product-card" @click="goDetail(product.id)">
      <image
        v-if="product.images && product.images.length"
        class="product-image"
        mode="aspectFill"
        :src="assetUrl(product.images[0])"
      />
      <view v-else class="image-placeholder">
        <text>校</text>
      </view>
      <view class="product-main">
        <text class="product-title">{{ product.title }}</text>
        <text class="product-meta">{{ product.category_name }} · {{ conditionLabel(product.condition) }}</text>
      </view>
      <text class="price">{{ formatPrice(product.price_cents) }}</text>
    </view>
  </view>
</template>

<script>
import { getAnnouncements, getHealth, getProducts, getReadiness } from '../../api'
import { getStoredUser, hasValidAuth } from '../../utils/auth'
import { assetUrl, conditionLabel, formatPrice } from '../../utils/product'

const pendingStatus = {
  state: 'pending',
  label: '等待检查',
}

export default {
  data() {
    return {
      checking: false,
      loadingProducts: false,
      loadingAnnouncements: false,
      currentUser: null,
      flaskStatus: { ...pendingStatus },
      mongoStatus: { ...pendingStatus },
      announcements: [],
      products: [],
    }
  },
  computed: {
    isAdmin() {
      return this.currentUser?.role === 'admin'
    },
    overallState() {
      if (this.checking) return 'checking'
      if (this.flaskStatus.state === 'error') return 'error'
      if (this.mongoStatus.state === 'error') return 'warning'
      if (
        this.flaskStatus.state === 'success' &&
        this.mongoStatus.state === 'success'
      ) {
        return 'success'
      }
      return 'pending'
    },
    overallLabel() {
      const labels = {
        checking: '正在检查',
        error: 'API 不可用',
        warning: '数据库未就绪',
        success: '系统已就绪',
        pending: '等待检查',
      }
      return labels[this.overallState]
    },
  },
  onLoad() {
    this.checkServices()
    this.loadProducts()
    this.loadAnnouncements()
  },
  onShow() {
    this.currentUser = hasValidAuth() ? getStoredUser() : null
  },
  onPullDownRefresh() {
    Promise.all([this.checkServices(), this.loadProducts(), this.loadAnnouncements()]).finally(() => {
      uni.stopPullDownRefresh()
    })
  },
  methods: {
    assetUrl,
    conditionLabel,
    formatPrice,
    async checkServices() {
      this.checking = true
      const health = getHealth()
        .then(() => {
          this.flaskStatus = { state: 'success', label: '正常' }
        })
        .catch(() => {
          this.flaskStatus = { state: 'error', label: '不可用' }
        })
      const ready = getReadiness()
        .then(() => {
          this.mongoStatus = { state: 'success', label: '已就绪' }
        })
        .catch(() => {
          this.mongoStatus = { state: 'error', label: '未就绪' }
        })

      await Promise.all([health, ready])
      this.checking = false
    },
    async loadProducts() {
      this.loadingProducts = true
      try {
        const data = await getProducts({ page: 1, page_size: 4, sort: 'newest' })
        this.products = data.items
      } catch (_error) {
        this.products = []
      } finally {
        this.loadingProducts = false
      }
    },
    async loadAnnouncements() {
      this.loadingAnnouncements = true
      try {
        const data = await getAnnouncements({ page: 1, page_size: 3 })
        this.announcements = data.items
      } catch (_error) {
        this.announcements = []
      } finally {
        this.loadingAnnouncements = false
      }
    },
    goProducts() {
      uni.navigateTo({ url: '/pages/products/list' })
    },
    goPublish() {
      uni.navigateTo({ url: '/pages/products/form' })
    },
    goMyProducts() {
      uni.navigateTo({ url: '/pages/products/my' })
    },
    goMessages() {
      uni.navigateTo({ url: '/pages/messages/messages' })
    },
    goBuyTrades() {
      uni.navigateTo({ url: '/pages/trades/buy' })
    },
    goSellTrades() {
      uni.navigateTo({ url: '/pages/trades/sell' })
    },
    goProfile() {
      uni.navigateTo({
        url: this.currentUser ? '/pages/profile/profile' : '/pages/auth/login',
      })
    },
    goDetail(id) {
      uni.navigateTo({ url: `/pages/products/detail?id=${id}` })
    },
    goAdminUsers() {
      uni.navigateTo({ url: '/pages/admin/users' })
    },
    goAdminProducts() {
      uni.navigateTo({ url: '/pages/admin/products' })
    },
    goAdminAnnouncements() {
      uni.navigateTo({ url: '/pages/admin/announcements' })
    },
    goAdminLogs() {
      uni.navigateTo({ url: '/pages/admin/logs' })
    },
    goAdminStats() {
      uni.navigateTo({ url: '/pages/admin/stats' })
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
  padding: 48rpx 28rpx 64rpx;
  color: #17221e;
}

.hero {
  display: flex;
  flex-direction: column;
  margin-bottom: 28rpx;
}

.eyebrow {
  margin-bottom: 10rpx;
  color: #367c6c;
  font-size: 22rpx;
  font-weight: 700;
}

.title {
  font-size: 58rpx;
  font-weight: 700;
  line-height: 1.25;
}

.subtitle {
  margin-top: 10rpx;
  color: #66736e;
  font-size: 28rpx;
}

.status-card,
.section-heading,
.product-card {
  display: flex;
  align-items: center;
}

.status-card,
.product-card,
.announcement-card,
.admin-panel {
  border: 1rpx solid #e3e9e6;
  border-radius: 22rpx;
  background: #fff;
}

.status-card {
  justify-content: space-between;
  padding: 26rpx;
}

.status-label {
  display: block;
  color: #75817c;
  font-size: 24rpx;
}

.status-value {
  display: block;
  margin-top: 6rpx;
  font-size: 34rpx;
  font-weight: 700;
}

.status-dot {
  width: 24rpx;
  height: 24rpx;
  border-radius: 50%;
  background: #a9b3af;
}

.dot-success {
  background: #63d6a5;
}

.dot-warning {
  background: #f4bd63;
}

.dot-error {
  background: #ef786f;
}

.dot-checking {
  background: #77b9ff;
}

.quick-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16rpx;
  margin-top: 22rpx;
}

.quick-button {
  border-radius: 18rpx;
  background: #fff;
  color: #24594e;
  font-size: 28rpx;
}

.quick-button.primary {
  background: #173f36;
  color: #fff;
}

.admin-panel {
  margin-top: 22rpx;
  padding: 22rpx;
}

.panel-title {
  display: block;
  margin-bottom: 16rpx;
  color: #17221e;
  font-size: 28rpx;
  font-weight: 700;
}

.admin-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12rpx;
}

.admin-button {
  min-width: 0;
  border-radius: 16rpx;
  background: #eef4f1;
  color: #24594e;
  font-size: 25rpx;
}

.section-heading {
  justify-content: space-between;
  margin: 42rpx 4rpx 18rpx;
}

.section-title {
  font-size: 31rpx;
  font-weight: 700;
}

.section-link {
  color: #367c6c;
  font-size: 25rpx;
}

.empty {
  padding: 80rpx 0;
  color: #75817c;
  font-size: 28rpx;
  text-align: center;
}

.empty.compact {
  padding: 32rpx 0;
}

.announcement-card {
  margin-bottom: 16rpx;
  padding: 22rpx;
}

.announcement-title {
  display: block;
  font-size: 29rpx;
  font-weight: 700;
  line-height: 1.35;
}

.announcement-content {
  display: block;
  margin-top: 10rpx;
  color: #66736e;
  font-size: 25rpx;
  line-height: 1.5;
}

.product-card {
  margin-bottom: 18rpx;
  padding: 20rpx;
}

.product-image,
.image-placeholder {
  width: 128rpx;
  height: 128rpx;
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

.product-main {
  display: flex;
  flex: 1;
  min-width: 0;
  flex-direction: column;
}

.product-title {
  font-size: 30rpx;
  font-weight: 700;
  line-height: 1.35;
}

.product-meta {
  margin-top: 8rpx;
  color: #75817c;
  font-size: 24rpx;
}

.price {
  margin-left: 12rpx;
  color: #b6533d;
  font-size: 30rpx;
  font-weight: 700;
}
</style>
