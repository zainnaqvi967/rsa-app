"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import Layout from "@/components/Layout";
import Link from "next/link";

export default function Home() {
  const router = useRouter();
  const { user, isLoading, isAuthenticated, isCustomer, isProvider, isAdmin } = useAuth();

  // Redirect authenticated users to their dashboard
  useEffect(() => {
    if (!isLoading && isAuthenticated && user) {
      if (isCustomer) {
        router.push('/customer');
      } else if (isProvider) {
        router.push('/provider');
      } else if (isAdmin) {
        router.push('/admin');
      }
    }
  }, [isLoading, isAuthenticated, user, isCustomer, isProvider, isAdmin, router]);

  if (isLoading) {
    return (
      <Layout showHeader={false}>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout showHeader={false}>
      <div className="py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="text-6xl mb-4">🚗</div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Roadside Assistance
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            Help when you need it most
          </p>
          <p className="text-sm text-gray-500">
            Connect with trusted providers nearby
          </p>
        </div>

        {/* CTA Button */}
        <div className="space-y-4">
          <Link
            href="/login"
            className="block w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-4 px-6 rounded-lg shadow-lg text-center transition duration-200"
          >
            Login / Continue
          </Link>

          <p className="text-center text-sm text-gray-600">
            New here? Sign up during login
          </p>
        </div>

        {/* Features */}
        <div className="mt-16 space-y-6">
          <h2 className="text-lg font-semibold text-gray-900 text-center mb-8">
            How it works
          </h2>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-start gap-4">
              <div className="text-3xl">👥</div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">
                  For Customers
                </h3>
                <p className="text-sm text-gray-600">
                  Request help, set your price, get offers from nearby providers, and choose the best one
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-start gap-4">
              <div className="text-3xl">🔧</div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">
                  For Providers
                </h3>
                <p className="text-sm text-gray-600">
                  See nearby requests, send competitive offers, and grow your business
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-start gap-4">
              <div className="text-3xl">⚡</div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">
                  Fast & Easy
                </h3>
                <p className="text-sm text-gray-600">
                  Get help in minutes with our simple, mobile-friendly platform
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Services */}
        <div className="mt-12 bg-white rounded-lg shadow-md p-6">
          <h3 className="font-semibold text-gray-900 mb-4 text-center">
            Services Available
          </h3>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="flex items-center gap-2">
              <span>🔧</span>
              <span className="text-gray-700">Flat Tire</span>
            </div>
            <div className="flex items-center gap-2">
              <span>🔋</span>
              <span className="text-gray-700">Jump Start</span>
            </div>
            <div className="flex items-center gap-2">
              <span>⛽</span>
              <span className="text-gray-700">Fuel Delivery</span>
            </div>
            <div className="flex items-center gap-2">
              <span>🚚</span>
              <span className="text-gray-700">Towing</span>
            </div>
            <div className="flex items-center gap-2">
              <span>🔑</span>
              <span className="text-gray-700">Lockout</span>
            </div>
            <div className="flex items-center gap-2">
              <span>➕</span>
              <span className="text-gray-700">And More</span>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
