"""
Job Deduplication System
Prevents re-scraping and re-evaluating the same jobs across runs and sources.
Uses exact URL matching + normalized company|title comparison.
"""

import re
from typing import List, Dict, Tuple
from datetime import datetime
from database.db_helper import db


class JobDeduplicator:
    """Prevents re-scraping and re-evaluating jobs"""

    def __init__(self):
        self._ensure_table()

    def _ensure_table(self):
        """Create scan_history table if it doesn't exist"""
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_url TEXT NOT NULL,
                normalized_key TEXT NOT NULL,
                source TEXT NOT NULL,
                company TEXT,
                title TEXT,
                first_seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
                times_seen INTEGER DEFAULT 1,
                evaluated BOOLEAN DEFAULT 0,
                evaluation_grade TEXT,
                evaluation_score REAL,
                applied BOOLEAN DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_scan_history_url
            ON scan_history(job_url)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_scan_history_normalized
            ON scan_history(normalized_key)
        ''')
        conn.commit()
        conn.close()

    @staticmethod
    def normalize_key(company: str, title: str) -> str:
        """Create normalized comparison key from company + title"""
        company_norm = re.sub(r'[^a-z0-9]', '', (company or '').lower())
        title_norm = re.sub(r'[^a-z0-9]', '', (title or '').lower())
        return f"{company_norm}|{title_norm}"

    def filter_new_jobs(self, jobs: List[Dict]) -> Tuple[List[Dict], int]:
        """
        Filter out already-seen jobs, return (new_jobs, skipped_count).
        Also marks new jobs as seen in the database.
        """
        new_jobs = []
        skipped = 0

        for job in jobs:
            url = job.get('job_url', '')
            company = job.get('company', '')
            title = job.get('title', '')
            norm_key = self.normalize_key(company, title)
            source = job.get('source', 'unknown')

            if self._is_seen(url, norm_key):
                self._update_last_seen(url, norm_key)
                skipped += 1
            else:
                new_jobs.append(job)
                self._mark_seen(url, norm_key, source, company, title)

        print(f"[Dedup] {len(new_jobs)} new jobs, {skipped} duplicates skipped")
        return new_jobs, skipped

    def _is_seen(self, url: str, normalized_key: str) -> bool:
        """Check if job URL or normalized key already exists"""
        conn = db.get_connection()
        cursor = conn.cursor()

        # Check by exact URL
        if url:
            cursor.execute('SELECT id FROM scan_history WHERE job_url = ?', (url,))
            if cursor.fetchone():
                conn.close()
                return True

        # Check by normalized company+role key
        if normalized_key and '|' in normalized_key:
            cursor.execute('SELECT id FROM scan_history WHERE normalized_key = ?', (normalized_key,))
            if cursor.fetchone():
                conn.close()
                return True

        conn.close()
        return False

    def _mark_seen(self, url: str, normalized_key: str, source: str, company: str, title: str):
        """Add job to scan history"""
        conn = db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO scan_history (job_url, normalized_key, source, company, title)
                VALUES (?, ?, ?, ?, ?)
            ''', (url or '', normalized_key, source, company, title))
            conn.commit()
        except Exception as e:
            print(f"[Dedup] Error marking seen: {e}")
        finally:
            conn.close()

    def _update_last_seen(self, url: str, normalized_key: str):
        """Update last_seen timestamp and increment counter"""
        conn = db.get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()

        if url:
            cursor.execute('''
                UPDATE scan_history SET last_seen_at = ?, times_seen = times_seen + 1
                WHERE job_url = ?
            ''', (now, url))
        elif normalized_key:
            cursor.execute('''
                UPDATE scan_history SET last_seen_at = ?, times_seen = times_seen + 1
                WHERE normalized_key = ?
            ''', (now, normalized_key))

        conn.commit()
        conn.close()

    def mark_evaluated(self, job_url: str, grade: str, score: float):
        """Mark a job as evaluated with its grade and score"""
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE scan_history SET evaluated = 1, evaluation_grade = ?, evaluation_score = ?
            WHERE job_url = ?
        ''', (grade, score, job_url))
        conn.commit()
        conn.close()

    def mark_applied(self, job_url: str):
        """Mark a job as applied"""
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE scan_history SET applied = 1 WHERE job_url = ?
        ''', (job_url,))
        conn.commit()
        conn.close()

    def get_stats(self) -> Dict:
        """Get deduplication statistics"""
        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) as total FROM scan_history')
        total = cursor.fetchone()['total']

        cursor.execute('SELECT COUNT(*) as evaluated FROM scan_history WHERE evaluated = 1')
        evaluated = cursor.fetchone()['evaluated']

        cursor.execute('SELECT COUNT(*) as applied FROM scan_history WHERE applied = 1')
        applied = cursor.fetchone()['applied']

        cursor.execute('''
            SELECT COUNT(*) as today FROM scan_history
            WHERE date(first_seen_at) = date('now')
        ''')
        today = cursor.fetchone()['today']

        cursor.execute('''
            SELECT source, COUNT(*) as count FROM scan_history
            GROUP BY source ORDER BY count DESC
        ''')
        by_source = {row['source']: row['count'] for row in cursor.fetchall()}

        cursor.execute('''
            SELECT evaluation_grade, COUNT(*) as count FROM scan_history
            WHERE evaluated = 1 AND evaluation_grade IS NOT NULL
            GROUP BY evaluation_grade ORDER BY evaluation_grade
        ''')
        by_grade = {row['evaluation_grade']: row['count'] for row in cursor.fetchall()}

        conn.close()

        return {
            'total_seen': total,
            'evaluated': evaluated,
            'applied': applied,
            'new_today': today,
            'by_source': by_source,
            'by_grade': by_grade,
        }
