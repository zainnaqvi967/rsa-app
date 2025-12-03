/**
 * API client with axios and authentication interceptor.
 * 
 * Automatically attaches JWT token to requests if available.
 */

import axios, { AxiosInstance } from 'axios';

// Create axios instance with base URL
const api: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - attach auth token
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle 401 Unauthorized - token expired or invalid
    if (error.response?.status === 401) {
      // Clear token and user data
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        // Redirect to login page
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;

// Export common API methods for convenience
export const authAPI = {
  requestOTP: (phone: string) => 
    api.post('/auth/request-otp', { phone }),
  
  verifyOTP: (phone: string, otp: string, name?: string) =>
    api.post('/auth/verify-otp', { phone, otp, name }),
  
  getCurrentUser: () => 
    api.get('/me'),
};

export const customerAPI = {
  createServiceRequest: (data: any) =>
    api.post('/customer/service-requests', data),
  
  getServiceRequest: (id: number) =>
    api.get(`/customer/service-requests/${id}`),
  
  getActiveRequest: () =>
    api.get('/customer/active-request'),
  
  acceptOffer: (offerId: number) =>
    api.post(`/customer/offers/${offerId}/accept`),
  
  getJob: (jobId: number) =>
    api.get(`/customer/jobs/${jobId}`),
};

export const providerAPI = {
  getProfile: () =>
    api.get('/provider/profile'),
  
  updateProfile: (data: any) =>
    api.put('/provider/profile', data),
  
  updateLocation: (lat: number, lng: number) =>
    api.post('/provider/location', { lat, lng }),
  
  getNearbyRequests: (radiusKm?: number) =>
    api.get('/provider/nearby-requests', { params: { radius_km: radiusKm } }),
  
  createOffer: (data: any) =>
    api.post('/provider/offers', data),
  
  getActiveJobs: () =>
    api.get('/provider/jobs/active'),
  
  updateJobStatus: (jobId: number, status: string) =>
    api.patch(`/provider/jobs/${jobId}/status`, { status }),
};

export const adminAPI = {
  getUsers: (role?: string) =>
    api.get('/admin/users', { params: { role } }),
  
  getProviders: () =>
    api.get('/admin/providers'),
  
  updateProviderVerification: (profileId: number, isVerified: boolean) =>
    api.patch(`/admin/providers/${profileId}`, { is_verified: isVerified }),
  
  getServiceRequests: (status?: string, customerId?: number) =>
    api.get('/admin/service-requests', { params: { status, customer_id: customerId } }),
  
  getJobs: (status?: string) =>
    api.get('/admin/jobs', { params: { status } }),
};

