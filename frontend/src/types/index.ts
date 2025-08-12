export interface LoginRequest {
  custom_id: string;
  password: string;
  csrf_token: string;
}

export interface LoginResponse {
  success: boolean;
  error?: string;
  redirect_url?: string;
}

export interface AuthorizationRequest {
  client_id: string;
  redirect_uri: string;
  scope: string;
  state?: string;
  response_type: string;
  nonce?: string;
}

export interface AuthorizationData {
  app: {
    name: string;
    client_id: string;
    redirect_uris: string[];
    scope: string;
  };
  user: {
    name: string;
    id: string;
  };
}

export interface ApiError {
  error: string;
  error_description?: string;
  error_uri?: string;
  state?: string;
}