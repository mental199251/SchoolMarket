<template>
  <view class="page">
    <view class="header">
      <text class="eyebrow">SELLER</text>
      <text class="title">我的商品</text>
      <button class="publish-button" @click="goPublish">发布商品</button>
    </view>

    <picker :range="statusNames" :value="statusIndex" @change="onStatusChange">
      <view class="select">{{ selectedStatusName }}</view>
    </picker>

    <view v-if="loading && products.length === 0" class="empty">正在加载商品</view>
    <view v-else-if="products.length === 0" class="empty">还没有商品</view>

    <view v-for="product in products" :key="product.id" class="product-card">
      <view class="card-row" @click="goDetail(product.id)">
        <image
          v-if="product.images && product.images.length"
          class="product-image"
          mode="aspectFill"
          :src="assetUrl(product.images[0])"
        />
        <view v-else class="image-placeholder">
          <text>校</text>
        </view>
        <view class="product-main">
          <text class="product-title">{{ product.title }}</text>
          <text class="product-meta">{{ product.category_name }} · {{ conditionLabel(product.condition) }}</text>
          <view class="product-bottom">
            <text :class="['status', `status-${product.status}`]">{{ statusLabel(product.status) }}</text>
            <text class="price">{{ formatPrice(product.price_cents) }}</text>
          </view>
        </view>
      </view>
      <view class="card-actions">
        <view class="action-button" @click.stop="goEdit(product.id)">编辑</view>
        <view
          v-if="product.status === 'available'"
          class="action-button"
          @click.stop="changeStatus(product, 'off_shelf')"
        >
          下架
        </view>
        <view
          v-if="product.status === 'off_shelf'"
          class="action-button"
          @click.stop="changeStatus(product, 'restore')"
        >
          上架
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { getProducts, updateProductStatus } from '../../api'
import { getAuthToken } from '../../utils/auth'
import {
  assetUrl,
  conditionLabel,
  formatPrice,
  statusLabel,
  statusOptions,
} from '../../utils/product'

export default {
  data() {
    return {
      loading: false,
      products: [],
      filters: {
        mine: true,
        page: 1,
        page_size: 50,
        status: '',
      },
    }
  },
  computed: {
    statusNames() {
      return statusOptions.map((item) => item.label)
    },
    statusIndex() {
      return Math.max(0, statusOptions.findIndex((item) => item.value === this.filters.status))
    },
    selectedStatusName() {
      return statusOptions[this.statusIndex]?.label || '全部状态'
    },
  },
  onLoad() {
    if (!getAuthToken()) {
      uni.redirectTo({ url: '/pages/auth/login' })
      return
    }
    this.fetchProducts()
  },
  onPullDownRefresh() {
    this.fetchProducts().finally(() => uni.stopPullDownRefresh())
  },
  methods: {
    assetUrl,
    conditionLabel,
    formatPrice,
    statusLabel,
    async fetchProducts() {
      this.loading = true
      try {
        const data = await getProducts(this.filters)
        this.products = data.items
      } finally {
        this.loading = false
      }
    },
    onStatusChange(event) {
      const index = Number(event.detail.value)
      this.filters.status = statusOptions[index]?.value || ''
      this.fetchProducts()
    },
    goPublish() {
      uni.navigateTo({ url: '/pages/products/form' })
    },
    goDetail(id) {
      uni.navigateTo({ url: `/pages/products/detail?id=${id}` })
    },
    goEdit(id) {
      uni.navigateTo({ url: `/pages/products/form?id=${id}` })
    },
    changeStatus(product, action) {
      uni.showModal({
        title: action === 'off_shelf' ? '确认下架？' : '确认上架？',
        success: async (result) => {
          if (!result.confirm) return
          await updateProductStatus(product.id, { action })
          uni.showToast({ title: '状态已更新', icon: 'success' })
          this.fetchProducts()
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

.publish-button {
  margin-top: 24rpx;
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

.product-card {
  margin-bottom: 18rpx;
  padding: 20rpx;
  border: 1rpx solid #e3e9e6;
  border-radius: 22rpx;
  background: #fff;
}

.card-row {
  display: flex;
  align-items: center;
}

.product-image,
.image-placeholder {
  width: 132rpx;
  height: 132rpx;
  margin-right: 18rpx;
  border-radius: 18rpx;
}

.image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ddf5eb;
  color: #25715f;
  font-size: 42rpx;
  font-weight: 700;
}

.product-main {
  display: flex;
  flex: 1;
  min-width: 0;
  flex-direction: column;
}

.product-title {
  font-size: 30rpx;
  font-weight: 700;
  line-height: 1.35;
}

.product-meta {
  margin-top: 8rpx;
  color: #75817c;
  font-size: 24rpx;
}

.status {
  padding: 8rpx 14rpx;
  border-radius: 999rpx;
  background: #ddf5eb;
  color: #25715f;
  font-size: 22rpx;
}

.status-off_shelf {
  background: #fff3d9;
  color: #94651e;
}

.status-sold {
  background: #fde6e3;
  color: #a74740;
}

.product-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
  margin-top: 12rpx;
}

.price {
  color: #b6533d;
  font-size: 30rpx;
  font-weight: 700;
  white-space: nowrap;
}

.card-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14rpx;
  margin-top: 18rpx;
}

.action-button {
  height: 64rpx;
  border-radius: 16rpx;
  background: #eef4f1;
  color: #24594e;
  font-size: 25rpx;
  font-weight: 600;
  line-height: 64rpx;
  text-align: center;
}
</style>
