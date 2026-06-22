<template>
  <view class="page">
    <view class="hero">
      <text class="eyebrow">SCHOOL MARKET</text>
      <text class="title">校淘空间</text>
      <text class="subtitle">M1 前后端联调状态</text>
    </view>

    <view class="summary-card">
      <view class="summary-row">
        <view>
          <text class="summary-label">系统状态</text>
          <text class="summary-value">{{ overallLabel }}</text>
        </view>
        <view :class="['summary-indicator', `indicator-${overallState}`]"></view>
      </view>
      <text class="api-label">API 地址</text>
      <text class="api-value">{{ apiBaseUrl }}</text>
    </view>

    <view class="auth-actions">
      <button class="auth-primary" @click="goProfile">
        {{ currentUser ? '进入个人中心' : '登录 / 注册' }}
      </button>
      <button class="auth-secondary" @click="goRegister">创建测试账号</button>
    </view>

    <view class="section-heading">
      <text class="section-title">服务检查</text>
      <text class="checked-at">{{ checkedAt || '尚未检查' }}</text>
    </view>

    <view class="status-card">
      <view class="status-main">
        <view :class="['status-icon', `status-${flaskStatus.state}`]">
          <text>{{ flaskStatus.state === 'success' ? 'OK' : 'API' }}</text>
        </view>
        <view class="status-copy">
          <text class="status-name">Flask API</text>
          <text class="status-detail">{{ flaskStatus.detail }}</text>
        </view>
      </view>
      <text :class="['status-tag', `tag-${flaskStatus.state}`]">
        {{ flaskStatus.label }}
      </text>
    </view>

    <view class="status-card">
      <view class="status-main">
        <view :class="['status-icon', `status-${mongoStatus.state}`]">
          <text>{{ mongoStatus.state === 'success' ? 'DB' : 'M' }}</text>
        </view>
        <view class="status-copy">
          <text class="status-name">MongoDB</text>
          <text class="status-detail">{{ mongoStatus.detail }}</text>
        </view>
      </view>
      <text :class="['status-tag', `tag-${mongoStatus.state}`]">
        {{ mongoStatus.label }}
      </text>
    </view>

    <button class="check-button" :loading="checking" :disabled="checking" @click="checkServices">
      {{ checking ? '正在检查...' : '重新检查' }}
    </button>

    <view class="tip-card">
      <text class="tip-title">联调说明</text>
      <text class="tip-text">/health 只检查 Flask；/ready 单独检查 MongoDB。数据库停止时，API 仍应保持健康。</text>
    </view>
  </view>
</template>

<script>
import { API_BASE_URL } from '../../api/config'
import { getHealth, getReadiness } from '../../api'
import { getStoredUser, hasValidAuth } from '../../utils/auth'

const pendingStatus = (detail) => ({
  state: 'pending',
  label: '等待检查',
  detail,
})

export default {
  data() {
    return {
      apiBaseUrl: API_BASE_URL,
      checking: false,
      checkedAt: '',
      currentUser: null,
      flaskStatus: pendingStatus('等待连接后端服务'),
      mongoStatus: pendingStatus('等待检查数据库连接'),
    }
  },
  computed: {
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
  },
  onShow() {
    this.currentUser = hasValidAuth() ? getStoredUser() : null
  },
  onPullDownRefresh() {
    this.checkServices().finally(() => uni.stopPullDownRefresh())
  },
  methods: {
    goProfile() {
      uni.navigateTo({
        url: this.currentUser ? '/pages/profile/profile' : '/pages/auth/login',
      })
    },
    goRegister() {
      uni.navigateTo({ url: '/pages/auth/register' })
    },
    async checkServices() {
      this.checking = true
      this.flaskStatus = {
        state: 'checking',
        label: '检查中',
        detail: '正在请求 /health',
      }
      this.mongoStatus = {
        state: 'checking',
        label: '检查中',
        detail: '正在请求 /ready',
      }

      const healthCheck = getHealth()
        .then((data) => {
          this.flaskStatus = {
            state: 'success',
            label: '正常',
            detail: `${data.service} · ${data.status}`,
          }
        })
        .catch((error) => {
          this.flaskStatus = {
            state: 'error',
            label: '不可用',
            detail: error.message,
          }
        })

      const readinessCheck = getReadiness()
        .then((data) => {
          this.mongoStatus = {
            state: 'success',
            label: '已就绪',
            detail: `MongoDB · ${data.dependencies.mongodb}`,
          }
        })
        .catch((error) => {
          this.mongoStatus = {
            state: 'error',
            label: '未就绪',
            detail: error.message,
          }
        })

      await Promise.all([healthCheck, readinessCheck])
      this.checkedAt = this.formatTime(new Date())
      this.checking = false
    },
    formatTime(date) {
      const pad = (value) => String(value).padStart(2, '0')
      return `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
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
  padding: 48rpx 32rpx 64rpx;
  color: #17221e;
}

.hero {
  display: flex;
  flex-direction: column;
  margin-bottom: 36rpx;
}

.eyebrow {
  margin-bottom: 10rpx;
  color: #367c6c;
  font-size: 22rpx;
  font-weight: 700;
  letter-spacing: 4rpx;
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

.summary-card {
  padding: 36rpx;
  border-radius: 28rpx;
  background: #173f36;
  box-shadow: 0 16rpx 40rpx rgba(23, 63, 54, 0.16);
  color: #fff;
}

.summary-row,
.section-heading,
.status-card,
.status-main {
  display: flex;
  align-items: center;
}

.summary-row,
.section-heading,
.status-card {
  justify-content: space-between;
}

.summary-label,
.api-label {
  display: block;
  color: rgba(255, 255, 255, 0.66);
  font-size: 24rpx;
}

.summary-value {
  display: block;
  margin-top: 8rpx;
  font-size: 40rpx;
  font-weight: 700;
}

.summary-indicator {
  width: 26rpx;
  height: 26rpx;
  border: 8rpx solid rgba(255, 255, 255, 0.16);
  border-radius: 50%;
  background: #a9b3af;
}

.indicator-success {
  background: #63d6a5;
}

.indicator-warning {
  background: #f4bd63;
}

.indicator-error {
  background: #ef786f;
}

.indicator-checking {
  background: #77b9ff;
}

.api-label {
  margin-top: 32rpx;
}

.api-value {
  display: block;
  margin-top: 8rpx;
  font-family: monospace;
  font-size: 24rpx;
  word-break: break-all;
}

.auth-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18rpx;
  margin-top: 24rpx;
}

.auth-primary,
.auth-secondary {
  border-radius: 18rpx;
  font-size: 28rpx;
}

.auth-primary {
  background: #173f36;
  color: #fff;
}

.auth-secondary {
  background: #fff;
  color: #24594e;
}

.section-heading {
  margin: 48rpx 4rpx 20rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 700;
}

.checked-at {
  color: #87918d;
  font-size: 24rpx;
}

.status-card {
  margin-bottom: 20rpx;
  padding: 28rpx;
  border: 1rpx solid #e3e9e6;
  border-radius: 24rpx;
  background: #fff;
}

.status-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 76rpx;
  height: 76rpx;
  margin-right: 24rpx;
  border-radius: 22rpx;
  background: #edf1ef;
  color: #5f6b66;
  font-size: 22rpx;
  font-weight: 700;
}

.status-success {
  background: #ddf5eb;
  color: #25715f;
}

.status-error {
  background: #fde6e3;
  color: #a74740;
}

.status-checking {
  background: #e4f0fd;
  color: #356c9e;
}

.status-copy {
  display: flex;
  flex-direction: column;
  max-width: 390rpx;
}

.status-name {
  font-size: 30rpx;
  font-weight: 600;
}

.status-detail {
  margin-top: 8rpx;
  color: #75817c;
  font-size: 23rpx;
  line-height: 1.45;
}

.status-tag {
  padding: 10rpx 16rpx;
  border-radius: 999rpx;
  background: #eef1f0;
  color: #69746f;
  font-size: 22rpx;
}

.tag-success {
  background: #ddf5eb;
  color: #25715f;
}

.tag-error {
  background: #fde6e3;
  color: #a74740;
}

.tag-checking {
  background: #e4f0fd;
  color: #356c9e;
}

.check-button {
  margin-top: 32rpx;
  border: 0;
  border-radius: 20rpx;
  background: #2f7d6c;
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
}

.check-button::after {
  border: 0;
}

.tip-card {
  margin-top: 28rpx;
  padding: 28rpx;
  border-radius: 22rpx;
  background: #e8eeeb;
}

.tip-title {
  display: block;
  margin-bottom: 10rpx;
  color: #315a50;
  font-size: 25rpx;
  font-weight: 700;
}

.tip-text {
  color: #65716c;
  font-size: 24rpx;
  line-height: 1.65;
}
</style>
