import { API_BASE_URL } from "@/lib/api";

import type {
  User,
  RegisterRequest,
  LoginRequest,
  TokenResponse,
} from "@/types/auth";

const TOKEN_KEY = "greensprint_access_token";

export class AuthService {
  static async register(
    payload: RegisterRequest
  ): Promise<User> {
    const response = await fetch(
      `${API_BASE_URL}/auth/register`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      }
    );

    if (!response.ok) {
      const error = await response.json();

      throw new Error(
        error.detail || "Registration failed"
      );
    }

    return response.json();
  }

  static async login(
    payload: LoginRequest
  ): Promise<TokenResponse> {
    const formData = new URLSearchParams();

    formData.append(
      "username",
      payload.email
    );

    formData.append(
      "password",
      payload.password
    );

    const response = await fetch(
      `${API_BASE_URL}/auth/login`,
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/x-www-form-urlencoded",
        },
        body: formData,
      }
    );

    if (!response.ok) {
      const error = await response.json();

      throw new Error(
        error.detail || "Login failed"
      );
    }

    const tokenData: TokenResponse =
      await response.json();

    localStorage.setItem(
      TOKEN_KEY,
      tokenData.access_token
    );

    return tokenData;
  }

  static logout(): void {
    localStorage.removeItem(TOKEN_KEY);
  }

  static getToken(): string | null {
    return localStorage.getItem(
      TOKEN_KEY
    );
  }

  static async getCurrentUser(): Promise<User> {
    const token = this.getToken();

    if (!token) {
      throw new Error(
        "User not authenticated"
      );
    }

    const response = await fetch(
      `${API_BASE_URL}/users/me`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error(
        "Failed to load user"
      );
    }

    return response.json();
  }
}