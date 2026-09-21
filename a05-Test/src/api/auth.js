import apiClient from './client'

export const login = (data) => apiClient.post('/api/auth/login', data)
export const register = (data) => apiClient.post('/api/auth/register', data)
