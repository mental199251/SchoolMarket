import { API_BASE_URL } from '../api/config'

export const conditionOptions = [
  { value: '', label: '全部成色' },
  { value: 'new', label: '全新' },
  { value: 'like_new', label: '几乎全新' },
  { value: 'good', label: '轻微使用' },
  { value: 'fair', label: '明显使用' },
]

export const statusOptions = [
  { value: '', label: '全部状态' },
  { value: 'available', label: '可交易' },
  { value: 'off_shelf', label: '已下架' },
  { value: 'sold', label: '已成交' },
]

export const sortOptions = [
  { value: 'newest', label: '最新发布' },
  { value: 'price_asc', label: '价格从低到高' },
  { value: 'price_desc', label: '价格从高到低' },
]

export const conditionLabel = (value) => {
  return conditionOptions.find((item) => item.value === value)?.label || '未知成色'
}

export const statusLabel = (value) => {
  return statusOptions.find((item) => item.value === value)?.label || '未知状态'
}

export const formatPrice = (priceCents) => {
  const cents = Number(priceCents) || 0
  return `¥${(cents / 100).toFixed(2)}`
}

export const assetUrl = (path) => {
  if (!path) return ''
  if (/^https?:\/\//.test(path)) return path
  return `${API_BASE_URL}${path}`
}
