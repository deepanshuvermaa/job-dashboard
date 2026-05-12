const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

async function request<T = any>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };
  // Don't set Content-Type for FormData (file uploads)
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      window.location.href = "/login";
    }
    throw new Error("Unauthorized");
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }

  return res.json();
}

export const api = {
  // ── Auth ──
  register: (data: { email: string; password: string; full_name: string }) =>
    request("/api/auth/register", { method: "POST", body: JSON.stringify(data) }),
  login: (data: { email: string; password: string }) =>
    request("/api/auth/login", { method: "POST", body: JSON.stringify(data) }),
  me: () => request("/api/auth/me"),

  // ── Jobs (v2) ──
  getJobs: (params: Record<string, any>) => {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") qs.set(k, String(v));
    });
    return request(`/api/jobs?${qs.toString()}`);
  },
  getJob: (id: string) => request(`/api/jobs/${id}`),
  patchJob: (id: string, data: Record<string, any>) =>
    request(`/api/jobs/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  getJobStats: () => request("/api/jobs/stats"),
  getCategories: () => request("/api/jobs/categories/list"),
  getLocations: () => request("/api/jobs/locations/list"),
  runCleanup: () => request("/api/jobs/cleanup", { method: "POST" }),
  ingestJobs: (jobs: any[], source: string) =>
    request("/api/jobs/ingest", { method: "POST", body: JSON.stringify({ jobs, source }) }),

  // ── Applications (v2) ──
  getApplications: (status?: string) =>
    request(`/api/jobs/applications${status ? `?status=${status}` : ""}`),
  getApplicationStats: () => request("/api/jobs/applications/stats"),

  // ── Legacy: Job Search (LinkedIn scraper) ──
  searchJobs: (params: Record<string, any>) => {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") qs.set(k, String(v));
    });
    return request(`/api/jobs/search?${qs.toString()}`);
  },

  // ── Legacy: Portal Scanner ──
  getPortalConfig: () => request("/api/portals/config"),
  scanPortals: (data?: { keyword_filter?: string; location_filter?: string }) =>
    request("/api/portals/scan", { method: "POST", body: JSON.stringify(data || {}) }),
  getScanStatus: () => request("/api/portals/scan/status"),
  detectATS: () => request("/api/portals/detect-ats", { method: "POST" }),
  getDetectStatus: () => request("/api/portals/detect-ats/status"),
  scanExtended: () => request("/api/portals/scan-extended", { method: "POST" }),

  // ── Legacy: Easy Apply ──
  startEasyApply: (data: any) =>
    request("/api/jobs/easy-apply/start", { method: "POST", body: JSON.stringify(data) }),
  applyToJob: (job_url: string) =>
    request("/api/jobs/apply", { method: "POST", body: JSON.stringify({ job_url }) }),

  // ── Legacy: Settings ──
  getSettings: () => request("/api/settings"),
  updateSettings: (data: any) =>
    request("/api/settings", { method: "PUT", body: JSON.stringify(data) }),

  // ── Legacy: Profile & Resume ──
  getProfile: () => request("/api/profile/get"),
  uploadResume: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request("/api/profile/upload-resume", { method: "POST", body: form });
  },
  updateProfile: (data: any) =>
    request("/api/profile/update", { method: "POST", body: JSON.stringify(data) }),
  analyzeJD: (data: any) =>
    request("/api/resume/analyze-jd", { method: "POST", body: JSON.stringify(data) }),
  generateResume: (data: any) =>
    request("/api/resume/generate", { method: "POST", body: JSON.stringify(data) }),

  // ── Legacy: Evaluations ──
  getEvaluations: (minGrade?: string) =>
    request(`/api/jobs/evaluations${minGrade ? `?min_grade=${minGrade}` : ""}`),

  // ── Legacy: Messages ──
  generateMessages: () => request("/api/messages/generate", { method: "POST" }),
  sendMessages: (data: any) =>
    request("/api/messages/send", { method: "POST", body: JSON.stringify(data) }),

  // ── Legacy: Automation ──
  runAutomation: (data: any) =>
    request("/api/automation/run", { method: "POST", body: JSON.stringify(data) }),
};
