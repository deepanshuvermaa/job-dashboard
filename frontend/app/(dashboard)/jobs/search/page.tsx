"use client";
import { useState } from "react";
import { api } from "@/lib/api";

export default function JobSearchPage() {
  const [keywords, setKeywords] = useState("Software Engineer");
  const [location, setLocation] = useState("United States");
  const [showFilters, setShowFilters] = useState(false);
  const [experienceLevel, setExperienceLevel] = useState("");
  const [postedWithin, setPostedWithin] = useState("");
  const [jobType, setJobType] = useState("");
  const [maxResults, setMaxResults] = useState(50);
  const [easyApply, setEasyApply] = useState(false);
  const [remote, setRemote] = useState(false);
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [savedCount, setSavedCount] = useState(0);

  const handleSearch = async () => {
    setLoading(true);
    setSearched(true);
    try {
      const data = await api.searchJobs({
        keywords,
        location,
        experience_level: experienceLevel || undefined,
        posted_within: postedWithin || undefined,
        job_type: jobType || undefined,
        max_results: maxResults,
        easy_apply: easyApply || undefined,
        remote: remote || undefined,
      });
      setJobs(data.jobs || []);
      setSavedCount(data.saved_to_db || 0);

      // Also ingest into v2 jobs table
      if (data.jobs?.length > 0) {
        try {
          await api.ingestJobs(data.jobs, "linkedin");
        } catch (e) {
          console.warn("Ingest failed:", e);
        }
      }
    } catch (err: any) {
      alert(err.message || "Search failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="px-8 py-6 max-w-wide mx-auto">
      <h1 className="text-heading text-obsidian font-display">
        Smart Job Search
      </h1>
      <p className="text-body text-gravel mt-1">
        Search LinkedIn and scrape jobs with AI-powered filters
      </p>

      {/* Search Form */}
      <div className="card mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-caption-strong text-obsidian mb-2">Keywords</label>
            <input
              type="text"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              className="input-el"
              placeholder="Software Engineer, React Developer..."
            />
          </div>
          <div>
            <label className="block text-caption-strong text-obsidian mb-2">Location</label>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="input-el"
              placeholder="United States"
            />
          </div>
        </div>

        {/* Toggle filters */}
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="text-caption text-obsidian hover:underline mb-4"
        >
          {showFilters ? "Hide Filters" : "Show Advanced Filters"}
        </button>

        {showFilters && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 p-4 bg-powder rounded-lg">
            <div>
              <label className="block text-caption text-gravel mb-1">Experience</label>
              <select value={experienceLevel} onChange={(e) => setExperienceLevel(e.target.value)} className="input-el !rounded-sm text-caption">
                <option value="">Any</option>
                <option value="entry">Entry Level</option>
                <option value="mid">Mid Level</option>
                <option value="senior">Senior</option>
                <option value="director">Director</option>
              </select>
            </div>
            <div>
              <label className="block text-caption text-gravel mb-1">Posted Within</label>
              <select value={postedWithin} onChange={(e) => setPostedWithin(e.target.value)} className="input-el !rounded-sm text-caption">
                <option value="">Any Time</option>
                <option value="1h">Last Hour</option>
                <option value="24h">Last 24 Hours</option>
                <option value="week">This Week</option>
                <option value="month">This Month</option>
              </select>
            </div>
            <div>
              <label className="block text-caption text-gravel mb-1">Job Type</label>
              <select value={jobType} onChange={(e) => setJobType(e.target.value)} className="input-el !rounded-sm text-caption">
                <option value="">Any</option>
                <option value="full-time">Full Time</option>
                <option value="part-time">Part Time</option>
                <option value="contract">Contract</option>
                <option value="internship">Internship</option>
              </select>
            </div>
            <div>
              <label className="block text-caption text-gravel mb-1">Max Results</label>
              <input type="number" value={maxResults} onChange={(e) => setMaxResults(Number(e.target.value))} className="input-el !rounded-sm text-caption" min={10} max={500} />
            </div>
            <div className="flex items-center gap-4 col-span-2">
              <label className="flex items-center gap-2 text-caption text-cinder cursor-pointer">
                <input type="checkbox" checked={easyApply} onChange={(e) => setEasyApply(e.target.checked)} className="w-4 h-4 accent-obsidian" />
                Easy Apply Only
              </label>
              <label className="flex items-center gap-2 text-caption text-cinder cursor-pointer">
                <input type="checkbox" checked={remote} onChange={(e) => setRemote(e.target.checked)} className="w-4 h-4 accent-obsidian" />
                Remote Only
              </label>
            </div>
          </div>
        )}

        <button onClick={handleSearch} disabled={loading || !keywords} className="btn-primary w-full md:w-auto disabled:opacity-50">
          {loading ? "Searching LinkedIn..." : "Search Jobs"}
        </button>
      </div>

      {/* Results */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-20">
          <div className="w-8 h-8 border-2 border-obsidian border-t-transparent rounded-full animate-spin mb-4" />
          <p className="text-body text-gravel">Scraping LinkedIn... this may take a minute</p>
          <p className="text-caption text-gravel mt-1">Browser session required for LinkedIn search</p>
        </div>
      )}

      {!loading && searched && (
        <>
          <div className="flex items-center justify-between mb-4">
            <p className="text-body text-obsidian">
              <span className="text-obsidian font-semibold">{jobs.length}</span> jobs found
              {savedCount > 0 && <span className="text-gravel"> · {savedCount} saved to database</span>}
            </p>
          </div>

          {jobs.length === 0 ? (
            <div className="card text-center py-16">
              <p className="text-body-lg text-gravel">No jobs found</p>
              <p className="text-body text-gravel mt-2">Try adjusting your search keywords or filters</p>
            </div>
          ) : (
            <div className="space-y-3">
              {jobs.map((job: any, i: number) => (
                <div key={i} className="card hover:shadow-product transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-body-medium text-obsidian">{job.title}</h3>
                        {job.easy_apply && (
                          <span className="px-2 py-0.5 bg-grade-a/10 text-grade-a rounded-xs text-[10px] font-medium">Easy Apply</span>
                        )}
                      </div>
                      <p className="text-caption text-gravel">{job.company} · {job.location}</p>
                      {job.salary && <p className="text-caption text-cinder mt-1">{job.salary}</p>}
                      {job.description_snippet && (
                        <p className="text-caption text-gravel mt-2 line-clamp-2">{job.description_snippet}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-2 ml-4 flex-shrink-0">
                      <a href={job.job_url} target="_blank" rel="noopener noreferrer" className="btn-primary text-caption !py-2 !px-4">
                        View Job
                      </a>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {!loading && !searched && (
        <div className="card text-center py-20">
          <p className="text-heading-sm font-display text-gravel mb-2">Ready to search</p>
          <p className="text-body text-gravel">Enter keywords and click Search to scrape LinkedIn for jobs</p>
          <p className="text-caption text-gravel mt-4">This uses a real browser session -- LinkedIn login required on first run</p>
        </div>
      )}
    </div>
  );
}
