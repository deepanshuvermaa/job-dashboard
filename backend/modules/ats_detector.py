"""
ATS Detection Engine
Automatically detects which Applicant Tracking System powers a company's career page.
Checks URL patterns first (fast), then falls back to HTML analysis.
"""

import re
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed


# URL-based detection patterns (no HTTP request needed)
URL_PATTERNS = [
    (r'boards\.greenhouse\.io/([^/?#]+)', 'greenhouse', lambda m: f'https://boards.greenhouse.io/{m.group(1)}'),
    (r'job-boards\.greenhouse\.io/([^/?#]+)', 'greenhouse', lambda m: f'https://boards.greenhouse.io/{m.group(1)}'),
    (r'jobs\.lever\.co/([^/?#]+)', 'lever', lambda m: f'https://jobs.lever.co/{m.group(1)}'),
    (r'jobs\.ashbyhq\.com/([^/?#]+)', 'ashby', lambda m: f'https://jobs.ashbyhq.com/{m.group(1)}'),
    (r'apply\.workable\.com/([^/?#]+)', 'workable', lambda m: f'https://apply.workable.com/{m.group(1)}'),
    (r'([^/]+)\.darwinbox\.in', 'darwinbox', lambda m: m.group(0)),
    (r'([^/]+)\.eightfold\.ai', 'eightfold', lambda m: m.group(0)),
    (r'([^/]+)\.freshteam\.com', 'freshteam', lambda m: m.group(0)),
    (r'([^/]+)\.recruitee\.com', 'recruitee', lambda m: m.group(0)),
    (r'([^/]+)\.zohorecruit\.com', 'zoho_recruit', lambda m: m.group(0)),
    (r'([^/]+)\.smartrecruiters\.com', 'smartrecruiters', lambda m: m.group(0)),
    (r'careers\.google\.com', 'google_careers', None),
    (r'amazon\.jobs', 'amazon_jobs', None),
    (r'linkedin\.com/company/([^/]+)/jobs', 'linkedin', None),
]

# HTML-based detection patterns (requires fetching the page)
HTML_SIGNATURES = [
    ('greenhouse', [
        r'boards\.greenhouse\.io/([^"\'>\s]+)',
        r'grnh\.se/',
        r'greenhouse\.io',
        r'id="grnhse_app"',
    ]),
    ('lever', [
        r'jobs\.lever\.co/([^"\'>\s]+)',
        r'lever\.co/([^"\'>\s]+)/apply',
        r'lever-jobs-container',
    ]),
    ('ashby', [
        r'jobs\.ashbyhq\.com/([^"\'>\s]+)',
        r'ashbyhq\.com',
    ]),
    ('workable', [
        r'apply\.workable\.com/([^"\'>\s]+)',
        r'workable\.com',
        r'wrkbl\.ink',
    ]),
    ('darwinbox', [
        r'darwinbox\.in',
        r'darwinbox\.io',
    ]),
    ('eightfold', [
        r'eightfold\.ai',
    ]),
    ('freshteam', [
        r'freshteam\.com',
    ]),
    ('smartrecruiters', [
        r'smartrecruiters\.com',
        r'jobs\.smartrecruiters\.com',
    ]),
    ('recruitee', [
        r'recruitee\.com',
        r'careers\.recruitee',
    ]),
    ('bamboohr', [
        r'bamboohr\.com/careers',
        r'bamboohr\.com/jobs',
    ]),
    ('icims', [
        r'icims\.com',
        r'careers-.*\.icims\.com',
    ]),
    ('myworkdayjobs', [
        r'myworkdayjobs\.com',
        r'workday\.com/.*career',
    ]),
    ('taleo', [
        r'taleo\.net',
        r'oracle\.com/.*taleo',
    ]),
    ('jobvite', [
        r'jobvite\.com',
        r'jobs\.jobvite\.com',
    ]),
    ('structured_data', [
        r'"@type"\s*:\s*"JobPosting"',
        r'schema\.org/JobPosting',
    ]),
]


class ATSDetector:
    """Detect which ATS system powers a company's career page"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        self.cache_path = Path(__file__).parent.parent / "config" / "detected_portals.json"

    def detect_single(self, url: str, company_name: str = "") -> Dict:
        """Detect ATS for a single URL"""
        result = {
            'company': company_name,
            'original_url': url,
            'ats': 'unknown',
            'ats_url': None,
            'detection_method': None,
            'has_structured_data': False,
        }

        # Phase 1: URL pattern matching (fast, no HTTP request)
        for pattern, ats_name, url_extractor in URL_PATTERNS:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                result['ats'] = ats_name
                result['ats_url'] = url_extractor(match) if url_extractor else url
                result['detection_method'] = 'url_pattern'
                return result

        # Phase 2: Fetch HTML and scan for signatures
        try:
            resp = self.session.get(url, timeout=10, allow_redirects=True)
            if resp.status_code != 200:
                result['detection_method'] = f'http_error_{resp.status_code}'
                return result

            html = resp.text
            final_url = resp.url  # After redirects

            # Check if redirect went to a known ATS
            for pattern, ats_name, url_extractor in URL_PATTERNS:
                match = re.search(pattern, final_url, re.IGNORECASE)
                if match:
                    result['ats'] = ats_name
                    result['ats_url'] = url_extractor(match) if url_extractor else final_url
                    result['detection_method'] = 'redirect'
                    return result

            # Scan HTML for ATS signatures
            for ats_name, patterns in HTML_SIGNATURES:
                for pat in patterns:
                    match = re.search(pat, html, re.IGNORECASE)
                    if match:
                        result['ats'] = ats_name
                        result['detection_method'] = 'html_signature'

                        # Try to extract the ATS-specific URL
                        if ats_name == 'greenhouse':
                            gh_match = re.search(r'boards\.greenhouse\.io/([^"\'>\s/]+)', html)
                            if gh_match:
                                result['ats_url'] = f'https://boards.greenhouse.io/{gh_match.group(1)}'
                        elif ats_name == 'lever':
                            lv_match = re.search(r'jobs\.lever\.co/([^"\'>\s/]+)', html)
                            if lv_match:
                                result['ats_url'] = f'https://jobs.lever.co/{lv_match.group(1)}'
                        elif ats_name == 'ashby':
                            ab_match = re.search(r'jobs\.ashbyhq\.com/([^"\'>\s/]+)', html)
                            if ab_match:
                                result['ats_url'] = f'https://jobs.ashbyhq.com/{ab_match.group(1)}'
                        elif ats_name == 'workable':
                            wk_match = re.search(r'apply\.workable\.com/([^"\'>\s/]+)', html)
                            if wk_match:
                                result['ats_url'] = f'https://apply.workable.com/{wk_match.group(1)}'

                        if ats_name == 'structured_data':
                            result['has_structured_data'] = True
                            result['ats'] = 'structured_data'
                        return result

        except requests.exceptions.Timeout:
            result['detection_method'] = 'timeout'
        except requests.exceptions.ConnectionError:
            result['detection_method'] = 'connection_error'
        except Exception as e:
            result['detection_method'] = f'error: {str(e)[:50]}'

        return result

    def detect_batch(self, companies: List[Dict], max_workers: int = 10,
                     progress_callback=None) -> List[Dict]:
        """Detect ATS for a batch of companies using thread pool"""
        results = []
        total = len(companies)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for company in companies:
                name = company.get('Title', company.get('name', ''))
                url = company.get('Link', company.get('url', ''))
                if url:
                    future = executor.submit(self.detect_single, url, name)
                    futures[future] = company

            for i, future in enumerate(as_completed(futures)):
                try:
                    result = future.result(timeout=15)
                    results.append(result)
                except Exception as e:
                    company = futures[future]
                    results.append({
                        'company': company.get('Title', company.get('name', '')),
                        'original_url': company.get('Link', company.get('url', '')),
                        'ats': 'error',
                        'detection_method': f'exception: {str(e)[:50]}',
                    })

                if progress_callback and (i + 1) % 10 == 0:
                    progress_callback({
                        'completed': i + 1,
                        'total': total,
                        'current': result.get('company', ''),
                        'ats': result.get('ats', ''),
                    })

        return results

    def load_awesome_career_pages(self) -> List[Dict]:
        """Load companies from awesome-career-pages Portal.json"""
        json_path = Path(__file__).parent.parent / "config" / "awesome_career_pages.json"
        if not json_path.exists():
            print(f"[ATSDetector] File not found: {json_path}")
            return []
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def detect_and_save(self, companies: List[Dict] = None, max_workers: int = 10,
                        progress_callback=None) -> Dict:
        """Detect ATS for all companies and save results"""
        if companies is None:
            companies = self.load_awesome_career_pages()

        if not companies:
            return {'error': 'No companies to detect'}

        print(f"[ATSDetector] Starting detection for {len(companies)} companies...")
        results = self.detect_batch(companies, max_workers=max_workers,
                                    progress_callback=progress_callback)

        # Save results
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)

        # Build summary
        ats_counts = {}
        for r in results:
            ats = r.get('ats', 'unknown')
            ats_counts[ats] = ats_counts.get(ats, 0) + 1

        summary = {
            'total_companies': len(results),
            'ats_breakdown': dict(sorted(ats_counts.items(), key=lambda x: -x[1])),
            'scrapeable': sum(1 for r in results if r.get('ats') in
                            ['greenhouse', 'lever', 'ashby', 'workable', 'darwinbox',
                             'eightfold', 'freshteam', 'structured_data']),
            'saved_to': str(self.cache_path),
        }

        print(f"[ATSDetector] Detection complete:")
        for ats, count in summary['ats_breakdown'].items():
            print(f"  {ats}: {count}")
        print(f"  Directly scrapeable: {summary['scrapeable']}")

        return summary

    def get_detected_portals(self, ats_filter: str = None) -> List[Dict]:
        """Load previously detected portals, optionally filtered by ATS type"""
        if not self.cache_path.exists():
            return []
        with open(self.cache_path, 'r', encoding='utf-8') as f:
            results = json.load(f)

        if ats_filter:
            results = [r for r in results if r.get('ats') == ats_filter]

        return results

    def generate_portals_yaml(self, ats_types: List[str] = None) -> List[Dict]:
        """Generate portal entries compatible with portals.yml format from detected results"""
        if ats_types is None:
            ats_types = ['greenhouse', 'lever', 'ashby', 'workable']

        detected = self.get_detected_portals()
        portals = []

        for entry in detected:
            ats = entry.get('ats')
            if ats not in ats_types:
                continue

            url = entry.get('ats_url') or entry.get('original_url')
            if not url:
                continue

            portals.append({
                'name': entry.get('company', 'Unknown'),
                'ats': ats,
                'url': url,
                'enabled': True,
                'source': 'awesome-career-pages',
            })

        return portals
