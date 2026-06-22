<template>
  <view class="page">
    <view class="header">
      <text class="eyebrow">MESSAGES</text>
      <text class="title">消息中心</text>
      <text class="subtitle">未读 {{ unreadCount }} 条</text>
      <button class="nav-button" :disabled="loading || unreadCount === 0" @click="readAll">
        全部已读
      </button>
    </view>

    <picker :range="readNames" :value="readIndex" @change="onReadChange">
      <view class="select">{{ selectedReadName }}</view>
    </picker>

    <view v-if="loading && messages.length === 0" class="empty">正在加载消息</view>
    <view v-else-if="messages.length === 0" class="empty">暂无消息</view>

    <view
      v-for="message in messages"
      :key="message.id"
      :class="['message-card', { unread: !message.is_read }]"
    >
      <view class="message-head">
        <text class="message-title">{{ message.title }}</text>
        <text :class="['read-dot', { active: !message.is_read }]"></text>
      </view>
      <text class="message-content">{{ message.content || '暂无内容' }}</text>
      <text class="message-time">{{ message.created_at || '-' }}</text>
      <view class="actions">
        <button class="action-button" :disabled="message.is_read" @click="readOne(message)">
          标记已读
        </button>
        <button
          v-if="message.related_type === 'trade'"
          class="action-button primary"
          @click="goTrade(message)"
        >
          查看交易
        </button>
      </view>
    </view>
  </view>
</template>

<script>
import { getMessages, markAllMessagesRead, markMessageRead } from '../../api'
import { getAuthToken } from '../../utils/auth'

const readOptions = [
  { value: '', label: '全部消息' },
  { value: 'false', label: '未读消息' },
  { value: 'true', label: '已读消息' },
]

export default {
  data() {
    return {
      loading: false,
      messages: [],
      unreadCount: 0,
      filters: {
        page: 1,
        page_size: 50,
        read: '',
      },
    }
  },
  computed: {
    readNames() {
      return readOptions.map((item) => item.label)
    },
    readIndex() {
      return Math.max(0, readOptions.findIndex((item) => item.value === this.filters.read))
    },
    selectedReadName() {
      return readOptions[this.readIndex]?.label || '全部消息'
    },
  },
  onLoad() {
    if (!getAuthToken()) {
      uni.redirectTo({ url: '/pages/auth/login' })
      return
    }
    this.fetchMessages()
  },
  onPullDownRefresh() {
    this.fetchMessages().finally(() => uni.stopPullDownRefresh())
  },
  methods: {
    async fetchMessages() {
      this.loading = true
      try {
        const data = await getMessages(this.filters)
        this.messages = data.items
        this.unreadCount = data.unread_count
      } finally {
        this.loading = false
      }
    },
    onReadChange(event) {
      const index = Number(event.detail.value)
      this.filters.read = readOptions[index]?.value || ''
      this.fetchMessages()
    },
    async readOne(message) {
      if (message.is_read) return
      await markMessageRead(message.id)
      await this.fetchMessages()
    },
    async readAll() {
      await markAllMessagesRead()
      uni.showToast({ title: '已全部标记', icon: 'success' })
      await this.fetchMessages()
    },
    async goTrade(message) {
      if (!message.is_read) {
        await markMessageRead(message.id)
      }
      const sellTitles = ['收到新的购买请求', '交易请求已取消']
      uni.navigateTo({
        url: sellTitles.includes(message.title) ? '/pages/trades/sell' : '/pages/trades/buy',
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

.subtitle {
  margin-top: 8rpx;
  color: #66736e;
  font-size: 27rpx;
}

.nav-button {
  margin-top: 22rpx;
  border-radius: 18rpx;
  background: #173f36;
  color: #fff;
  font-size: 28rpx;
}

.select {
  height: 74rpx;
  box-sizing: border-box;
  margin-bottom: 22rpx;
  padding: 0 20rpx;
  border: 1rpx solid #dbe3df;
  border-radius: 16rpx;
  background: #fff;
  color: #43504b;
  font-size: 26rpx;
  line-height: 74rpx;
}

.empty {
  padding: 100rpx 0;
  color: #75817c;
  font-size: 28rpx;
  text-align: center;
}

.message-card {
  margin-bottom: 18rpx;
  padding: 22rpx;
  border: 1rpx solid #e3e9e6;
  border-radius: 22rpx;
  background: #fff;
}

.message-card.unread {
  border-color: #afd8cc;
}

.message-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18rpx;
}

.message-title {
  flex: 1;
  min-width: 0;
  font-size: 31rpx;
  font-weight: 700;
  line-height: 1.35;
}

.read-dot {
  width: 18rpx;
  height: 18rpx;
  border-radius: 50%;
  background: #d9e0dc;
}

.read-dot.active {
  background: #25715f;
}

.message-content,
.message-time {
  display: block;
  margin-top: 10rpx;
  color: #66736e;
  font-size: 25rpx;
  line-height: 1.5;
}

.message-time {
  color: #8b9692;
  font-size: 22rpx;
}

.actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14rpx;
  margin-top: 18rpx;
}

.action-button {
  border-radius: 16rpx;
  background: #eef4f1;
  color: #24594e;
  font-size: 25rpx;
}

.action-button.primary {
  background: #173f36;
  color: #fff;
}
</style>
