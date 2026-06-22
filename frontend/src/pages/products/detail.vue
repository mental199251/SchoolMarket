<template>
  <view class="page">
    <view v-if="loading" class="empty">正在加载商品</view>

    <view v-else-if="product.id">
      <swiper v-if="product.images && product.images.length" class="image-swiper" circular>
        <swiper-item v-for="image in product.images" :key="image">
          <image class="hero-image" mode="aspectFill" :src="assetUrl(image)" />
        </swiper-item>
      </swiper>
      <view v-else class="hero-placeholder">
        <text>校淘</text>
      </view>

      <view class="title-row">
        <text class="title">{{ product.title }}</text>
        <text class="price">{{ formatPrice(product.price_cents) }}</text>
      </view>

      <view class="tag-row">
        <text class="tag">{{ product.category_name }}</text>
        <text class="tag">{{ conditionLabel(product.condition) }}</text>
        <text :class="['tag', `status-${product.status}`]">{{ statusLabel(product.status) }}</text>
      </view>

      <view class="seller-row">
        <view class="avatar">
          <text>{{ sellerInitial }}</text>
        </view>
        <view class="seller-main">
          <text class="seller-name">{{ product.owner?.nickname || product.owner?.username || '匿名用户' }}</text>
          <text class="seller-campus">{{ product.owner?.campus || '校区未填写' }}</text>
        </view>
      </view>

      <view class="section">
        <text class="section-title">商品描述</text>
        <text class="description">{{ product.description || '卖家暂未填写描述。' }}</text>
      </view>

      <view v-if="isOwner" class="owner-actions">
        <button class="primary-button" @click="goEdit">编辑商品</button>
        <button class="secondary-button" @click="goSellTrades">收到的请求</button>
        <button v-if="product.status === 'available'" class="secondary-button" @click="changeStatus('off_shelf')">
          下架商品
        </button>
        <button v-if="product.status === 'off_shelf'" class="secondary-button" @click="changeStatus('restore')">
          恢复上架
        </button>
        <button class="danger-button" @click="confirmDelete">删除商品</button>
      </view>

      <view v-else class="buyer-actions">
        <button
          v-if="product.status === 'available'"
          class="primary-button"
          :loading="submittingTrade"
          :disabled="submittingTrade"
          @click="requestTrade"
        >
          发起购买
        </button>
        <button class="secondary-button" @click="goBuyTrades">我的购买</button>
      </view>
    </view>
  </view>
</template>

<script>
import { createTrade, deleteProduct, getProduct, updateProductStatus } from '../../api'
import { getAuthToken, getStoredUser } from '../../utils/auth'
import {
  assetUrl,
  conditionLabel,
  formatPrice,
  statusLabel,
} from '../../utils/product'

export default {
  data() {
    return {
      id: '',
      loading: true,
      submittingTrade: false,
      product: {},
      currentUser: null,
    }
  },
  computed: {
    isOwner() {
      return this.currentUser && this.product.owner_id === this.currentUser.id
    },
    sellerInitial() {
      const name = this.product.owner?.nickname || this.product.owner?.username || '校'
      return name.slice(0, 1).toUpperCase()
    },
  },
  onLoad(options) {
    this.id = options.id
    this.currentUser = getStoredUser()
    this.loadProduct()
  },
  methods: {
    assetUrl,
    conditionLabel,
    formatPrice,
    statusLabel,
    async loadProduct() {
      this.loading = true
      try {
        this.product = await getProduct(this.id)
      } finally {
        this.loading = false
      }
    },
    goEdit() {
      uni.navigateTo({ url: `/pages/products/form?id=${this.product.id}` })
    },
    goBuyTrades() {
      uni.navigateTo({ url: '/pages/trades/buy' })
    },
    goSellTrades() {
      uni.navigateTo({ url: '/pages/trades/sell' })
    },
    requestTrade() {
      if (!getAuthToken()) {
        uni.navigateTo({ url: '/pages/auth/login' })
        return
      }
      uni.showModal({
        title: '确认发起购买？',
        content: '卖家确认后，双方线下完成交易。',
        success: async (result) => {
          if (!result.confirm) return
          this.submittingTrade = true
          try {
            await createTrade({ product_id: this.product.id })
            uni.showToast({ title: '请求已发送', icon: 'success' })
            uni.navigateTo({ url: '/pages/trades/buy' })
          } finally {
            this.submittingTrade = false
          }
        },
      })
    },
    changeStatus(action) {
      const title = action === 'off_shelf' ? '确认下架该商品？' : '确认恢复上架？'
      uni.showModal({
        title,
        success: async (result) => {
          if (!result.confirm) return
          this.product = await updateProductStatus(this.product.id, { action })
          uni.showToast({ title: '状态已更新', icon: 'success' })
        },
      })
    },
    confirmDelete() {
      uni.showModal({
        title: '确认删除该商品？',
        content: '删除后不会再出现在商品列表中。',
        success: async (result) => {
          if (!result.confirm) return
          await deleteProduct(this.product.id)
          uni.showToast({ title: '已删除', icon: 'success' })
          uni.navigateBack()
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
  padding: 28rpx 28rpx 64rpx;
  color: #17221e;
}

.empty {
  padding: 120rpx 0;
  color: #75817c;
  font-size: 28rpx;
  text-align: center;
}

.image-swiper,
.hero-placeholder {
  width: 100%;
  height: 520rpx;
  border-radius: 24rpx;
  overflow: hidden;
}

.hero-image {
  width: 100%;
  height: 100%;
}

.hero-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ddf5eb;
  color: #25715f;
  font-size: 58rpx;
  font-weight: 700;
}

.title-row {
  display: flex;
  justify-content: space-between;
  gap: 24rpx;
  margin-top: 30rpx;
}

.title {
  flex: 1;
  font-size: 42rpx;
  font-weight: 700;
  line-height: 1.35;
}

.price {
  color: #b6533d;
  font-size: 40rpx;
  font-weight: 700;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 14rpx;
  margin-top: 20rpx;
}

.tag {
  padding: 10rpx 16rpx;
  border-radius: 999rpx;
  background: #fff;
  color: #43504b;
  font-size: 23rpx;
}

.status-off_shelf {
  background: #fff3d9;
  color: #94651e;
}

.status-sold {
  background: #fde6e3;
  color: #a74740;
}

.seller-row,
.section,
.owner-actions,
.buyer-actions {
  margin-top: 26rpx;
  padding: 28rpx;
  border: 1rpx solid #e3e9e6;
  border-radius: 22rpx;
  background: #fff;
}

.seller-row {
  display: flex;
  align-items: center;
}

.avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 82rpx;
  height: 82rpx;
  margin-right: 22rpx;
  border-radius: 24rpx;
  background: #173f36;
  color: #fff;
  font-size: 34rpx;
  font-weight: 700;
}

.seller-main,
.section {
  display: flex;
  flex-direction: column;
}

.seller-name {
  font-size: 30rpx;
  font-weight: 700;
}

.seller-campus {
  margin-top: 6rpx;
  color: #75817c;
  font-size: 24rpx;
}

.section-title {
  margin-bottom: 14rpx;
  font-size: 28rpx;
  font-weight: 700;
}

.description {
  color: #43504b;
  font-size: 27rpx;
  line-height: 1.65;
  white-space: pre-wrap;
}

.primary-button,
.secondary-button,
.danger-button {
  margin-top: 18rpx;
  border-radius: 18rpx;
  font-size: 28rpx;
}

.primary-button {
  margin-top: 0;
  background: #173f36;
  color: #fff;
}

.secondary-button {
  background: #eef4f1;
  color: #24594e;
}

.danger-button {
  background: #fff;
  color: #a74740;
}
</style>
