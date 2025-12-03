"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { providerAPI } from "@/lib/api";
import Layout from "@/components/Layout";

interface NearbyRequest {
  id: number;
  customer_id: number;
  service_type: string;
  vehicle_type: string;
  description: string | null;
  price_offered: number;
  lat: number;
  lng: number;
  status: string;
  distance_km: number;
  created_at: string;
}

export default function ProviderRequests() {
  const router = useRouter();
  const { isAuthenticated, isProvider, isLoading: authLoading } = useAuth();
  
  const [requests, setRequests] = useState<NearbyRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [radiusKm, setRadiusKm] = useState(10);
  
  // Track offer forms
  const [offerForms, setOfferForms] = useState<Record<number, { price: string; eta: string }>>({});
  const [sendingOffer, setSendingOffer] = useState<number | null>(null);

  // Redirect if not authenticated or not provider
  useEffect(() => {
    if (!authLoading && (!isAuthenticated || !isProvider)) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, isProvider, router]);

  // Fetch nearby requests
  const fetchRequests = async (isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
    setError('');

    try {
      const response = await providerAPI.getNearbyRequests(radiusKm);
      setRequests(response.data);
      
      // Initialize offer forms with default values
      const forms: Record<number, { price: string; eta: string }> = {};
      response.data.forEach((req: NearbyRequest) => {
        forms[req.id] = {
          price: req.price_offered.toString(),
          eta: Math.ceil(req.distance_km * 3).toString() // 3 min per km estimate
        };
      });
      setOfferForms(forms);
    } catch (err: any) {
      console.error('Fetch error:', err);
      setError(err.response?.data?.detail || 'Failed to load requests');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated && isProvider) {
      fetchRequests();
    }
  }, [isAuthenticated, isProvider, radiusKm]);

  const handleSendOffer = async (requestId: number, useCustomPrice: boolean) => {
    const form = offerForms[requestId];
    if (!form) return;

    setSendingOffer(requestId);
    setError('');

    try {
      const request = requests.find(r => r.id === requestId);
      if (!request) return;

      await providerAPI.createOffer({
        service_request_id: requestId,
        price: useCustomPrice ? parseFloat(form.price) : request.price_offered,
        eta_minutes: parseInt(form.eta) || null
      });

      alert('Offer sent successfully! The customer will review your offer.');
      
      // Refresh the list to remove this request
      fetchRequests(true);
    } catch (err: any) {
      console.error('Offer error:', err);
      setError(err.response?.data?.detail || 'Failed to send offer');
    } finally {
      setSendingOffer(null);
    }
  };

  const updateOfferForm = (requestId: number, field: 'price' | 'eta', value: string) => {
    setOfferForms(prev => ({
      ...prev,
      [requestId]: {
        ...prev[requestId],
        [field]: value
      }
    }));
  };

  if (authLoading || loading) {
    return (
      <Layout>
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading nearby requests...</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-1">
              Nearby Requests
            </h1>
            <p className="text-sm text-gray-600">
              {requests.length} request{requests.length !== 1 ? 's' : ''} within {radiusKm} km
            </p>
          </div>
          <button
            onClick={() => fetchRequests(true)}
            disabled={refreshing}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition"
          >
            {refreshing ? '⟳' : '🔄'} Refresh
          </button>
        </div>

        {/* Radius Selector */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Search Radius: {radiusKm} km
          </label>
          <input
            type="range"
            min="5"
            max="50"
            step="5"
            value={radiusKm}
            onChange={(e) => setRadiusKm(parseInt(e.target.value))}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-gray-600 mt-1">
            <span>5 km</span>
            <span>50 km</span>
          </div>
        </div>

        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Requests List */}
        {requests.length === 0 ? (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-8 text-center">
            <div className="text-4xl mb-3">🔍</div>
            <h3 className="font-semibold text-gray-900 mb-2">
              No requests nearby
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              Try increasing your search radius or check back later
            </p>
            <button
              onClick={() => setRadiusKm(prev => Math.min(prev + 10, 50))}
              className="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
            >
              Increase radius to {Math.min(radiusKm + 10, 50)} km
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {requests.map((request) => {
              const form = offerForms[request.id] || { price: '', eta: '' };
              
              return (
                <div
                  key={request.id}
                  className="bg-white rounded-lg shadow-md p-6 border-2 border-gray-200"
                >
                  {/* Request Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="font-bold text-lg text-gray-900 capitalize">
                        {request.service_type.replace('_', ' ')}
                      </h3>
                      <p className="text-sm text-gray-600 capitalize">
                        {request.vehicle_type}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-indigo-600">
                        ${request.price_offered.toFixed(2)}
                      </p>
                      <p className="text-xs text-gray-600">
                        {request.distance_km.toFixed(1)} km away
                      </p>
                    </div>
                  </div>

                  {/* Description */}
                  {request.description && (
                    <div className="mb-4 p-3 bg-gray-50 rounded">
                      <p className="text-sm text-gray-700">
                        "{request.description}"
                      </p>
                    </div>
                  )}

                  {/* Offer Form */}
                  <div className="bg-gray-50 rounded-lg p-4 mb-4">
                    <h4 className="font-semibold text-gray-900 mb-3 text-sm">
                      Your Offer
                    </h4>
                    <div className="grid grid-cols-2 gap-3 mb-3">
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">
                          Your Price ($)
                        </label>
                        <input
                          type="number"
                          value={form.price}
                          onChange={(e) => updateOfferForm(request.id, 'price', e.target.value)}
                          step="0.01"
                          min="1"
                          disabled={sendingOffer === request.id}
                          className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">
                          ETA (minutes)
                        </label>
                        <input
                          type="number"
                          value={form.eta}
                          onChange={(e) => updateOfferForm(request.id, 'eta', e.target.value)}
                          min="1"
                          disabled={sendingOffer === request.id}
                          className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <button
                        onClick={() => handleSendOffer(request.id, false)}
                        disabled={sendingOffer !== null}
                        className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-semibold py-2 px-4 rounded text-sm transition"
                      >
                        {sendingOffer === request.id ? 'Sending...' : '✓ Accept Offered Price'}
                      </button>
                      <button
                        onClick={() => handleSendOffer(request.id, true)}
                        disabled={sendingOffer !== null}
                        className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-semibold py-2 px-4 rounded text-sm transition"
                      >
                        {sendingOffer === request.id ? 'Sending...' : '📤 Send Counter-Offer'}
                      </button>
                    </div>
                  </div>

                  {/* Additional Info */}
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>Request #{request.id}</span>
                    <span>{new Date(request.created_at).toLocaleString()}</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Back Button */}
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

