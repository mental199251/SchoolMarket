<template>
  <view class="page">
    <view class="header">
      <text class="eyebrow">ADMIN</text>
      <text class="title">统计报表</text>
      <text class="subtitle">{{ rangeLabel }}</text>
    </view>

    <picker :range="rangeNames" :value="rangeIndex" @change="onRangeChange">
      <view class="select">{{ selectedRangeName }}</view>
    </picker>

    <view v-if="loading && !overview" class="empty">正在加载统计</view>

    <view v-if="overview" class="metric-grid">
      <view class="metric-card">
        <text class="metric-label">发布量</text>
        <text class="metric-value">{{ overview.totals.published_products }}</text>
        <text class="metric-sub">总商品 {{ overview.totals.products_total }}</text>
      </view>
      <view class="metric-card">
        <text class="metric-label">成交量</text>
        <text class="metric-value">{{ overview.totals.completed_trades }}</text>
        <text class="metric-sub">完成率 {{ overview.totals.completion_rate }}%</text>
      </view>
      <view class="metric-card">
        <text class="metric-label">交易请求</text>
        <text class="metric-value">{{ overview.totals.created_trades }}</text>
        <text class="metric-sub">总请求 {{ overview.totals.trades_total }}</text>
      </view>
      <view class="metric-card">
        <text class="metric-label">新增用户</text>
        <text class="metric-value">{{ overview.totals.new_users }}</text>
        <text class="metric-sub">总用户 {{ overview.totals.users_total }}</text>
      </view>
    </view>

    <view v-if="overview" class="status-panel">
      <view class="status-row">
        <text class="status-label">商品</text>
        <text class="status-value">
          可交易 {{ overview.status.products.available }} · 已成交 {{ overview.status.products.sold }} · 已下架 {{ overview.status.products.off_shelf }}
        </text>
      </view>
      <view class="status-row">
        <text class="status-label">交易</text>
        <text class="status-value">
          待处理 {{ overview.status.trades.pending }} · 已确认 {{ overview.status.trades.confirmed }} · 已取消 {{ overview.status.trades.cancelled }}
        </text>
      </view>
    </view>

    <view class="section-heading">
      <text class="section-title">热门分类</text>
      <text class="section-link" @click="loadStats">刷新</text>
    </view>

    <view v-if="categories.length === 0 && !loading" class="empty compact">暂无分类数据</view>
    <view v-for="item in categories" :key="item.category_key" class="chart-card">
      <view class="chart-head">
        <text class="chart-title">{{ item.category_name }}</text>
        <text class="chart-number">{{ item.published_count }}</text>
      </view>
      <view class="bar-track">
        <view class="bar-fill" :style="barStyle(item.published_count, maxCategoryCount)"></view>
      </view>
      <text class="chart-meta">
        可交易 {{ item.available_count }} · 已成交 {{ item.sold_count }} · 已下架 {{ item.off_shelf_count }}
      </text>
    </view>

    <view class="section-heading">
      <text class="section-title">活跃用户</text>
      <text class="section-link" @click="loadStats">刷新</text>
    </view>

    <view v-if="users.length === 0 && !loading" class="empty compact">暂无用户数据</view>
    <view v-for="item in users" :key="item.user.id" class="chart-card">
      <view class="chart-head">
        <text class="chart-title">{{ item.user.nickname || item.user.username }}</text>
        <text class="chart-number">{{ item.activity_score }}</text>
      </view>
      <view class="bar-track">
        <view class="bar-fill user" :style="barStyle(item.activity_score, maxUserScore)"></view>
      </view>
      <text class="chart-meta">
        发布 {{ item.published_count }} · 购买请求 {{ item.buy_request_count }} · 收到请求 {{ item.received_request_count }} · 完成 {{ item.completed_count }}
      </text>
    </view>
  </view>
</template>

<script>
import { getStatsCategories, getStatsOverview, getStatsUsers } from '../../api'
import { getAuthToken, getStoredUser } from '../../utils/auth'

const rangeOptions = [
  { value: 7, label: '近 7 天' },
  { value: 30, label: '近 30 天' },
  { value: 90, label: '近 90 天' },
  { value: 365, label: '近 365 天' },
]

export default {
  data() {
    return {
      loading: false,
      selectedDays: 30,
      overview: null,
      categories: [],
      users: [],
    }
  },
  computed: {
    rangeNames() {
      return rangeOptions.map((item) => item.label)
    },
    rangeIndex() {
      return Math.max(0, rangeOptions.findIndex((item) => item.value === this.selectedDays))
    },
    selectedRangeName() {
      return rangeOptions[this.rangeIndex]?.label || '近 30 天'
    },
    rangeLabel() {
      const range = this.overview?.range
      return range ? `${range.start_date} 至 ${range.end_date}` : this.selectedRangeName
    },
    maxCategoryCount() {
      return Math.max(1, ...this.categories.map((item) => item.published_count))
    },
    maxUserScore() {
      return Math.max(1, ...this.users.map((item) => item.activity_score))
    },
  },
  onLoad() {
    if (!this.ensureAdmin()) return
    this.loadStats()
  },
  onPullDownRefresh() {
    this.loadStats().finally(() => uni.stopPullDownRefresh())
  },
  methods: {
    ensureAdmin() {
      const user = getStoredUser() || {}
      if (!getAuthToken()) {
        uni.redirectTo({ url: '/pages/auth/login' })
        return false
      }
      if (user.role !== 'admin') {
        uni.showToast({ title: '无管理权限', icon: 'none' })
        setTimeout(() => uni.navigateBack(), 600)
        return false
      }
      return true
    },
    async loadStats() {
      this.loading = true
      const params = { days: this.selectedDays, limit: 8 }
      try {
        const [overview, categories, users] = await Promise.all([
          getStatsOverview(params),
          getStatsCategories(params),
          getStatsUsers(params),
        ])
        this.overview = overview
        this.categories = categories.items
        this.users = users.items
      } finally {
        this.loading = false
      }
    },
    onRangeChange(event) {
      const index = Number(event.detail.value)
      this.selectedDays = rangeOptions[index]?.value || 30
      this.loadStats()
    },
    barStyle(value, max) {
      const percent = Math.max(6, Math.round((Number(value || 0) / max) * 100))
      return `width: ${Math.min(100, percent)}%;`
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
  line-height: 1.2;
}

.subtitle {
  margin-top: 8rpx;
  color: #66736e;
  font-size: 26rpx;
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

.empty.compact {
  padding: 34rpx 0;
}

.metric-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16rpx;
}

.metric-card,
.status-panel,
.chart-card {
  border: 1rpx solid #e3e9e6;
  border-radius: 22rpx;
  background: #fff;
}

.metric-card {
  padding: 22rpx;
}

.metric-label,
.metric-sub,
.chart-meta,
.status-value {
  color: #66736e;
  font-size: 24rpx;
  line-height: 1.45;
}

.metric-label,
.metric-value,
.metric-sub {
  display: block;
}

.metric-value {
  margin-top: 8rpx;
  color: #17221e;
  font-size: 44rpx;
  font-weight: 700;
}

.metric-sub {
  margin-top: 6rpx;
}

.status-panel {
  margin-top: 18rpx;
  padding: 8rpx 22rpx;
}

.status-row {
  display: flex;
  justify-content: space-between;
  gap: 18rpx;
  padding: 18rpx 0;
  border-bottom: 1rpx solid #edf1ef;
}

.status-row:last-child {
  border-bottom: 0;
}

.status-label {
  flex-shrink: 0;
  color: #17221e;
  font-size: 26rpx;
  font-weight: 700;
}

.status-value {
  text-align: right;
}

.section-heading {
  display: flex;
  align-items: center;
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

.chart-card {
  margin-bottom: 18rpx;
  padding: 22rpx;
}

.chart-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18rpx;
}

.chart-title {
  flex: 1;
  min-width: 0;
  font-size: 30rpx;
  font-weight: 700;
  line-height: 1.35;
}

.chart-number {
  color: #24594e;
  font-size: 30rpx;
  font-weight: 700;
}

.bar-track {
  height: 18rpx;
  margin-top: 16rpx;
  overflow: hidden;
  border-radius: 999rpx;
  background: #edf1ef;
}

.bar-fill {
  height: 100%;
  border-radius: 999rpx;
  background: #25715f;
}

.bar-fill.user {
  background: #4b72a8;
}

.chart-meta {
  display: block;
  margin-top: 12rpx;
}
</style>
