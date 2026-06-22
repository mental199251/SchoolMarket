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
