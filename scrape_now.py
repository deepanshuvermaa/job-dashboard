#!/usr/bin/env python3
"""
Batch scraper — dynamically loads ALL portals from portals.yml + detected_portals.json
and scrapes them alongside LinkedIn.

Usage: python scrape_now.py
"""
import os, sys, time, json, requests
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from pathlib import Path

BACKEND_URL = os.getenv("BACKEND_URL", "https://job-dashboard-production-3016.up.railway.app")
BACKEND_DIR = Path(__file__).parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

SCRAPER_EMAIL = "scraper@jobflow.io"
SCRAPER_PASS  = "ScraperBot2024!"

KEYWORDS = [
    "Software Engineer",
    "Software Developer",
    "Full Stack Developer",
    "AI Engineer",
    "Cloud Engineer",
]
LOCATION    = "India"
DURATION    = "24h"
MAX_LI      = 100
MAX_BOARD   = 30

if sys.platform == "win32": os.system("color")

def ok(m):   print(f"  [OK]  {m}")
def warn(m): print(f"  [!!]  {m}")
def info(m): print(f"  [>>]  {m}")

# ─── Load ALL portals from config files ───

def load_all_portals():
    """Load and merge portals from portals.yml and detected_portals.json"""
    portals = {"greenhouse": [], "lever": [], "ashby": [], "workable": [], "darwinbox": [], "generic": []}

    # Load from portals.yml (curated, high quality)
    yml_path = BACKEND_DIR / "config" / "portals.yml"
    if yml_path.exists():
        import yaml
        with open(yml_path) as f:
            data = yaml.safe_load(f)
        for p in data.get("portals", []):
            if not p.get("enabled", True):
                continue
            ats = p.get("ats", "")
            if ats == "generic":
                portals["generic"].append((p["name"], p["url"]))
            elif ats in portals:
                portals[ats].append((p["name"], p["url"]))

    # Load from detected_portals.json (auto-detected, supplement)
    json_path = BACKEND_DIR / "config" / "detected_portals.json"
    if json_path.exists():
        with open(json_path) as f:
            detected = json.load(f)
        existing_urls = set()
        for ats_list in portals.values():
            for _, url in ats_list:
                existing_urls.add(url.rstrip("/").lower())

        for p in detected:
            ats = p.get("ats", "unknown")
            url = p.get("ats_url") or p.get("original_url", "")
            if not url or url.rstrip("/").lower() in existing_urls:
                continue
            if not url.startswith("http"):
                continue
            # Skip errored/blocked ones
            method = p.get("detection_method") or ""
            if "error" in method or "403" in method or "404" in method:
                continue

            if ats in portals:
                portals[ats].append((p["company"], url))
            elif ats == "unknown":
                portals["generic"].append((p["company"], url))
            existing_urls.add(url.rstrip("/").lower())

    return portals

# ─── Auth & Ingest ───

def get_token():
    try:
        requests.post(f"{BACKEND_URL}/api/auth/register",
                      json={"email": SCRAPER_EMAIL, "password": SCRAPER_PASS, "full_name": "Scraper Bot"},
                      timeout=10)
    except: pass
    r = requests.post(f"{BACKEND_URL}/api/auth/login",
                      json={"email": SCRAPER_EMAIL, "password": SCRAPER_PASS}, timeout=10)
    r.raise_for_status()
    ok(f"Authenticated -> {BACKEND_URL}")
    return r.json()["access_token"]

def ingest(token, jobs, source):
    if not jobs: return {"new": 0, "updated": 0, "skipped": 0}
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
        info(f"  [{source}] sent={len(deduped)} +{s.get('new',0)} new {s.get('updated',0)} upd {s.get('skipped',0)} skip")
        return s
    except Exception as e:
        warn(f"Ingest failed [{source}]: {e}")
        return {"new": 0, "updated": 0, "skipped": 0}

def run_with_timeout(fn, timeout):
    with ThreadPoolExecutor(max_workers=1) as ex:
        try:
            return ex.submit(fn).result(timeout=timeout)
        except (FutureTimeout, Exception) as e:
            return []

# ─── Scraper functions ───

def scrape_linkedin_direct(keyword, scraper_instance):
    try:
        jobs = scraper_instance.search_jobs(
            keywords=keyword, location=LOCATION,
            posted_within=DURATION, max_results=MAX_LI,
            experience_level="entry_associate",
        )
        for j in jobs:
            j.setdefault("source", "linkedin")
        ok(f"LinkedIn '{keyword}' -> {len(jobs)} jobs")
        return jobs
    except Exception as e:
        warn(f"LinkedIn '{keyword}' failed: {e}")
        return []

def scrape_ats_companies(keyword, ats_type, companies):
    """Scrape all companies for a given ATS type, filtering by keyword"""
    scrapers = {
        "greenhouse": ("modules.board_scrapers.greenhouse_scraper", "GreenhouseScraper"),
        "lever": ("modules.board_scrapers.lever_scraper", "LeverScraper"),
        "ashby": ("modules.board_scrapers.ashby_scraper", "AshbyScraper"),
        "workable": ("modules.board_scrapers.workable_scraper", "WorkableScraper"),
        "darwinbox": ("modules.board_scrapers.darwinbox_scraper", "DarwinboxScraper"),
        "generic": ("modules.board_scrapers.generic_html_scraper", "GenericHTMLScraper"),
    }
    if ats_type not in scrapers:
        return []

    mod_path, cls_name = scrapers[ats_type]
    try:
        import importlib
        mod = importlib.import_module(mod_path)
        scraper_cls = getattr(mod, cls_name)
        s = scraper_cls()
    except Exception as e:
        warn(f"{ats_type} scraper import failed: {e}")
        return []

    out = []
    kw_lower = keyword.lower()
    for company, url in companies:
        try:
            raw = s.scrape_company(url, company)
            matched = [j for j in raw if kw_lower in (j.get("title","")+" "+j.get("description_snippet","")).lower()][:5]
            out.extend(matched)
        except Exception:
            continue

    ok(f"{ats_type.title()} '{keyword}' → {len(out)} jobs from {len(companies)} companies")
    return out

def scrape_reddit(keyword):
    try:
        from modules.board_scrapers.reddit_scraper import RedditScraper
        jobs = RedditScraper().scrape_search(keyword, LOCATION)
        ok(f"Reddit '{keyword}' → {len(jobs)} jobs")
        return jobs[:MAX_BOARD]
    except Exception as e:
        warn(f"Reddit '{keyword}' failed: {e}")
        return []

def scrape_wellfound(keyword):
    try:
        from modules.board_scrapers.wellfound_scraper import WellfoundScraper
        jobs = WellfoundScraper().scrape_search(keyword, LOCATION)
        ok(f"Wellfound '{keyword}' → {len(jobs)} jobs")
        return jobs[:MAX_BOARD]
    except Exception as e:
        warn(f"Wellfound '{keyword}' failed: {e}")
        return []

def scrape_dailyremote(keyword):
    try:
        from modules.board_scrapers.dailyremote_scraper import DailyRemoteScraper
        jobs = DailyRemoteScraper().scrape_search(keyword, LOCATION)
        ok(f"DailyRemote '{keyword}' → {len(jobs)} jobs")
        return jobs[:MAX_BOARD]
    except Exception as e:
        warn(f"DailyRemote '{keyword}' failed: {e}")
        return []

def scrape_remotefront(keyword):
    try:
        from modules.board_scrapers.remotefront_scraper import RemoteFrontScraper
        jobs = RemoteFrontScraper().scrape_search(keyword, LOCATION)
        ok(f"RemoteFront '{keyword}' → {len(jobs)} jobs")
        return jobs[:MAX_BOARD]
    except Exception as e:
        warn(f"RemoteFront '{keyword}' failed: {e}")
        return []

# ─── Main ───

def main():
    # Load all portals dynamically
    all_portals = load_all_portals()

    total_companies = sum(len(v) for v in all_portals.values())
    print(f"\n{'='*60}")
    print(f"  Batch Scraper -> {BACKEND_URL}")
    print(f"  Keywords: {', '.join(KEYWORDS)}")
    print(f"  Portals loaded: {total_companies} companies")
    for ats, companies in all_portals.items():
        if companies:
            print(f"    {ats.title()}: {len(companies)} companies")
    print(f"  + LinkedIn, Reddit, Wellfound, DailyRemote, RemoteFront")
    print(f"  Location: {LOCATION}  |  Duration: {DURATION}")
    print(f"{'='*60}\n")

    token = get_token()
    grand = {"new": 0, "updated": 0, "skipped": 0}

    # Init LinkedIn scraper once
    li_scraper = None
    try:
        from modules.linkedin_job_scraper import LinkedInJobScraper
        li_scraper = LinkedInJobScraper()
        if li_scraper.login():
            ok("LinkedIn logged in — Chrome session ready")
        else:
            warn("LinkedIn login failed — skipping LinkedIn")
            li_scraper = None
    except Exception as e:
        warn(f"LinkedIn init failed: {e}")

    for keyword in KEYWORDS:
        print(f"\n{'─'*50}")
        print(f"  KEYWORD: {keyword}")
        print(f"{'─'*50}")

        # ── LinkedIn (Selenium, ingest immediately) ──
        if li_scraper:
            li_jobs = scrape_linkedin_direct(keyword, li_scraper)
            if li_jobs:
                li_jobs = [j for j in li_jobs if j.get("job_url")]
                s = ingest(token, li_jobs, "linkedin")
                for k in grand: grand[k] += s.get(k, 0)

        # ── ATS company scrapers (all loaded dynamically) ──
        board_jobs = []

        for ats_type, companies in all_portals.items():
            if not companies:
                continue
            # Generic scraper has many companies — batch them
            if ats_type == "generic" and len(companies) > 50:
                # Scrape in batches of 50 to avoid timeout
                for batch_start in range(0, len(companies), 50):
                    batch = companies[batch_start:batch_start+50]
                    jobs = run_with_timeout(
                        lambda at=ats_type, co=batch, kw=keyword: scrape_ats_companies(kw, at, co),
                        180
                    )
                    board_jobs.extend(jobs or [])
            else:
                timeout = 120 if len(companies) > 10 else 60
                jobs = run_with_timeout(
                    lambda at=ats_type, co=companies, kw=keyword: scrape_ats_companies(kw, at, co),
                    timeout
                )
                board_jobs.extend(jobs or [])

        # ── Search-based scrapers ──
        board_jobs += run_with_timeout(lambda kw=keyword: scrape_reddit(kw), 60)
        board_jobs += run_with_timeout(lambda kw=keyword: scrape_wellfound(kw), 40)
        board_jobs += run_with_timeout(lambda kw=keyword: scrape_dailyremote(kw), 30)
        board_jobs += run_with_timeout(lambda kw=keyword: scrape_remotefront(kw), 30)

        # Ingest all board jobs for this keyword
        if board_jobs:
            s = ingest(token, board_jobs, f"batch_{keyword.lower().replace(' ','_')}")
            for k in grand: grand[k] += s.get(k, 0)

        info(f"  Total for '{keyword}': {len(board_jobs)} board jobs")

    # Close Chrome
    if li_scraper:
        try: li_scraper.driver.quit(); ok("Chrome closed")
        except: pass

    print(f"\n{'='*60}")
    print(f"  RESULTS")
    print(f"{'='*60}")
    print(f"  New jobs added:   {grand['new']}")
    print(f"  Updated:          {grand['updated']}")
    print(f"  Skipped (dup):    {grand['skipped']}")
    print(f"\n  Dashboard: {BACKEND_URL}\n")

if __name__ == "__main__":
    main()
