import { request, uploadFile } from './http'

export const getHealth = (options = {}) => {
  return request({
    path: '/health',
    showError: false,
    ...options,
  })
}

export const getReadiness = (options = {}) => {
  return request({
    path: '/ready',
    showError: false,
    ...options,
  })
}

export const register = (data) => {
  return request({
    path: '/api/v1/auth/register',
    method: 'POST',
    data,
  })
}

export const login = (data) => {
  return request({
    path: '/api/v1/auth/login',
    method: 'POST',
    data,
  })
}

export const logout = (options = {}) => {
  return request({
    path: '/api/v1/auth/logout',
    method: 'POST',
    ...options,
  })
}

export const changePassword = (data) => {
  return request({
    path: '/api/v1/auth/password',
    method: 'PUT',
    data,
  })
}

export const getMe = (options = {}) => {
  return request({
    path: '/api/v1/users/me',
    ...options,
  })
}

export const updateMe = (data) => {
  return request({
    path: '/api/v1/users/me',
    method: 'PUT',
    data,
  })
}

export const getCategories = () => {
  return request({
    path: '/api/v1/categories',
  })
}

export const getProducts = (data = {}) => {
  return request({
    path: '/api/v1/products',
    data,
  })
}

export const getProduct = (id, options = {}) => {
  return request({
    path: `/api/v1/products/${id}`,
    ...options,
  })
}

export const createProduct = (data) => {
  return request({
    path: '/api/v1/products',
    method: 'POST',
    data,
  })
}

export const updateProduct = (id, data) => {
  return request({
    path: `/api/v1/products/${id}`,
    method: 'PUT',
    data,
  })
}

export const deleteProduct = (id) => {
  return request({
    path: `/api/v1/products/${id}`,
    method: 'DELETE',
  })
}

export const updateProductStatus = (id, data) => {
  return request({
    path: `/api/v1/products/${id}/status`,
    method: 'PUT',
    data,
  })
}

export const uploadProductImage = (filePath) => {
  return uploadFile({
    path: '/api/v1/uploads/images',
    filePath,
    name: 'images',
  })
}

export const createTrade = (data) => {
  return request({
    path: '/api/v1/trades',
    method: 'POST',
    data,
  })
}

export const getMyBuyTrades = (data = {}) => {
  return request({
    path: '/api/v1/trades/my-buy',
    data,
  })
}

export const getMySellTrades = (data = {}) => {
  return request({
    path: '/api/v1/trades/my-sell',
    data,
  })
}

export const confirmTrade = (id) => {
  return request({
    path: `/api/v1/trades/${id}/confirm`,
    method: 'PUT',
  })
}

export const cancelTrade = (id) => {
  return request({
    path: `/api/v1/trades/${id}/cancel`,
    method: 'PUT',
  })
}

export const completeTrade = (id) => {
  return request({
    path: `/api/v1/trades/${id}/complete`,
    method: 'PUT',
  })
}

export const getMessages = (data = {}) => {
  return request({
    path: '/api/v1/messages',
    data,
  })
}

export const markMessageRead = (id) => {
  return request({
    path: `/api/v1/messages/${id}/read`,
    method: 'PUT',
  })
}

export const markAllMessagesRead = () => {
  return request({
    path: '/api/v1/messages/read-all',
    method: 'PUT',
  })
}

export const getAnnouncements = (data = {}) => {
  return request({
    path: '/api/v1/announcements',
    data,
  })
}

export const getAdminUsers = (data = {}) => {
  return request({
    path: '/api/v1/admin/users',
    data,
  })
}

export const updateAdminUserStatus = (id, data) => {
  return request({
    path: `/api/v1/admin/users/${id}/status`,
    method: 'PUT',
    data,
  })
}

export const getAdminProducts = (data = {}) => {
  return request({
    path: '/api/v1/admin/products',
    data,
  })
}

export const updateAdminProductStatus = (id, data) => {
  return request({
    path: `/api/v1/admin/products/${id}/status`,
    method: 'PUT',
    data,
  })
}

export const deleteAdminProduct = (id) => {
  return request({
    path: `/api/v1/admin/products/${id}`,
    method: 'DELETE',
  })
}

export const getAdminAnnouncements = (data = {}) => {
  return request({
    path: '/api/v1/admin/announcements',
    data,
  })
}

export const createAdminAnnouncement = (data) => {
  return request({
    path: '/api/v1/admin/announcements',
    method: 'POST',
    data,
  })
}

export const updateAdminAnnouncement = (id, data) => {
  return request({
    path: `/api/v1/admin/announcements/${id}`,
    method: 'PUT',
    data,
  })
}

export const deleteAdminAnnouncement = (id) => {
  return request({
    path: `/api/v1/admin/announcements/${id}`,
    method: 'DELETE',
  })
}

export const getAdminLogs = (data = {}) => {
  return request({
    path: '/api/v1/admin/logs',
    data,
  })
}
