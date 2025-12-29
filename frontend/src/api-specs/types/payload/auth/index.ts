export interface LoginPayload {
  email: string
  password: string
}

export interface RefreshTokenPayload {
  refresh: string
}

export interface RegisterPayload {
  username: string
  email: string
  password1: string
  password2: string
}
