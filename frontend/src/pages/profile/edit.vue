<template>
  <view class="page">
    <view class="header">
      <text class="title">编辑资料</text>
      <text class="subtitle">这些信息会在后续商品发布和交易沟通中使用。</text>
    </view>

    <view class="form-card">
      <text class="label">昵称</text>
      <input v-model="form.nickname" class="input" placeholder="请输入昵称" />

      <text class="label">联系方式</text>
      <input v-model="form.contact" class="input" placeholder="手机号、邮箱或微信号" />

      <text class="label">校区</text>
      <input v-model="form.campus" class="input" placeholder="例如：东校区" />

      <text class="label">头像 URL</text>
      <input v-model="form.avatar_url" class="input" placeholder="可选" />

      <button class="primary-button" :loading="submitting" :disabled="submitting" @click="submit">
        保存
      </button>
    </view>
  </view>
</template>

<script>
import { getMe, updateMe } from '../../api'
import { replaceStoredUser } from '../../utils/auth'

export default {
  data() {
    return {
      submitting: false,
      form: {
        nickname: '',
        contact: '',
        campus: '',
        avatar_url: '',
      },
    }
  },
  async onLoad() {
    const user = await getMe()
    this.form = {
      nickname: user.nickname || '',
      contact: user.contact || '',
      campus: user.campus || '',
      avatar_url: user.avatar_url || '',
    }
  },
  methods: {
    async submit() {
      this.submitting = true
      try {
        const user = await updateMe(this.form)
        replaceStoredUser(user)
        uni.showToast({ title: '已保存', icon: 'success' })
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
