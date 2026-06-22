<template>
  <view class="page">
    <view class="header">
      <text class="title">创建账号</text>
      <text class="subtitle">账号只用于校园二手交易身份识别，买家和卖家不拆分角色。</text>
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
        注册并登录
      </button>
      <button class="secondary-button" @click="goLogin">已有账号，去登录</button>
    </view>
  </view>
</template>

<script>
import { register } from '../../api'
import { setAuthSession } from '../../utils/auth'

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
        const session = await register(this.form)
        setAuthSession(session)
        uni.showToast({ title: '注册成功', icon: 'success' })
        uni.redirectTo({ url: '/pages/profile/profile' })
      } finally {
        this.submitting = false
      }
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
</style>
