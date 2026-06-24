<template>
  <view class="page">
    <view class="header">
      <text class="eyebrow">JOIN SCHOOL MARKET</text>
      <text class="title">创建账号</text>
      <text class="subtitle">用一个轻量身份开启校园二手交易，买家和卖家身份随时切换。</text>
    </view>

    <view class="form-card">
      <text class="label">账号</text>
      <input v-model="form.username" class="input" placeholder="3-32 位字母、数字或下划线" />

      <text class="label">密码</text>
      <input
        v-model="form.password"
        class="input"
        type="password"
        placeholder="至少 8 位"
      />

      <text class="label">昵称</text>
      <input v-model="form.nickname" class="input" placeholder="用于商品和交易展示" />

      <text class="label">联系方式</text>
      <input v-model="form.contact" class="input" placeholder="手机号、邮箱或微信号" />

      <text class="label">校区</text>
      <input v-model="form.campus" class="input" placeholder="例如：东校区" />

      <button class="primary-button" :loading="submitting" :disabled="submitting" @click="submit">
        注册
      </button>
      <button class="secondary-button" @click="goLogin">已有账号，去登录</button>
    </view>
  </view>
</template>

<script>
import { register } from '../../api'
import {
  clearAuthStorage,
  clearRememberedLogin,
  saveRememberedLogin,
} from '../../utils/auth'

export default {
  data() {
    return {
      submitting: false,
      form: {
        username: '',
        password: '',
        nickname: '',
        contact: '',
        campus: '',
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
        const credentials = {
          username: this.form.username,
          password: this.form.password,
        }
        await register(this.form)
        clearAuthStorage()
        const shouldSave = await this.confirmSavePassword()
        if (shouldSave) {
          saveRememberedLogin(credentials)
        } else {
          clearRememberedLogin()
        }
        uni.redirectTo({ url: '/pages/auth/login' })
      } finally {
        this.submitting = false
      }
    },
    confirmSavePassword() {
      return new Promise((resolve) => {
        uni.showModal({
          title: '注册成功',
          content: '是否把账号和密码保存在本地？保存后返回登录页会自动填充，密码默认隐藏。',
          confirmText: '保存',
          cancelText: '不保存',
          success: (result) => resolve(Boolean(result.confirm)),
          fail: () => resolve(false),
        })
      })
    },
    goLogin() {
      uni.redirectTo({ url: '/pages/auth/login' })
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
  background: rgba(141, 221, 240, 0.24);
}
</style>
