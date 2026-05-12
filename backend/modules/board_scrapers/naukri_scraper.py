"""
Naukri.com scraper — uses their public search API (no Selenium needed).
"""
import requests
import re
from typing import List, Dict

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.naukri.com/",
    "appid": "109",
    "systemid": "109",
}

LOCATION_MAP = {
    "india": "",  # blank = all India
    "bangalore": "bangalore",
    "bengaluru": "bangalore",
    "mumbai": "mumbai",
    "hyderabad": "hyderabad",
    "pune": "pune",
    "delhi": "delhi",
    "noida": "noida",
    "gurgaon": "gurgaon",
    "chennai": "chennai",
    "remote": "work from home",
}


class NaukriScraper:
    API_URL = "https://www.naukri.com/jobapi/v3/search"

    def scrape_search(self, keyword: str, location: str = "India", max_results: int = 50) -> List[Dict]:
        loc = LOCATION_MAP.get(location.lower().strip(), location)
        params = {
            "noOfResults": min(max_results, 50),
            "urlType": "search_by_keyword",
            "searchType": "adv",
            "keyword": keyword,
            "location": loc,
            "pageNo": 1,
            "sort": "1",  # sort by date
            "functionAreaIdGte": "",
            "industryIdGte": "",
            "educationIdGte": "",
            "seoKey": "",
            "src": "jobsearchDesk",
            "latLong": "",
        }
        try:
            r = requests.get(self.API_URL, params=params, headers=HEADERS, timeout=15)
            r.raise_for_status()
            data = r.json()
            jobs_raw = data.get("jobDetails", [])
            return [self._normalize(j) for j in jobs_raw if j.get("jobId")]
        except Exception as e:
            print(f"[Naukri] Error: {e}")
            return []

    def _normalize(self, j: dict) -> dict:
        salary = j.get("salary", "")
        loc = ", ".join(j.get("placeholders", [{}])[0].get("label", "").split(",")[:2]) if j.get("placeholders") else "India"
        return {
            "title": j.get("title", "").strip(),
            "company": j.get("companyName", "").strip(),
            "location": loc or "India",
            "job_url": f"https://www.naukri.com{j.get('jdURL', '')}",
            "description_snippet": re.sub(r"<[^>]+>", " ", j.get("jobDescription", ""))[:500].strip(),
            "salary": salary,
            "source": "naukri",
            "external_id": str(j.get("jobId", "")),
            "posted_date": j.get("footerPlaceholderLabel", ""),
            "employment_type": "full-time",
        }
