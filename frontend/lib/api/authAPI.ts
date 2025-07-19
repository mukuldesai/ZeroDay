import { getAuthHeaders, makeAuthenticatedRequest } from '../auth/authUtils';

interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterRequest {
  name: string;
  email: string;
  password: string;
}

interface AuthResponse {
  token: string;
  user: {
    id: number;
    name: string;
    email: string;
    isDemo: boolean;
  };
}

interface UserProfile {
  id: number;
  name: string;
  email: string;
  isDemo: boolean;
  organizations: Array<{
    id: number;
    name: string;
  }>;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const authAPI = {
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
      credentials: 'include'
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    return response.json();
  },

  register: async (userData: RegisterRequest): Promise<{ message: string }> => {
    const response = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    return response.json();
  },

  logout: async (): Promise<{ message: string }> => {
    const response = await makeAuthenticatedRequest(`${API_BASE}/auth/logout`, {
      method: 'POST',
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error('Logout failed');
    }

    return response.json();
  },

  getCurrentUser: async () => {
    const response = await makeAuthenticatedRequest(`${API_BASE}/auth/me`);

    if (!response.ok) {
      throw new Error('Failed to get user info');
    }

    return response.json();
  },

  getUserProfile: async (): Promise<UserProfile> => {
    const response = await makeAuthenticatedRequest(`${API_BASE}/users/profile`);

    if (!response.ok) {
      throw new Error('Failed to get user profile');
    }

    return response.json();
  },

  updateProfile: async (updates: { name?: string; email?: string }) => {
    const response = await makeAuthenticatedRequest(`${API_BASE}/users/profile`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Profile update failed');
    }

    return response.json();
  },

  createOrganization: async (name: string) => {
    const response = await makeAuthenticatedRequest(`${API_BASE}/users/organizations`, {
      method: 'POST',
      body: JSON.stringify({ name })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Organization creation failed');
    }

    return response.json();
  },

  getOrganizations: async () => {
    const response = await makeAuthenticatedRequest(`${API_BASE}/users/organizations`);

    if (!response.ok) {
      throw new Error('Failed to get organizations');
    }

    return response.json();
  },

  deleteOrganization: async (orgId: number) => {
    const response = await makeAuthenticatedRequest(`${API_BASE}/users/organizations/${orgId}`, {
      method: 'DELETE'
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Organization deletion failed');
    }

    return response.json();
  }
};