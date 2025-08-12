import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  withCredentials: true, // クッキーを送信するために必要
  headers: {
    'Content-Type': 'application/json',
  },
});

// レスポンスインターセプター
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 認証エラー時の処理
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;