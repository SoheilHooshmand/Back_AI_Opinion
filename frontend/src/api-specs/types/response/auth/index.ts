export interface LoginUser {
  pk: number
  email: string
  username: string
}

export interface LoginResponse {
  access: string
  refresh: string
  user: LoginUser
}

export interface RefreshTokenResponse {
  refresh: string
  access: string
}

export interface RegisterResponse {
  detail: string
}
