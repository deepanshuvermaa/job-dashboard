#!/usr/bin/env python3
"""
Job Scraper — scrapes LinkedIn, Naukri, InstaHyre, Greenhouse, Lever, Ashby,
Wellfound, Reddit, DailyRemote, RemoteFront and pushes jobs to the backend API.

Usage:
  python run_scraper.py                          # starts local backend + frontend
  BACKEND_URL=https://your.railway.app python run_scraper.py  # use Railway backend directly
"""

import os
import sys
import time
import socket
import subprocess
import webbrowser
import requests
import atexit
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from pathlib import Path
from datetime import datetime, timedelta, timezone

ROOT        = Path(__file__).parent.resolve()
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"

# If BACKEND_URL is set, skip starting local backend/frontend
REMOTE_BACKEND = os.getenv("BACKEND_URL", "").rstrip("/")

class C:
    GRN = "\033[92m"; YLW = "\033[93m"; RED = "\033[91m"
    CYN = "\033[96m"; BLD = "\033[1m";  DIM = "\033[2m"; RST = "\033[0m"

if sys.platform == "win32":
    os.system("color")

def ok(m):   print(f"  {C.GRN}✓{C.RST}  {m}")
def warn(m): print(f"  {C.YLW}⚠{C.RST}  {m}")
def err(m):  print(f"  {C.RED}✗{C.RST}  {m}")
def info(m): print(f"  {C.CYN}→{C.RST}  {m}")

def section(title):
    print(f"\n{C.BLD}{C.CYN}┌{'─'*58}┐{C.RST}")
    print(f"{C.BLD}{C.CYN}│  {title:<56}│{C.RST}")
    print(f"{C.BLD}{C.CYN}└{'─'*58}┘{C.RST}")

def banner():
    print(f"\n{C.BLD}{C.CYN}{'═'*62}{C.RST}")
    print(f"{C.BLD}  Job Dashboard Scraper{C.RST}")
    print(f"{C.DIM}  LinkedIn · Naukri · InstaHyre · Greenhouse · Lever · Ashby{C.RST}")
    print(f"{C.BLD}{C.CYN}{'═'*62}{C.RST}\n")


# ── Port helpers ──────────────────────────────────────────────────────────────

def is_port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) != 0

def find_free_port(start):
    for p in range(start, start + 30):
        if is_port_free(p):
            return p
    raise RuntimeError(f"No free port in {start}–{start+30}")


# ── Process management ────────────────────────────────────────────────────────

_procs = []

def _cleanup():
    for p in _procs:
        try: p.terminate()
        except: pass

atexit.register(_cleanup)

def _popen(args, cwd, env):
    flags = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if sys.platform == "win32" else {}
    proc = subprocess.Popen(args, cwd=str(cwd), env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, **flags)
    _procs.append(proc)
    return proc

def start_backend(port):
    info(f"Starting backend  → http://localhost:{port}")
    py = "python" if sys.platform == "win32" else "python3"
    env = {**os.environ, "PYTHONPATH": str(BACKEND_DIR), "ENABLE_LEGACY": "true"}
    return _popen([py, "-m", "uvicorn", "api.v2.app:app",
                   "--host", "0.0.0.0", "--port", str(port), "--log-level", "warning"],
                  cwd=BACKEND_DIR, env=env)

def start_frontend(port, backend_port):
    info(f"Starting frontend → http://localhost:{port}")
    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    env = {**os.environ, "NEXT_PUBLIC_API_URL": f"http://localhost:{backend_port}", "PORT": str(port)}
    return _popen([npm, "run", "dev", "--", "--port", str(port)], cwd=FRONTEND_DIR, env=env)

def wait_for_url(url, label, timeout):
    deadline = time.time() + timeout
    print(f"  {C.DIM}Waiting for {label}", end="", flush=True)
    while time.time() < deadline:
        try:
            if requests.get(url, timeout=2).status_code < 500:
                print(f" {C.GRN}ready ✓{C.RST}")
                return True
        except: pass
        print(".", end="", flush=True)
        time.sleep(1.5)
    print(f" {C.YLW}timed-out{C.RST}")
    return False


# ── Auth ──────────────────────────────────────────────────────────────────────

_SCRAPER_EMAIL = "scraper@jobflow.io"
_SCRAPER_PASS  = "ScraperBot2024!"
_SCRAPER_NAME  = "Scraper Bot"

def get_token(base):
    try:
        requests.post(f"{base}/api/auth/register",
                      json={"email": _SCRAPER_EMAIL, "password": _SCRAPER_PASS, "full_name": _SCRAPER_NAME},
                      timeout=10)
    except: pass
    r = requests.post(f"{base}/api/auth/login",
                      json={"email": _SCRAPER_EMAIL, "password": _SCRAPER_PASS}, timeout=10)
    r.raise_for_status()
    token = r.json().get("access_token")
    if not token:
        raise RuntimeError("No access_token in login response")
    ok("Authenticated with backend")
    return token


# ── ATS company lists ─────────────────────────────────────────────────────────

GREENHOUSE_COMPANIES = [
    ("Stripe", "https://boards.greenhouse.io/stripe"),
    ("Airbnb", "https://boards.greenhouse.io/airbnb"),
    ("Figma", "https://boards.greenhouse.io/figma"),
    ("Notion", "https://boards.greenhouse.io/notion"),
    ("Databricks", "https://boards.greenhouse.io/databricks"),
    ("Confluent", "https://boards.greenhouse.io/confluent"),
    ("MongoDB", "https://boards.greenhouse.io/mongodb"),
    ("Cloudflare", "https://boards.greenhouse.io/cloudflare"),
    ("Twilio", "https://boards.greenhouse.io/twilio"),
    ("GitLab", "https://boards.greenhouse.io/gitlab"),
]

LEVER_COMPANIES = [
    ("Netflix", "https://jobs.lever.co/netflix"),
    ("Shopify", "https://jobs.lever.co/shopify"),
    ("Coinbase", "https://jobs.lever.co/coinbase"),
    ("OpenAI", "https://jobs.lever.co/openai"),
    ("Anthropic", "https://jobs.lever.co/anthropic"),
    ("Grammarly", "https://jobs.lever.co/grammarly"),
    ("Brex", "https://jobs.lever.co/brex"),
    ("Ramp", "https://jobs.lever.co/ramp"),
]

ASHBY_COMPANIES = [
    ("Linear", "https://jobs.ashbyhq.com/linear"),
    ("Vercel", "https://jobs.ashbyhq.com/vercel"),
    ("Retool", "https://jobs.ashbyhq.com/retool"),
    ("Replit", "https://jobs.ashbyhq.com/replit"),
    ("PostHog", "https://jobs.ashbyhq.com/posthog"),
]

ROLE_ALIASES = {
    "software engineer": ["software engineer", "swe", "developer"],
    "frontend": ["frontend", "front-end", "react", "ui engineer"],
    "backend": ["backend", "back-end", "api engineer", "python developer"],
    "full stack": ["full stack", "fullstack", "full-stack"],
    "data engineer": ["data engineer", "etl", "spark"],
    "machine learning": ["machine learning", "ml engineer", "ai engineer"],
    "devops": ["devops", "sre", "platform engineer", "cloud engineer"],
}

DURATIONS = {
    "1": ("1h",    "past 1 hour",    1),
    "2": ("6h",    "past 6 hours",   6),
    "3": ("12h",   "past 12 hours",  12),
    "4": ("24h",   "past 24 hours",  24),
    "5": ("week",  "past week",      168),
    "6": ("month", "past month",     720),
}

BOARD_WEIGHTS = {
    "LinkedIn":    30,
    "Naukri":      15,
    "InstaHyre":   10,
    "Greenhouse":  10,
    "Lever":       10,
    "Ashby":        8,
    "Wellfound":    7,
    "Reddit":       5,
    "DailyRemote":  3,
    "RemoteFront":  2,
}

def _allocate_times(total_secs):
    return {b: max(10, int(total_secs * w / 100)) for b, w in BOARD_WEIGHTS.items()}

def _kw_match(job, keywords):
    text = (job.get("title", "") + " " + job.get("description_snippet", "")).lower()
    return any(k.lower() in text for k in keywords)

def _fmt_secs(secs):
    secs = int(secs)
    return f"{secs//60}m {secs%60}s" if secs >= 60 else f"{secs}s"


# ── Scraper functions ─────────────────────────────────────────────────────────

def scrape_linkedin(base, keyword, duration_code, location, max_results, timeout_secs=360):
    section(f"LinkedIn  ('{keyword}' in '{location}', within={duration_code})")
    try:
        r = requests.get(f"{base}/api/jobs/search",
                         params={"keywords": keyword, "location": location,
                                 "posted_within": duration_code, "max_results": max_results},
                         timeout=timeout_secs)
        r.raise_for_status()
        jobs = r.json().get("jobs", [])
        ok(f"LinkedIn → {len(jobs)} jobs")
        return jobs
    except requests.exceptions.Timeout:
        warn("LinkedIn timed out")
        return []
    except Exception as e:
        warn(f"LinkedIn failed: {e}")
        return []


def scrape_naukri(keyword, location, max_results):
    """HTTP-based Naukri scraper using their search API."""
    section(f"Naukri  ('{keyword}' in '{location}')")
    try:
        sys.path.insert(0, str(BACKEND_DIR))
        from modules.board_scrapers.naukri_scraper import NaukriScraper
        jobs = NaukriScraper().scrape_search(keyword, location)[:max_results]
        ok(f"Naukri → {len(jobs)} jobs")
        return jobs
    except Exception as e:
        warn(f"Naukri failed: {e}")
        return []


def scrape_instahyre(keyword, location, max_results):
    """HTTP-based InstaHyre scraper."""
    section(f"InstaHyre  ('{keyword}' in '{location}')")
    try:
        sys.path.insert(0, str(BACKEND_DIR))
        from modules.board_scrapers.instahyre_scraper import InstaHyreScraper
        jobs = InstaHyreScraper().scrape_search(keyword, location)[:max_results]
        ok(f"InstaHyre → {len(jobs)} jobs")
        return jobs
    except Exception as e:
        warn(f"InstaHyre failed: {e}")
        return []


def scrape_wellfound(keyword, max_results):
    try:
        sys.path.insert(0, str(BACKEND_DIR))
        from modules.board_scrapers.wellfound_scraper import WellfoundScraper
        return WellfoundScraper().scrape_search(keyword)[:max_results]
    except Exception as e:
        warn(f"Wellfound failed: {e}")
        return []


def scrape_dailyremote(keyword, max_results):
    try:
        sys.path.insert(0, str(BACKEND_DIR))
        from modules.board_scrapers.dailyremote_scraper import DailyRemoteScraper
        return DailyRemoteScraper().scrape_search(keyword)[:max_results]
    except Exception as e:
        warn(f"DailyRemote failed: {e}")
        return []


def scrape_remotefront(keyword, max_results):
    try:
        sys.path.insert(0, str(BACKEND_DIR))
        from modules.board_scrapers.remotefront_scraper import RemoteFrontScraper
        return RemoteFrontScraper().scrape_search(keyword)[:max_results]
    except Exception as e:
        warn(f"RemoteFront failed: {e}")
        return []


def scrape_reddit(keyword, max_results):
    try:
        sys.path.insert(0, str(BACKEND_DIR))
        from modules.board_scrapers.reddit_scraper import RedditScraper
        return RedditScraper().scrape_search(keyword)[:max_results]
    except Exception as e:
        warn(f"Reddit failed: {e}")
        return []


def scrape_greenhouse(keywords, max_per_company):
    section(f"Greenhouse ATS  ({len(GREENHOUSE_COMPANIES)} companies)")
    sys.path.insert(0, str(BACKEND_DIR))
    try:
        from modules.board_scrapers.greenhouse_scraper import GreenhouseScraper
        scraper = GreenhouseScraper()
        out = []
        for company, url in GREENHOUSE_COMPANIES:
            try:
                raw = scraper.scrape_company(url, company)
                matched = [j for j in raw if _kw_match(j, keywords)][:max_per_company]
                out.extend(matched)
            except: continue
        ok(f"Greenhouse → {len(out)} jobs")
        return out
    except Exception as e:
        warn(f"Greenhouse failed: {e}")
        return []


def scrape_lever(keywords, max_per_company):
    section(f"Lever ATS  ({len(LEVER_COMPANIES)} companies)")
    sys.path.insert(0, str(BACKEND_DIR))
    try:
        from modules.board_scrapers.lever_scraper import LeverScraper
        scraper = LeverScraper()
        out = []
        for company, url in LEVER_COMPANIES:
            try:
                raw = scraper.scrape_company(url, company)
                matched = [j for j in raw if _kw_match(j, keywords)][:max_per_company]
                out.extend(matched)
            except: continue
        ok(f"Lever → {len(out)} jobs")
        return out
    except Exception as e:
        warn(f"Lever failed: {e}")
        return []


def scrape_ashby(keywords, max_per_company):
    section(f"Ashby ATS  ({len(ASHBY_COMPANIES)} companies)")
    sys.path.insert(0, str(BACKEND_DIR))
    try:
        from modules.board_scrapers.ashby_scraper import AshbyScraper
        scraper = AshbyScraper()
        out = []
        for company, url in ASHBY_COMPANIES:
            try:
                raw = scraper.scrape_company(url, company)
                matched = [j for j in raw if _kw_match(j, keywords)][:max_per_company]
                out.extend(matched)
            except: continue
        ok(f"Ashby → {len(out)} jobs")
        return out
    except Exception as e:
        warn(f"Ashby failed: {e}")
        return []


def ingest(base, token, jobs, source):
    """POST jobs to /api/jobs/ingest."""
    if not jobs:
        return {"new": 0, "updated": 0, "skipped": 0}
    try:
        r = requests.post(f"{base}/api/jobs/ingest",
                          json={"jobs": jobs, "source": source},
                          headers={"Authorization": f"Bearer {token}"},
                          timeout=120)
        r.raise_for_status()
        s = r.json()
        info(f"  [{source}] +{s.get('new',0)} new  {s.get('updated',0)} updated  {s.get('skipped',0)} skipped")
        return s
    except Exception as e:
        warn(f"Ingest failed [{source}]: {e}")
        return {"new": 0, "updated": 0, "skipped": 0}


# ── Inputs ────────────────────────────────────────────────────────────────────

def ask_inputs():
    section("Search Parameters")

    raw = input(f"\n  {C.BLD}Keywords{C.RST} {C.DIM}(comma-separated, e.g. 'React Developer, Node.js'){C.RST}\n  > ").strip()
    keywords = [k.strip() for k in raw.split(",") if k.strip()] or ["Software Engineer"]

    all_filter_terms = list(keywords)
    for kw in keywords:
        for base_kw, variants in ROLE_ALIASES.items():
            if base_kw in kw.lower():
                all_filter_terms = list(set(all_filter_terms + variants))
                break

    print(f"\n  {C.BLD}Duration{C.RST}")
    for k, (_, label, _) in DURATIONS.items():
        print(f"    [{k}]  {label}")
    while True:
        d = input(f"\n  Choose [1-6] (default 4 = 24h): ").strip() or "4"
        if d in DURATIONS: break
    dur_code, dur_label, dur_hours = DURATIONS[d]

    location = input(f"\n  {C.BLD}Location{C.RST} {C.DIM}(e.g. India, Remote, United States){C.RST}: ").strip() or "India"

    raw_time = input(f"\n  {C.BLD}Time budget{C.RST} {C.DIM}(e.g. 10m, 30m, 1h — default 15m){C.RST}: ").strip() or "15m"
    def _parse(s):
        s = s.lower().strip()
        if s.endswith("h"): return int(s[:-1]) * 3600
        if s.endswith("m"): return int(s[:-1]) * 60
        return int(s)
    try:
        total_secs = _parse(raw_time)
    except:
        total_secs = 900

    try:
        max_li = int(input("  LinkedIn max / keyword (default 30): ").strip() or "30")
    except: max_li = 30
    try:
        max_board = int(input("  Other boards max / keyword (default 20): ").strip() or "20")
    except: max_board = 20

    return {
        "keywords": keywords,
        "all_filter_terms": all_filter_terms,
        "dur_code": dur_code,
        "dur_label": dur_label,
        "location": location,
        "max_li": max_li,
        "max_board": max_board,
        "total_secs": total_secs,
        "alloc": _allocate_times(total_secs),
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    banner()

    fe_proc = None

    if REMOTE_BACKEND:
        # Use Railway backend directly — no local services needed
        base = REMOTE_BACKEND
        ok(f"Using remote backend: {base}")
    else:
        section("Starting local services")
        be_port = find_free_port(8000)
        fe_port = find_free_port(3000)
        base = f"http://localhost:{be_port}"
        be_proc = start_backend(be_port)
        fe_proc = start_frontend(fe_port, be_port)

        section("Waiting for backend")
        if not wait_for_url(f"{base}/health", "backend", timeout=90):
            try:
                errs = be_proc.stderr.read(3000).decode(errors="replace")
                if errs: print(f"\n{C.RED}Backend stderr:{C.RST}\n{errs}")
            except: pass
            err("Backend failed to start.")
            sys.exit(1)

    section("Authentication")
    try:
        token = get_token(base)
    except Exception as e:
        err(f"Auth failed: {e}")
        sys.exit(1)

    p = ask_inputs()

    print(f"\n  Keywords: {', '.join(p['keywords'])}")
    print(f"  Location: {p['location']}  |  Duration: {p['dur_label']}  |  Budget: {_fmt_secs(p['total_secs'])}")
    input(f"\n  {C.YLW}Press Enter to start scraping…{C.RST} ")

    grand = {"new": 0, "updated": 0, "skipped": 0}
    board_stats = {}
    alloc = p["alloc"]

    def _dedup(jobs):
        seen, out = set(), []
        for j in jobs:
            key = j.get("job_url") or j.get("url") or str(j.get("id", ""))
            if key and key not in seen:
                seen.add(key); out.append(j)
        return out

    def _run_board(label, fn, source):
        budget = alloc.get(label, 60)
        t0 = time.time()
        jobs = []
        try:
            with ThreadPoolExecutor(max_workers=1) as ex:
                jobs = ex.submit(fn).result(timeout=budget)
        except FutureTimeout:
            warn(f"{label} hit budget ({_fmt_secs(budget)})")
        except Exception as e:
            warn(f"{label} error: {e}")
        jobs = _dedup(jobs)
        s = ingest(base, token, jobs, source)
        for k in grand: grand[k] += s.get(k, 0)
        board_stats[label] = {"count": len(jobs), "secs": time.time() - t0}

    # ── LinkedIn: ingest per-keyword immediately so data isn't lost on crash ──
    li_budget = alloc.get("LinkedIn", 180)
    li_per_kw = max(60, li_budget // max(len(p["keywords"]), 1))
    li_total = 0
    for kw in p["keywords"]:
        section(f"LinkedIn '{kw}'")
        jobs = []
        try:
            with ThreadPoolExecutor(max_workers=1) as ex:
                jobs = ex.submit(
                    scrape_linkedin, base, kw, p["dur_code"], p["location"], p["max_li"], li_per_kw
                ).result(timeout=li_per_kw + 30)
        except FutureTimeout:
            warn(f"LinkedIn '{kw}' timed out")
        except Exception as e:
            warn(f"LinkedIn '{kw}' error: {e}")
        if jobs:
            jobs = _dedup(jobs)
            s = ingest(base, token, jobs, "linkedin")
            for k in grand: grand[k] += s.get(k, 0)
            li_total += len(jobs)
    board_stats["LinkedIn"] = {"count": li_total, "secs": li_per_kw * len(p["keywords"])}

    # ── Naukri: one search per keyword ────────────────────────────────────────
    def _naukri():
        out = []
        for kw in p["keywords"]:
            out += scrape_naukri(kw, p["location"], p["max_board"])
        return out
    _run_board("Naukri", _naukri, "naukri")

    # ── InstaHyre: one search per keyword ─────────────────────────────────────
    def _instahyre():
        out = []
        for kw in p["keywords"]:
            out += scrape_instahyre(kw, p["location"], p["max_board"])
        return out
    _run_board("InstaHyre", _instahyre, "instahyre")

    # ── Other boards ──────────────────────────────────────────────────────────
    def _wf():
        out = []
        for kw in p["keywords"]: out += scrape_wellfound(kw, p["max_board"])
        return out
    _run_board("Wellfound", _wf, "wellfound")

    def _dr():
        out = []
        for kw in p["keywords"]: out += scrape_dailyremote(kw, p["max_board"])
        return out
    _run_board("DailyRemote", _dr, "dailyremote")

    def _rf():
        out = []
        for kw in p["keywords"]: out += scrape_remotefront(kw, p["max_board"])
        return out
    _run_board("RemoteFront", _rf, "remotefront")

    def _rd():
        out = []
        for kw in p["keywords"]: out += scrape_reddit(kw, p["max_board"])
        return out
    _run_board("Reddit", _rd, "reddit")

    _run_board("Greenhouse", lambda: scrape_greenhouse(p["all_filter_terms"], 10), "greenhouse")
    _run_board("Lever",      lambda: scrape_lever(p["all_filter_terms"], 10),      "lever")
    _run_board("Ashby",      lambda: scrape_ashby(p["all_filter_terms"], 10),      "ashby")

    # ── Summary ───────────────────────────────────────────────────────────────
    section("Results")
    total_scraped = sum(v["count"] for v in board_stats.values())
    for label, bdata in board_stats.items():
        bar = C.GRN + "█" * min(bdata["count"] // 2, 30) + C.RST
        print(f"  {label:<16}  {bdata['count']:>5} jobs  {_fmt_secs(bdata['secs']):>8}  {bar}")
    print(f"\n  Total scraped: {total_scraped}  |  New in DB: {C.GRN}{grand['new']}{C.RST}  |  Updated: {grand['updated']}")

    if not REMOTE_BACKEND and fe_proc:
        fe_port_used = find_free_port(3000) - 1  # approximate
        wait_for_url(f"http://localhost:3000", "frontend", timeout=60)
        dashboard_url = "http://localhost:3000/dashboard/jobs"
        print(f"\n  {C.BLD}Dashboard:{C.RST}  {C.CYN}{dashboard_url}{C.RST}")
        print(f"  Login: {_SCRAPER_EMAIL}  /  {_SCRAPER_PASS}\n")
        try: webbrowser.open(dashboard_url)
        except: pass
        print(f"  {C.YLW}Press Ctrl+C to stop.{C.RST}\n")
        try:
            while True: time.sleep(15)
        except KeyboardInterrupt:
            _cleanup()
            ok("Stopped.")


if __name__ == "__main__":
    main()
