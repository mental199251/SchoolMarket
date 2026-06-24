<template>
  <view class="page market-home">
    <view class="market-top">
      <view class="brand-row">
        <view class="brand-copy">
          <text class="brand-title">校淘空间</text>
          <text class="brand-subtitle">校园二手交易平台</text>
        </view>
      </view>

      <view class="search-row">
        <view class="search-box" @click="goProducts">
          <text class="search-symbol">搜</text>
          <text class="search-placeholder">搜教材 / 耳机 / 自行车</text>
        </view>
      </view>
    </view>

    <view class="shortcut-grid">
      <view
        v-for="item in shortcuts"
        :key="item.label"
        class="shortcut-item"
        @click="handleShortcut(item)"
      >
        <view :class="['shortcut-icon', item.tone]">
          <text>{{ item.icon }}</text>
        </view>
        <text class="shortcut-label">{{ item.label }}</text>
      </view>
    </view>

    <view v-if="isAdmin" class="admin-strip">
      <text class="admin-title">管理后台</text>
      <view class="admin-actions">
        <text @click="goAdminUsers">用户</text>
        <text @click="goAdminProducts">商品</text>
        <text @click="goAdminAnnouncements">公告</text>
        <text @click="goAdminLogs">日志</text>
        <text @click="goAdminStats">统计</text>
      </view>
    </view>

    <view class="channel-row">
      <view
        v-for="tab in channelTabs"
        :key="tab.label"
        :class="['channel-tab', { active: activeCategory === tab.category }]"
        @click="selectChannel(tab)"
      >
        <text>{{ tab.label }}</text>
      </view>
      <view class="channel-more" @click="goProducts">更多</view>
    </view>

    <view v-if="loadingProducts && products.length === 0" class="empty">正在加载商品</view>
    <view v-else-if="products.length === 0" class="empty">暂无商品</view>

    <view class="goods-grid">
      <view
        v-for="product in products"
        :key="product.id"
        class="goods-card product-card"
        @click="goDetail(product.id)"
      >
        <view class="goods-cover-wrap">
          <image
            v-if="product.images && product.images.length"
            class="goods-cover"
            mode="aspectFill"
            :src="assetUrl(product.images[0])"
          />
          <view v-else class="goods-placeholder">
            <text>校</text>
          </view>
          <text class="goods-badge">校园自提</text>
        </view>
        <view class="goods-body">
          <text class="goods-title">{{ product.title }}</text>
          <view class="goods-meta-row">
            <text class="goods-tag">{{ product.category_name }}</text>
            <text class="goods-condition">{{ conditionLabel(product.condition) }}</text>
          </view>
          <view class="goods-bottom">
            <text class="goods-price">{{ formatPrice(product.price_cents) }}</text>
            <text class="goods-campus">{{ product.owner?.campus || '校内' }}</text>
          </view>
        </view>
      </view>
    </view>

    <view class="bottom-nav">
      <view class="bottom-item active" @click="loadProducts">
        <text class="bottom-icon">首</text>
        <text>首页</text>
      </view>
      <view class="bottom-item" @click="goProducts">
        <text class="bottom-icon">场</text>
        <text>广场</text>
      </view>
      <view class="sell-center" @click="goPublish">
        <view class="sell-bubble">发布闲置</view>
        <view class="sell-button">
          <text>+</text>
        </view>
      </view>
      <view class="bottom-item" @click="goMessages">
        <text class="bottom-icon">信</text>
        <text>消息</text>
      </view>
      <view class="bottom-item" @click="goProfile">
        <text class="bottom-icon">我</text>
        <text>我的</text>
      </view>
    </view>
  </view>
</template>

<script>
import { getHealth, getProducts, getReadiness } from '../../api'
import { clearAuthStorage, getStoredUser, hasValidAuth } from '../../utils/auth'
import { assetUrl, conditionLabel, formatPrice } from '../../utils/product'

const pendingStatus = {
  state: 'pending',
  label: '等待检查',
}

export default {
  data() {
    return {
      activeCategory: '',
      checking: false,
      loadingProducts: false,
      currentUser: null,
      flaskStatus: { ...pendingStatus },
      mongoStatus: { ...pendingStatus },
      products: [],
      shortcuts: [
        { label: '免费送', icon: '0', tone: 'tone-red', type: 'free' },
        { label: '校淘公告', icon: '告', tone: 'tone-blue', type: 'announcements' },
        { label: '客服售后', icon: '客', tone: 'tone-green', type: 'service' },
        { label: '合作咨询', icon: '合', tone: 'tone-orange', type: 'cooperation' },
      ],
      channelTabs: [
        { label: '推荐', category: '' },
        { label: '教材', category: 'books' },
        { label: '数码', category: 'electronics' },
        { label: '生活', category: 'daily' },
        { label: '运动', category: 'sports' },
      ],
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
        checking: '检查中',
        error: '服务异常',
        warning: '数据库未就绪',
        success: '系统就绪',
        pending: '待检查',
      }
      return labels[this.overallState]
    },
  },
  onLoad() {
    if (!this.ensureLoggedIn()) return
    this.checkServices()
    this.loadProducts()
  },
  onShow() {
    this.ensureLoggedIn()
  },
  onPullDownRefresh() {
    Promise.all([this.checkServices(), this.loadProducts()]).finally(() => {
      uni.stopPullDownRefresh()
    })
  },
  methods: {
    assetUrl,
    conditionLabel,
    formatPrice,
    ensureLoggedIn() {
      if (hasValidAuth()) {
        this.currentUser = getStoredUser()
        return true
      }
      clearAuthStorage()
      this.currentUser = null
      uni.redirectTo({ url: '/pages/auth/login' })
      return false
    },
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
        const params = { page: 1, page_size: 10, sort: 'newest' }
        if (this.activeCategory) {
          params.category_key = this.activeCategory
        }
        const data = await getProducts(params)
        this.products = data.items
      } catch (_error) {
        this.products = []
      } finally {
        this.loadingProducts = false
      }
    },
    selectChannel(tab) {
      if (this.activeCategory === tab.category) return
      this.activeCategory = tab.category
      this.loadProducts()
    },
    handleShortcut(item) {
      uni.navigateTo({ url: `/pages/info/center?type=${item.type}` })
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
.market-home.page {
  max-width: 980px !important;
  padding: 26rpx 24rpx 190rpx !important;
  background: #f7f7f7 !important;
  color: #1f2623 !important;
  animation: none !important;
}

.market-top {
  padding: 18rpx 0 16rpx;
}

.brand-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
}

.brand-copy {
  display: flex;
  min-width: 0;
  flex: 1;
  flex-direction: column;
}

.brand-title {
  color: #ff5a1f;
  font-size: 46rpx;
  font-weight: 950;
  line-height: 1.08;
}

.brand-subtitle {
  margin-top: 8rpx;
  color: #797f7b;
  font-size: 23rpx;
  line-height: 1.3;
}

.search-row {
  display: flex;
  align-items: center;
  margin-top: 24rpx;
}

.search-box {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
  height: 86rpx;
  padding: 0 24rpx;
  border-radius: 18rpx;
  background: #fffaf0;
  box-shadow: inset 0 0 0 1rpx rgba(255, 120, 48, 0.1);
}

.search-symbol {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 42rpx;
  height: 42rpx;
  margin-right: 14rpx;
  border: 3rpx solid #b9b4aa;
  border-radius: 50%;
  color: #9f9b93;
  font-size: 18rpx;
  font-weight: 900;
}

.search-placeholder {
  color: #a5a099;
  font-size: 30rpx;
  line-height: 1;
}

.shortcut-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16rpx;
  margin: 22rpx 0 24rpx;
}

.shortcut-item {
  display: flex;
  align-items: center;
  min-width: 0;
  flex-direction: column;
}

.shortcut-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 86rpx;
  height: 76rpx;
  border-radius: 20rpx;
  color: #fff;
  font-size: 33rpx;
  font-weight: 950;
  box-shadow: 0 12rpx 18rpx rgba(31, 38, 35, 0.1);
}

.shortcut-label {
  margin-top: 10rpx;
  color: #262d29;
  font-size: 25rpx;
  font-weight: 800;
  line-height: 1.2;
}

.tone-red {
  background: linear-gradient(135deg, #ff5a1f, #ffb131);
}

.tone-blue {
  background: linear-gradient(135deg, #2773ff, #60b7ff);
}

.tone-purple {
  background: linear-gradient(135deg, #6c55d9, #a686ff);
}

.tone-green {
  background: linear-gradient(135deg, #24a86f, #55d898);
}

.tone-orange {
  background: linear-gradient(135deg, #ff8533, #ffcd42);
}

.admin-strip {
  margin-bottom: 24rpx;
  padding: 20rpx 22rpx;
  border-radius: 18rpx;
  background: #fff;
  box-shadow: 0 8rpx 18rpx rgba(31, 38, 35, 0.06);
}

.admin-title {
  display: block;
  color: #1d2924;
  font-size: 25rpx;
  font-weight: 950;
}

.admin-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 14rpx;
  margin-top: 14rpx;
}

.admin-actions text {
  padding: 8rpx 18rpx;
  border-radius: 999rpx;
  background: #fff2ea;
  color: #e85b21;
  font-size: 23rpx;
  font-weight: 800;
}

.channel-row {
  display: flex;
  align-items: center;
  gap: 28rpx;
  margin: 12rpx 0 22rpx;
  overflow-x: auto;
  white-space: nowrap;
}

.channel-tab {
  position: relative;
  flex-shrink: 0;
  padding-bottom: 12rpx;
  color: #767d79;
  font-size: 31rpx;
  font-weight: 850;
}

.channel-tab.active {
  color: #20352f;
  font-size: 36rpx;
  font-weight: 950;
}

.channel-tab.active::after {
  content: "";
  position: absolute;
  left: 8rpx;
  right: 8rpx;
  bottom: 0;
  height: 6rpx;
  border-radius: 999rpx;
  background: #ff6b2b;
}

.channel-more {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 66rpx;
  height: 54rpx;
  border-radius: 999rpx;
  background: #e7eee9;
  color: #4f6159;
  font-size: 22rpx;
  font-weight: 900;
}

.goods-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
}

.goods-card {
  width: calc(50% - 9rpx) !important;
  margin: 0 0 18rpx !important;
  padding: 0 !important;
  border: 0 !important;
  border-radius: 14rpx !important;
  background: #fff !important;
  box-shadow: 0 8rpx 20rpx rgba(31, 38, 35, 0.08) !important;
  overflow: hidden !important;
}

.goods-cover-wrap {
  position: relative;
  width: 100%;
  height: 340rpx;
  background: #f1f1f1;
}

.goods-cover,
.goods-placeholder {
  width: 100%;
  height: 100%;
}

.goods-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fff2ea, #f0f0f0);
  color: #ff6b2b;
  font-size: 58rpx;
  font-weight: 950;
}

.goods-badge {
  position: absolute;
  right: 14rpx;
  top: 14rpx;
  padding: 6rpx 12rpx;
  border-radius: 8rpx;
  background: #ff6b2b;
  color: #fff;
  font-size: 20rpx;
  font-weight: 900;
}

.goods-body {
  padding: 18rpx 18rpx 20rpx;
}

.goods-title {
  display: -webkit-box;
  min-height: 76rpx;
  overflow: hidden;
  color: #262b28;
  font-size: 29rpx;
  font-weight: 700;
  line-height: 1.32;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.goods-meta-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8rpx;
  margin-top: 12rpx;
}

.goods-tag,
.goods-condition {
  max-width: 100%;
  padding: 5rpx 10rpx;
  border-radius: 8rpx;
  background: #fff2ea;
  color: #e65b23;
  font-size: 20rpx;
  font-weight: 800;
}

.goods-condition {
  background: #f1f3f2;
  color: #767d79;
}

.goods-bottom {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 10rpx;
  margin-top: 12rpx;
}

.goods-price {
  color: #f02d3a;
  font-size: 39rpx;
  font-weight: 950;
  line-height: 1;
}

.goods-campus {
  min-width: 0;
  overflow: hidden;
  color: #6f7572;
  font-size: 22rpx;
  line-height: 1.2;
  text-align: right;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bottom-nav {
  position: fixed;
  left: 50%;
  bottom: 0;
  z-index: 20;
  display: grid;
  grid-template-columns: 1fr 1fr 132rpx 1fr 1fr;
  align-items: end;
  width: 100%;
  max-width: 980px;
  padding: 18rpx 22rpx calc(18rpx + env(safe-area-inset-bottom));
  border-radius: 28rpx 28rpx 0 0;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 -12rpx 28rpx rgba(31, 38, 35, 0.12);
  transform: translateX(-50%);
  box-sizing: border-box;
}

.bottom-item {
  display: flex;
  align-items: center;
  flex-direction: column;
  justify-content: center;
  color: #a2a5a3;
  font-size: 22rpx;
  font-weight: 800;
}

.bottom-item.active {
  color: #ff5a1f;
}

.bottom-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 42rpx;
  height: 42rpx;
  margin-bottom: 8rpx;
  border-radius: 14rpx;
  background: #eeeeee;
  color: inherit;
  font-size: 22rpx;
  font-weight: 950;
}

.bottom-item.active .bottom-icon {
  background: #fff0e8;
}

.sell-center {
  position: relative;
  display: flex;
  align-items: center;
  flex-direction: column;
  justify-content: flex-end;
  height: 128rpx;
}

.sell-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 118rpx;
  height: 118rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff4f28, #ff9b36);
  color: #fff;
  font-size: 70rpx;
  font-weight: 400;
  line-height: 1;
  box-shadow: 0 16rpx 26rpx rgba(255, 90, 31, 0.28);
}

.sell-bubble {
  position: absolute;
  top: -26rpx;
  left: 50%;
  padding: 12rpx 26rpx;
  border-radius: 999rpx;
  background: linear-gradient(135deg, #ff4f28, #ff8d34);
  color: #fff;
  font-size: 24rpx;
  font-weight: 950;
  white-space: nowrap;
  box-shadow: 0 10rpx 18rpx rgba(255, 90, 31, 0.24);
  transform: translateX(-50%);
}

.empty {
  margin: 50rpx 0;
  color: #8a908d;
  font-size: 26rpx;
  text-align: center;
}

@media screen and (max-width: 420px) {
  .brand-title {
    font-size: 42rpx;
  }

  .goods-cover-wrap {
    height: 310rpx;
  }
}
</style>
