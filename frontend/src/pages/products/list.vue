<template>
  <view class="page">
    <view class="header">
      <text class="eyebrow">MARKET</text>
      <text class="title">商品列表</text>
      <view class="header-actions">
        <button class="icon-button" @click="goPublish">发布</button>
        <button class="icon-button ghost" @click="goMyProducts">我的</button>
      </view>
    </view>

    <view class="search-row">
      <input v-model="filters.keyword" class="search-input" placeholder="搜索教材、耳机、球拍" />
      <button class="search-button" :disabled="loading" @click="applyFilters">搜索</button>
    </view>

    <view class="filter-grid">
      <picker :range="categoryNames" :value="categoryIndex" @change="onCategoryChange">
        <view class="select">{{ selectedCategoryName }}</view>
      </picker>
      <picker :range="conditionNames" :value="conditionIndex" @change="onConditionChange">
        <view class="select">{{ selectedConditionName }}</view>
      </picker>
      <picker :range="sortNames" :value="sortIndex" @change="onSortChange">
        <view class="select wide">{{ selectedSortName }}</view>
      </picker>
    </view>

    <view v-if="loading && products.length === 0" class="empty">正在加载商品</view>
    <view v-else-if="products.length === 0" class="empty">暂无符合条件的商品</view>

    <view v-for="product in products" :key="product.id" class="product-card" @click="goDetail(product.id)">
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
        <text class="seller">{{ product.owner?.nickname || product.owner?.username || '匿名用户' }}</text>
      </view>
      <text class="price">{{ formatPrice(product.price_cents) }}</text>
    </view>

    <button
      v-if="hasMore"
      class="load-more"
      :loading="loading"
      :disabled="loading"
      @click="loadMore"
    >
      加载更多
    </button>
  </view>
</template>

<script>
import { getCategories, getProducts } from '../../api'
import {
  assetUrl,
  conditionLabel,
  conditionOptions,
  formatPrice,
  sortOptions,
} from '../../utils/product'

export default {
  data() {
    return {
      loading: false,
      products: [],
      total: 0,
      categories: [{ key: '', name: '全部分类' }],
      filters: {
        page: 1,
        page_size: 10,
        keyword: '',
        category_key: '',
        condition: '',
        sort: 'newest',
      },
    }
  },
  computed: {
    hasMore() {
      return this.products.length < this.total
    },
    categoryNames() {
      return this.categories.map((item) => item.name)
    },
    categoryIndex() {
      return Math.max(0, this.categories.findIndex((item) => item.key === this.filters.category_key))
    },
    selectedCategoryName() {
      return this.categories[this.categoryIndex]?.name || '全部分类'
    },
    conditionNames() {
      return conditionOptions.map((item) => item.label)
    },
    conditionIndex() {
      return Math.max(0, conditionOptions.findIndex((item) => item.value === this.filters.condition))
    },
    selectedConditionName() {
      return conditionOptions[this.conditionIndex]?.label || '全部成色'
    },
    sortNames() {
      return sortOptions.map((item) => item.label)
    },
    sortIndex() {
      return Math.max(0, sortOptions.findIndex((item) => item.value === this.filters.sort))
    },
    selectedSortName() {
      return sortOptions[this.sortIndex]?.label || '最新发布'
    },
  },
  async onLoad() {
    await this.loadCategories()
    await this.fetchProducts(true)
  },
  onPullDownRefresh() {
    this.fetchProducts(true).finally(() => uni.stopPullDownRefresh())
  },
  methods: {
    assetUrl,
    conditionLabel,
    formatPrice,
    async loadCategories() {
      const data = await getCategories()
      this.categories = [{ key: '', name: '全部分类' }, ...data.items]
    },
    async fetchProducts(reset = false) {
      if (reset) {
        this.filters.page = 1
      }
      this.loading = true
      try {
        const data = await getProducts(this.filters)
        this.total = data.total
        this.products = reset ? data.items : [...this.products, ...data.items]
      } finally {
        this.loading = false
      }
    },
    applyFilters() {
      this.fetchProducts(true)
    },
    loadMore() {
      if (this.loading || !this.hasMore) return
      this.filters.page += 1
      this.fetchProducts(false)
    },
    onCategoryChange(event) {
      const index = Number(event.detail.value)
      this.filters.category_key = this.categories[index]?.key || ''
      this.fetchProducts(true)
    },
    onConditionChange(event) {
      const index = Number(event.detail.value)
      this.filters.condition = conditionOptions[index]?.value || ''
      this.fetchProducts(true)
    },
    onSortChange(event) {
      const index = Number(event.detail.value)
      this.filters.sort = sortOptions[index]?.value || 'newest'
      this.fetchProducts(true)
    },
    goDetail(id) {
      uni.navigateTo({ url: `/pages/products/detail?id=${id}` })
    },
    goPublish() {
      uni.navigateTo({ url: '/pages/products/form' })
    },
    goMyProducts() {
      uni.navigateTo({ url: '/pages/products/my' })
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
  margin-bottom: 28rpx;
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

.header-actions,
.search-row,
.filter-grid,
.product-card {
  display: flex;
  align-items: center;
}

.header-actions {
  gap: 16rpx;
  margin-top: 24rpx;
}

.icon-button {
  flex: 1;
  border-radius: 18rpx;
  background: #173f36;
  color: #fff;
  font-size: 28rpx;
}

.icon-button.ghost {
  background: #fff;
  color: #24594e;
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

.select.wide {
  grid-column: span 2;
}

.empty {
  padding: 80rpx 0;
  color: #75817c;
  font-size: 28rpx;
  text-align: center;
}

.product-card {
  position: relative;
  margin-bottom: 18rpx;
  padding: 20rpx;
  border: 1rpx solid #e3e9e6;
  border-radius: 22rpx;
  background: #fff;
}

.product-image,
.image-placeholder {
  width: 140rpx;
  height: 140rpx;
  margin-right: 20rpx;
  border-radius: 18rpx;
}

.image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ddf5eb;
  color: #25715f;
  font-size: 46rpx;
  font-weight: 700;
}

.product-main {
  display: flex;
  flex: 1;
  min-width: 0;
  flex-direction: column;
}

.product-title {
  color: #17221e;
  font-size: 31rpx;
  font-weight: 700;
  line-height: 1.35;
}

.product-meta,
.seller {
  margin-top: 8rpx;
  color: #75817c;
  font-size: 24rpx;
}

.price {
  align-self: flex-start;
  margin-left: 14rpx;
  color: #b6533d;
  font-size: 30rpx;
  font-weight: 700;
}

.load-more {
  margin-top: 20rpx;
  border-radius: 18rpx;
  background: #fff;
  color: #24594e;
  font-size: 28rpx;
}
</style>
