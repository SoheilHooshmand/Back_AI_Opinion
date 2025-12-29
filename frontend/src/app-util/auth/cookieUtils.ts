const setCookie = (name: string, value: string, daysToLive: number | undefined) => {
  let cookie = `${name}=${encodeURIComponent(value)}`

  if (typeof daysToLive === 'number') {
    cookie += `; max-age=${daysToLive * 24 * 60 * 60}`
  }

  cookie += '; sameSite=strict'
  cookie += '; path=/'
  document.cookie = cookie
}

const getCookie = (name: string) => {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop()?.split(';').shift()
  return undefined
}

const removeCookie = (name: string) => {
  document.cookie = `${name}=; Max-Age=0`
}

const cookieUtil = { getCookie, setCookie, removeCookie }

export default cookieUtil
