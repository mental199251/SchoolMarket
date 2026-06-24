<template>
  <view class="page info-page">
    <view class="info-hero">
      <text class="info-eyebrow">校淘服务</text>
      <text class="info-title">{{ current.title }}</text>
      <text class="info-subtitle">{{ current.subtitle }}</text>
    </view>

    <view v-if="pageType === 'free'" class="free-panel">
      <view class="intro-block">
        <text class="block-title">学长学姐的好物接力</text>
        <text class="block-text">
          免费送专区用于发布往届学长学姐不再使用、但仍然适合继续使用的物品。比如教材、文具、收纳用品和生活小物，可以免费送给有需要的学弟学妹。
        </text>
      </view>
      <view class="goods-empty">
        <text class="empty-icon">0</text>
        <text class="empty-title">免费送列表暂未开放</text>
        <text class="empty-text">后续这里会像商品列表一样展示免费领取物品，现在先保留入口和说明。</text>
      </view>
    </view>

    <view v-else-if="pageType === 'announcements'" class="announcement-list">
      <view v-if="loading" class="empty">正在加载公告</view>
      <view v-else-if="announcements.length === 0" class="empty">暂无公告</view>
      <view
        v-for="item in announcements"
        :key="item.id"
        class="notice-card"
      >
        <text class="notice-title">{{ item.title }}</text>
        <text class="notice-content">{{ item.content || '暂无内容' }}</text>
        <text class="notice-time">{{ item.created_at || '' }}</text>
      </view>
    </view>

    <view v-else-if="pageType === 'service'" class="service-list">
      <view class="info-card">
        <text class="block-title">商品售后说明</text>
        <text class="block-text">平台主要提供校园二手信息撮合服务，商品成色、配件和交易方式建议买卖双方线下当面确认。</text>
        <text class="block-text">如果遇到商品信息不实、交易纠纷或账号异常，可以联系校淘客服协助记录和处理。</text>
      </view>
      <view class="contact-card">
        <text class="block-title">联系方式</text>
        <text class="contact-line">客服微信：schoolmarket_service</text>
        <text class="contact-line">客服邮箱：support@schoolmarket.example</text>
        <text class="contact-line">服务时间：工作日 9:00-18:00</text>
      </view>
    </view>

    <view v-else class="cooperation-list">
      <view class="info-card">
        <text class="block-title">合作咨询</text>
        <text class="block-text">欢迎校园二手商家、社团组织和校内服务平台与校淘空间合作，共同建设更可靠、更方便的校园闲置流转服务。</text>
        <text class="block-text">可合作方向包括二手商品供给、线下回收活动、校园公益赠送、毕业季闲置处理和平台联合运营。</text>
      </view>
      <view class="contact-card">
        <text class="block-title">具体事宜联系</text>
        <text class="contact-line">合作微信：schoolmarket_business</text>
        <text class="contact-line">合作邮箱：business@schoolmarket.example</text>
        <text class="contact-line">请备注：合作咨询 + 单位/姓名</text>
      </view>
    </view>
  </view>
</template>

<script>
import { getAnnouncements } from '../../api'
import { clearAuthStorage, hasValidAuth } from '../../utils/auth'

const pageConfig = {
  free: {
    title: '免费送',
    subtitle: '把不用的闲置留给下一届有需要的同学。',
  },
  announcements: {
    title: '校淘公告',
    subtitle: '平台通知、交易提醒和重要说明集中展示。',
  },
  service: {
    title: '客服售后',
    subtitle: '交易问题、商品售后和平台使用问题都可以在这里找到联系方式。',
  },
  cooperation: {
    title: '合作咨询',
    subtitle: '欢迎二手商家、社团组织和平台服务方与校淘空间建立合作。',
  },
}

export default {
  data() {
    return {
      pageType: 'free',
      loading: false,
      announcements: [],
    }
  },
  computed: {
    current() {
      return pageConfig[this.pageType] || pageConfig.free
    },
  },
  onLoad(options = {}) {
    if (!hasValidAuth()) {
      clearAuthStorage()
      uni.redirectTo({ url: '/pages/auth/login' })
      return
    }
    this.pageType = pageConfig[options.type] ? options.type : 'free'
    uni.setNavigationBarTitle({ title: this.current.title })
    if (this.pageType === 'announcements') {
      this.loadAnnouncements()
    }
  },
  methods: {
    async loadAnnouncements() {
      this.loading = true
      try {
        const data = await getAnnouncements({ page: 1, page_size: 20 })
        this.announcements = data.items
      } catch (_error) {
        this.announcements = []
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style>
.info-page.page {
  max-width: 980px !important;
  padding: 28rpx 24rpx 64rpx !important;
  background: #f7f7f7 !important;
  animation: none !important;
}

.info-hero {
  padding: 34rpx 30rpx;
  border-radius: 24rpx;
  background: linear-gradient(135deg, #ff5a1f, #ff9d39);
  box-shadow: 0 16rpx 30rpx rgba(255, 90, 31, 0.2);
}

.info-eyebrow {
  display: inline-flex;
  padding: 7rpx 16rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  font-size: 22rpx;
  font-weight: 900;
}

.info-title {
  display: block;
  margin-top: 18rpx;
  color: #fff;
  font-size: 50rpx;
  font-weight: 950;
  line-height: 1.1;
}

.info-subtitle {
  display: block;
  margin-top: 14rpx;
  color: rgba(255, 255, 255, 0.9);
  font-size: 27rpx;
  line-height: 1.5;
}

.free-panel,
.announcement-list,
.service-list,
.cooperation-list {
  margin-top: 24rpx;
}

.intro-block,
.info-card,
.contact-card,
.notice-card,
.goods-empty {
  margin-bottom: 20rpx;
  padding: 26rpx;
  border-radius: 18rpx;
  background: #fff;
  box-shadow: 0 8rpx 20rpx rgba(31, 38, 35, 0.07);
}

.block-title,
.notice-title {
  display: block;
  color: #202825;
  font-size: 32rpx;
  font-weight: 950;
  line-height: 1.3;
}

.block-text,
.notice-content,
.contact-line {
  display: block;
  margin-top: 14rpx;
  color: #606966;
  font-size: 27rpx;
  line-height: 1.62;
}

.notice-time {
  display: block;
  margin-top: 16rpx;
  color: #a0a6a3;
  font-size: 22rpx;
}

.goods-empty {
  display: flex;
  align-items: center;
  min-height: 360rpx;
  flex-direction: column;
  justify-content: center;
  text-align: center;
}

.empty-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 104rpx;
  height: 104rpx;
  border-radius: 26rpx;
  background: linear-gradient(135deg, #ff5a1f, #ffb131);
  color: #fff;
  font-size: 52rpx;
  font-weight: 950;
}

.empty-title {
  margin-top: 24rpx;
  color: #202825;
  font-size: 32rpx;
  font-weight: 950;
}

.empty-text,
.empty {
  margin-top: 12rpx;
  color: #7a827e;
  font-size: 26rpx;
  line-height: 1.5;
  text-align: center;
}

.empty {
  padding: 80rpx 0;
}

.contact-card {
  background: #fff8f3;
}

.contact-line {
  color: #d95520;
  font-weight: 800;
}
</style>
