"""Naukri.com scraper — uses their search API with correct headers."""
import requests, re
from typing import List, Dict

class NaukriScraper:
    def scrape_search(self, keyword: str, location: str = "India", max_results: int = 50) -> List[Dict]:
        loc_map = {
            "india": "", "bangalore": "bangalore", "bengaluru": "bangalore",
            "mumbai": "mumbai", "hyderabad": "hyderabad", "pune": "pune",
            "delhi": "delhi", "noida": "noida", "gurgaon": "gurgaon",
            "chennai": "chennai", "remote": "work from home",
        }
        loc = loc_map.get(location.lower().strip(), location)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.naukri.com/",
            "appid": "109",
            "systemid": "Naukri",
            "gid": "LOCATION,INDUSTRY,EDUCATION,FAREA_ROLE",
        }

        # Build slug-style URL for Naukri API
        kw_slug = keyword.lower().replace(" ", "-")
        loc_slug = loc.lower().replace(" ", "-") if loc else ""
        url = f"https://www.naukri.com/jobapi/v3/search"

        params = {
            "noOfResults": min(max_results, 50),
            "urlType": "search_by_keyword",
            "searchType": "adv",
            "keyword": keyword,
            "location": loc,
            "pageNo": 1,
            "sort": "1",
            "src": "jobsearchDesk",
            "latLong": "",
            "seoKey": f"{kw_slug}-jobs" + (f"-in-{loc_slug}" if loc_slug else ""),
        }

        try:
            r = requests.get(url, params=params, headers=headers, timeout=15)
            r.raise_for_status()
            jobs_raw = r.json().get("jobDetails", [])
            return [self._normalize(j) for j in jobs_raw if j.get("jobId")]
        except Exception as e:
            # Fallback: scrape the HTML search page
            return self._scrape_html(keyword, loc, max_results)

    def _scrape_html(self, keyword: str, location: str, max_results: int) -> List[Dict]:
        """Fallback: parse Naukri search results page."""
        try:
            kw = keyword.replace(" ", "-").lower()
            loc = location.replace(" ", "-").lower() if location else ""
            url = f"https://www.naukri.com/{kw}-jobs" + (f"-in-{loc}" if loc else "")
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"}
            r = requests.get(url, headers=headers, timeout=15)
            # Extract JSON from script tag
            match = re.search(r'"jobDetails"\s*:\s*(\[.*?\])\s*,\s*"', r.text, re.DOTALL)
            if not match:
                return []
            import json
            jobs_raw = json.loads(match.group(1))
            return [self._normalize(j) for j in jobs_raw[:max_results] if j.get("jobId")]
        except Exception as e:
            print(f"[Naukri] HTML fallback failed: {e}")
            return []

    def _normalize(self, j: dict) -> dict:
        loc_parts = j.get("placeholders", [])
        loc = loc_parts[0].get("label", "India") if loc_parts else "India"
        return {
            "title": j.get("title", "").strip(),
            "company": j.get("companyName", "").strip(),
            "location": loc,
            "job_url": f"https://www.naukri.com{j.get('jdURL', '')}",
            "description_snippet": re.sub(r"<[^>]+>", " ", j.get("jobDescription", ""))[:500].strip(),
            "source": "naukri",
            "external_id": str(j.get("jobId", "")),
            "employment_type": "full-time",
        }
