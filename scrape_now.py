#!/usr/bin/env python3
"""
Batch scraper — runs 4 keyword searches and pushes to Railway backend.
Usage: python scrape_now.py
"""
import os, sys, time, requests
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from pathlib import Path

BACKEND_URL = os.getenv("BACKEND_URL", "https://job-dashboard-production-3016.up.railway.app")
BACKEND_DIR = Path(__file__).parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

SCRAPER_EMAIL = "scraper@jobflow.io"
SCRAPER_PASS  = "ScraperBot2024!"

KEYWORDS = [
    "AI Engineer",
    "Software Developer",
    "Software Engineer",
    "Full Stack Engineer",
]
LOCATION    = "India"
DURATION    = "24h"
BUDGET_SECS = 200
MAX_LI      = 100
MAX_BOARD   = 30

class C:
    GRN="\033[92m"; YLW="\033[93m"; RED="\033[91m"; CYN="\033[96m"
    BLD="\033[1m";  DIM="\033[2m";  RST="\033[0m"

if sys.platform == "win32": os.system("color")

def ok(m):   print(f"  [OK]  {m}")
def warn(m): print(f"  [!!]  {m}")
def info(m): print(f"  [>>]  {m}")

def get_token():
    try:
        requests.post(f"{BACKEND_URL}/api/auth/register",
                      json={"email": SCRAPER_EMAIL, "password": SCRAPER_PASS, "full_name": "Scraper Bot"},
                      timeout=10)
    except: pass
    r = requests.post(f"{BACKEND_URL}/api/auth/login",
                      json={"email": SCRAPER_EMAIL, "password": SCRAPER_PASS}, timeout=10)
    r.raise_for_status()
    token = r.json()["access_token"]
    ok(f"Authenticated -> {BACKEND_URL}")
    return token

def ingest(token, jobs, source):
    if not jobs: return {"new": 0, "updated": 0, "skipped": 0}
    # Deduplicate by job_url before sending
    seen, deduped = set(), []
    for j in jobs:
        key = j.get("job_url") or j.get("url") or str(j.get("id",""))
        if key and key not in seen:
            seen.add(key); deduped.append(j)
    try:
        r = requests.post(f"{BACKEND_URL}/api/jobs/ingest",
                          json={"jobs": deduped, "source": source},
                          headers={"Authorization": f"Bearer {token}"},
                          timeout=120)
        r.raise_for_status()
        s = r.json()
        info(f"  [{source}] sent={len(deduped)} +{s.get('new',0)} new {s.get('updated',0)} updated {s.get('skipped',0)} skipped")
        return s
    except Exception as e:
        warn(f"Ingest failed [{source}]: {e}")
        return {"new": 0, "updated": 0, "skipped": 0}

def scrape_linkedin(keyword):
    try:
        r = requests.get(f"http://localhost:8000/api/jobs/search",
                         params={"keywords": keyword, "location": LOCATION,
                                 "posted_within": DURATION, "max_results": MAX_LI},
                         timeout=BUDGET_SECS)
        r.raise_for_status()
        jobs = r.json().get("jobs", [])
        ok(f"LinkedIn '{keyword}' → {len(jobs)} jobs")
        return jobs
    except Exception as e:
        warn(f"LinkedIn '{keyword}' failed: {e}")
        return []

def scrape_naukri(keyword):
    try:
        from modules.board_scrapers.naukri_scraper import NaukriScraper
        jobs = NaukriScraper().scrape_search(keyword, LOCATION, MAX_BOARD)
        ok(f"Naukri '{keyword}' → {len(jobs)} jobs")
        return jobs
    except Exception as e:
        warn(f"Naukri '{keyword}' failed: {e}")
        return []

def scrape_instahyre(keyword):
    try:
        from modules.board_scrapers.instahyre_scraper import InstaHyreScraper
        jobs = InstaHyreScraper().scrape_search(keyword, LOCATION, MAX_BOARD)
        ok(f"InstaHyre '{keyword}' → {len(jobs)} jobs")
        return jobs
    except Exception as e:
        warn(f"InstaHyre '{keyword}' failed: {e}")
        return []

def scrape_greenhouse(keyword):
    try:
        from modules.board_scrapers.greenhouse_scraper import GreenhouseScraper
        s = GreenhouseScraper()
        COMPANIES = [
            ("Stripe","https://boards.greenhouse.io/stripe"),
            ("Databricks","https://boards.greenhouse.io/databricks"),
            ("MongoDB","https://boards.greenhouse.io/mongodb"),
            ("Cloudflare","https://boards.greenhouse.io/cloudflare"),
            ("GitLab","https://boards.greenhouse.io/gitlab"),
        ]
        out = []
        for company, url in COMPANIES:
            try:
                raw = s.scrape_company(url, company)
                out += [j for j in raw if keyword.lower() in (j.get("title","")+" "+j.get("description_snippet","")).lower()][:5]
            except: continue
        ok(f"Greenhouse '{keyword}' → {len(out)} jobs")
        return out
    except Exception as e:
        warn(f"Greenhouse '{keyword}' failed: {e}")
        return []

def scrape_lever(keyword):
    try:
        from modules.board_scrapers.lever_scraper import LeverScraper
        s = LeverScraper()
        COMPANIES = [
            ("OpenAI","https://jobs.lever.co/openai"),
            ("Anthropic","https://jobs.lever.co/anthropic"),
            ("Grammarly","https://jobs.lever.co/grammarly"),
            ("Ramp","https://jobs.lever.co/ramp"),
        ]
        out = []
        for company, url in COMPANIES:
            try:
                raw = s.scrape_company(url, company)
                out += [j for j in raw if keyword.lower() in (j.get("title","")+" "+j.get("description_snippet","")).lower()][:5]
            except: continue
        ok(f"Lever '{keyword}' → {len(out)} jobs")
        return out
    except Exception as e:
        warn(f"Lever '{keyword}' failed: {e}")
        return []

def run_with_timeout(fn, timeout):
    with ThreadPoolExecutor(max_workers=1) as ex:
        try:
            return ex.submit(fn).result(timeout=timeout)
        except FutureTimeout:
            warn(f"Timed out after {timeout}s")
            return []
        except Exception as e:
            warn(f"Error: {e}")
            return []

def main():
    print(f"\n{'='*60}")
    print(f"  Batch Scraper -> {BACKEND_URL}")
    print(f"  Keywords: {', '.join(KEYWORDS)}")
    print(f"  Location: {LOCATION}  |  Duration: {DURATION}  |  Budget: {BUDGET_SECS}s/keyword")
    print(f"{'='*60}\n")

    token = get_token()
    grand = {"new": 0, "updated": 0, "skipped": 0}

    # Check if local backend is running for LinkedIn
    local_backend_up = False
    try:
        requests.get("http://localhost:8000/health", timeout=3)
        local_backend_up = True
        ok("Local backend detected — LinkedIn scraping enabled")
    except:
        warn("No local backend — LinkedIn scraping skipped (start run_scraper.py first for LinkedIn)")

    for keyword in KEYWORDS:
        print(f"\n--- {keyword} ---")
        all_jobs = []

        # LinkedIn (needs local backend with Selenium)
        if local_backend_up:
            li_jobs = run_with_timeout(lambda kw=keyword: scrape_linkedin(kw), BUDGET_SECS)
            all_jobs += li_jobs

        # Naukri (HTTP, fast)
        naukri_jobs = run_with_timeout(lambda kw=keyword: scrape_naukri(kw), 30)
        all_jobs += naukri_jobs

        # InstaHyre (HTTP, fast)
        ih_jobs = run_with_timeout(lambda kw=keyword: scrape_instahyre(kw), 30)
        all_jobs += ih_jobs

        # Greenhouse (HTTP, fast)
        gh_jobs = run_with_timeout(lambda kw=keyword: scrape_greenhouse(kw), 30)
        all_jobs += gh_jobs

        # Lever (HTTP, fast)
        lv_jobs = run_with_timeout(lambda kw=keyword: scrape_lever(kw), 30)
        all_jobs += lv_jobs

        # Ingest all for this keyword
        s = ingest(token, all_jobs, f"batch_{keyword.lower().replace(' ','_')}")
        for k in grand: grand[k] += s.get(k, 0)
        info(f"  Total for '{keyword}': {len(all_jobs)} scraped")

    print(f"\n{'-'*40}")
    print(f"  Total new in DB:  {grand['new']}")
    print(f"  Updated:          {grand['updated']}")
    print(f"  Skipped (dup):    {grand['skipped']}")
    print(f"\n  Dashboard: {BACKEND_URL}/dashboard/jobs\n")

if __name__ == "__main__":
    main()
