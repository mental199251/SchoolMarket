<template>
  <view class="page">
    <view class="header">
      <text class="eyebrow">MARKET</text>
      <text class="title">发现好物</text>
      <text class="subtitle">从教材到数码配件，校园里的小惊喜都在这里。</text>
      <view class="header-actions">
        <button class="icon-button" @click="goPublish">发布</button>
        <button class="icon-button ghost" @click="goMyProducts">我的</button>
      </view>
    </view>

    <view class="filter-shell">
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
    </view>

    <view v-if="loading && products.length === 0" class="empty">正在加载商品</view>
    <view v-else-if="products.length === 0" class="empty">暂无符合条件的商品</view>

    <view class="product-grid">
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
.header-actions {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16rpx;
  margin-top: 24rpx;
}

.filter-shell {
  margin-bottom: 24rpx;
  padding: 22rpx;
  border: 2rpx solid rgba(255, 255, 255, 0.78);
  border-radius: 34rpx;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 18rpx 42rpx rgba(77, 130, 120, 0.12);
}

.filter-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.select.wide {
  grid-column: span 2;
}

.product-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 18rpx;
}

.product-card {
  display: flex;
  align-items: center;
  min-height: 180rpx;
}

.product-image,
.image-placeholder {
  width: 148rpx;
  height: 148rpx;
  margin-right: 22rpx;
  flex-shrink: 0;
}

.product-main {
  display: flex;
  flex: 1;
  min-width: 0;
  flex-direction: column;
}

.seller {
  margin-top: 8rpx;
}

.price {
  align-self: flex-start;
  margin-left: 16rpx;
  font-size: 31rpx;
}

.load-more {
  width: 100%;
  margin-top: 24rpx;
}

@media screen and (min-width: 760px) {
  .product-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .product-card {
    flex-direction: column;
    align-items: stretch;
  }

  .product-image,
  .image-placeholder {
    width: 100%;
    height: 280rpx;
    margin-right: 0;
    margin-bottom: 18rpx;
  }

  .price {
    margin: 18rpx 0 0;
  }
}
</style>
