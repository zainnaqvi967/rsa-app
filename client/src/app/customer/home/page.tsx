"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { useLocation } from "@/context/LocationContext";
import Layout from "@/components/Layout";

export default function CustomerHome() {
  const router = useRouter();
  const { user, isAuthenticated, isCustomer, isLoading } = useAuth();
  const { location, setLocation } = useLocation();
  const [locationError, setLocationError] = useState<string | null>(null);
  const [loadingLocation, setLoadingLocation] = useState(false);

  // Redirect if not authenticated or not customer
  useEffect(() => {
    if (!isLoading && (!isAuthenticated || !isCustomer)) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, isCustomer, router]);

  // Get geolocation on mount
  useEffect(() => {
    if (!location && navigator.geolocation) {
      setLoadingLocation(true);
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
          setLoadingLocation(false);
        },
        (error) => {
          console.error('Geolocation error:', error);
          setLocationError('Could not get your location. Please enable location services.');
          setLoadingLocation(false);
        }
      );
    }
  }, [location, setLocation]);

  if (isLoading || !isAuthenticated) {
    return (
      <Layout>
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="py-8">
        {/* Greeting */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Hello, {user?.name || 'there'}! 👋
          </h1>
          <p className="text-gray-600">
            Wherever you are stranded, request help in a few taps.
          </p>
        </div>

        {/* Location Status */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <span className="text-2xl">📍</span>
            <div>
              <h3 className="font-semibold text-gray-900">Your Location</h3>
              {loadingLocation && (
                <p className="text-sm text-gray-600">Getting your location...</p>
              )}
              {location && !loadingLocation && (
                <p className="text-sm text-green-600">
                  ✓ Location detected ({location.lat.toFixed(4)}, {location.lng.toFixed(4)})
                </p>
              )}
              {locationError && (
                <p className="text-sm text-red-600">{locationError}</p>
              )}
            </div>
          </div>

          {/* Simple map placeholder */}
          {location && (
            <div className="bg-gray-100 rounded-lg h-48 flex items-center justify-center relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-100 to-green-100"></div>
              <div className="relative z-10 text-center">
                <div className="text-4xl mb-2">📍</div>
                <p className="text-sm text-gray-700 font-medium">You are here</p>
                <p className="text-xs text-gray-600 mt-1">
                  {location.lat.toFixed(4)}, {location.lng.toFixed(4)}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Main CTA */}
        <button
          onClick={() => router.push('/customer/request')}
          disabled={!location && !locationError}
          className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-bold py-4 px-6 rounded-lg shadow-lg transition duration-200 mb-4"
        >
          {!location && !locationError ? '📍 Detecting Location...' : '🆘 Need Roadside Help'}
        </button>

        {locationError && (
          <p className="text-center text-sm text-gray-600">
            You can still request help, but providers may need your location.
          </p>
        )}

        {/* Quick Info */}
        <div className="mt-8 space-y-4">
          <h3 className="font-semibold text-gray-900">How it works:</h3>
          
          <div className="flex items-start gap-3">
            <span className="text-2xl">1️⃣</span>
            <div>
              <p className="font-medium text-gray-900">Describe your problem</p>
              <p className="text-sm text-gray-600">Tell us what service you need</p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <span className="text-2xl">2️⃣</span>
            <div>
              <p className="font-medium text-gray-900">Get offers</p>
              <p className="text-sm text-gray-600">Nearby providers will send you offers</p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <span className="text-2xl">3️⃣</span>
            <div>
              <p className="font-medium text-gray-900">Choose & track</p>
              <p className="text-sm text-gray-600">Accept the best offer and track your helper</p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}

