/**
 * Layout Component
 * 
 * Provides consistent layout with centered content and mobile-friendly width.
 */

"use client";

import { ReactNode } from 'react';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';

interface LayoutProps {
  children: ReactNode;
  showHeader?: boolean;
}

export default function Layout({ children, showHeader = true }: LayoutProps) {
  const { user, logout, isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      {showHeader && (
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-md mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <Link href="/" className="flex items-center gap-2">
                <span className="text-2xl">🚗</span>
                <span className="font-bold text-gray-900">RSA</span>
              </Link>

              {isAuthenticated && user && (
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">
                      {user.name || `User ${user.phone.slice(-4)}`}
                    </p>
                    <p className="text-xs text-gray-500 capitalize">
                      {user.role}
                    </p>
                  </div>
                  <button
                    onClick={logout}
                    className="text-sm text-red-600 hover:text-red-700 font-medium"
                  >
                    Logout
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>
      )}

      {/* Main Content */}
      <main className="max-w-md mx-auto px-4 py-6">
        {children}
      </main>

      {/* Footer */}
      <footer className="max-w-md mx-auto px-4 py-6 text-center text-sm text-gray-600">
        <p>Roadside Assistance Marketplace</p>
        <p className="text-xs mt-1">© 2025 RSA. All rights reserved.</p>
      </footer>
    </div>
  );
}

