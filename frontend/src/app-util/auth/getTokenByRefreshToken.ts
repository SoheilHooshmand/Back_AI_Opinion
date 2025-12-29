import { notifications } from '@mantine/notifications'
import getRefreshToken from './getRefreshToken'
import cookieUtil from './cookieUtils'
import setToken from './setToken'
import { refreshTokenRequest } from '@/api-specs/api'

export const logoutAndRedirect = () => {
  cookieUtil.removeCookie('token')
  cookieUtil.removeCookie('refreshToken')
  localStorage.removeItem('token')
  localStorage.removeItem('refreshToken')
  localStorage.clear()

  window.location.href = '/login'
}

export const handleTokenRefresh = async () => {
  try {
    const refreshToken = getRefreshToken()
    if (refreshToken) {
      const response = await refreshTokenRequest({ refresh: refreshToken })
      setToken(response?.data?.access, response?.data?.refresh)
      notifications.show({
        id: 'refreshToken',
        message: 'Refresh token success',
        color: 'green',
      })
      setTimeout(() => {
        window.location.reload()
      }, 1000)
    } else {
      logoutAndRedirect()
    }
  } catch (e) {
    console.error(e)
    logoutAndRedirect()
  }
}
