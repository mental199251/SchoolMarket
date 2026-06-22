<template>
  <view class="page">
    <view class="header">
      <text class="eyebrow">ADMIN</text>
      <text class="title">公告维护</text>
    </view>

    <view class="form-panel">
      <input v-model="form.title" class="input" placeholder="公告标题" />
      <textarea v-model="form.content" class="textarea" placeholder="公告内容" maxlength="2000" />
      <picker :range="statusNamesForForm" :value="formStatusIndex" @change="onFormStatusChange">
        <view class="select">{{ formStatusName }}</view>
      </picker>
      <view class="form-actions">
        <button class="primary-button" :loading="saving" :disabled="saving" @click="saveAnnouncement">
          {{ editingId ? '保存修改' : '创建公告' }}
        </button>
        <button v-if="editingId" class="secondary-button" @click="resetForm">取消编辑</button>
      </view>
    </view>

    <picker :range="statusNames" :value="statusIndex" @change="onStatusChange">
      <view class="select list-select">{{ selectedStatusName }}</view>
    </picker>

    <view v-if="loading && announcements.length === 0" class="empty">正在加载公告</view>
    <view v-else-if="announcements.length === 0" class="empty">暂无公告</view>

    <view v-for="item in announcements" :key="item.id" class="announcement-card">
      <view class="announcement-head">
        <text class="announcement-title">{{ item.title }}</text>
        <text :class="['status', `status-${item.status}`]">{{ announcementStatusLabel(item.status) }}</text>
      </view>
      <text class="announcement-content">{{ item.content || '暂无内容' }}</text>
      <text class="announcement-time">{{ item.updated_at || item.created_at || '-' }}</text>
      <view class="actions">
        <button class="action-button" @click="editAnnouncement(item)">编辑</button>
        <button
          class="action-button"
          @click="quickStatus(item, item.status === 'published' ? 'hidden' : 'published')"
        >
          {{ item.status === 'published' ? '隐藏' : '发布' }}
        </button>
        <button class="action-button danger" @click="removeAnnouncement(item)">删除</button>
      </view>
    </view>
  </view>
</template>

<script>
import {
  createAdminAnnouncement,
  deleteAdminAnnouncement,
  getAdminAnnouncements,
  updateAdminAnnouncement,
} from '../../api'
import { getAuthToken, getStoredUser } from '../../utils/auth'
import {
  announcementStatusLabel,
  announcementStatusOptions,
} from '../../utils/product'

const editableStatusOptions = announcementStatusOptions.filter((item) => item.value)

export default {
  data() {
    return {
      loading: false,
      saving: false,
      editingId: '',
      announcements: [],
      form: {
        title: '',
        content: '',
        status: 'published',
      },
      filters: {
        page: 1,
        page_size: 50,
        status: '',
      },
    }
  },
  computed: {
    statusNames() {
      return announcementStatusOptions.map((item) => item.label)
    },
    statusIndex() {
      return Math.max(0, announcementStatusOptions.findIndex((item) => item.value === this.filters.status))
    },
    selectedStatusName() {
      return announcementStatusOptions[this.statusIndex]?.label || '全部状态'
    },
    statusNamesForForm() {
      return editableStatusOptions.map((item) => item.label)
    },
    formStatusIndex() {
      return Math.max(0, editableStatusOptions.findIndex((item) => item.value === this.form.status))
    },
    formStatusName() {
      return editableStatusOptions[this.formStatusIndex]?.label || '已发布'
    },
  },
  onLoad() {
    if (!this.ensureAdmin()) return
    this.fetchAnnouncements()
  },
  onPullDownRefresh() {
    this.fetchAnnouncements().finally(() => uni.stopPullDownRefresh())
  },
  methods: {
    announcementStatusLabel,
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
    async fetchAnnouncements() {
      this.loading = true
      try {
        const data = await getAdminAnnouncements(this.filters)
        this.announcements = data.items
      } finally {
        this.loading = false
      }
    },
    onStatusChange(event) {
      const index = Number(event.detail.value)
      this.filters.status = announcementStatusOptions[index]?.value || ''
      this.fetchAnnouncements()
    },
    onFormStatusChange(event) {
      const index = Number(event.detail.value)
      this.form.status = editableStatusOptions[index]?.value || 'published'
    },
    validateForm() {
      if (!this.form.title.trim()) {
        uni.showToast({ title: '请填写标题', icon: 'none' })
        return false
      }
      return true
    },
    async saveAnnouncement() {
      if (!this.validateForm()) return
      this.saving = true
      try {
        const payload = {
          title: this.form.title.trim(),
          content: this.form.content.trim(),
          status: this.form.status,
        }
        if (this.editingId) {
          await updateAdminAnnouncement(this.editingId, payload)
        } else {
          await createAdminAnnouncement(payload)
        }
        uni.showToast({ title: this.editingId ? '已保存' : '已创建', icon: 'success' })
        this.resetForm()
        await this.fetchAnnouncements()
      } finally {
        this.saving = false
      }
    },
    editAnnouncement(item) {
      this.editingId = item.id
      this.form = {
        title: item.title,
        content: item.content || '',
        status: item.status || 'published',
      }
    },
    resetForm() {
      this.editingId = ''
      this.form = {
        title: '',
        content: '',
        status: 'published',
      }
    },
    async quickStatus(item, status) {
      await updateAdminAnnouncement(item.id, {
        title: item.title,
        content: item.content || '',
        status,
      })
      uni.showToast({ title: status === 'published' ? '已发布' : '已隐藏', icon: 'success' })
      await this.fetchAnnouncements()
    },
    removeAnnouncement(item) {
      uni.showModal({
        title: '确认隐藏公告？',
        content: item.title,
        success: async (result) => {
          if (!result.confirm) return
          await deleteAdminAnnouncement(item.id)
          uni.showToast({ title: '已隐藏', icon: 'success' })
          if (this.editingId === item.id) {
            this.resetForm()
          }
          await this.fetchAnnouncements()
        },
      })
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

.form-panel,
.announcement-card {
  border: 1rpx solid #e3e9e6;
  border-radius: 22rpx;
  background: #fff;
}

.form-panel {
  margin-bottom: 24rpx;
  padding: 22rpx;
}

.input,
.textarea,
.select {
  box-sizing: border-box;
  width: 100%;
  border: 1rpx solid #dbe3df;
  border-radius: 16rpx;
  background: #fff;
  color: #17221e;
  font-size: 27rpx;
}

.input {
  height: 76rpx;
  padding: 0 18rpx;
}

.textarea {
  height: 170rpx;
  margin-top: 16rpx;
  padding: 18rpx;
  line-height: 1.5;
}

.select {
  height: 72rpx;
  margin-top: 16rpx;
  padding: 0 18rpx;
  color: #43504b;
  line-height: 72rpx;
}

.list-select {
  margin-bottom: 22rpx;
}

.form-actions,
.actions,
.announcement-head {
  display: flex;
  align-items: center;
}

.form-actions {
  gap: 14rpx;
  margin-top: 18rpx;
}

.primary-button,
.secondary-button {
  flex: 1;
  border-radius: 16rpx;
  font-size: 26rpx;
}

.primary-button {
  background: #173f36;
  color: #fff;
}

.secondary-button {
  background: #eef4f1;
  color: #24594e;
}

.empty {
  padding: 100rpx 0;
  color: #75817c;
  font-size: 28rpx;
  text-align: center;
}

.announcement-card {
  margin-bottom: 18rpx;
  padding: 22rpx;
}

.announcement-head {
  justify-content: space-between;
  gap: 18rpx;
}

.announcement-title {
  flex: 1;
  min-width: 0;
  font-size: 31rpx;
  font-weight: 700;
  line-height: 1.35;
}

.status {
  padding: 8rpx 14rpx;
  border-radius: 999rpx;
  background: #ddf5eb;
  color: #25715f;
  font-size: 22rpx;
}

.status-hidden {
  background: #f0f2f1;
  color: #69746f;
}

.announcement-content,
.announcement-time {
  display: block;
  margin-top: 10rpx;
  color: #66736e;
  font-size: 25rpx;
  line-height: 1.5;
}

.announcement-time {
  color: #8b9692;
  font-size: 22rpx;
}

.actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14rpx;
  margin-top: 18rpx;
}

.action-button {
  min-width: 0;
  border-radius: 16rpx;
  background: #eef4f1;
  color: #24594e;
  font-size: 25rpx;
}

.action-button.danger {
  background: #f1e2df;
  color: #a74740;
}
</style>
