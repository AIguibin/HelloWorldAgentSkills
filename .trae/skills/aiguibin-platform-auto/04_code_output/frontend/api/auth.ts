import request from '@/utils/request'

export interface LoginRequest {
  username: string
  password: string
}

export interface SelectOrgRequest {
  tempToken: string
  orgCode: string
}

export const loginApi = (data: LoginRequest) => {
  return request.post('/api/auth/login', data)
}

export const selectOrgApi = (data: SelectOrgRequest) => {
  return request.post('/api/auth/select-org', data)
}

export const logoutApi = () => {
  return request.post('/api/auth/logout')
}

export const getUserInfoApi = () => {
  return request.get('/api/auth/user-info')
}

export const refreshTokenApi = (refreshToken: string) => {
  return request.post('/api/auth/refresh', null, {
    headers: { 'X-Refresh-Token': refreshToken }
  })
}
