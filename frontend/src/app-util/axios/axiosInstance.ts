import axios from 'axios'
import { BASE_API_URL } from '../env'
import { logoutAndRedirect } from '../auth/getTokenByRefreshToken'
import getRefreshToken from '../auth/getRefreshToken'
import setToken from '../auth/setToken'
import setAxiosHeader from './setAxiosHeader'
import type { AxiosRequestConfig } from 'axios'
import { refreshTokenRequest } from '@/api-specs/api'

interface RetryQueueItem {
  resolve: (value?: any) => void
  reject: (error?: any) => void
  config: AxiosRequestConfig
}

const axiosInstance = axios.create({
  baseURL: BASE_API_URL,
})

const refreshAndRetryQueue: Array<RetryQueueItem> = []

let isRefreshing = false

// attach request interceptor
axiosInstance.interceptors.request.use(
  (config) => setAxiosHeader(config),
  (error) => Promise.reject(error),
)

// Response interceptor → handle 401
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest: AxiosRequestConfig = error.config

    if (originalRequest.url?.includes('/token/refresh')) {
      console.log('⚠️ Refresh token request failed - skipping interceptor')
      return Promise.reject(error)
    }

    if (error.response && error.response.status === 401) {
      // handleTokenRefresh()
      if (!isRefreshing) {
        isRefreshing = true
        const refreshToken = getRefreshToken()
        console.log('refresh', refreshToken)
        try {
          console.log('try')
          if (refreshToken) {
            const response = await refreshTokenRequest({ refresh: refreshToken })
            console.log('response', response)
            setToken(response?.data?.access, response?.data?.refresh)
            error.config.headers['Authorization'] = `Bearer ${response.data.access}`
            refreshAndRetryQueue.forEach(({ config, resolve, reject }) => {
              axiosInstance
                .request(config)
                .then((response) => resolve(response))
                .catch((err) => reject(err))
            })

            // Clear the queue
            refreshAndRetryQueue.length = 0

            // Retry the original request
            return axiosInstance(originalRequest)
          } else {
            // no refresh token exists
            logoutAndRedirect()
          }
        } catch (refreshError) {
          console.error('refreshError', refreshError)
          logoutAndRedirect()
          throw refreshError
        } finally {
          isRefreshing = false
        }
      }

      // Add the original request to the queue
      return new Promise<void>((resolve, reject) => {
        refreshAndRetryQueue.push({ config: originalRequest, resolve, reject })
      })
    }
    // error not 401
    return Promise.reject(error)
  },
)

export default axiosInstance
