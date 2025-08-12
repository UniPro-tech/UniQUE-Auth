import api from './api';
import type { LoginRequest, LoginResponse, AuthorizationData, AuthorizationRequest } from '../types';

export const login = async (data: LoginRequest, queryString: string): Promise<LoginResponse> => {
  try {
    const response = await api.post(`/login${queryString}`, data);
    return {
      success: true,
      redirect_url: response.data.redirect_url,
    };
  } catch (error: any) {
    return {
      success: false,
      error: error.response?.data?.error_description || error.response?.data?.error || 'ログインに失敗しました',
    };
  }
};

export const getCsrfToken = async (queryString: string = ''): Promise<string> => {
  const response = await api.get(`/login${queryString}`);
  return response.data.csrf_token;
};

export const getAuthorizationData = async (params: AuthorizationRequest): Promise<AuthorizationData> => {
  const response = await api.get('/auth', { params });
  return response.data;
};

export const authorize = async (params: AuthorizationRequest): Promise<string> => {
  const response = await api.post('/auth', params);
  return response.data.redirect_url;
};

export const logout = async (): Promise<void> => {
  await api.get('/logout');
};