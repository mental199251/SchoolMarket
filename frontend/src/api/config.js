const trimTrailingSlash = (value) => value.replace(/\/+$/, '')

const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5001'
const configuredTimeout = Number(import.meta.env.VITE_API_TIMEOUT)

export const API_BASE_URL = trimTrailingSlash(configuredBaseUrl)
export const REQUEST_TIMEOUT = Number.isFinite(configuredTimeout)
  ? configuredTimeout
  : 8000

