/**
 * Location Context
 * 
 * Shares geolocation data across customer pages.
 */

"use client";

import React, { createContext, useState, useContext, ReactNode } from 'react';

interface Location {
  lat: number;
  lng: number;
}

interface LocationContextType {
  location: Location | null;
  setLocation: (location: Location | null) => void;
}

const LocationContext = createContext<LocationContextType>({
  location: null,
  setLocation: () => {},
});

export function LocationProvider({ children }: { children: ReactNode }) {
  const [location, setLocation] = useState<Location | null>(null);

  return (
    <LocationContext.Provider value={{ location, setLocation }}>
      {children}
    </LocationContext.Provider>
  );
}

export function useLocation() {
  const context = useContext(LocationContext);
  if (!context) {
    throw new Error('useLocation must be used within LocationProvider');
  }
  return context;
}

