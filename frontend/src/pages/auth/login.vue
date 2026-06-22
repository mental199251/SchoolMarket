<template>
  <view class="page">
    <view class="header">
      <text class="title">欢迎回来</text>
      <text class="subtitle">登录后可以维护资料，并继续后续商品和交易流程。</text>
    </view>

    <view class="form-card">
      <text class="label">账号</text>
      <input v-model="form.username" class="input" placeholder="请输入账号" />

      <text class="label">密码</text>
      <input
        v-model="form.password"
        class="input"
        type="password"
        placeholder="请输入密码"
      />

      <button class="primary-button" :loading="submitting" :disabled="submitting" @click="submit">
        登录
      </button>
      <button class="secondary-button" @click="goRegister">创建新账号</button>
    </view>
  </view>
</template>

<script>
import { login } from '../../api'
import { setAuthSession } from '../../utils/auth'

export default {
  data() {
    return {
      submitting: false,
      form: {
        username: '',
        password: '',
      },
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
        uni.showToast({ title: '登录成功', icon: 'success' })
        uni.redirectTo({ url: '/pages/profile/profile' })
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

.input {
  height: 88rpx;
  box-sizing: border-box;
  padding: 0 24rpx;
  border: 1rpx solid #dbe3df;
  border-radius: 18rpx;
  background: #f8faf9;
  font-size: 29rpx;
}

.primary-button,
.secondary-button {
  margin-top: 28rpx;
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
</style>
