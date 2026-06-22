<template>
  <view class="page">
    <view class="header">
      <text class="title">修改密码</text>
      <text class="subtitle">修改后请使用新密码登录，当前 token 会继续用于本次会话。</text>
    </view>

    <view class="form-card">
      <text class="label">当前密码</text>
      <input
        v-model="form.current_password"
        class="input"
        type="password"
        placeholder="请输入当前密码"
      />

      <text class="label">新密码</text>
      <input
        v-model="form.new_password"
        class="input"
        type="password"
        placeholder="至少 8 位"
      />

      <text class="label">确认新密码</text>
      <input
        v-model="confirmPassword"
        class="input"
        type="password"
        placeholder="再次输入新密码"
      />

      <button class="primary-button" :loading="submitting" :disabled="submitting" @click="submit">
        更新密码
      </button>
    </view>
  </view>
</template>

<script>
import { changePassword } from '../../api'

export default {
  data() {
    return {
      submitting: false,
      confirmPassword: '',
      form: {
        current_password: '',
        new_password: '',
      },
    }
  },
  methods: {
    async submit() {
      if (!this.form.current_password || !this.form.new_password) {
        uni.showToast({ title: '请输入完整密码', icon: 'none' })
        return
      }
      if (this.form.new_password !== this.confirmPassword) {
        uni.showToast({ title: '两次新密码不一致', icon: 'none' })
        return
      }

      this.submitting = true
      try {
        await changePassword(this.form)
        uni.showToast({ title: '密码已更新', icon: 'success' })
        uni.navigateBack()
      } finally {
        this.submitting = false
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

.primary-button {
  margin-top: 30rpx;
  border-radius: 18rpx;
  background: #173f36;
  color: #fff;
  font-size: 29rpx;
}
</style>
