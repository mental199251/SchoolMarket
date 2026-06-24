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
        <button
          v-if="product.status === 'available'"
          class="secondary-button"
          :loading="productAction === 'off_shelf'"
          :disabled="Boolean(productAction)"
          @click="changeStatus('off_shelf')"
        >
          下架商品
        </button>
        <button
          v-if="product.status === 'off_shelf'"
          class="secondary-button"
          :loading="productAction === 'restore'"
          :disabled="Boolean(productAction)"
          @click="changeStatus('restore')"
        >
          恢复上架
        </button>
        <button
          class="danger-button"
          :loading="productAction === 'delete'"
          :disabled="Boolean(productAction)"
          @click="confirmDelete"
        >
          删除商品
        </button>
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
      productAction: '',
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
      if (this.productAction) return
      const title = action === 'off_shelf' ? '确认下架该商品？' : '确认恢复上架？'
      uni.showModal({
        title,
        success: async (result) => {
          if (!result.confirm) return
          this.productAction = action
          try {
            this.product = await updateProductStatus(this.product.id, { action })
            uni.showToast({ title: '状态已更新', icon: 'success' })
          } finally {
            this.productAction = ''
          }
        },
      })
    },
    confirmDelete() {
      if (this.productAction) return
      uni.showModal({
        title: '确认删除该商品？',
        content: '删除后不会再出现在商品列表中。',
        success: async (result) => {
          if (!result.confirm) return
          this.productAction = 'delete'
          try {
            await deleteProduct(this.product.id)
            uni.showToast({ title: '已删除', icon: 'success' })
            uni.navigateBack()
          } finally {
            this.productAction = ''
          }
        },
      })
    },
  },
}
</script>

<style>
.image-swiper,
.hero-placeholder {
  position: relative;
  overflow: hidden;
  width: 100%;
  height: 560rpx;
  margin-bottom: 28rpx;
  border-radius: 48rpx !important;
}

.image-swiper {
  box-shadow: 0 30rpx 70rpx rgba(52, 115, 101, 0.18);
}

.hero-image {
  width: 100%;
  height: 100%;
}

.hero-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 68rpx;
  font-weight: 950;
}

.title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24rpx;
  margin-top: 8rpx;
  padding: 28rpx;
  border: 2rpx solid rgba(255, 255, 255, 0.78);
  border-radius: 38rpx;
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 20rpx 42rpx rgba(77, 130, 120, 0.12);
}

.title-row .title {
  flex: 1;
  font-size: 42rpx !important;
  line-height: 1.28 !important;
}

.title-row .price {
  flex-shrink: 0;
  font-size: 40rpx;
  line-height: 1.2;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 14rpx;
  margin: 22rpx 0 4rpx;
}

.seller-row {
  display: flex;
  align-items: center;
  margin-top: 24rpx !important;
}

.avatar {
  width: 90rpx;
  height: 90rpx;
  margin-right: 22rpx;
  flex-shrink: 0;
  font-size: 34rpx;
}

.seller-main,
.section {
  display: flex;
  flex-direction: column;
}

.section {
  margin-top: 24rpx !important;
}

.section-title {
  margin-bottom: 14rpx;
}

.description {
  white-space: pre-wrap;
}

.owner-actions,
.buyer-actions {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16rpx;
  margin-top: 26rpx;
  padding: 26rpx;
  border: 2rpx solid rgba(255, 255, 255, 0.8);
  border-radius: 34rpx;
  background: rgba(255, 255, 255, 0.76);
  box-shadow: 0 22rpx 52rpx rgba(77, 130, 120, 0.12);
}

.owner-actions button,
.buyer-actions button {
  margin-top: 0 !important;
}

@media screen and (min-width: 760px) {
  .image-swiper,
  .hero-placeholder {
    height: 660rpx;
  }

  .owner-actions,
  .buyer-actions {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
