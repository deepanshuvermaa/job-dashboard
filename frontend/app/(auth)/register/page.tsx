"use client";
import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(email, password, name);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center px-4">
      {/* Video Background */}
      <video
        autoPlay
        loop
        muted
        playsInline
        className="absolute inset-0 w-full h-full object-cover z-0"
        style={{ filter: "brightness(0.3)" }}
      >
        <source
          src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260314_131748_f2ca2a28-fed7-44c8-b9a9-bd9acdd5ec31.mp4"
          type="video/mp4"
        />
      </video>

      <div className="relative z-10 w-full max-w-[420px] animate-fade-rise">
        <div className="text-center mb-10">
          <Link href="/" className="inline-block">
            <h1
              className="text-5xl text-white tracking-tight"
              style={{ fontFamily: "var(--font-display-serif), 'Instrument Serif', serif" }}
            >
              JobFlow<sup className="text-sm">®</sup>
            </h1>
          </Link>
          <p className="text-white/40 text-base mt-2">Create your account</p>
        </div>

        <div className="liquid-glass rounded-2xl p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-white/60 mb-2">Full Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full bg-white/5 text-white rounded-xl px-4 py-3 border border-white/10 outline-none focus:border-white/30 focus:ring-1 focus:ring-white/10 placeholder:text-white/20 text-sm"
                placeholder="John Doe"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-white/60 mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-white/5 text-white rounded-xl px-4 py-3 border border-white/10 outline-none focus:border-white/30 focus:ring-1 focus:ring-white/10 placeholder:text-white/20 text-sm"
                placeholder="you@example.com"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-white/60 mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-white/5 text-white rounded-xl px-4 py-3 border border-white/10 outline-none focus:border-white/30 focus:ring-1 focus:ring-white/10 placeholder:text-white/20 text-sm"
                placeholder="At least 8 characters"
                minLength={8}
                required
              />
            </div>

            {error && <p className="text-sm text-red-400">{error}</p>}

            <button
              type="submit"
              disabled={loading}
              className="w-full liquid-glass rounded-full py-3.5 text-white text-sm font-medium hover:scale-[1.02] transition-transform disabled:opacity-50"
            >
              {loading ? "Creating account..." : "Create Account"}
            </button>
          </form>

          <p className="text-sm text-white/30 text-center mt-6">
            Already have an account?{" "}
            <Link href="/login" className="text-white/60 hover:text-white transition-colors">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
