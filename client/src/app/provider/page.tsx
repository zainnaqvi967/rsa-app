"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";

export default function ProviderDashboard() {
  const router = useRouter();
  const { isAuthenticated, isProvider, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated || !isProvider) {
        router.push('/login');
      } else {
        // Redirect to provider home
        router.push('/provider/home');
      }
    }
  }, [isLoading, isAuthenticated, isProvider, router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
    </div>
  );
}
