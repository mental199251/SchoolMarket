<template>
  <view class="page">
    <view class="header">
      <text class="eyebrow">MY ACCOUNT</text>
      <text class="title">{{ user.nickname || user.username || '个人中心' }}</text>
      <text class="subtitle">{{ user.username ? `账号：${user.username}` : '请先登录' }}</text>
    </view>

    <view v-if="user.username" class="profile-card">
      <view class="avatar">
        <text>{{ avatarText }}</text>
      </view>
      <view class="profile-main">
        <text class="name">{{ user.nickname || user.username }}</text>
        <text class="meta">{{ roleLabel }} · {{ statusLabel }}</text>
      </view>
    </view>

    <view v-if="user.username" class="info-list">
      <view class="info-row">
        <text class="info-label">联系方式</text>
        <text class="info-value">{{ user.contact || '未填写' }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">校区</text>
        <text class="info-value">{{ user.campus || '未填写' }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">注册时间</text>
        <text class="info-value">{{ user.created_at || '-' }}</text>
      </view>
    </view>

    <view class="actions">
      <button class="primary-button" @click="goEdit">编辑资料</button>
      <button class="secondary-button" @click="goPassword">修改密码</button>
      <button class="ghost-button" :loading="loggingOut" :disabled="loggingOut" @click="submitLogout">
        退出登录
      </button>
    </view>
  </view>
</template>

<script>
import { getMe, logout } from '../../api'
import {
  clearAuthStorage,
  getAuthToken,
  getStoredExpiresAt,
  replaceStoredUser,
} from '../../utils/auth'

export default {
  data() {
    return {
      user: {},
      loggingOut: false,
    }
  },
  computed: {
    avatarText() {
      const name = this.user.nickname || this.user.username || '校'
      return name.slice(0, 1).toUpperCase()
    },
    roleLabel() {
      return this.user.role === 'admin' ? '管理员' : '普通用户'
    },
    statusLabel() {
      return this.user.status === 'active' ? '正常' : '已禁用'
    },
  },
  onShow() {
    this.loadProfile()
  },
  methods: {
    async loadProfile() {
      if (!getAuthToken()) {
        uni.redirectTo({ url: '/pages/auth/login' })
        return
      }

      try {
        const user = await getMe()
        this.user = user
        replaceStoredUser(user)
      } catch (error) {
        if (error.statusCode === 401) {
          uni.redirectTo({ url: '/pages/auth/login' })
        }
      }
    },
    goEdit() {
      uni.navigateTo({ url: '/pages/profile/edit' })
    },
    goPassword() {
      uni.navigateTo({ url: '/pages/profile/password' })
    },
    async submitLogout() {
      this.loggingOut = true
      try {
        if (getStoredExpiresAt()) {
          await logout({ showError: false })
        }
      } catch (_error) {
        // 本地退出优先，服务端失败不阻断用户清理登录态。
      } finally {
        clearAuthStorage()
        this.loggingOut = false
        uni.reLaunch({ url: '/pages/index/index' })
      }
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

.header {
  display: flex;
  flex-direction: column;
  margin-bottom: 32rpx;
}

.eyebrow {
  margin-bottom: 10rpx;
  color: #367c6c;
  font-size: 22rpx;
  font-weight: 700;
}

.title {
  font-size: 50rpx;
  font-weight: 700;
  line-height: 1.25;
}

.subtitle {
  margin-top: 10rpx;
  color: #66736e;
  font-size: 27rpx;
}

.profile-card,
.info-list {
  border: 1rpx solid #e3e9e6;
  border-radius: 24rpx;
  background: #fff;
}

.profile-card {
  display: flex;
  align-items: center;
  padding: 32rpx;
}

.avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 96rpx;
  height: 96rpx;
  margin-right: 24rpx;
  border-radius: 28rpx;
  background: #173f36;
  color: #fff;
  font-size: 42rpx;
  font-weight: 700;
}

.profile-main {
  display: flex;
  flex-direction: column;
}

.name {
  font-size: 34rpx;
  font-weight: 700;
}

.meta {
  margin-top: 8rpx;
  color: #66736e;
  font-size: 25rpx;
}

.info-list {
  margin-top: 24rpx;
  padding: 8rpx 28rpx;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #edf1ef;
}

.info-row:last-child {
  border-bottom: 0;
}

.info-label {
  color: #66736e;
  font-size: 26rpx;
}

.info-value {
  max-width: 420rpx;
  color: #17221e;
  font-size: 26rpx;
  text-align: right;
  word-break: break-all;
}

.actions {
  margin-top: 32rpx;
}

.primary-button,
.secondary-button,
.ghost-button {
  margin-top: 22rpx;
  border-radius: 18rpx;
  font-size: 29rpx;
}

.primary-button {
  background: #173f36;
  color: #fff;
}

.secondary-button {
  background: #eef4f1;
  color: #24594e;
}

.ghost-button {
  background: #fff;
  color: #a74740;
}
</style>
