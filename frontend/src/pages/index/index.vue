<template>
  <view class="page">
    <view class="hero">
      <view class="hero-copy">
        <text class="eyebrow">SCHOOL MARKET V2</text>
        <text class="title">校淘空间</text>
        <text class="subtitle">把闲置变成下一位同学的小确幸。浏览、发布、沟通、交易，都轻轻松松。</text>
      </view>
      <view class="hero-orbit">
        <view class="orbit-card card-a">
          <text class="orbit-label">今日好物</text>
          <text class="orbit-value">{{ products.length }}</text>
        </view>
        <view class="orbit-card card-b">
          <text class="orbit-label">公告</text>
          <text class="orbit-value">{{ announcements.length }}</text>
        </view>
      </view>
    </view>

    <view class="status-card">
      <view>
        <text class="status-label">系统状态</text>
        <text class="status-value">{{ overallLabel }}</text>
      </view>
      <view :class="['status-dot', `dot-${overallState}`]"></view>
    </view>

    <view class="primary-actions">
      <button class="quick-button primary" @click="goProducts">去逛校园好物</button>
      <button class="quick-button publish" @click="goPublish">发布我的闲置</button>
    </view>

    <view class="quick-grid">
      <button class="quick-button" @click="goMyProducts">我的商品</button>
      <button class="quick-button" @click="goMessages">消息中心</button>
      <button class="quick-button" @click="goBuyTrades">我的购买</button>
      <button class="quick-button" @click="goSellTrades">收到请求</button>
      <button class="quick-button" @click="goProfile">
        {{ currentUser ? '个人中心' : '登录 / 注册' }}
      </button>
    </view>

    <view v-if="isAdmin" class="admin-panel">
      <text class="panel-title">后台控制台</text>
      <view class="admin-grid">
        <button class="admin-button" @click="goAdminUsers">用户</button>
        <button class="admin-button" @click="goAdminProducts">商品</button>
        <button class="admin-button" @click="goAdminAnnouncements">公告</button>
        <button class="admin-button" @click="goAdminLogs">日志</button>
        <button class="admin-button" @click="goAdminStats">统计</button>
      </view>
    </view>

    <view class="section-heading">
      <view>
        <text class="section-title">校园公告</text>
        <text class="section-subtitle">重要提醒会在这里轻轻冒泡</text>
      </view>
      <text class="section-link" @click="loadAnnouncements">刷新</text>
    </view>

    <view v-if="loadingAnnouncements" class="empty compact">正在加载公告</view>
    <view v-else-if="announcements.length === 0" class="empty compact">暂无公告</view>
    <view v-for="item in announcements" :key="item.id" class="announcement-card">
      <text class="announcement-title">{{ item.title }}</text>
      <text class="announcement-content">{{ item.content || '暂无内容' }}</text>
    </view>

    <view class="section-heading">
      <view>
        <text class="section-title">刚刚上新</text>
        <text class="section-subtitle">同学们正在转让的宝藏</text>
      </view>
      <text class="section-link" @click="goProducts">查看全部</text>
    </view>

    <view v-if="loadingProducts" class="empty">正在加载商品</view>
    <view v-else-if="products.length === 0" class="empty">暂无商品</view>

    <view v-for="product in products" :key="product.id" class="product-card home-product" @click="goDetail(product.id)">
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
.hero {
  min-height: 360rpx;
  display: flex;
  justify-content: space-between;
  gap: 24rpx;
}

.hero-copy {
  position: relative;
  z-index: 1;
  flex: 1;
}

.hero .title {
  margin-top: 12rpx;
  font-size: 68rpx !important;
}

.hero .subtitle {
  max-width: 560rpx;
}

.hero-orbit {
  position: relative;
  z-index: 1;
  width: 224rpx;
  min-height: 220rpx;
}

.orbit-card {
  position: absolute;
  display: flex;
  flex-direction: column;
  justify-content: center;
  width: 156rpx;
  height: 156rpx;
  padding: 20rpx;
  border: 3rpx solid rgba(255, 255, 255, 0.82);
  border-radius: 44rpx;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(224, 255, 245, 0.88));
  box-shadow: 0 22rpx 40rpx rgba(53, 125, 109, 0.16), inset 0 -10rpx 18rpx rgba(95, 205, 176, 0.13);
}

.card-a {
  right: 34rpx;
  top: 8rpx;
  animation: home-orbit-a 5.8s ease-in-out infinite alternate;
}

.card-b {
  right: 0;
  bottom: 8rpx;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.94), rgba(255, 238, 214, 0.9));
  animation: home-orbit-b 6.2s ease-in-out infinite alternate;
}

.orbit-label {
  color: #5f766f;
  font-size: 22rpx;
  font-weight: 800;
}

.orbit-value {
  margin-top: 6rpx;
  color: #183b34;
  font-size: 48rpx;
  font-weight: 950;
}

.status-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.status-value {
  display: block;
  margin-top: 8rpx;
  font-size: 36rpx;
  font-weight: 950;
}

.status-dot {
  width: 28rpx;
  height: 28rpx;
  border-radius: 50%;
  background: #a9b3af;
  box-shadow: 0 0 0 10rpx rgba(169, 179, 175, 0.14);
}

.dot-success {
  background: #30c990;
  box-shadow: 0 0 0 10rpx rgba(48, 201, 144, 0.16);
}

.dot-warning {
  background: #f2ac4f;
  box-shadow: 0 0 0 10rpx rgba(242, 172, 79, 0.16);
}

.dot-error {
  background: #eb5d72;
  box-shadow: 0 0 0 10rpx rgba(235, 93, 114, 0.16);
}

.dot-checking {
  background: #5caef5;
  box-shadow: 0 0 0 10rpx rgba(92, 174, 245, 0.16);
}

.primary-actions {
  display: grid;
  grid-template-columns: 1.25fr 1fr;
  gap: 18rpx;
  margin: 24rpx 0 18rpx;
}

.quick-button.publish {
  background: linear-gradient(135deg, #fff3dc 0%, #ffd6aa 100%) !important;
  color: #8a471b !important;
}

.admin-panel {
  margin-top: 22rpx;
}

.section-subtitle {
  display: block;
  margin-top: 8rpx;
  color: #6a8078;
  font-size: 23rpx;
  line-height: 1.4;
}

.home-product {
  display: flex;
  align-items: center;
}

.product-image,
.image-placeholder {
  width: 136rpx;
  height: 136rpx;
  margin-right: 20rpx;
  flex-shrink: 0;
}

.product-main {
  display: flex;
  flex: 1;
  min-width: 0;
  flex-direction: column;
}

.price {
  margin-left: 14rpx;
  font-size: 32rpx;
}

@keyframes home-orbit-a {
  from {
    transform: translateY(0) rotate(-2deg);
  }
  to {
    transform: translateY(18rpx) rotate(2deg);
  }
}

@keyframes home-orbit-b {
  from {
    transform: translateY(12rpx) rotate(2deg);
  }
  to {
    transform: translateY(-8rpx) rotate(-2deg);
  }
}

@media screen and (max-width: 420px) {
  .hero {
    flex-direction: column;
  }

  .hero-orbit {
    width: 100%;
    min-height: 180rpx;
  }

  .card-a {
    left: 0;
    right: auto;
  }

  .card-b {
    right: 26rpx;
  }

  .primary-actions {
    grid-template-columns: 1fr;
  }
}
</style>
