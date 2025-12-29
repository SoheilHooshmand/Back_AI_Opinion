import type { ApiAxiosResponse } from '../types/common/types'
import type { LoginPayload, RefreshTokenPayload, RegisterPayload } from '../types/payload/auth'
import type { CreateProjectPayload } from '../types/payload/userProjects'
import type { LoginResponse, RefreshTokenResponse, RegisterResponse } from '../types/response/auth'
import type { TokenCostResponse } from '../types/response/cost'
import type { CreateProjectResponse, ProjectListResponse } from '../types/response/userProjects'
import axiosInstance from '@/app-util/axios/axiosInstance'

export const loginRequest = (data: LoginPayload): Promise<ApiAxiosResponse<LoginResponse>> => {
  return axiosInstance.post('/auth/login/', data)
}

export const refreshTokenRequest = (data: RefreshTokenPayload): Promise<ApiAxiosResponse<RefreshTokenResponse>> => {
  return axiosInstance.post('/auth/token/refresh/', data)
}

export const registrationRequest = (data: RegisterPayload): Promise<ApiAxiosResponse<RegisterResponse>> => {
  return axiosInstance.post('/auth/registration/', data)
}

export const calculateTokenCostRequest = (data: FormData): Promise<ApiAxiosResponse<TokenCostResponse>> => {
  return axiosInstance.post('/project/token-cost/', data)
}

export const fetchUserProjectsRequest = (): Promise<ApiAxiosResponse<ProjectListResponse>> => {
  return axiosInstance.get('/project/')
}

export const createProjectRequest = (data: CreateProjectPayload): Promise<ApiAxiosResponse<CreateProjectResponse>> => {
  return axiosInstance.post('/project/', data)
}
