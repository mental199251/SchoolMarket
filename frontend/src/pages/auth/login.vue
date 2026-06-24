<template>
  <view class="page">
    <view class="header">
      <text class="eyebrow">WELCOME BACK</text>
      <text class="title">登录校淘空间</text>
      <text class="subtitle">登录后直接进入首页，浏览、发布、交易和消息都会保持同步。</text>
    </view>

    <view class="form-card">
      <text class="label">账号</text>
      <input v-model="form.username" class="input" placeholder="请输入账号" />

      <view class="label-row">
        <text class="label inline">密码</text>
        <text class="toggle-password" @click="showPassword = !showPassword">
          {{ showPassword ? '隐藏密码' : '显示密码' }}
        </text>
      </view>
      <input
        v-model="form.password"
        class="input"
        :password="!showPassword"
        placeholder="请输入密码"
      />

      <view class="remember-row" @click="rememberPassword = !rememberPassword">
        <view :class="['check-box', { checked: rememberPassword }]">
          <text v-if="rememberPassword">✓</text>
        </view>
        <text class="remember-text">保存账号和密码到本地，下次自动填充</text>
      </view>

      <button class="primary-button" :loading="submitting" :disabled="submitting" @click="submit">
        登录
      </button>
      <button class="secondary-button" @click="goRegister">创建新账号</button>
    </view>
  </view>
</template>

<script>
import { login } from '../../api'
import {
  clearRememberedLogin,
  getRememberedLogin,
  hasValidAuth,
  saveRememberedLogin,
  setAuthSession,
} from '../../utils/auth'

export default {
  data() {
    return {
      rememberPassword: true,
      showPassword: false,
      submitting: false,
      form: {
        username: '',
        password: '',
      },
    }
  },
  onLoad() {
    if (hasValidAuth()) {
      uni.reLaunch({ url: '/pages/index/index' })
      return
    }
    const remembered = getRememberedLogin()
    if (remembered.remember) {
      this.form.username = remembered.username || ''
      this.form.password = remembered.password || ''
      this.rememberPassword = true
    }
  },
  methods: {
    async submit() {
      if (!this.form.username || !this.form.password) {
        uni.showToast({ title: '请输入账号和密码', icon: 'none' })
        return
      }

      this.submitting = true
      try {
        const session = await login(this.form)
        setAuthSession(session)
        if (this.rememberPassword) {
          saveRememberedLogin({
            username: this.form.username,
            password: this.form.password,
          })
        } else {
          clearRememberedLogin()
        }
        uni.showToast({ title: '登录成功', icon: 'success' })
        uni.reLaunch({ url: '/pages/index/index' })
      } finally {
        this.submitting = false
      }
    },
    goRegister() {
      uni.navigateTo({ url: '/pages/auth/register' })
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
  padding: 56rpx 32rpx 64rpx;
  color: #17221e;
}

.header {
  display: flex;
  flex-direction: column;
  margin-bottom: 36rpx;
}

.title {
  font-size: 50rpx;
  font-weight: 700;
  line-height: 1.25;
}

.subtitle {
  margin-top: 12rpx;
  color: #66736e;
  font-size: 27rpx;
  line-height: 1.6;
}

.form-card {
  padding: 32rpx;
  border: 1rpx solid #e3e9e6;
  border-radius: 24rpx;
  background: #fff;
}

.label {
  display: block;
  margin: 24rpx 0 12rpx;
  color: #43504b;
  font-size: 25rpx;
  font-weight: 600;
}

.label:first-child {
  margin-top: 0;
}

.label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 24rpx 0 12rpx;
}

.label.inline {
  margin: 0;
}

.toggle-password {
  color: #ff5a1f;
  font-size: 24rpx;
  font-weight: 700;
}

.input {
  height: 88rpx;
  box-sizing: border-box;
  padding: 0 24rpx;
  border: 1rpx solid #dbe3df;
  border-radius: 18rpx;
  background: #f8faf9;
  font-size: 29rpx;
}

.remember-row {
  display: flex;
  align-items: center;
  gap: 14rpx;
  margin-top: 22rpx;
}

.check-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34rpx;
  height: 34rpx;
  border: 2rpx solid #d4ddd9;
  border-radius: 8rpx;
  background: #fff;
  color: #fff;
  font-size: 24rpx;
  font-weight: 900;
  line-height: 1;
  box-sizing: border-box;
}

.check-box.checked {
  border-color: #ff5a1f;
  background: #ff5a1f;
}

.remember-text {
  flex: 1;
  min-width: 0;
  color: #69736f;
  font-size: 24rpx;
  line-height: 1.35;
}

.primary-button,
.secondary-button {
  margin-top: 28rpx;
  border-radius: 18rpx;
  font-size: 29rpx;
}

.primary-button {
  background: linear-gradient(135deg, #ff4f28, #ff8d34);
  color: #fff;
}

.secondary-button {
  background: #eef4f1;
  color: #24594e;
}

.form-card {
  position: relative;
  overflow: hidden;
}

.form-card::before {
  content: "";
  position: absolute;
  right: -40rpx;
  top: -40rpx;
  width: 180rpx;
  height: 180rpx;
  border-radius: 999rpx;
  background: rgba(255, 205, 162, 0.24);
}
</style>
