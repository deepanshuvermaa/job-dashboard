"""InstaHyre scraper — uses their public jobs search."""
import requests
from typing import List, Dict

class InstaHyreScraper:
    def scrape_search(self, keyword: str, location: str = "India", max_results: int = 50) -> List[Dict]:
        loc_map = {
            "india": "India", "bangalore": "Bangalore", "bengaluru": "Bangalore",
            "mumbai": "Mumbai", "hyderabad": "Hyderabad", "pune": "Pune",
            "delhi": "Delhi", "noida": "Noida", "gurgaon": "Gurgaon",
            "chennai": "Chennai", "remote": "Remote",
        }
        loc = loc_map.get(location.lower().strip(), location)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
            "Accept": "application/json",
            "Referer": "https://www.instahyre.com/",
            "X-Requested-With": "XMLHttpRequest",
        }

        # Try the jobs search endpoint
        urls_to_try = [
            f"https://www.instahyre.com/api/v1/opportunity/?format=json&designation={requests.utils.quote(keyword)}&location={requests.utils.quote(loc)}&limit={min(max_results,50)}&offset=0",
            f"https://www.instahyre.com/candidate/explore/?q={requests.utils.quote(keyword)}&location={requests.utils.quote(loc)}",
        ]

        for url in urls_to_try:
            try:
                r = requests.get(url, headers=headers, timeout=15)
                if r.status_code == 200:
                    data = r.json()
                    jobs_raw = data.get("results", data.get("opportunities", []))
                    if jobs_raw:
                        return [self._normalize(j) for j in jobs_raw if j.get("id")]
            except Exception:
                continue

        print(f"[InstaHyre] No results for '{keyword}' in '{loc}'")
        return []

    def _normalize(self, j: dict) -> dict:
        employer = j.get("employer", {}) or {}
        skills = [s.get("name", "") for s in (j.get("skills") or []) if s.get("name")]
        return {
            "title": j.get("designation", j.get("title", "")).strip(),
            "company": employer.get("name", j.get("company", "")).strip(),
            "location": j.get("location", "India"),
            "job_url": f"https://www.instahyre.com/job-{j.get('id', '')}/",
            "description_snippet": j.get("description", "")[:500].strip(),
            "source": "instahyre",
            "external_id": str(j.get("id", "")),
            "skills_required": skills,
            "employment_type": "full-time",
        }
