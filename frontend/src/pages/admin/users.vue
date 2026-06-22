<template>
  <view class="page">
    <view class="header">
      <text class="eyebrow">ADMIN</text>
      <text class="title">用户管理</text>
    </view>

    <view class="search-row">
      <input v-model="filters.keyword" class="search-input" placeholder="搜索账号或昵称" />
      <button class="search-button" :disabled="loading" @click="fetchUsers">搜索</button>
    </view>

    <view class="filter-grid">
      <picker :range="roleNames" :value="roleIndex" @change="onRoleChange">
        <view class="select">{{ selectedRoleName }}</view>
      </picker>
      <picker :range="statusNames" :value="statusIndex" @change="onStatusChange">
        <view class="select">{{ selectedStatusName }}</view>
      </picker>
    </view>

    <view v-if="loading && users.length === 0" class="empty">正在加载用户</view>
    <view v-else-if="users.length === 0" class="empty">暂无用户</view>

    <view v-for="user in users" :key="user.id" class="user-card">
      <view class="avatar">
        <text>{{ avatarText(user) }}</text>
      </view>
      <view class="user-main">
        <text class="name">{{ user.nickname || user.username }}</text>
        <text class="meta">{{ user.username }} · {{ roleLabel(user.role) }}</text>
        <text :class="['status', `status-${user.status}`]">{{ userStatusLabel(user.status) }}</text>
      </view>
      <button
        v-if="user.id !== currentUser.id"
        class="action-button"
        :class="{ warn: user.status === 'active' }"
        :disabled="updatingId === user.id"
        :loading="updatingId === user.id"
        @click="toggleStatus(user)"
      >
        {{ user.status === 'active' ? '禁用' : '恢复' }}
      </button>
      <text v-else class="self-label">当前账号</text>
    </view>
  </view>
</template>

<script>
import { getAdminUsers, updateAdminUserStatus } from '../../api'
import { getAuthToken, getStoredUser } from '../../utils/auth'
import { roleLabel, roleOptions, userStatusLabel, userStatusOptions } from '../../utils/product'

export default {
  data() {
    return {
      loading: false,
      updatingId: '',
      currentUser: {},
      users: [],
      filters: {
        page: 1,
        page_size: 50,
        keyword: '',
        role: '',
        status: '',
      },
    }
  },
  computed: {
    roleNames() {
      return roleOptions.map((item) => item.label)
    },
    roleIndex() {
      return Math.max(0, roleOptions.findIndex((item) => item.value === this.filters.role))
    },
    selectedRoleName() {
      return roleOptions[this.roleIndex]?.label || '全部角色'
    },
    statusNames() {
      return userStatusOptions.map((item) => item.label)
    },
    statusIndex() {
      return Math.max(0, userStatusOptions.findIndex((item) => item.value === this.filters.status))
    },
    selectedStatusName() {
      return userStatusOptions[this.statusIndex]?.label || '全部状态'
    },
  },
  onLoad() {
    if (!this.ensureAdmin()) return
    this.fetchUsers()
  },
  onPullDownRefresh() {
    this.fetchUsers().finally(() => uni.stopPullDownRefresh())
  },
  methods: {
    roleLabel,
    userStatusLabel,
    ensureAdmin() {
      this.currentUser = getStoredUser() || {}
      if (!getAuthToken()) {
        uni.redirectTo({ url: '/pages/auth/login' })
        return false
      }
      if (this.currentUser.role !== 'admin') {
        uni.showToast({ title: '无管理权限', icon: 'none' })
        setTimeout(() => uni.navigateBack(), 600)
        return false
      }
      return true
    },
    avatarText(user) {
      return (user.nickname || user.username || '校').slice(0, 1).toUpperCase()
    },
    async fetchUsers() {
      this.loading = true
      try {
        const data = await getAdminUsers(this.filters)
        this.users = data.items
      } finally {
        this.loading = false
      }
    },
    onRoleChange(event) {
      const index = Number(event.detail.value)
      this.filters.role = roleOptions[index]?.value || ''
      this.fetchUsers()
    },
    onStatusChange(event) {
      const index = Number(event.detail.value)
      this.filters.status = userStatusOptions[index]?.value || ''
      this.fetchUsers()
    },
    toggleStatus(user) {
      const nextStatus = user.status === 'active' ? 'disabled' : 'active'
      uni.showModal({
        title: nextStatus === 'disabled' ? '确认禁用用户？' : '确认恢复用户？',
        success: async (result) => {
          if (!result.confirm) return
          this.updatingId = user.id
          try {
            await updateAdminUserStatus(user.id, { status: nextStatus })
            uni.showToast({ title: nextStatus === 'disabled' ? '已禁用' : '已恢复', icon: 'success' })
            await this.fetchUsers()
          } finally {
            this.updatingId = ''
          }
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

.search-row,
.filter-grid,
.user-card {
  display: flex;
  align-items: center;
}

.search-row {
  gap: 16rpx;
  margin-bottom: 18rpx;
}

.search-input {
  flex: 1;
  height: 82rpx;
  box-sizing: border-box;
  padding: 0 22rpx;
  border: 1rpx solid #dbe3df;
  border-radius: 18rpx;
  background: #fff;
  font-size: 28rpx;
}

.search-button {
  width: 150rpx;
  border-radius: 18rpx;
  background: #24594e;
  color: #fff;
  font-size: 27rpx;
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

.user-card {
  margin-bottom: 18rpx;
  padding: 22rpx;
  border: 1rpx solid #e3e9e6;
  border-radius: 22rpx;
  background: #fff;
}

.avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 86rpx;
  height: 86rpx;
  margin-right: 18rpx;
  border-radius: 22rpx;
  background: #173f36;
  color: #fff;
  font-size: 36rpx;
  font-weight: 700;
}

.user-main {
  display: flex;
  flex: 1;
  min-width: 0;
  flex-direction: column;
}

.name {
  font-size: 31rpx;
  font-weight: 700;
  line-height: 1.35;
}

.meta {
  margin-top: 6rpx;
  color: #66736e;
  font-size: 24rpx;
}

.status {
  align-self: flex-start;
  margin-top: 10rpx;
  padding: 7rpx 13rpx;
  border-radius: 999rpx;
  background: #ddf5eb;
  color: #25715f;
  font-size: 22rpx;
}

.status-disabled {
  background: #f1e2df;
  color: #a74740;
}

.action-button {
  width: 132rpx;
  margin-left: 14rpx;
  border-radius: 16rpx;
  background: #eef4f1;
  color: #24594e;
  font-size: 25rpx;
}

.action-button.warn {
  background: #f1e2df;
  color: #a74740;
}

.self-label {
  margin-left: 14rpx;
  color: #75817c;
  font-size: 24rpx;
}
</style>
