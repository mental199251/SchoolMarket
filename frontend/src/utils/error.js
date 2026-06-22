import { clearAuthStorage as clearStoredAuth } from './auth'

export const clearAuthStorage = clearStoredAuth

export const createRequestError = ({
  statusCode = 0,
  errorCode = 'UNKNOWN_ERROR',
  message = '请求失败',
  data = null,
  cause = null,
}) => ({
  name: 'RequestError',
  statusCode,
  errorCode,
  message,
  data,
  cause,
})

export const showRequestError = (error) => {
  uni.showToast({
    title: error?.message || '请求失败，请稍后重试',
    icon: 'none',
    duration: 2500,
  })
}
