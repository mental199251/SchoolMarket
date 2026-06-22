import { API_BASE_URL, REQUEST_TIMEOUT } from './config'
import {
  clearAuthStorage,
  createRequestError,
  showRequestError,
} from '../utils/error'

const isSuccessStatus = (statusCode) => statusCode >= 200 && statusCode < 300

export const request = ({
  path,
  method = 'GET',
  data,
  header = {},
  timeout = REQUEST_TIMEOUT,
  showError = true,
}) => {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('auth_token')
    const requestHeader = {
      'Content-Type': 'application/json',
      ...header,
    }

    if (token && !requestHeader.Authorization) {
      requestHeader.Authorization = `Bearer ${token}`
    }

    uni.request({
      url: `${API_BASE_URL}${path}`,
      method: method.toUpperCase(),
      data,
      header: requestHeader,
      timeout,
      success: (response) => {
        const payload = response.data

        if (isSuccessStatus(response.statusCode) && payload?.success === true) {
          resolve(payload.data)
          return
        }

        const error = createRequestError({
          statusCode: response.statusCode,
          errorCode: payload?.error_code,
          message: payload?.message || '服务返回了无法识别的响应',
          data: payload?.data,
        })

        if (response.statusCode === 401) {
          clearAuthStorage()
        }
        if (showError) {
          showRequestError(error)
        }
        reject(error)
      },
      fail: (failure) => {
        const error = createRequestError({
          statusCode: 0,
          errorCode: 'NETWORK_ERROR',
          message: failure.errMsg?.includes('timeout')
            ? '请求超时，请稍后重试'
            : '无法连接服务器，请检查网络和后端地址',
          cause: failure,
        })

        if (showError) {
          showRequestError(error)
        }
        reject(error)
      },
    })
  })
}

export const uploadFile = ({
  path,
  filePath,
  name = 'file',
  formData = {},
  header = {},
  timeout = REQUEST_TIMEOUT,
  showError = true,
}) => {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('auth_token')
    const requestHeader = { ...header }

    if (token && !requestHeader.Authorization) {
      requestHeader.Authorization = `Bearer ${token}`
    }

    uni.uploadFile({
      url: `${API_BASE_URL}${path}`,
      filePath,
      name,
      formData,
      header: requestHeader,
      timeout,
      success: (response) => {
        let payload = response.data
        if (typeof payload === 'string') {
          try {
            payload = JSON.parse(payload)
          } catch (_error) {
            payload = null
          }
        }

        if (isSuccessStatus(response.statusCode) && payload?.success === true) {
          resolve(payload.data)
          return
        }

        const error = createRequestError({
          statusCode: response.statusCode,
          errorCode: payload?.error_code,
          message: payload?.message || '上传失败',
          data: payload?.data,
        })

        if (response.statusCode === 401) {
          clearAuthStorage()
        }
        if (showError) {
          showRequestError(error)
        }
        reject(error)
      },
      fail: (failure) => {
        const error = createRequestError({
          statusCode: 0,
          errorCode: 'NETWORK_ERROR',
          message: failure.errMsg?.includes('timeout')
            ? '上传超时，请稍后重试'
            : '无法连接服务器，请检查网络和后端地址',
          cause: failure,
        })

        if (showError) {
          showRequestError(error)
        }
        reject(error)
      },
    })
  })
}
