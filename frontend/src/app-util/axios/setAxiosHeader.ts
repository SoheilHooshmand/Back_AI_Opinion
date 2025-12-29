import getToken from '../auth/getToken'
import type { AxiosHeaders, InternalAxiosRequestConfig } from 'axios'

const setAxiosHeader = (config: InternalAxiosRequestConfig<any>): InternalAxiosRequestConfig<any> => {
  if (typeof window !== 'undefined') {
    const token = localStorage && getToken()
    if (token) (config.headers as AxiosHeaders).set('Authorization', `Bearer ${token}`)
  }

  return {
    ...config,
    withCredentials: true,
  }
}

export default setAxiosHeader
