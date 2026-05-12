"use client";
import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Sidebar from "@/components/layout/Sidebar";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-eggshell flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-obsidian border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="min-h-screen bg-eggshell">
      <Sidebar />
      <main className="ml-[240px] min-h-screen px-10 py-8">
        <div className="max-w-page mx-auto">{children}</div>
      </main>
    </div>
  );
}
