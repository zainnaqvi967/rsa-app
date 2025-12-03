"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { customerAPI } from "@/lib/api";
import Layout from "@/components/Layout";

interface JobData {
  id: number;
  status: string;
  created_at: string;
  updated_at: string;
  service_request: {
    id: number;
    service_type: string;
    vehicle_type: string;
    description: string | null;
    lat: number;
    lng: number;
  };
  offer: {
    id: number;
    price: number;
    eta_minutes: number | null;
    provider: {
      id: number;
      name: string | null;
      phone: string;
      provider_profile: {
        city: string | null;
        average_rating: number;
        total_ratings: number;
        current_lat: number | null;
        current_lng: number | null;
        is_verified: boolean;
      } | null;
    };
  };
}

const JOB_STATUS_INFO: Record<string, { label: string; color: string; icon: string }> = {
  assigned: { label: 'Assigned', color: 'bg-blue-100 text-blue-800', icon: '📝' },
  on_the_way: { label: 'On the Way', color: 'bg-yellow-100 text-yellow-800', icon: '🚗' },
  arrived: { label: 'Arrived', color: 'bg-orange-100 text-orange-800', icon: '📍' },
  in_progress: { label: 'In Progress', color: 'bg-purple-100 text-purple-800', icon: '🔧' },
  completed: { label: 'Completed', color: 'bg-green-100 text-green-800', icon: '✅' },
  cancelled: { label: 'Cancelled', color: 'bg-red-100 text-red-800', icon: '❌' },
};

export default function CustomerJobTracking() {
  const router = useRouter();
  const params = useParams();
  const jobId = parseInt(params.jobId as string);
  const { isAuthenticated, isCustomer, isLoading: authLoading } = useAuth();

  const [job, setJob] = useState<JobData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [rating, setRating] = useState(5);

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && (!isAuthenticated || !isCustomer)) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, isCustomer, router]);

  // Fetch job data
  const fetchJob = async () => {
    try {
      const response = await customerAPI.getJob(jobId);
      setJob(response.data);
      setLoading(false);
    } catch (err: any) {
      console.error('Fetch error:', err);
      setError(err.response?.data?.detail || 'Failed to load job');
      setLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    if (isAuthenticated && isCustomer && jobId) {
      fetchJob();
    }
  }, [isAuthenticated, isCustomer, jobId]);

  // Polling every 10 seconds (unless completed/cancelled)
  useEffect(() => {
    if (!job || job.status === 'completed' || job.status === 'cancelled') return;

    const interval = setInterval(() => {
      fetchJob();
    }, 10000);

    return () => clearInterval(interval);
  }, [job]);

  if (authLoading || loading) {
    return (
      <Layout>
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading job details...</p>
        </div>
      </Layout>
    );
  }

  if (error || !job) {
    return (
      <Layout>
        <div className="py-8">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
            {error || 'Job not found'}
          </div>
          <button
            onClick={() => router.push('/customer/home')}
            className="text-indigo-600 hover:text-indigo-700"
          >
            ← Back to Home
          </button>
        </div>
      </Layout>
    );
  }

  const statusInfo = JOB_STATUS_INFO[job.status] || JOB_STATUS_INFO.assigned;
  const provider = job.offer.provider;
  const hasProviderLocation = provider.provider_profile?.current_lat && provider.provider_profile?.current_lng;

  return (
    <Layout>
      <div className="py-8">
        {/* Job Status Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">Job Status</h2>
            <span className={`px-3 py-1 text-sm font-medium rounded-full ${statusInfo.color}`}>
              {statusInfo.icon} {statusInfo.label}
            </span>
          </div>

          {/* Status Messages */}
          <div className="text-center py-4">
            {job.status === 'assigned' && (
              <p className="text-gray-700">🎯 Your helper has been assigned and notified</p>
            )}
            {job.status === 'on_the_way' && (
              <p className="text-gray-700">🚗 Your helper is on the way!</p>
            )}
            {job.status === 'arrived' && (
              <p className="text-gray-700">📍 Your helper has arrived at your location</p>
            )}
            {job.status === 'in_progress' && (
              <p className="text-gray-700">🔧 Service is in progress...</p>
            )}
            {job.status === 'completed' && (
              <div>
                <p className="text-green-600 font-semibold mb-2">✅ Job completed successfully!</p>
                <p className="text-sm text-gray-600">Thank you for using our service</p>
              </div>
            )}
            {job.status === 'cancelled' && (
              <p className="text-red-600">❌ Job was cancelled</p>
            )}
          </div>
        </div>

        {/* Service Details */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="font-semibold text-gray-900 mb-4">Service Details</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Service:</span>
              <span className="font-medium text-gray-900 capitalize">
                {job.service_request.service_type.replace('_', ' ')}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Vehicle:</span>
              <span className="font-medium text-gray-900 capitalize">
                {job.service_request.vehicle_type}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Price:</span>
              <span className="font-medium text-gray-900">
                ${job.offer.price.toFixed(2)}
              </span>
            </div>
          </div>
          {job.service_request.description && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-600">{job.service_request.description}</p>
            </div>
          )}
        </div>

        {/* Provider Info */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="font-semibold text-gray-900 mb-4">Your Helper</h3>
          <div className="flex items-start gap-4">
            <div className="text-4xl">👤</div>
            <div className="flex-1">
              <h4 className="font-medium text-gray-900">
                {provider.name || `Provider #${provider.id}`}
              </h4>
              {provider.provider_profile && (
                <div className="mt-2 space-y-1 text-sm">
                  {provider.provider_profile.city && (
                    <p className="text-gray-600">
                      📍 {provider.provider_profile.city}
                    </p>
                  )}
                  <div className="flex items-center gap-3">
                    {provider.provider_profile.is_verified && (
                      <span className="text-green-600 text-xs">✓ Verified</span>
                    )}
                    {provider.provider_profile.total_ratings > 0 && (
                      <span className="text-gray-600 text-xs">
                        ⭐ {provider.provider_profile.average_rating.toFixed(1)} ({provider.provider_profile.total_ratings} ratings)
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Map */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="font-semibold text-gray-900 mb-4">Location</h3>
          <div className="bg-gradient-to-br from-blue-100 to-green-100 rounded-lg h-64 relative overflow-hidden">
            {/* Simple map placeholder */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                {/* Customer location */}
                <div className="mb-6">
                  <div className="text-3xl mb-1">📍</div>
                  <p className="text-xs text-gray-700 font-medium">Your Location</p>
                  <p className="text-xs text-gray-600">
                    {job.service_request.lat.toFixed(4)}, {job.service_request.lng.toFixed(4)}
                  </p>
                </div>

                {/* Provider location */}
                {hasProviderLocation && (
                  <div>
                    <div className="text-3xl mb-1">🚗</div>
                    <p className="text-xs text-gray-700 font-medium">Provider Location</p>
                    <p className="text-xs text-gray-600">
                      {provider.provider_profile!.current_lat!.toFixed(4)}, {provider.provider_profile!.current_lng!.toFixed(4)}
                    </p>
                  </div>
                )}
              </div>
            </div>

            {!hasProviderLocation && (
              <div className="absolute bottom-4 left-4 right-4 bg-white/90 rounded p-2 text-xs text-center text-gray-600">
                Provider location will appear here when they're on the way
              </div>
            )}
          </div>
        </div>

        {/* Rating Form (if completed) */}
        {job.status === 'completed' && (
          <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-6 mb-6">
            <h3 className="font-semibold text-gray-900 mb-4">Rate Your Experience</h3>
            <div className="flex justify-center gap-2 mb-4">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  onClick={() => setRating(star)}
                  className="text-3xl hover:scale-110 transition"
                >
                  {star <= rating ? '⭐' : '☆'}
                </button>
              ))}
            </div>
            <p className="text-center text-sm text-gray-600 mb-4">
              {rating === 5 && 'Excellent!'}
              {rating === 4 && 'Very Good!'}
              {rating === 3 && 'Good'}
              {rating === 2 && 'Fair'}
              {rating === 1 && 'Needs Improvement'}
            </p>
            <button
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg"
              onClick={() => alert('Rating system coming soon!')}
            >
              Submit Rating
            </button>
          </div>
        )}

        {/* Action Buttons */}
        <div className="space-y-3">
          {job.status === 'completed' && (
            <button
              onClick={() => router.push('/customer/home')}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg"
            >
              Request Another Service
            </button>
          )}
          
          <button
            onClick={() => router.push('/customer/home')}
            className="w-full text-gray-600 hover:text-gray-900 font-medium"
          >
            ← Back to Home
          </button>
        </div>

        {/* Auto-refresh indicator */}
        {job.status !== 'completed' && job.status !== 'cancelled' && (
          <div className="mt-4 text-center text-xs text-gray-500">
            <div className="flex items-center justify-center gap-2">
              <div className="animate-pulse">●</div>
              <span>Auto-updating every 10 seconds</span>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}

