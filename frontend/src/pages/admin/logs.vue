<template>
  <view class="page">
    <view class="header">
      <text class="eyebrow">ADMIN</text>
      <text class="title">操作日志</text>
    </view>

    <view class="filter-grid">
      <picker :range="actionNames" :value="actionIndex" @change="onActionChange">
        <view class="select">{{ selectedActionName }}</view>
      </picker>
      <picker :range="targetNames" :value="targetIndex" @change="onTargetChange">
        <view class="select">{{ selectedTargetName }}</view>
      </picker>
    </view>

    <view v-if="loading && logs.length === 0" class="empty">正在加载日志</view>
    <view v-else-if="logs.length === 0" class="empty">暂无日志</view>

    <view v-for="log in logs" :key="log.id" class="log-card">
      <view class="log-head">
        <text class="log-title">{{ logActionLabel(log.action) }}</text>
        <text class="target">{{ targetLabel(log.target_type) }}</text>
      </view>
      <text class="meta">
        {{ log.operator?.nickname || log.operator?.username || log.operator_id }} · {{ log.created_at || '-' }}
      </text>
      <text class="target-id">目标：{{ log.target_id || '-' }}</text>
      <text class="details">{{ detailText(log.details) }}</text>
    </view>
  </view>
</template>

<script>
import { getAdminLogs } from '../../api'
import { getAuthToken, getStoredUser } from '../../utils/auth'
import { logActionLabel } from '../../utils/product'

const actionOptions = [
  { value: '', label: '全部操作' },
  { value: 'user_status_update', label: '用户状态更新' },
  { value: 'product_status_update', label: '商品状态更新' },
  { value: 'product_delete', label: '商品删除' },
  { value: 'announcement_create', label: '公告创建' },
  { value: 'announcement_update', label: '公告更新' },
  { value: 'announcement_delete', label: '公告隐藏' },
]

const targetOptions = [
  { value: '', label: '全部目标' },
  { value: 'user', label: '用户' },
  { value: 'product', label: '商品' },
  { value: 'announcement', label: '公告' },
]

export default {
  data() {
    return {
      loading: false,
      logs: [],
      filters: {
        page: 1,
        page_size: 50,
        action: '',
        target_type: '',
      },
    }
  },
  computed: {
    actionNames() {
      return actionOptions.map((item) => item.label)
    },
    actionIndex() {
      return Math.max(0, actionOptions.findIndex((item) => item.value === this.filters.action))
    },
    selectedActionName() {
      return actionOptions[this.actionIndex]?.label || '全部操作'
    },
    targetNames() {
      return targetOptions.map((item) => item.label)
    },
    targetIndex() {
      return Math.max(0, targetOptions.findIndex((item) => item.value === this.filters.target_type))
    },
    selectedTargetName() {
      return targetOptions[this.targetIndex]?.label || '全部目标'
    },
  },
  onLoad() {
    if (!this.ensureAdmin()) return
    this.fetchLogs()
  },
  onPullDownRefresh() {
    this.fetchLogs().finally(() => uni.stopPullDownRefresh())
  },
  methods: {
    logActionLabel,
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
    async fetchLogs() {
      this.loading = true
      try {
        const data = await getAdminLogs(this.filters)
        this.logs = data.items
      } finally {
        this.loading = false
      }
    },
    onActionChange(event) {
      const index = Number(event.detail.value)
      this.filters.action = actionOptions[index]?.value || ''
      this.fetchLogs()
    },
    onTargetChange(event) {
      const index = Number(event.detail.value)
      this.filters.target_type = targetOptions[index]?.value || ''
      this.fetchLogs()
    },
    targetLabel(value) {
      return targetOptions.find((item) => item.value === value)?.label || value || '目标'
    },
    detailText(details) {
      if (!details || Object.keys(details).length === 0) {
        return '无详情'
      }
      return Object.entries(details)
        .map(([key, value]) => `${key}: ${value}`)
        .join('，')
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

.filter-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14rpx;
  margin-bottom: 24rpx;
}

.select {
  height: 72rpx;
  box-sizing: border-box;
  padding: 0 18rpx;
  border: 1rpx solid #dbe3df;
  border-radius: 16rpx;
  background: #fff;
  color: #43504b;
  font-size: 25rpx;
  line-height: 72rpx;
}

.empty {
  padding: 100rpx 0;
  color: #75817c;
  font-size: 28rpx;
  text-align: center;
}

.log-card {
  margin-bottom: 18rpx;
  padding: 22rpx;
  border: 1rpx solid #e3e9e6;
  border-radius: 22rpx;
  background: #fff;
}

.log-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18rpx;
}

.log-title {
  flex: 1;
  min-width: 0;
  font-size: 31rpx;
  font-weight: 700;
  line-height: 1.35;
}

.target {
  padding: 8rpx 14rpx;
  border-radius: 999rpx;
  background: #eef4f1;
  color: #24594e;
  font-size: 22rpx;
}

.meta,
.target-id,
.details {
  display: block;
  margin-top: 10rpx;
  color: #66736e;
  font-size: 24rpx;
  line-height: 1.5;
  word-break: break-all;
}

.target-id {
  color: #8b9692;
  font-size: 22rpx;
}

.details {
  color: #43504b;
}
</style>
