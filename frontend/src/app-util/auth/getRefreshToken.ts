const getRefreshToken = () => {
  const refreshToken = localStorage.getItem('refreshToken')
  if (refreshToken) return refreshToken
  return null
}

export default getRefreshToken
