"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { providerAPI } from "@/lib/api";
import Layout from "@/components/Layout";

interface ProviderProfile {
  id: number;
  user_id: number;
  city: string | null;
  services_offered: string | null;
  vehicle_types: string | null;
  is_verified: boolean;
  average_rating: number;
  total_ratings: number;
  current_lat: number | null;
  current_lng: number | null;
  is_online: boolean;
}

export default function ProviderHome() {
  const router = useRouter();
  const { user, isAuthenticated, isProvider, isLoading: authLoading } = useAuth();
  
  const [profile, setProfile] = useState<ProviderProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [updatingStatus, setUpdatingStatus] = useState(false);
  const [updatingLocation, setUpdatingLocation] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Redirect if not authenticated or not provider
  useEffect(() => {
    if (!authLoading && (!isAuthenticated || !isProvider)) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, isProvider, router]);

  // Fetch provider profile
  const fetchProfile = async () => {
    try {
      const response = await providerAPI.getProfile();
      setProfile(response.data);
      setLoading(false);
    } catch (err: any) {
      console.error('Fetch error:', err);
      setError(err.response?.data?.detail || 'Failed to load profile');
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated && isProvider) {
      fetchProfile();
    }
  }, [isAuthenticated, isProvider]);

  const handleToggleOnline = async () => {
    if (!profile) return;
    
    setUpdatingStatus(true);
    setError('');
    setSuccess('');

    try {
      const response = await providerAPI.updateProfile({
        is_online: !profile.is_online
      });
      setProfile(response.data);
      setSuccess(`You are now ${response.data.is_online ? 'online' : 'offline'}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update status');
    } finally {
      setUpdatingStatus(false);
    }
  };

  const handleUpdateLocation = async () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser');
      return;
    }

    setUpdatingLocation(true);
    setError('');
    setSuccess('');

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const response = await providerAPI.updateLocation(
            position.coords.latitude,
            position.coords.longitude
          );
          setProfile(response.data);
          setSuccess('Location updated successfully');
        } catch (err: any) {
          setError(err.response?.data?.detail || 'Failed to update location');
        } finally {
          setUpdatingLocation(false);
        }
      },
      (error) => {
        console.error('Geolocation error:', error);
        setError('Could not get your location. Please enable location services.');
        setUpdatingLocation(false);
      }
    );
  };

  if (authLoading || loading) {
    return (
      <Layout>
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
        </div>
      </Layout>
    );
  }

  if (!profile) {
    return (
      <Layout>
        <div className="py-8">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            Failed to load profile
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="py-8">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.name || 'Provider'}! 🔧
          </h1>
          <p className="text-gray-600">
            Manage your profile and find nearby jobs
          </p>
        </div>

        {/* Alerts */}
        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}
        {success && (
          <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
            {success}
          </div>
        )}

        {/* Online Status Card */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className={`w-4 h-4 rounded-full ${profile.is_online ? 'bg-green-500' : 'bg-gray-400'}`}></div>
              <div>
                <h3 className="font-semibold text-gray-900">
                  {profile.is_online ? 'You are Online' : 'You are Offline'}
                </h3>
                <p className="text-sm text-gray-600">
                  {profile.is_online ? 'Customers can see your offers' : 'Go online to receive requests'}
                </p>
              </div>
            </div>
          </div>
          
          <button
            onClick={handleToggleOnline}
            disabled={updatingStatus}
            className={`w-full font-semibold py-3 px-6 rounded-lg transition duration-200 ${
              profile.is_online
                ? 'bg-gray-600 hover:bg-gray-700 text-white'
                : 'bg-green-600 hover:bg-green-700 text-white'
            } disabled:bg-gray-400`}
          >
            {updatingStatus ? 'Updating...' : profile.is_online ? '⏸️ Go Offline' : '▶️ Go Online'}
          </button>
        </div>

        {/* Profile Info Card */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="font-semibold text-gray-900 mb-4">Profile Information</h3>
          
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">City:</span>
              <span className="font-medium text-gray-900">
                {profile.city || 'Not set'}
              </span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-600">Services:</span>
              <span className="font-medium text-gray-900 text-right">
                {profile.services_offered ? profile.services_offered.split(',').join(', ') : 'Not set'}
              </span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-600">Vehicle Types:</span>
              <span className="font-medium text-gray-900 capitalize">
                {profile.vehicle_types || 'Not set'}
              </span>
            </div>

            <div className="flex justify-between">
              <span className="text-gray-600">Verified:</span>
              <span className={`font-medium ${profile.is_verified ? 'text-green-600' : 'text-yellow-600'}`}>
                {profile.is_verified ? '✓ Yes' : '⚠ Pending'}
              </span>
            </div>

            <div className="flex justify-between">
              <span className="text-gray-600">Rating:</span>
              <span className="font-medium text-gray-900">
                {profile.total_ratings > 0 
                  ? `⭐ ${profile.average_rating.toFixed(1)} (${profile.total_ratings} ratings)`
                  : 'No ratings yet'}
              </span>
            </div>

            {profile.current_lat && profile.current_lng && (
              <div className="flex justify-between">
                <span className="text-gray-600">Last Location:</span>
                <span className="font-medium text-gray-900 text-xs">
                  {profile.current_lat.toFixed(4)}, {profile.current_lng.toFixed(4)}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="space-y-4">
          <button
            onClick={handleUpdateLocation}
            disabled={updatingLocation}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg shadow-lg transition duration-200"
          >
            {updatingLocation ? 'Updating...' : '📍 Update My Location'}
          </button>

          <button
            onClick={() => router.push('/provider/requests')}
            disabled={!profile.is_online}
            className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg shadow-lg transition duration-200"
          >
            🔍 View Nearby Requests
          </button>

          {!profile.is_online && (
            <p className="text-center text-sm text-gray-600">
              Go online to view nearby requests
            </p>
          )}

          <button
            onClick={() => router.push('/provider/jobs/active')}
            className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg shadow-lg transition duration-200"
          >
            📋 View My Active Jobs
          </button>
        </div>

        {/* Quick Stats */}
        <div className="mt-8 grid grid-cols-2 gap-4">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 text-center">
            <p className="text-2xl font-bold text-blue-900">
              {profile.total_ratings}
            </p>
            <p className="text-sm text-blue-700">Total Jobs</p>
          </div>
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 text-center">
            <p className="text-2xl font-bold text-green-900">
              {profile.average_rating.toFixed(1)}
            </p>
            <p className="text-sm text-green-700">Avg Rating</p>
          </div>
        </div>
      </div>
    </Layout>
  );
}

