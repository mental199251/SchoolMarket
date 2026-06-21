import { request } from './http'

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

