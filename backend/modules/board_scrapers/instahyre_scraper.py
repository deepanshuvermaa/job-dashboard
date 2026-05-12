"""
InstaHyre scraper — uses their public jobs API (no Selenium needed).
"""
import requests
from typing import List, Dict

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.instahyre.com/",
}

LOCATION_MAP = {
    "india": "India",
    "bangalore": "Bangalore",
    "bengaluru": "Bangalore",
    "mumbai": "Mumbai",
    "hyderabad": "Hyderabad",
    "pune": "Pune",
    "delhi": "Delhi",
    "noida": "Noida",
    "gurgaon": "Gurgaon",
    "chennai": "Chennai",
    "remote": "Remote",
}


class InstaHyreScraper:
    API_URL = "https://www.instahyre.com/api/v1/opportunity/"

    def scrape_search(self, keyword: str, location: str = "India", max_results: int = 50) -> List[Dict]:
        loc = LOCATION_MAP.get(location.lower().strip(), location)
        params = {
            "format": "json",
            "designation": keyword,
            "location": loc,
            "limit": min(max_results, 50),
            "offset": 0,
        }
        try:
            r = requests.get(self.API_URL, params=params, headers=HEADERS, timeout=15)
            r.raise_for_status()
            data = r.json()
            jobs_raw = data.get("results", [])
            return [self._normalize(j) for j in jobs_raw if j.get("id")]
        except Exception as e:
            print(f"[InstaHyre] Error: {e}")
            return []

    def _normalize(self, j: dict) -> dict:
        employer = j.get("employer", {}) or {}
        skills = [s.get("name", "") for s in (j.get("skills") or []) if s.get("name")]
        loc = j.get("location", "") or "India"
        return {
            "title": j.get("designation", "").strip(),
            "company": employer.get("name", "").strip(),
            "location": loc,
            "job_url": f"https://www.instahyre.com/job-{j.get('id', '')}/",
            "description_snippet": j.get("description", "")[:500].strip(),
            "salary": "",
            "source": "instahyre",
            "external_id": str(j.get("id", "")),
            "skills_required": skills,
            "employment_type": "full-time",
        }
