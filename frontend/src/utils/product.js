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

export const tradeStatusOptions = [
  { value: '', label: '全部状态' },
  { value: 'pending', label: '待处理' },
  { value: 'confirmed', label: '已确认' },
  { value: 'cancelled', label: '已取消' },
  { value: 'completed', label: '已完成' },
]

export const tradeStatusLabel = (value) => {
  return tradeStatusOptions.find((item) => item.value === value)?.label || '未知状态'
}

export const userStatusOptions = [
  { value: '', label: '全部状态' },
  { value: 'active', label: '正常' },
  { value: 'disabled', label: '已禁用' },
]

export const roleOptions = [
  { value: '', label: '全部角色' },
  { value: 'user', label: '普通用户' },
  { value: 'admin', label: '管理员' },
]

export const announcementStatusOptions = [
  { value: '', label: '全部状态' },
  { value: 'published', label: '已发布' },
  { value: 'hidden', label: '已隐藏' },
]

export const userStatusLabel = (value) => {
  return userStatusOptions.find((item) => item.value === value)?.label || '未知状态'
}

export const roleLabel = (value) => {
  return roleOptions.find((item) => item.value === value)?.label || '未知角色'
}

export const announcementStatusLabel = (value) => {
  return announcementStatusOptions.find((item) => item.value === value)?.label || '未知状态'
}

export const logActionLabel = (value) => {
  const labels = {
    user_status_update: '用户状态更新',
    product_status_update: '商品状态更新',
    product_delete: '商品删除',
    announcement_create: '公告创建',
    announcement_update: '公告更新',
    announcement_delete: '公告隐藏',
  }
  return labels[value] || value || '未知操作'
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
