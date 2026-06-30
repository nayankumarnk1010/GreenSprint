export type UserRole =
  | "USER"
  | "ORGANIZATION"
  | "ADMIN";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
}

export interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
  role: UserRole;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}