const AUTH_STORAGE_KEYS = ['auth_token', 'auth_user', 'auth_expires_at']
const REMEMBER_LOGIN_KEY = 'remember_login_credentials'

export const clearAuthStorage = () => {
  AUTH_STORAGE_KEYS.forEach((key) => uni.removeStorageSync(key))
}

export const setAuthSession = ({ token, user, expires_at }) => {
  uni.setStorageSync('auth_token', token)
  uni.setStorageSync('auth_user', user)
  uni.setStorageSync('auth_expires_at', expires_at)
}

export const replaceStoredUser = (user) => {
  uni.setStorageSync('auth_user', user)
}

export const getAuthToken = () => uni.getStorageSync('auth_token')

export const getStoredUser = () => uni.getStorageSync('auth_user')

export const getStoredExpiresAt = () => uni.getStorageSync('auth_expires_at')

export const hasValidAuth = () => {
  const token = getAuthToken()
  const expiresAt = getStoredExpiresAt()
  if (!token || !expiresAt) return false
  return new Date(expiresAt).getTime() > Date.now()
}

export const getRememberedLogin = () => {
  return uni.getStorageSync(REMEMBER_LOGIN_KEY) || {
    remember: false,
    username: '',
    password: '',
  }
}

export const saveRememberedLogin = ({ username, password }) => {
  uni.setStorageSync(REMEMBER_LOGIN_KEY, {
    remember: true,
    username,
    password,
  })
}

export const clearRememberedLogin = () => {
  uni.removeStorageSync(REMEMBER_LOGIN_KEY)
}
