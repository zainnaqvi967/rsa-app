/**
 * useAuth Hook
 * 
 * Custom hook for accessing authentication context and utilities.
 */

"use client";

import { useContext } from 'react';
import { AuthContext } from '@/context/AuthContext';

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  const { user, token, login, logout, isLoading } = context;

  // Role helper functions
  const isCustomer = user?.role === 'customer';
  const isProvider = user?.role === 'provider';
  const isAdmin = user?.role === 'admin';
  const isAuthenticated = !!user && !!token;

  return {
    user,
    token,
    login,
    logout,
    isLoading,
    isAuthenticated,
    isCustomer,
    isProvider,
    isAdmin,
  };
}

