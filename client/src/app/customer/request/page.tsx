"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { useLocation } from "@/context/LocationContext";
import { customerAPI } from "@/lib/api";
import Layout from "@/components/Layout";

const SERVICE_TYPES = [
  { value: 'flat_tyre', label: '🔧 Flat Tire' },
  { value: 'jump_start', label: '🔋 Jump Start' },
  { value: 'fuel', label: '⛽ Fuel Delivery' },
  { value: 'tow', label: '🚚 Towing' },
  { value: 'key_lock', label: '🔑 Lockout' },
  { value: 'other', label: '➕ Other' },
];

const VEHICLE_TYPES = [
  { value: 'bike', label: '🏍️ Bike/Motorcycle' },
  { value: 'car', label: '🚗 Car' },
];

export default function CustomerRequest() {
  const router = useRouter();
  const { isAuthenticated, isCustomer, isLoading: authLoading } = useAuth();
  const { location } = useLocation();

  const [serviceType, setServiceType] = useState('flat_tyre');
  const [vehicleType, setVehicleType] = useState('car');
  const [description, setDescription] = useState('');
  const [priceOffered, setPriceOffered] = useState('75');
  const [manualLat, setManualLat] = useState('');
  const [manualLng, setManualLng] = useState('');
  const [useManualLocation, setUseManualLocation] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Redirect if not authenticated or not customer
  useEffect(() => {
    if (!authLoading && (!isAuthenticated || !isCustomer)) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, isCustomer, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Determine which location to use
      let lat: number, lng: number;

      if (useManualLocation) {
        lat = parseFloat(manualLat);
        lng = parseFloat(manualLng);

        if (isNaN(lat) || isNaN(lng)) {
          throw new Error('Invalid coordinates');
        }
      } else if (location) {
        lat = location.lat;
        lng = location.lng;
      } else {
        throw new Error('Location is required. Please enable location services or enter manually.');
      }

      // Create service request
      const response = await customerAPI.createServiceRequest({
        service_type: serviceType,
        vehicle_type: vehicleType,
        description: description.trim() || null,
        price_offered: parseFloat(priceOffered),
        lat,
        lng,
      });

      const requestId = response.data.id;

      // Redirect to offers page
      router.push(`/customer/offers/${requestId}`);
    } catch (err: any) {
      console.error('Request creation error:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to create request');
    } finally {
      setLoading(false);
    }
  };

  if (authLoading || !isAuthenticated) {
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
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Request Assistance
          </h1>
          <p className="text-gray-600">
            Fill in the details and nearby providers will send you offers
          </p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Service Type */}
          <div>
            <label htmlFor="serviceType" className="block text-sm font-medium text-gray-700 mb-2">
              What do you need? *
            </label>
            <select
              id="serviceType"
              value={serviceType}
              onChange={(e) => setServiceType(e.target.value)}
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              {SERVICE_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Vehicle Type */}
          <div>
            <label htmlFor="vehicleType" className="block text-sm font-medium text-gray-700 mb-2">
              Vehicle Type *
            </label>
            <select
              id="vehicleType"
              value={vehicleType}
              onChange={(e) => setVehicleType(e.target.value)}
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              {VEHICLE_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
              Description (Optional)
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="E.g., Flat tire on Highway 101 near Exit 45"
              rows={3}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>

          {/* Price Offered */}
          <div>
            <label htmlFor="priceOffered" className="block text-sm font-medium text-gray-700 mb-2">
              Price You're Willing to Pay ($) *
            </label>
            <input
              id="priceOffered"
              type="number"
              value={priceOffered}
              onChange={(e) => setPriceOffered(e.target.value)}
              min="1"
              step="0.01"
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-600 mt-1">
              Providers can offer lower or match your price
            </p>
          </div>

          {/* Location */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-medium text-gray-900">Location *</h3>
              <button
                type="button"
                onClick={() => setUseManualLocation(!useManualLocation)}
                className="text-sm text-indigo-600 hover:text-indigo-700"
              >
                {useManualLocation ? 'Use Auto Location' : 'Enter Manually'}
              </button>
            </div>

            {!useManualLocation ? (
              <div>
                {location ? (
                  <div className="flex items-center gap-2 text-sm text-green-600">
                    <span>✓</span>
                    <span>Using your current location</span>
                  </div>
                ) : (
                  <div className="text-sm text-yellow-600">
                    ⚠ Location not detected. Enable location services or enter manually.
                  </div>
                )}
                {location && (
                  <p className="text-xs text-gray-600 mt-2">
                    {location.lat.toFixed(4)}, {location.lng.toFixed(4)}
                  </p>
                )}
              </div>
            ) : (
              <div className="space-y-3">
                <input
                  type="number"
                  value={manualLat}
                  onChange={(e) => setManualLat(e.target.value)}
                  placeholder="Latitude (e.g., 37.7749)"
                  step="any"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                />
                <input
                  type="number"
                  value={manualLng}
                  onChange={(e) => setManualLng(e.target.value)}
                  placeholder="Longitude (e.g., -122.4194)"
                  step="any"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                />
              </div>
            )}
          </div>

          {/* Submit Button */}
          <div className="space-y-3">
            <button
              type="submit"
              disabled={loading || (!location && !useManualLocation)}
              className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg shadow-lg transition duration-200"
            >
              {loading ? 'Creating Request...' : '📤 Submit Request'}
            </button>

            <button
              type="button"
              onClick={() => router.back()}
              className="w-full text-gray-600 hover:text-gray-900 font-medium"
            >
              ← Back
            </button>
          </div>
        </form>
      </div>
    </Layout>
  );
}

