"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { providerAPI } from "@/lib/api";
import Layout from "@/components/Layout";

interface JobData {
  id: number;
  status: string;
  created_at: string;
  updated_at: string;
  service_request: {
    id: number;
    customer_id: number;
    service_type: string;
    vehicle_type: string;
    description: string | null;
    price_offered: number;
    lat: number;
    lng: number;
  };
  offer: {
    id: number;
    price: number;
    eta_minutes: number | null;
    provider: any;
  };
}

const JOB_STATUSES = [
  { value: 'on_the_way', label: 'On the Way', icon: '🚗', color: 'bg-yellow-600' },
  { value: 'arrived', label: 'Arrived', icon: '📍', color: 'bg-orange-600' },
  { value: 'in_progress', label: 'In Progress', icon: '🔧', color: 'bg-purple-600' },
  { value: 'completed', label: 'Completed', icon: '✅', color: 'bg-green-600' },
];

export default function ProviderJobDetail() {
  const router = useRouter();
  const params = useParams();
  const jobId = parseInt(params.jobId as string);
  const { isAuthenticated, isProvider, isLoading: authLoading } = useAuth();
  
  const [job, setJob] = useState<JobData | null>(null);
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

  // Fetch job data
  const fetchJob = async () => {
    try {
      // Get all active jobs and find this one
      const response = await providerAPI.getActiveJobs();
      const jobData = response.data.find((j: JobData) => j.id === jobId);
      
      if (jobData) {
        setJob(jobData);
      } else {
        setError('Job not found or no longer active');
      }
      setLoading(false);
    } catch (err: any) {
      console.error('Fetch error:', err);
      setError(err.response?.data?.detail || 'Failed to load job');
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated && isProvider && jobId) {
      fetchJob();
    }
  }, [isAuthenticated, isProvider, jobId]);

  // Poll every 10 seconds
  useEffect(() => {
    if (!job || job.status === 'completed' || job.status === 'cancelled') return;

    const interval = setInterval(() => {
      fetchJob();
    }, 10000);

    return () => clearInterval(interval);
  }, [job]);

  const handleUpdateStatus = async (newStatus: string) => {
    if (!job) return;

    setUpdatingStatus(true);
    setError('');
    setSuccess('');

    try {
      await providerAPI.updateJobStatus(jobId, newStatus);
      setSuccess(`Status updated to ${newStatus.replace('_', ' ')}`);
      fetchJob(); // Refresh job data
    } catch (err: any) {
      console.error('Update error:', err);
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

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          await providerAPI.updateLocation(
            position.coords.latitude,
            position.coords.longitude
          );
          setSuccess('Location updated successfully');
        } catch (err: any) {
          setError(err.response?.data?.detail || 'Failed to update location');
        } finally {
          setUpdatingLocation(false);
        }
      },
      (error) => {
        console.error('Geolocation error:', error);
        setError('Could not get your location');
        setUpdatingLocation(false);
      }
    );
  };

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

  if (error && !job) {
    return (
      <Layout>
        <div className="py-8">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
            {error}
          </div>
          <button
            onClick={() => router.push('/provider/home')}
            className="text-indigo-600 hover:text-indigo-700"
          >
            ← Back to Home
          </button>
        </div>
      </Layout>
    );
  }

  if (!job) return null;

  const currentStatusIndex = JOB_STATUSES.findIndex(s => s.value === job.status);

  return (
    <Layout>
      <div className="py-8">
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

        {/* Job Status Card */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Job #{job.id}
          </h2>
          <div className="flex items-center gap-2 mb-4">
            <span className="text-sm text-gray-600">Current Status:</span>
            <span className="px-3 py-1 text-sm font-medium rounded-full bg-blue-100 text-blue-800 capitalize">
              {job.status.replace('_', ' ')}
            </span>
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
              <span className="text-gray-600">Your Price:</span>
              <span className="font-medium text-green-600">
                ${job.offer.price.toFixed(2)}
              </span>
            </div>
            {job.offer.eta_minutes && (
              <div className="flex justify-between">
                <span className="text-gray-600">Estimated ETA:</span>
                <span className="font-medium text-gray-900">
                  {job.offer.eta_minutes} minutes
                </span>
              </div>
            )}
          </div>
          {job.service_request.description && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-700">
                <strong>Description:</strong> {job.service_request.description}
              </p>
            </div>
          )}
        </div>

        {/* Customer Location Map */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="font-semibold text-gray-900 mb-4">Customer Location</h3>
          <div className="bg-gradient-to-br from-blue-100 to-green-100 rounded-lg h-48 relative overflow-hidden">
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="text-4xl mb-2">📍</div>
                <p className="text-sm text-gray-700 font-medium">Customer Location</p>
                <p className="text-xs text-gray-600">
                  {job.service_request.lat.toFixed(4)}, {job.service_request.lng.toFixed(4)}
                </p>
              </div>
            </div>
          </div>
          
          <button
            onClick={handleUpdateLocation}
            disabled={updatingLocation}
            className="w-full mt-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition"
          >
            {updatingLocation ? 'Updating...' : '📍 Update My Location'}
          </button>
        </div>

        {/* Status Update Buttons */}
        {job.status !== 'completed' && job.status !== 'cancelled' && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h3 className="font-semibold text-gray-900 mb-4">Update Job Status</h3>
            <div className="space-y-3">
              {JOB_STATUSES.map((status, index) => {
                const isDisabled = 
                  updatingStatus || 
                  job.status === 'completed' || 
                  job.status === 'cancelled' ||
                  index <= currentStatusIndex;

                return (
                  <button
                    key={status.value}
                    onClick={() => handleUpdateStatus(status.value)}
                    disabled={isDisabled}
                    className={`w-full ${status.color} hover:opacity-90 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition duration-200`}
                  >
                    {status.icon} {status.label}
                  </button>
                );
              })}
            </div>
            <p className="text-xs text-gray-600 mt-4 text-center">
              Update status as you progress through the job
            </p>
          </div>
        )}

        {job.status === 'completed' && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6 text-center">
            <div className="text-4xl mb-2">✅</div>
            <h3 className="font-semibold text-green-900 mb-2">
              Job Completed!
            </h3>
            <p className="text-sm text-green-700">
              Great work! The payment will be processed soon.
            </p>
          </div>
        )}

        {/* Back Button */}
        <button
          onClick={() => router.push('/provider/home')}
          className="w-full text-gray-600 hover:text-gray-900 font-medium"
        >
          ← Back to Home
        </button>

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

