"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { customerAPI } from "@/lib/api";
import Layout from "@/components/Layout";

interface Offer {
  id: number;
  price: number;
  eta_minutes: number | null;
  status: string;
  provider: {
    id: number;
    name: string | null;
    provider_profile: any;
  };
}

interface ServiceRequestData {
  id: number;
  service_type: string;
  vehicle_type: string;
  description: string | null;
  price_offered: number;
  status: string;
  created_at: string;
  offers: Offer[];
  job: any;
}

export default function CustomerOffers() {
  const router = useRouter();
  const params = useParams();
  const requestId = parseInt(params.requestId as string);
  const { isAuthenticated, isCustomer, isLoading: authLoading } = useAuth();

  const [request, setRequest] = useState<ServiceRequestData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [acceptingOfferId, setAcceptingOfferId] = useState<number | null>(null);

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && (!isAuthenticated || !isCustomer)) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, isCustomer, router]);

  // Fetch request data
  const fetchRequest = async () => {
    try {
      const response = await customerAPI.getServiceRequest(requestId);
      setRequest(response.data);
      setLoading(false);

      // If job exists, redirect to job page
      if (response.data.job) {
        router.push(`/customer/job/${response.data.job.id}`);
      }
    } catch (err: any) {
      console.error('Fetch error:', err);
      setError(err.response?.data?.detail || 'Failed to load request');
      setLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    if (isAuthenticated && isCustomer && requestId) {
      fetchRequest();
    }
  }, [isAuthenticated, isCustomer, requestId]);

  // Polling every 5 seconds
  useEffect(() => {
    if (!request || request.job) return;

    const interval = setInterval(() => {
      fetchRequest();
    }, 5000);

    return () => clearInterval(interval);
  }, [request]);

  const handleAcceptOffer = async (offerId: number) => {
    setAcceptingOfferId(offerId);
    setError('');

    try {
      const response = await customerAPI.acceptOffer(offerId);
      const jobId = response.data.id;

      // Redirect to job page
      router.push(`/customer/job/${jobId}`);
    } catch (err: any) {
      console.error('Accept error:', err);
      setError(err.response?.data?.detail || 'Failed to accept offer');
      setAcceptingOfferId(null);
    }
  };

  if (authLoading || loading) {
    return (
      <Layout>
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading offers...</p>
        </div>
      </Layout>
    );
  }

  if (error && !request) {
    return (
      <Layout>
        <div className="py-8">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
            {error}
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

  if (!request) return null;

  const offers = request.offers || [];
  const pendingOffers = offers.filter(o => o.status === 'pending');

  return (
    <Layout>
      <div className="py-8">
        {/* Request Summary */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Your Request
          </h2>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Service:</span>
              <span className="font-medium text-gray-900 capitalize">
                {request.service_type.replace('_', ' ')}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Vehicle:</span>
              <span className="font-medium text-gray-900 capitalize">
                {request.vehicle_type}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Your Price:</span>
              <span className="font-medium text-gray-900">
                ${request.price_offered.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Status:</span>
              <span className="px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800 capitalize">
                {request.status.replace('_', ' ')}
              </span>
            </div>
          </div>
          {request.description && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-600">{request.description}</p>
            </div>
          )}
        </div>

        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Offers Section */}
        <div>
          <h2 className="text-lg font-bold text-gray-900 mb-4">
            Offers Received ({pendingOffers.length})
          </h2>

          {pendingOffers.length === 0 ? (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
              <div className="text-4xl mb-3">⏳</div>
              <h3 className="font-semibold text-gray-900 mb-2">
                We're notifying nearby helpers...
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                Providers in your area are being notified. You'll see offers here as they arrive.
              </p>
              <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
                <div className="animate-pulse">●</div>
                <span>Refreshing automatically...</span>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {pendingOffers.map((offer) => (
                <div
                  key={offer.id}
                  className="bg-white rounded-lg shadow-md p-6 border-2 border-gray-200 hover:border-indigo-300 transition"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {offer.provider.name || `Provider #${offer.provider.id}`}
                      </h3>
                      {offer.provider.provider_profile && (
                        <div className="flex items-center gap-2 mt-1">
                          {offer.provider.provider_profile.is_verified && (
                            <span className="text-xs text-green-600">✓ Verified</span>
                          )}
                          {offer.provider.provider_profile.average_rating && (
                            <span className="text-xs text-gray-600">
                              ⭐ {offer.provider.provider_profile.average_rating.toFixed(1)}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <p className="text-2xl font-bold text-indigo-600">
                        ${offer.price.toFixed(2)}
                      </p>
                      {offer.price < request.price_offered && (
                        <p className="text-xs text-green-600">
                          💰 ${(request.price_offered - offer.price).toFixed(2)} less than your offer
                        </p>
                      )}
                    </div>
                    {offer.eta_minutes && (
                      <div className="text-right">
                        <p className="text-sm text-gray-600">ETA</p>
                        <p className="font-semibold text-gray-900">
                          {offer.eta_minutes} min
                        </p>
                      </div>
                    )}
                  </div>

                  <button
                    onClick={() => handleAcceptOffer(offer.id)}
                    disabled={acceptingOfferId !== null}
                    className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition duration-200"
                  >
                    {acceptingOfferId === offer.id ? 'Accepting...' : '✓ Accept This Offer'}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Back Button */}
        <button
          onClick={() => router.push('/customer/home')}
          className="mt-6 text-gray-600 hover:text-gray-900 font-medium"
        >
          ← Back to Home
        </button>
      </div>
    </Layout>
  );
}

