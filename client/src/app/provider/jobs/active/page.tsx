"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { providerAPI } from "@/lib/api";
import Layout from "@/components/Layout";

interface ActiveJob {
  id: number;
  status: string;
  created_at: string;
  service_request: {
    service_type: string;
    vehicle_type: string;
  };
  offer: {
    price: number;
  };
}

export default function ProviderActiveJobs() {
  const router = useRouter();
  const { isAuthenticated, isProvider, isLoading: authLoading } = useAuth();
  
  const [jobs, setJobs] = useState<ActiveJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Redirect if not authenticated or not provider
  useEffect(() => {
    if (!authLoading && (!isAuthenticated || !isProvider)) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, isProvider, router]);

  // Fetch active jobs
  const fetchJobs = async () => {
    try {
      const response = await providerAPI.getActiveJobs();
      setJobs(response.data);
      setLoading(false);
    } catch (err: any) {
      console.error('Fetch error:', err);
      setError(err.response?.data?.detail || 'Failed to load jobs');
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated && isProvider) {
      fetchJobs();
    }
  }, [isAuthenticated, isProvider]);

  if (authLoading || loading) {
    return (
      <Layout>
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading active jobs...</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            My Active Jobs
          </h1>
          <p className="text-gray-600">
            {jobs.length} active job{jobs.length !== 1 ? 's' : ''}
          </p>
        </div>

        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {jobs.length === 0 ? (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-8 text-center">
            <div className="text-4xl mb-3">📋</div>
            <h3 className="font-semibold text-gray-900 mb-2">
              No active jobs
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              Your accepted jobs will appear here
            </p>
            <button
              onClick={() => router.push('/provider/requests')}
              className="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
            >
              View Nearby Requests →
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {jobs.map((job) => (
              <div
                key={job.id}
                onClick={() => router.push(`/provider/job/${job.id}`)}
                className="bg-white rounded-lg shadow-md p-6 border-2 border-gray-200 hover:border-indigo-300 cursor-pointer transition"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-bold text-lg text-gray-900 capitalize">
                      {job.service_request.service_type.replace('_', ' ')}
                    </h3>
                    <p className="text-sm text-gray-600 capitalize">
                      {job.service_request.vehicle_type}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xl font-bold text-green-600">
                      ${job.offer.price.toFixed(2)}
                    </p>
                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800 capitalize">
                      {job.status.replace('_', ' ')}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Job #{job.id}</span>
                  <span>{new Date(job.created_at).toLocaleString()}</span>
                </div>

                <div className="mt-4 pt-4 border-t border-gray-200">
                  <p className="text-sm text-indigo-600 font-medium">
                    Tap to view details →
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}

        <button
          onClick={() => router.push('/provider/home')}
          className="mt-6 text-gray-600 hover:text-gray-900 font-medium"
        >
          ← Back to Home
        </button>
      </div>
    </Layout>
  );
}

