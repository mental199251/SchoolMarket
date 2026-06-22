<template>
  <view class="page">
    <view class="header">
      <text class="title">{{ isEdit ? '编辑商品' : '发布商品' }}</text>
    </view>

    <view class="form-card">
      <text class="label">标题</text>
      <input v-model="form.title" class="input" placeholder="例如：高等数学教材" />

      <text class="label">价格</text>
      <input v-model="priceText" class="input" type="digit" placeholder="例如：28.00" />

      <text class="label">分类</text>
      <picker :range="categoryNames" :value="categoryIndex" @change="onCategoryChange">
        <view class="select">{{ selectedCategoryName }}</view>
      </picker>

      <text class="label">成色</text>
      <picker :range="formConditionNames" :value="conditionIndex" @change="onConditionChange">
        <view class="select">{{ selectedConditionName }}</view>
      </picker>

      <text class="label">描述</text>
      <textarea
        v-model="form.description"
        class="textarea"
        placeholder="补充型号、使用情况、交付地点等信息"
      />

      <view class="image-header">
        <text class="label inline">图片</text>
        <button class="small-button" :loading="uploading" :disabled="uploading" @click="chooseImages">
          上传
        </button>
      </view>

      <view class="image-grid">
        <view v-for="image in form.images" :key="image" class="image-item">
          <image class="preview" mode="aspectFill" :src="assetUrl(image)" />
          <button class="remove-button" @click="removeImage(image)">移除</button>
        </view>
        <view v-if="form.images.length === 0" class="image-empty">暂未上传图片</view>
      </view>

      <button class="primary-button" :loading="submitting" :disabled="submitting" @click="submit">
        {{ isEdit ? '保存商品' : '发布商品' }}
      </button>
    </view>
  </view>
</template>

<script>
import {
  createProduct,
  getCategories,
  getProduct,
  updateProduct,
  uploadProductImage,
} from '../../api'
import { getAuthToken } from '../../utils/auth'
import { assetUrl, conditionOptions } from '../../utils/product'

const formConditions = conditionOptions.filter((item) => item.value)

export default {
  data() {
    return {
      id: '',
      uploading: false,
      submitting: false,
      categories: [],
      priceText: '',
      form: {
        title: '',
        description: '',
        category_key: '',
        condition: 'good',
        images: [],
      },
    }
  },
  computed: {
    isEdit() {
      return Boolean(this.id)
    },
    categoryNames() {
      return this.categories.map((item) => item.name)
    },
    categoryIndex() {
      const index = this.categories.findIndex((item) => item.key === this.form.category_key)
      return Math.max(0, index)
    },
    selectedCategoryName() {
      return this.categories[this.categoryIndex]?.name || '请选择分类'
    },
    formConditionNames() {
      return formConditions.map((item) => item.label)
    },
    conditionIndex() {
      const index = formConditions.findIndex((item) => item.value === this.form.condition)
      return Math.max(0, index)
    },
    selectedConditionName() {
      return formConditions[this.conditionIndex]?.label || '轻微使用'
    },
  },
  async onLoad(options) {
    if (!getAuthToken()) {
      uni.redirectTo({ url: '/pages/auth/login' })
      return
    }

    this.id = options.id || ''
    uni.setNavigationBarTitle({ title: this.isEdit ? '编辑商品' : '发布商品' })
    await this.loadCategories()
    if (this.isEdit) {
      await this.loadProduct()
    } else if (this.categories.length && !this.form.category_key) {
      this.form.category_key = this.categories[0].key
    }
  },
  methods: {
    assetUrl,
    async loadCategories() {
      const data = await getCategories()
      this.categories = data.items
    },
    async loadProduct() {
      const product = await getProduct(this.id)
      this.form = {
        title: product.title,
        description: product.description || '',
        category_key: product.category_key,
        condition: product.condition,
        images: product.images || [],
      }
      this.priceText = (product.price_cents / 100).toFixed(2)
    },
    onCategoryChange(event) {
      const index = Number(event.detail.value)
      this.form.category_key = this.categories[index]?.key || ''
    },
    onConditionChange(event) {
      const index = Number(event.detail.value)
      this.form.condition = formConditions[index]?.value || 'good'
    },
    chooseImages() {
      const remaining = 9 - this.form.images.length
      if (remaining <= 0) {
        uni.showToast({ title: '最多上传 9 张图片', icon: 'none' })
        return
      }

      uni.chooseImage({
        count: remaining,
        success: async (result) => {
          this.uploading = true
          try {
            for (const filePath of result.tempFilePaths) {
              const data = await uploadProductImage(filePath)
              this.form.images = [...this.form.images, ...data.urls]
            }
          } finally {
            this.uploading = false
          }
        },
      })
    },
    removeImage(image) {
      this.form.images = this.form.images.filter((item) => item !== image)
    },
    buildPayload() {
      const price = Number(this.priceText)
      if (!this.form.title.trim()) {
        throw new Error('请输入商品标题')
      }
      if (!Number.isFinite(price) || price <= 0) {
        throw new Error('请输入有效价格')
      }
      if (!this.form.category_key) {
        throw new Error('请选择分类')
      }

      return {
        ...this.form,
        title: this.form.title.trim(),
        description: this.form.description.trim(),
        price_cents: Math.round(price * 100),
      }
    },
    async submit() {
      let payload
      try {
        payload = this.buildPayload()
      } catch (error) {
        uni.showToast({ title: error.message, icon: 'none' })
        return
      }

      this.submitting = true
      try {
        const product = this.isEdit
          ? await updateProduct(this.id, payload)
          : await createProduct(payload)
        uni.showToast({ title: this.isEdit ? '已保存' : '已发布', icon: 'success' })
        uni.redirectTo({ url: `/pages/products/detail?id=${product.id}` })
      } finally {
        this.submitting = false
      }
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
  padding: 44rpx 28rpx 64rpx;
  color: #17221e;
}

.header {
  margin-bottom: 28rpx;
}

.title {
  font-size: 48rpx;
  font-weight: 700;
  line-height: 1.25;
}

.form-card {
  padding: 28rpx;
  border: 1rpx solid #e3e9e6;
  border-radius: 24rpx;
  background: #fff;
}

.label {
  display: block;
  margin: 24rpx 0 12rpx;
  color: #43504b;
  font-size: 25rpx;
  font-weight: 700;
}

.label:first-child {
  margin-top: 0;
}

.label.inline {
  margin: 0;
}

.input,
.select,
.textarea {
  box-sizing: border-box;
  width: 100%;
  border: 1rpx solid #dbe3df;
  border-radius: 18rpx;
  background: #f8faf9;
  font-size: 28rpx;
}

.input,
.select {
  height: 86rpx;
  padding: 0 22rpx;
  line-height: 86rpx;
}

.textarea {
  min-height: 220rpx;
  padding: 22rpx;
  line-height: 1.5;
}

.image-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 26rpx;
}

.small-button {
  width: 150rpx;
  border-radius: 16rpx;
  background: #eef4f1;
  color: #24594e;
  font-size: 25rpx;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14rpx;
  margin-top: 16rpx;
}

.image-item,
.preview,
.image-empty {
  min-height: 150rpx;
  border-radius: 16rpx;
}

.image-item {
  position: relative;
  overflow: hidden;
}

.preview {
  width: 100%;
  height: 150rpx;
}

.remove-button {
  position: absolute;
  right: 8rpx;
  bottom: 8rpx;
  width: 92rpx;
  height: 42rpx;
  border-radius: 999rpx;
  background: rgba(23, 34, 30, 0.72);
  color: #fff;
  font-size: 20rpx;
  line-height: 42rpx;
}

.image-empty {
  display: flex;
  grid-column: span 3;
  align-items: center;
  justify-content: center;
  border: 1rpx dashed #cfd9d4;
  color: #75817c;
  font-size: 26rpx;
}

.primary-button {
  margin-top: 34rpx;
  border-radius: 18rpx;
  background: #173f36;
  color: #fff;
  font-size: 29rpx;
}
</style>
