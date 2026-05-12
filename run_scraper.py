#!/usr/bin/env python3
"""
LinkedIn Automation Suite — One-Click Job Scraper
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Starts the full stack (backend + frontend) on available ports,
asks you what to search for, then scrapes every connected job board
and populates the dashboard automatically.

Supported boards:
  • LinkedIn       (Selenium, uses your .env credentials)
  • Wellfound      (HTTP + Selenium fallback)
  • DailyRemote    (HTTP)
  • RemoteFront    (HTTP)
  • Reddit         (Public JSON API — r/forhire, r/hiring, +9 more)
  • Greenhouse ATS (Public API — 16 top-tier companies)
  • Lever ATS      (Public API — 15 top-tier companies)
  • Ashby ATS      (GraphQL API — 12 top-tier companies)

Usage:
  python run_scraper.py
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

# ── Project paths ─────────────────────────────────────────────────────────────
ROOT        = Path(__file__).parent.resolve()
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR= ROOT / "frontend"

# ── ANSI colours ──────────────────────────────────────────────────────────────
class C:
    GRN  = "\033[92m"
    YLW  = "\033[93m"
    RED  = "\033[91m"
    CYN  = "\033[96m"
    BLD  = "\033[1m"
    DIM  = "\033[2m"
    RST  = "\033[0m"

# Enable ANSI on Windows
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
    print(f"{C.BLD}  LinkedIn Automation Suite  —  Job Scraper{C.RST}")
    print(f"{C.DIM}  Scrapes 8 boards and populates your dashboard{C.RST}")
    print(f"{C.BLD}{C.CYN}{'═'*62}{C.RST}\n")


# ── Port helpers ──────────────────────────────────────────────────────────────
def is_port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) != 0

def find_free_port(start: int) -> int:
    for p in range(start, start + 30):
        if is_port_free(p):
            return p
    raise RuntimeError(f"No free port in range {start}–{start+30}")


# ── Process management ────────────────────────────────────────────────────────
_procs: list = []

def _cleanup():
    for p in _procs:
        try:
            p.terminate()
        except Exception:
            pass

atexit.register(_cleanup)

def _popen(args, cwd, env, **kw):
    flags = {}
    if sys.platform == "win32":
        flags["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    proc = subprocess.Popen(
        args, cwd=str(cwd), env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        **flags, **kw
    )
    _procs.append(proc)
    return proc

def start_backend(port: int) -> subprocess.Popen:
    info(f"Starting backend  → http://localhost:{port}")
    py  = "python" if sys.platform == "win32" else "python3"
    env = {**os.environ, "PYTHONPATH": str(BACKEND_DIR)}
    return _popen(
        [py, "-m", "uvicorn", "api.v2.app:app",
         "--host", "0.0.0.0", "--port", str(port),
         "--log-level", "warning"],
        cwd=BACKEND_DIR, env=env,
    )

def start_frontend(port: int, backend_port: int) -> subprocess.Popen:
    info(f"Starting frontend → http://localhost:{port}")
    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    env = {
        **os.environ,
        "NEXT_PUBLIC_API_URL": f"http://localhost:{backend_port}",
        "PORT": str(port),
    }
    return _popen(
        [npm, "run", "dev", "--", "--port", str(port)],
        cwd=FRONTEND_DIR, env=env,
    )

def wait_for_url(url: str, label: str, timeout: int, ok_statuses=(200,)) -> bool:
    deadline = time.time() + timeout
    print(f"  {C.DIM}Waiting for {label}", end="", flush=True)
    while time.time() < deadline:
        try:
            r = requests.get(url, timeout=2)
            if r.status_code < 500:
                print(f" {C.GRN}ready ✓{C.RST}")
                return True
        except Exception:
            pass
        print(".", end="", flush=True)
        time.sleep(1.5)
    print(f" {C.YLW}timed-out{C.RST}")
    return False


# ── Auth ──────────────────────────────────────────────────────────────────────
_SCRAPER_EMAIL = "scraper@jobflow.io"
_SCRAPER_PASS  = "ScraperBot2024!"
_SCRAPER_NAME  = "Scraper Bot"

def get_token(base: str) -> str:
    """Register (ignore duplicate) then login — return JWT access token."""
    try:
        requests.post(f"{base}/api/auth/register", json={
            "email": _SCRAPER_EMAIL,
            "password": _SCRAPER_PASS,
            "full_name": _SCRAPER_NAME,
        }, timeout=10)
    except Exception:
        pass

    r = requests.post(f"{base}/api/auth/login", json={
        "email": _SCRAPER_EMAIL,
        "password": _SCRAPER_PASS,
    }, timeout=10)
    r.raise_for_status()
    token = r.json().get("access_token")
    if not token:
        raise RuntimeError("Login succeeded but no access_token in response")
    ok("Authenticated with backend")
    return token


# ── Company lists for ATS scrapers ───────────────────────────────────────────
# These boards have no global keyword search — we target known companies
# and filter results by keyword client-side.

GREENHOUSE_COMPANIES = [
    ("Stripe",       "https://boards.greenhouse.io/stripe"),
    ("Airbnb",       "https://boards.greenhouse.io/airbnb"),
    ("Reddit",       "https://boards.greenhouse.io/reddit"),
    ("Figma",        "https://boards.greenhouse.io/figma"),
    ("Notion",       "https://boards.greenhouse.io/notion"),
    ("Dropbox",      "https://boards.greenhouse.io/dropbox"),
    ("DoorDash",     "https://boards.greenhouse.io/doordash"),
    ("Robinhood",    "https://boards.greenhouse.io/robinhood"),
    ("Databricks",   "https://boards.greenhouse.io/databricks"),
    ("Confluent",    "https://boards.greenhouse.io/confluent"),
    ("HashiCorp",    "https://boards.greenhouse.io/hashicorp"),
    ("Plaid",        "https://boards.greenhouse.io/plaid"),
    ("MongoDB",      "https://boards.greenhouse.io/mongodb"),
    ("Cloudflare",   "https://boards.greenhouse.io/cloudflare"),
    ("Twilio",       "https://boards.greenhouse.io/twilio"),
    ("GitLab",       "https://boards.greenhouse.io/gitlab"),
]

LEVER_COMPANIES = [
    ("Netflix",       "https://jobs.lever.co/netflix"),
    ("Shopify",       "https://jobs.lever.co/shopify"),
    ("Coinbase",      "https://jobs.lever.co/coinbase"),
    ("Lyft",          "https://jobs.lever.co/lyft"),
    ("Pinterest",     "https://jobs.lever.co/pinterest"),
    ("Instacart",     "https://jobs.lever.co/instacart"),
    ("OpenAI",        "https://jobs.lever.co/openai"),
    ("Anthropic",     "https://jobs.lever.co/anthropic"),
    ("Cohere",        "https://jobs.lever.co/cohere"),
    ("Scale AI",      "https://jobs.lever.co/scaleai"),
    ("Hugging Face",  "https://jobs.lever.co/huggingface"),
    ("Grammarly",     "https://jobs.lever.co/grammarly"),
    ("Brex",          "https://jobs.lever.co/brex"),
    ("Faire",         "https://jobs.lever.co/faire"),
    ("Ramp",          "https://jobs.lever.co/ramp"),
]

ASHBY_COMPANIES = [
    ("Linear",    "https://jobs.ashbyhq.com/linear"),
    ("Vercel",    "https://jobs.ashbyhq.com/vercel"),
    ("Railway",   "https://jobs.ashbyhq.com/railway"),
    ("Supabase",  "https://jobs.ashbyhq.com/supabase"),
    ("Retool",    "https://jobs.ashbyhq.com/retool"),
    ("Descript",  "https://jobs.ashbyhq.com/descript"),
    ("Replit",    "https://jobs.ashbyhq.com/replit"),
    ("Clerk",     "https://jobs.ashbyhq.com/clerk"),
    ("Resend",    "https://jobs.ashbyhq.com/resend"),
    ("PostHog",   "https://jobs.ashbyhq.com/posthog"),
    ("Raycast",   "https://jobs.ashbyhq.com/raycast"),
    ("Zed",       "https://jobs.ashbyhq.com/zed-industries"),
]


def _kw_match(job: dict, keywords: list) -> bool:
    """True if any keyword appears in the job title or description snippet."""
    text = (
        job.get("title", "") + " " + job.get("description_snippet", "")
    ).lower()
    return any(k.lower() in text for k in keywords)


# ── Duration config ───────────────────────────────────────────────────────────
# Maps user choice → (LinkedIn f_TPR code, display label, hours for cutoff)
DURATIONS = {
    "1": ("1h",    "past 1 hour",    1),
    "2": ("6h",    "past 6 hours",   6),
    "3": ("12h",   "past 12 hours",  12),
    "4": ("24h",   "past 24 hours",  24),
    "5": ("week",  "past week",      168),
    "6": ("month", "past month",     720),
}

# Role aliases so "React Developer" also matches "frontend" jobs etc.
ROLE_ALIASES = {
    "software engineer": ["software engineer", "swe", "developer", "software developer"],
    "frontend":          ["frontend", "front-end", "react", "ui engineer", "vue", "angular"],
    "backend":           ["backend", "back-end", "api engineer", "node", "python developer"],
    "full stack":        ["full stack", "fullstack", "full-stack"],
    "data engineer":     ["data engineer", "data pipeline", "etl", "spark", "kafka"],
    "machine learning":  ["machine learning", "ml engineer", "ai engineer", "deep learning"],
    "devops":            ["devops", "sre", "platform engineer", "infrastructure", "cloud engineer"],
    "product manager":   ["product manager", "pm", "program manager"],
    "data scientist":    ["data scientist", "data science", "analyst"],
    "mobile":            ["mobile", "ios", "android", "react native", "flutter"],
}

# ── Board weights (must sum to 100) ───────────────────────────────────────────
# Weights reflect typical job yield + scraping speed of each source.
# LinkedIn gets the most because it's Selenium-based and returns rich results.
# API-based ATS boards (Greenhouse/Lever/Ashby) are fast so get less time.
BOARD_WEIGHTS = {
    "LinkedIn":    35,   # Selenium, slow, richest results
    "Greenhouse":  12,   # Fast REST API, 16 companies
    "Lever":       12,   # Fast REST API, 15 companies
    "Ashby":        8,   # Fast GraphQL, 12 companies
    "Wellfound":    9,   # HTTP + Selenium fallback, medium yield
    "Reddit":       9,   # Fast public JSON API, broad reach
    "DailyRemote":  8,   # HTTP, lower yield
    "RemoteFront":  7,   # HTTP, lowest yield
}
# Total = 100


def _allocate_times(total_secs: int) -> dict:
    """Return {board_name: allocated_seconds} proportional to BOARD_WEIGHTS."""
    return {
        board: max(10, int(total_secs * weight / 100))
        for board, weight in BOARD_WEIGHTS.items()
    }


# ── Scraper functions ─────────────────────────────────────────────────────────

def scrape_linkedin(base: str, keyword: str, duration_code: str,
                    location: str, max_results: int, timeout_secs: int = 360) -> list:
    section(f"LinkedIn  (keyword='{keyword}', within={duration_code}, budget={_fmt_secs(timeout_secs)})")
    info("This opens a Chrome window — complete any 2FA if prompted.")
    try:
        r = requests.get(
            f"{base}/api/jobs/search",
            params={
                "keywords":     keyword,
                "location":     location,
                "posted_within": duration_code,
                "max_results":  max_results,
            },
            timeout=timeout_secs,
        )
        r.raise_for_status()
        jobs = r.json().get("jobs", [])
        ok(f"LinkedIn → {len(jobs)} jobs found")
        return jobs
    except requests.exceptions.Timeout:
        warn("LinkedIn scraper timed out — partial results may have been saved")
        return []
    except Exception as e:
        warn(f"LinkedIn scraper failed: {e}")
        return []


def scrape_wellfound(keyword: str, max_results: int) -> list:
    section("Wellfound  (formerly AngelList)")
    try:
        sys.path.insert(0, str(BACKEND_DIR))
        from modules.board_scrapers.wellfound_scraper import WellfoundScraper
        jobs = WellfoundScraper().scrape_search(keyword)[:max_results]
        ok(f"Wellfound → {len(jobs)} jobs")
        return jobs
    except Exception as e:
        warn(f"Wellfound failed: {e}")
        return []


def scrape_dailyremote(keyword: str, max_results: int) -> list:
    section("DailyRemote")
    try:
        sys.path.insert(0, str(BACKEND_DIR))
        from modules.board_scrapers.dailyremote_scraper import DailyRemoteScraper
        jobs = DailyRemoteScraper().scrape_search(keyword)[:max_results]
        ok(f"DailyRemote → {len(jobs)} jobs")
        return jobs
    except Exception as e:
        warn(f"DailyRemote failed: {e}")
        return []


def scrape_remotefront(keyword: str, max_results: int) -> list:
    section("RemoteFront")
    try:
        sys.path.insert(0, str(BACKEND_DIR))
        from modules.board_scrapers.remotefront_scraper import RemoteFrontScraper
        jobs = RemoteFrontScraper().scrape_search(keyword)[:max_results]
        ok(f"RemoteFront → {len(jobs)} jobs")
        return jobs
    except Exception as e:
        warn(f"RemoteFront failed: {e}")
        return []


def scrape_reddit(keyword: str, max_results: int) -> list:
    section("Reddit  (r/forhire, r/hiring + 9 subreddits)")
    try:
        sys.path.insert(0, str(BACKEND_DIR))
        from modules.board_scrapers.reddit_scraper import RedditScraper
        jobs = RedditScraper().scrape_search(keyword)[:max_results]
        ok(f"Reddit → {len(jobs)} job posts")
        return jobs
    except Exception as e:
        warn(f"Reddit failed: {e}")
        return []


def scrape_greenhouse(keywords: list, max_per_company: int) -> list:
    section(f"Greenhouse ATS  ({len(GREENHOUSE_COMPANIES)} companies)")
    sys.path.insert(0, str(BACKEND_DIR))
    try:
        from modules.board_scrapers.greenhouse_scraper import GreenhouseScraper
        scraper = GreenhouseScraper()
        all_jobs = []
        for company, url in GREENHOUSE_COMPANIES:
            try:
                raw = scraper.scrape_company(url, company)
                matched = [j for j in raw if _kw_match(j, keywords)]
                all_jobs.extend(matched[:max_per_company])
                if matched:
                    info(f"  {company}: {len(matched)} matching")
            except Exception:
                continue
        ok(f"Greenhouse → {len(all_jobs)} matching jobs across all companies")
        return all_jobs
    except Exception as e:
        warn(f"Greenhouse failed: {e}")
        return []


def scrape_lever(keywords: list, max_per_company: int) -> list:
    section(f"Lever ATS  ({len(LEVER_COMPANIES)} companies)")
    sys.path.insert(0, str(BACKEND_DIR))
    try:
        from modules.board_scrapers.lever_scraper import LeverScraper
        scraper = LeverScraper()
        all_jobs = []
        for company, url in LEVER_COMPANIES:
            try:
                raw = scraper.scrape_company(url, company)
                matched = [j for j in raw if _kw_match(j, keywords)]
                all_jobs.extend(matched[:max_per_company])
                if matched:
                    info(f"  {company}: {len(matched)} matching")
            except Exception:
                continue
        ok(f"Lever → {len(all_jobs)} matching jobs across all companies")
        return all_jobs
    except Exception as e:
        warn(f"Lever failed: {e}")
        return []


def scrape_ashby(keywords: list, max_per_company: int) -> list:
    section(f"Ashby ATS  ({len(ASHBY_COMPANIES)} companies)")
    sys.path.insert(0, str(BACKEND_DIR))
    try:
        from modules.board_scrapers.ashby_scraper import AshbyScraper
        scraper = AshbyScraper()
        all_jobs = []
        for company, url in ASHBY_COMPANIES:
            try:
                raw = scraper.scrape_company(url, company)
                matched = [j for j in raw if _kw_match(j, keywords)]
                all_jobs.extend(matched[:max_per_company])
                if matched:
                    info(f"  {company}: {len(matched)} matching")
            except Exception:
                continue
        ok(f"Ashby → {len(all_jobs)} matching jobs across all companies")
        return all_jobs
    except Exception as e:
        warn(f"Ashby failed: {e}")
        return []


def ingest(base: str, token: str, jobs: list, source: str) -> dict:
    """POST jobs to /api/jobs/ingest and return stats."""
    if not jobs:
        return {"new": 0, "updated": 0, "skipped": 0}
    try:
        r = requests.post(
            f"{base}/api/jobs/ingest",
            json={"jobs": jobs, "source": source},
            headers={"Authorization": f"Bearer {token}"},
            timeout=120,
        )
        r.raise_for_status()
        stats = r.json()
        info(f"  Ingested [{source}]: "
             f"+{stats.get('new',0)} new  "
             f"{stats.get('updated',0)} updated  "
             f"{stats.get('skipped',0)} skipped")
        return stats
    except Exception as e:
        warn(f"Ingest failed for '{source}': {e}")
        return {"new": 0, "updated": 0, "skipped": 0}


# ── Timing helper ─────────────────────────────────────────────────────────────

def _fmt_secs(secs: float) -> str:
    secs = int(secs)
    return f"{secs // 60}m {secs % 60}s" if secs >= 60 else f"{secs}s"


# ── User prompt ───────────────────────────────────────────────────────────────

def ask_inputs() -> dict:
    section("Search Parameters")

    # ── Keywords (comma-separated) ────────────────────────────────────────────
    raw = input(
        f"\n  {C.BLD}Job role / keywords{C.RST}  "
        f"{C.DIM}comma-separated, e.g. 'React Developer, Node.js Engineer'{C.RST}\n  > "
    ).strip()
    if not raw:
        raw = "Software Engineer"
        warn(f"No input — defaulting to 'Software Engineer'")

    # Split on comma, clean each keyword
    keywords = [k.strip() for k in raw.split(",") if k.strip()]
    if not keywords:
        keywords = ["Software Engineer"]

    # Expand each keyword with role aliases, collect unique filter terms
    all_filter_terms: list = list(keywords)  # used for ATS company filtering
    for kw in keywords:
        for base_kw, variants in ROLE_ALIASES.items():
            if base_kw in kw.lower():
                all_filter_terms = list(set(all_filter_terms + variants))
                break

    # ── Duration ──────────────────────────────────────────────────────────────
    print(f"\n  {C.BLD}Duration (how recently posted){C.RST}")
    for k, (_, label, _) in DURATIONS.items():
        print(f"    [{k}]  {label}")
    while True:
        dur_raw = input(f"\n  Choose [1-6]  {C.DIM}(default 4 = past 24 hours){C.RST}: ").strip()
        if not dur_raw:
            dur_raw = "4"
        if dur_raw in DURATIONS:
            break
        warn(f"Invalid choice '{dur_raw}' — enter a number 1 to 6")
    dur_code, dur_label, dur_hours = DURATIONS[dur_raw]

    # ── Location ──────────────────────────────────────────────────────────────
    location = input(
        f"\n  {C.BLD}Location{C.RST}  "
        f"{C.DIM}(e.g. 'Remote', 'United States', 'India') — default: Remote{C.RST}: "
    ).strip() or "Remote"

    # ── Total time budget ─────────────────────────────────────────────────────
    print(f"\n  {C.BLD}Total scrape time budget{C.RST}  "
          f"{C.DIM}(script divides this across all 8 boards by their typical yield){C.RST}")
    print(f"    Examples: 5m, 10m, 15m, 30m, 1h — or just enter seconds (e.g. 300)")
    raw_time = input("    Budget  (default 10m): ").strip() or "10m"

    # Parse time string → seconds
    def _parse_time(s: str) -> int:
        s = s.lower().strip()
        if s.endswith("h"):
            return int(s[:-1]) * 3600
        if s.endswith("m"):
            return int(s[:-1]) * 60
        if s.endswith("s"):
            return int(s[:-1])
        return int(s)  # bare number treated as seconds

    try:
        total_budget_secs = _parse_time(raw_time)
        if total_budget_secs < 60:
            warn("Budget is very short (<60s) — some boards may timeout with 0 results")
    except ValueError:
        warn(f"Could not parse '{raw_time}', defaulting to 10 minutes")
        total_budget_secs = 600

    # ── Result limits ─────────────────────────────────────────────────────────
    print(f"\n  {C.BLD}Result limits per keyword{C.RST}  {C.DIM}(Enter = use defaults){C.RST}")
    try:
        max_li = int(input("    LinkedIn max results / keyword  (default 30): ").strip() or "30")
    except ValueError:
        max_li = 30
    try:
        max_board = int(input("    Other boards max / keyword      (default 20): ").strip() or "20")
    except ValueError:
        max_board = 20

    posted_after = datetime.now(timezone.utc) - timedelta(hours=dur_hours)
    alloc = _allocate_times(total_budget_secs)

    return {
        "keywords":           keywords,
        "all_filter_terms":   all_filter_terms,
        "dur_code":           dur_code,
        "dur_label":          dur_label,
        "location":           location,
        "max_li":             max_li,
        "max_board":          max_board,
        "posted_after":       posted_after,
        "total_budget_secs":  total_budget_secs,
        "alloc":              alloc,      # {board_name: seconds}
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    banner()

    # ── 1. Ports ──────────────────────────────────────────────────────────────
    section("Finding available ports")
    be_port = find_free_port(8000)
    fe_port = find_free_port(3000)
    ok(f"Backend  port: {be_port}")
    ok(f"Frontend port: {fe_port}")
    base = f"http://localhost:{be_port}"

    # ── 2. Start services ─────────────────────────────────────────────────────
    section("Starting services")
    be_proc = start_backend(be_port)
    fe_proc = start_frontend(fe_port, be_port)

    # ── 3. Wait for backend ───────────────────────────────────────────────────
    section("Waiting for backend")
    if not wait_for_url(f"{base}/health", "backend", timeout=90):
        try:
            errs = be_proc.stderr.read(3000).decode(errors="replace")
            if errs:
                print(f"\n{C.RED}Backend stderr:{C.RST}\n{errs}")
        except Exception:
            pass
        err("Backend failed to start. Check your virtual environment and .env file.")
        sys.exit(1)

    # ── 4. Auth ───────────────────────────────────────────────────────────────
    section("Authentication")
    try:
        token = get_token(base)
    except Exception as exc:
        err(f"Auth failed: {exc}")
        sys.exit(1)

    # ── 5. Inputs ─────────────────────────────────────────────────────────────
    p = ask_inputs()

    print(f"\n  {C.BLD}Confirmed search:{C.RST}")
    print(f"    Keywords ({len(p['keywords'])}):")
    for kw in p["keywords"]:
        print(f"      • {kw}")
    print(f"    Duration:        {p['dur_label']}")
    print(f"    Location:        {p['location']}")
    print(f"    Total budget:    {_fmt_secs(p['total_budget_secs'])}")
    print(f"    LinkedIn:        up to {p['max_li']} results / keyword")
    print(f"    Per board:       up to {p['max_board']} results / keyword")
    extra = [t for t in p["all_filter_terms"] if t not in p["keywords"]]
    if extra:
        print(f"    ATS filter:      + {', '.join(extra[:6])}")

    # Show time allocation table
    print(f"\n  {C.BLD}Time allocation across boards:{C.RST}")
    print(f"    {'Board':<16}  {'Weight':>7}  {'Allocated'}")
    print(f"    {'─'*16}  {'─'*7}  {'─'*10}")
    for board, secs in p["alloc"].items():
        weight = BOARD_WEIGHTS[board]
        bar = "▓" * (weight // 3)
        print(f"    {board:<16}  {weight:>5}%   {_fmt_secs(secs):>8}  {bar}")

    input(f"\n  {C.YLW}Press Enter to start scraping…{C.RST} ")

    # ── 6. Scrape ─────────────────────────────────────────────────────────────
    # Each board: scrape each keyword separately, deduplicate by job_url, ingest once.

    grand_total  = {"new": 0, "updated": 0, "skipped": 0}
    board_stats  : dict = {}   # label → {count, secs}
    scrape_start = time.time()

    alloc = p["alloc"]   # {board_name: allocated_seconds}

    def _dedup(jobs: list) -> list:
        """Remove duplicate jobs by job_url."""
        seen, out = set(), []
        for j in jobs:
            key = j.get("job_url") or j.get("url") or str(j.get("id", ""))
            if key and key not in seen:
                seen.add(key)
                out.append(j)
        return out

    def _run_board(label: str, fn, source: str):
        """
        Run fn() inside a thread with a hard timeout = alloc[label].
        If it times out, we get whatever the thread collected before cutoff
        (it will be 0 for Selenium-based boards since results come all at once).
        """
        budget = alloc.get(label, 60)
        t0 = time.time()
        info(f"Starting {label}  (budget: {_fmt_secs(budget)})")
        jobs = []
        try:
            with ThreadPoolExecutor(max_workers=1) as ex:
                future = ex.submit(fn)
                jobs = future.result(timeout=budget)
        except FutureTimeout:
            warn(f"{label} hit its time budget ({_fmt_secs(budget)}) — using partial results")
        except Exception as e:
            warn(f"{label} error: {e}")

        jobs = _dedup(jobs)
        elapsed = time.time() - t0
        status = f"{C.YLW}TIMEOUT{C.RST}" if elapsed >= budget - 1 else f"{C.GRN}done{C.RST}"
        stats = ingest(base, token, jobs, source)
        grand_total["new"]     += stats.get("new", 0)
        grand_total["updated"] += stats.get("updated", 0)
        grand_total["skipped"] += stats.get("skipped", 0)
        board_stats[label] = {"count": len(jobs), "secs": elapsed, "budget": budget}
        print(f"  {C.DIM}  ↳ {label}: {len(jobs)} jobs  {_fmt_secs(elapsed)} / {_fmt_secs(budget)}  [{status}{C.DIM}]{C.RST}")

    # LinkedIn — one search per keyword, merged + deduped
    # Note: timeout here is passed to requests; the outer _run_board also enforces it.
    li_budget = alloc.get("LinkedIn", 210)
    def _li():
        all_li = []
        per_kw = max(10, li_budget // max(len(p["keywords"]), 1))
        for kw in p["keywords"]:
            all_li += scrape_linkedin(
                base, kw, p["dur_code"], p["location"], p["max_li"],
                timeout_secs=per_kw,
            )
        return _dedup(all_li)
    _run_board("LinkedIn",    _li, "linkedin")

    # Wellfound — one search per keyword
    def _wf():
        out = []
        for kw in p["keywords"]:
            out += scrape_wellfound(kw, p["max_board"])
        return out
    _run_board("Wellfound",   _wf, "wellfound")

    # DailyRemote — one search per keyword
    def _dr():
        out = []
        for kw in p["keywords"]:
            out += scrape_dailyremote(kw, p["max_board"])
        return out
    _run_board("DailyRemote", _dr, "dailyremote")

    # RemoteFront — one search per keyword
    def _rf():
        out = []
        for kw in p["keywords"]:
            out += scrape_remotefront(kw, p["max_board"])
        return out
    _run_board("RemoteFront", _rf, "remotefront")

    # Reddit — one search per keyword
    def _rd():
        out = []
        for kw in p["keywords"]:
            out += scrape_reddit(kw, p["max_board"])
        return out
    _run_board("Reddit",      _rd, "reddit")

    # ATS boards use expanded keyword list for filtering (company-level scrape, no global search)
    _run_board("Greenhouse", lambda: scrape_greenhouse(p["all_filter_terms"], 10), "greenhouse")
    _run_board("Lever",      lambda: scrape_lever(p["all_filter_terms"],      10), "lever")
    _run_board("Ashby",      lambda: scrape_ashby(p["all_filter_terms"],      10), "ashby")

    total_elapsed = time.time() - scrape_start

    # ── 7. Wait for frontend ──────────────────────────────────────────────────
    section("Frontend")
    wait_for_url(f"http://localhost:{fe_port}", "frontend (Next.js)", timeout=120)

    # ── 8. Summary ────────────────────────────────────────────────────────────
    section("Results")
    print()
    print(f"  {'Board':<16}  {'Jobs':>5}  {'Actual':>8}  {'Budget':>8}  {'Bar'}")
    print(f"  {'─'*16}  {'─'*5}  {'─'*8}  {'─'*8}  {'─'*26}")
    total_scraped = 0
    for label, bdata in board_stats.items():
        count  = bdata["count"]
        secs   = bdata["secs"]
        budget = bdata.get("budget", 0)
        timed_out = secs >= budget - 1 and budget > 0
        bar   = (C.YLW if timed_out else C.GRN) + "█" * min(count // 2, 26) + C.RST
        flag  = f" {C.YLW}⏱{C.RST}" if timed_out else ""
        total_scraped += count
        print(f"  {label:<16}  {count:>5}  {_fmt_secs(secs):>8}  {_fmt_secs(budget):>8}  {bar}{flag}")
    print(f"  {'─'*16}  {'─'*5}  {'─'*8}  {'─'*8}")
    print(f"  {'TOTAL':<16}  {total_scraped:>5}  {_fmt_secs(total_elapsed):>8}  {_fmt_secs(p['total_budget_secs']):>8}")
    print()
    print(f"  {C.BLD}New in DB     :{C.RST}  {C.GRN}{grand_total['new']}{C.RST}")
    print(f"  {C.BLD}Updated       :{C.RST}  {grand_total['updated']}")
    print(f"  {C.BLD}Skipped (dup) :{C.RST}  {grand_total['skipped']}")
    print(f"  {C.BLD}Keywords      :{C.RST}  {', '.join(p['keywords'])}")

    dashboard_url = f"http://localhost:{fe_port}/dashboard/jobs"
    print(f"\n  {C.BLD}Dashboard:{C.RST}  {C.CYN}{dashboard_url}{C.RST}")
    print(f"\n  {C.DIM}Dashboard login:  {_SCRAPER_EMAIL}  /  {_SCRAPER_PASS}{C.RST}\n")

    try:
        webbrowser.open(dashboard_url)
    except Exception:
        pass

    # ── 9. Keep alive ─────────────────────────────────────────────────────────
    print(f"  {C.YLW}Services are running. Press Ctrl+C to stop.{C.RST}\n")
    try:
        while True:
            if be_proc.poll() is not None:
                warn("Backend process exited unexpectedly.")
            if fe_proc.poll() is not None:
                warn("Frontend process exited unexpectedly.")
            time.sleep(15)
    except KeyboardInterrupt:
        section("Shutting down")
        _cleanup()
        ok("All services stopped.")


if __name__ == "__main__":
    main()
