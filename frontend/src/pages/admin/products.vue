<template>
  <view class="page">
    <view class="header">
      <text class="eyebrow">ADMIN</text>
      <text class="title">商品治理</text>
    </view>

    <view class="search-row">
      <input v-model="filters.keyword" class="search-input" placeholder="搜索商品标题或描述" />
      <button class="search-button" :disabled="loading" @click="fetchProducts">搜索</button>
    </view>

    <picker :range="statusNames" :value="statusIndex" @change="onStatusChange">
      <view class="select">{{ selectedStatusName }}</view>
    </picker>

    <view v-if="loading && products.length === 0" class="empty">正在加载商品</view>
    <view v-else-if="products.length === 0" class="empty">暂无商品</view>

    <view v-for="product in products" :key="product.id" class="product-card">
      <view class="product-main" @click="goDetail(product.id)">
        <image
          v-if="product.images && product.images.length"
          class="product-image"
          mode="aspectFill"
          :src="assetUrl(product.images[0])"
        />
        <view v-else class="image-placeholder">
          <text>校</text>
        </view>
        <view class="product-copy">
          <text class="product-title">{{ product.title }}</text>
          <text class="product-meta">
            {{ product.owner?.nickname || product.owner?.username || '匿名用户' }} · {{ product.category_name }}
          </text>
          <view class="product-bottom">
            <text :class="['status', `status-${product.status}`]">{{ statusLabel(product.status) }}</text>
            <text class="price">{{ formatPrice(product.price_cents) }}</text>
          </view>
        </view>
      </view>

      <view class="actions">
        <button
          v-if="product.status !== 'available'"
          class="action-button"
          :disabled="updatingId === product.id"
          @click="setStatus(product, 'available')"
        >
          上架
        </button>
        <button
          v-if="product.status !== 'off_shelf'"
          class="action-button"
          :disabled="updatingId === product.id"
          @click="setStatus(product, 'off_shelf')"
        >
          下架
        </button>
        <button
          v-if="product.status !== 'sold'"
          class="action-button"
          :disabled="updatingId === product.id"
          @click="setStatus(product, 'sold')"
        >
          已售
        </button>
        <button
          class="action-button danger"
          :disabled="updatingId === product.id"
          @click="removeProduct(product)"
        >
          删除
        </button>
      </view>
    </view>
  </view>
</template>

<script>
import { deleteAdminProduct, getAdminProducts, updateAdminProductStatus } from '../../api'
import { getAuthToken, getStoredUser } from '../../utils/auth'
import { assetUrl, formatPrice, statusLabel, statusOptions } from '../../utils/product'

export default {
  data() {
    return {
      loading: false,
      updatingId: '',
      products: [],
      filters: {
        page: 1,
        page_size: 50,
        keyword: '',
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
    if (!this.ensureAdmin()) return
    this.fetchProducts()
  },
  onPullDownRefresh() {
    this.fetchProducts().finally(() => uni.stopPullDownRefresh())
  },
  methods: {
    assetUrl,
    formatPrice,
    statusLabel,
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
    async fetchProducts() {
      this.loading = true
      try {
        const data = await getAdminProducts(this.filters)
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
    goDetail(id) {
      uni.navigateTo({ url: `/pages/products/detail?id=${id}` })
    },
    setStatus(product, status) {
      const labels = { available: '上架', off_shelf: '下架', sold: '标记已售' }
      uni.showModal({
        title: `确认${labels[status]}？`,
        success: async (result) => {
          if (!result.confirm) return
          this.updatingId = product.id
          try {
            await updateAdminProductStatus(product.id, { status })
            uni.showToast({ title: '已更新', icon: 'success' })
            await this.fetchProducts()
          } finally {
            this.updatingId = ''
          }
        },
      })
    },
    removeProduct(product) {
      uni.showModal({
        title: '确认删除商品？',
        content: product.title,
        success: async (result) => {
          if (!result.confirm) return
          this.updatingId = product.id
          try {
            await deleteAdminProduct(product.id)
            uni.showToast({ title: '已删除', icon: 'success' })
            await this.fetchProducts()
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
.product-main,
.product-bottom {
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

.product-copy {
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

.product-bottom {
  justify-content: space-between;
  gap: 16rpx;
  margin-top: 12rpx;
}

.status {
  padding: 8rpx 14rpx;
  border-radius: 999rpx;
  background: #ddf5eb;
  color: #25715f;
  font-size: 22rpx;
}

.status-off_shelf {
  background: #f0f2f1;
  color: #69746f;
}

.status-sold {
  background: #e4f0fd;
  color: #356c9e;
}

.price {
  color: #b6533d;
  font-size: 30rpx;
  font-weight: 700;
}

.actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12rpx;
  margin-top: 18rpx;
}

.action-button {
  min-width: 0;
  border-radius: 16rpx;
  background: #eef4f1;
  color: #24594e;
  font-size: 24rpx;
}

.action-button.danger {
  background: #f1e2df;
  color: #a74740;
}
</style>
