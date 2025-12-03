"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";

export default function CustomerDashboard() {
  const router = useRouter();
  const { isAuthenticated, isCustomer, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated || !isCustomer) {
        router.push('/login');
      } else {
        // Redirect to customer home
        router.push('/customer/home');
      }
    }
  }, [isLoading, isAuthenticated, isCustomer, router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
    </div>
  );
}

