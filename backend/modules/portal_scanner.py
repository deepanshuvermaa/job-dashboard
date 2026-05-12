"""
Portal Scanner - Orchestrates scraping across all configured company career pages and job boards.
Loads configuration from portals.yml and runs the appropriate scraper for each portal.
Also supports auto-detected portals from awesome-career-pages via ATS detection.
"""

import json
import yaml
from pathlib import Path
from typing import List, Dict, Callable, Optional

from modules.board_scrapers import SCRAPER_MAP


class PortalScanner:
    """Scans configured company career portals and job boards"""

    def __init__(self, config_path: str = None):
        self.config_path = config_path or str(
            Path(__file__).parent.parent / "config" / "portals.yml"
        )
        self.detected_path = str(
            Path(__file__).parent.parent / "config" / "detected_portals.json"
        )
        self.config = self._load_config()
        self._scraper_instances = {}

    def _load_config(self) -> dict:
        """Load portal configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(f"[WARN] Portal config not found at {self.config_path}")
            return {"portals": [], "search_queries": [], "board_settings": {}}
        except Exception as e:
            print(f"[ERROR] Failed to load portal config: {e}")
            return {"portals": [], "search_queries": [], "board_settings": {}}

    def _get_scraper(self, ats_type: str):
        """Get or create a scraper instance for the given ATS type"""
        if ats_type not in self._scraper_instances:
            scraper_class = SCRAPER_MAP.get(ats_type)
            if not scraper_class:
                print(f"[WARN] No scraper for ATS type: {ats_type}")
                return None

            # Apply board-specific rate limit if configured
            board_settings = self.config.get('board_settings', {}).get(ats_type, {})
            rate_limit = board_settings.get('rate_limit_ms', 1000)
            self._scraper_instances[ats_type] = scraper_class(rate_limit_ms=rate_limit)

        return self._scraper_instances[ats_type]

    def scan_all_portals(self, progress_callback: Optional[Callable] = None, keyword_filter: str = None, location_filter: str = None) -> List[Dict]:
        """Scan all enabled portals and search queries, return normalized jobs"""
        all_jobs = []
        portals = self.config.get('portals', [])
        queries = self.config.get('search_queries', [])

        enabled_portals = [p for p in portals if p.get('enabled', True)]
        total_tasks = len(enabled_portals) + len(queries)
        completed = 0

        print(f"\n{'='*60}")
        print(f"PORTAL SCANNER: {len(enabled_portals)} companies + {len(queries)} search queries")
        print(f"{'='*60}")

        # Phase 1: Scan company career pages
        print(f"\n--- Phase 1: Company Career Pages ({len(enabled_portals)} portals) ---")
        for portal in enabled_portals:
            try:
                jobs = self.scan_portal(portal)
                all_jobs.extend(jobs)
                completed += 1
                if progress_callback:
                    progress_callback({
                        "status": "scanning",
                        "completed": completed,
                        "total": total_tasks,
                        "current": portal.get('name', 'Unknown'),
                        "jobs_found": len(all_jobs)
                    })
            except Exception as e:
                print(f"[ERROR] Failed to scan {portal.get('name')}: {e}")
                completed += 1

        # Phase 2: Run search queries on aggregator boards
        print(f"\n--- Phase 2: Search Queries ({len(queries)} queries) ---")
        for query_config in queries:
            try:
                jobs = self.scan_search_query(query_config)
                all_jobs.extend(jobs)
                completed += 1
                if progress_callback:
                    progress_callback({
                        "status": "searching",
                        "completed": completed,
                        "total": total_tasks,
                        "current": query_config.get('keywords', 'Unknown'),
                        "jobs_found": len(all_jobs)
                    })
            except Exception as e:
                print(f"[ERROR] Failed search query '{query_config.get('keywords')}': {e}")
                completed += 1

        # Apply optional keyword/location filters
        if keyword_filter or location_filter:
            filtered = []
            kw_lower = keyword_filter.lower() if keyword_filter else None
            loc_lower = location_filter.lower() if location_filter else None
            for job in all_jobs:
                title = (job.get('title', '') or '').lower()
                desc = (job.get('description_snippet', '') or '').lower()
                location = (job.get('location', '') or '').lower()

                kw_match = not kw_lower or (kw_lower in title or kw_lower in desc)
                loc_match = not loc_lower or loc_lower in location

                if kw_match and loc_match:
                    filtered.append(job)

            print(f"[Filter] {len(filtered)} jobs match filters (keyword='{keyword_filter}', location='{location_filter}') out of {len(all_jobs)}")
            all_jobs = filtered

        print(f"\n{'='*60}")
        print(f"PORTAL SCANNER COMPLETE: {len(all_jobs)} total jobs found")
        print(f"{'='*60}")

        return all_jobs

    def scan_portal(self, portal_config: dict) -> List[Dict]:
        """Scan a single company portal"""
        name = portal_config.get('name', 'Unknown')
        ats = portal_config.get('ats', '')
        url = portal_config.get('url', '')

        if not ats or not url:
            print(f"  [SKIP] {name}: missing ats or url")
            return []

        scraper = self._get_scraper(ats)
        if not scraper:
            return []

        print(f"\nScanning: {name} ({ats})")
        jobs = scraper.scrape_company(url, name)
        return jobs

    def scan_search_query(self, query_config: dict) -> List[Dict]:
        """Run a search query across configured boards"""
        keywords = query_config.get('keywords', '')
        boards = query_config.get('boards', [])

        if not keywords or not boards:
            return []

        all_jobs = []
        print(f"\nSearching: '{keywords}' on {boards}")

        for board_name in boards:
            scraper = self._get_scraper(board_name)
            if not scraper:
                continue

            try:
                jobs = scraper.scrape_search(keywords)
                all_jobs.extend(jobs)
            except Exception as e:
                print(f"  [ERROR] {board_name} search for '{keywords}': {e}")

        return all_jobs

    def scan_single(self, portal_name: str) -> List[Dict]:
        """Scan a single portal by name"""
        portals = self.config.get('portals', [])
        portal = next((p for p in portals if p.get('name', '').lower() == portal_name.lower()), None)

        if not portal:
            print(f"[ERROR] Portal '{portal_name}' not found in config")
            return []

        return self.scan_portal(portal)

    def get_enabled_portals(self) -> List[Dict]:
        """Get list of enabled portals"""
        return [p for p in self.config.get('portals', []) if p.get('enabled', True)]

    def get_search_queries(self) -> List[Dict]:
        """Get configured search queries"""
        return self.config.get('search_queries', [])

    def _load_detected_portals(self, ats_types: List[str] = None) -> List[Dict]:
        """Load auto-detected portals from ATS detection results"""
        if ats_types is None:
            ats_types = ['greenhouse', 'lever', 'ashby', 'workable', 'darwinbox',
                         'structured_data', 'generic', 'eightfold', 'freshteam']
        try:
            with open(self.detected_path, 'r', encoding='utf-8') as f:
                detected = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

        # Convert detected entries to portal format, dedup against existing
        existing_urls = {p.get('url', '').lower() for p in self.config.get('portals', [])}
        existing_names = {p.get('name', '').lower() for p in self.config.get('portals', [])}

        new_portals = []
        for entry in detected:
            ats = entry.get('ats', 'unknown')
            if ats not in ats_types:
                continue

            url = entry.get('ats_url') or entry.get('original_url', '')
            name = entry.get('company', '')
            if not url or not name:
                continue

            # Skip if already in portals.yml
            if url.lower() in existing_urls or name.lower() in existing_names:
                continue

            new_portals.append({
                'name': name,
                'ats': ats,
                'url': url,
                'enabled': True,
                'source': 'auto-detected',
            })

        return new_portals

    def scan_all_portals_extended(self, progress_callback: Optional[Callable] = None,
                                  keyword_filter: str = None, location_filter: str = None,
                                  include_detected: bool = True,
                                  detected_ats_types: List[str] = None) -> List[Dict]:
        """Extended scan that includes both portals.yml AND auto-detected portals"""
        # Start with normal scan
        all_jobs = self.scan_all_portals(
            progress_callback=progress_callback,
            keyword_filter=keyword_filter,
            location_filter=location_filter
        )

        # Add auto-detected portals
        if include_detected:
            detected_portals = self._load_detected_portals(ats_types=detected_ats_types)
            if detected_portals:
                print(f"\n--- Phase 3: Auto-Detected Portals ({len(detected_portals)} companies) ---")
                for i, portal in enumerate(detected_portals):
                    try:
                        jobs = self.scan_portal(portal)

                        # Apply filters
                        if keyword_filter or location_filter:
                            kw_lower = keyword_filter.lower() if keyword_filter else None
                            loc_lower = location_filter.lower() if location_filter else None
                            jobs = [j for j in jobs if
                                    (not kw_lower or kw_lower in (j.get('title', '') + j.get('description_snippet', '')).lower()) and
                                    (not loc_lower or loc_lower in (j.get('location', '')).lower())]

                        all_jobs.extend(jobs)

                        if progress_callback:
                            progress_callback({
                                "status": "scanning_detected",
                                "completed": i + 1,
                                "total": len(detected_portals),
                                "current": portal.get('name', 'Unknown'),
                                "jobs_found": len(all_jobs),
                                "phase": "auto-detected"
                            })
                    except Exception as e:
                        print(f"[ERROR] Auto-detected portal {portal.get('name')}: {e}")

                print(f"[OK] Auto-detected portals added {len(all_jobs)} total jobs")

        return all_jobs
