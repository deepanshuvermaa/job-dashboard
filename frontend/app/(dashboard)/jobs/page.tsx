"use client";
import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import JobCard from "@/components/jobs/JobCard";
import JobFilters from "@/components/jobs/JobFilters";
import JobDetailDrawer from "@/components/jobs/JobDetailDrawer";

interface FilterState {
  search: string;
  category: string;
  source: string;
  grade: string;
  work_mode: string;
  sort: string;
  bookmarked: boolean;
  posted_after: string;
  location: string;
  salary_min: string;
  experience_level: string;
  easy_apply: boolean;
  company: string;
}

const DEFAULT_FILTERS: FilterState = {
  search: "",
  category: "",
  source: "",
  grade: "",
  work_mode: "",
  sort: "newest",
  bookmarked: false,
  posted_after: "",
  location: "",
  salary_min: "",
  experience_level: "",
  easy_apply: false,
  company: "",
};

export default function JobsPage() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);
  const [stats, setStats] = useState<any>({});
  const [selectedJob, setSelectedJob] = useState<any | null>(null);

  const fetchJobs = useCallback(async () => {
    setLoading(true);
    try {
      const params: any = { page, per_page: 24 };
      if (filters.search) params.search = filters.search;
      if (filters.category) params.category = filters.category;
      if (filters.source) params.source = filters.source;
      if (filters.grade) params.grade = filters.grade;
      if (filters.work_mode) params.work_mode = filters.work_mode;
      if (filters.sort) params.sort = filters.sort;
      if (filters.bookmarked) params.bookmarked = true;
      if (filters.posted_after) params.posted_after = filters.posted_after;
      if (filters.location) params.location = filters.location;
      if (filters.salary_min) params.salary_min = filters.salary_min;
      if (filters.experience_level) params.experience_level = filters.experience_level;
      if (filters.easy_apply) params.easy_apply = true;
      if (filters.company) params.company = filters.company;

      const data = await api.getJobs(params);
      setJobs(data.jobs);
      setTotal(data.total);
      setTotalPages(data.total_pages);
    } catch (err) {
      console.error("Failed to fetch jobs:", err);
    } finally {
      setLoading(false);
    }
  }, [page, filters]);

  const fetchStats = useCallback(async () => {
    try {
      const data = await api.getJobStats();
      setStats(data);
    } catch (err) {
      console.error("Failed to fetch stats:", err);
    }
  }, []);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  // Debounce search
  useEffect(() => {
    setPage(1);
  }, [filters]);

  const handleBookmark = async (id: string, val: boolean) => {
    try {
      await api.patchJob(id, { is_bookmarked: val });
      setJobs((prev) =>
        prev.map((j) => (j.id === id ? { ...j, is_bookmarked: val } : j))
      );
      if (selectedJob?.id === id) {
        setSelectedJob((prev: any) => prev ? { ...prev, is_bookmarked: val } : null);
      }
    } catch (err) {
      console.error("Bookmark failed:", err);
    }
  };

  const handleMarkApplied = async (id: string) => {
    try {
      await api.markApplied(id);
      setJobs((prev) => prev.filter((j) => j.id !== id));
    } catch (err) {
      console.error("Mark applied failed:", err);
    }
  };

  const handleExport = async () => {
    try {
      const data = await api.exportJobs();
      if (data?.download_url) {
        window.open(data.download_url, "_blank");
      }
    } catch (err) {
      console.error("Export failed:", err);
    }
  };

  const handleJobClick = async (job: any) => {
    try {
      const detail = await api.getJob(job.id);
      setSelectedJob(detail);
    } catch {
      setSelectedJob(job);
    }
  };

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-heading text-obsidian font-display">
            Discover your next role
          </h1>
          <p className="text-body text-gravel mt-1">
            AI-powered job discovery across 696+ sources
          </p>
        </div>
        <div className="flex gap-2">
          <button onClick={async () => { await api.evaluateAll(); fetchJobs(); }} className="btn-secondary flex items-center gap-2">
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 20V10M12 20V4M6 20v-6"/></svg>
            Evaluate
          </button>
          <button onClick={handleExport} className="btn-secondary flex items-center gap-2">
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
            Export
          </button>
        </div>
      </div>

      {/* Filters */}
      <JobFilters
        filters={filters}
        onChange={setFilters}
        stats={stats}
        total={total}
      />

      {/* Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-8 h-8 border-2 border-obsidian border-t-transparent rounded-full animate-spin" />
        </div>
      ) : jobs.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-subheading text-gravel">No jobs found</p>
          <p className="text-body text-gravel mt-2">
            Try adjusting your filters or search terms
          </p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5 mt-6">
            {jobs.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                onClick={handleJobClick}
                onBookmark={handleBookmark}
                onMarkApplied={handleMarkApplied}
              />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-8">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="btn-secondary disabled:opacity-30"
              >
                Previous
              </button>
              <span className="text-caption text-gravel px-4">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="btn-secondary disabled:opacity-30"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}

      {/* Detail drawer */}
      <JobDetailDrawer
        job={selectedJob}
        onClose={() => setSelectedJob(null)}
        onBookmark={handleBookmark}
      />
    </div>
  );
}
