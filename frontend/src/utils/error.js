const AUTH_STORAGE_KEYS = ['auth_token', 'auth_user', 'auth_expires_at']

export const clearAuthStorage = () => {
  AUTH_STORAGE_KEYS.forEach((key) => uni.removeStorageSync(key))
}

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

