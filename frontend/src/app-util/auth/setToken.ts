import cookieUtil from './cookieUtils'

const setToken = (token: string, refreshToken: string) => {
  // Persist in localStorage (source of truth for request headers)
  if (token) localStorage.setItem('token', token)
  if (refreshToken) localStorage.setItem('refreshToken', refreshToken)

  // Optional: also mirror in cookies for simple cross-tab/session access
  // cookieUtil expects days, not seconds. 7 = 7 days
  if (token) cookieUtil.setCookie('token', token, 7)
  if (refreshToken) cookieUtil.setCookie('refreshToken', refreshToken, 7)
}

export default setToken
