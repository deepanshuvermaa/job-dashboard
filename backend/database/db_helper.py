"""
Database Helper for SQLite
Simple in-memory database for MVP
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

class DatabaseHelper:
    def __init__(self, db_path="data/linkedin_automation.db"):
        self.db_path = db_path
        Path("data").mkdir(exist_ok=True)
        self.init_database()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Content sources (GitHub repos)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_name TEXT NOT NULL,
                repo_url TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                last_synced TEXT,
                post_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Generated posts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER,
                content TEXT NOT NULL,
                hooks TEXT,
                hashtags TEXT,
                pillar TEXT,
                status TEXT DEFAULT 'pending',
                published_at TEXT,
                linkedin_url TEXT,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                views INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES content_sources(id)
            )
        ''')

        # Job applications (Enhanced with comprehensive tracking)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT NOT NULL,
                job_url TEXT NOT NULL,
                status TEXT DEFAULT 'applied',
                applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
                response_date TEXT,

                -- Enhanced fields from GodsScion approach
                hr_name TEXT,
                hr_profile_url TEXT,
                work_style TEXT,
                experience_required TEXT,
                salary_range TEXT,
                date_listed TEXT,
                date_applied TEXT,
                is_reposted BOOLEAN DEFAULT 0,

                -- Skills and requirements
                skills_required TEXT,
                skills_matched TEXT,

                -- Application details
                application_method TEXT DEFAULT 'Easy Apply',
                resume_used TEXT,
                questions_asked TEXT,
                answers_provided TEXT,

                -- Tracking
                application_success BOOLEAN DEFAULT 1,
                error_message TEXT,
                screenshot_path TEXT,

                -- Follow-up
                followed_company BOOLEAN DEFAULT 0,
                connection_requested BOOLEAN DEFAULT 0,
                notes TEXT
            )
        ''')

        # Settings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    # Content Sources Methods
    def add_content_source(self, repo_name, repo_url):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO content_sources (repo_name, repo_url) VALUES (?, ?)',
            (repo_name, repo_url)
        )
        conn.commit()
        source_id = cursor.lastrowid
        conn.close()
        return source_id

    def get_content_sources(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM content_sources ORDER BY created_at DESC')
        sources = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return sources

    def update_content_source(self, source_id, **kwargs):
        conn = self.get_connection()
        cursor = conn.cursor()

        update_fields = []
        values = []
        for key, value in kwargs.items():
            update_fields.append(f"{key} = ?")
            values.append(value)

        values.append(source_id)
        query = f"UPDATE content_sources SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        conn.close()

    def delete_content_source(self, source_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM content_sources WHERE id = ?', (source_id,))
        conn.commit()
        conn.close()

    # Posts Methods
    def add_post(self, content, hooks, hashtags, pillar, source_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO posts (source_id, content, hooks, hashtags, pillar)
            VALUES (?, ?, ?, ?, ?)
        ''', (source_id, content, json.dumps(hooks), json.dumps(hashtags), pillar))
        conn.commit()
        post_id = cursor.lastrowid
        conn.close()
        return post_id

    def get_posts(self, status=None):
        conn = self.get_connection()
        cursor = conn.cursor()

        if status:
            cursor.execute('SELECT * FROM posts WHERE status = ? ORDER BY created_at DESC', (status,))
        else:
            cursor.execute('SELECT * FROM posts ORDER BY created_at DESC')

        posts = []
        for row in cursor.fetchall():
            post = dict(row)
            post['hooks'] = json.loads(post['hooks']) if post['hooks'] else []
            post['hashtags'] = json.loads(post['hashtags']) if post['hashtags'] else []
            posts.append(post)

        conn.close()
        return posts

    def update_post(self, post_id, **kwargs):
        conn = self.get_connection()
        cursor = conn.cursor()

        update_fields = []
        values = []
        for key, value in kwargs.items():
            update_fields.append(f"{key} = ?")
            values.append(value)

        values.append(post_id)
        query = f"UPDATE posts SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        conn.close()

    def get_post_by_id(self, post_id):
        """Get a single post by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            post = dict(row)
            post['hooks'] = json.loads(post['hooks']) if post['hooks'] else []
            post['hashtags'] = json.loads(post['hashtags']) if post['hashtags'] else []
            return post
        return None

    def update_post_status(self, post_id, status):
        """Update post status (pending, published, scheduled)"""
        self.update_post(post_id, status=status)

    # Applications Methods
    def add_application(self, job_title, company, location, job_url, **kwargs):
        """
        Add job application with comprehensive tracking

        Required args: job_title, company, location, job_url

        Optional kwargs: hr_name, hr_profile_url, work_style, experience_required,
                        salary_range, date_listed, date_applied, is_reposted,
                        skills_required, skills_matched, application_method,
                        resume_used, questions_asked, answers_provided,
                        application_success, error_message, screenshot_path,
                        followed_company, connection_requested, notes
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # Base fields
        fields = ['job_title', 'company', 'location', 'job_url']
        values = [job_title, company, location, job_url]

        # Add optional fields if provided
        optional_fields = [
            'hr_name', 'hr_profile_url', 'work_style', 'experience_required',
            'salary_range', 'date_listed', 'date_applied', 'is_reposted',
            'skills_required', 'skills_matched', 'application_method',
            'resume_used', 'questions_asked', 'answers_provided',
            'application_success', 'error_message', 'screenshot_path',
            'followed_company', 'connection_requested', 'notes', 'status'
        ]

        for field in optional_fields:
            if field in kwargs:
                fields.append(field)
                # Convert lists/dicts to JSON strings
                value = kwargs[field]
                if isinstance(value, (list, dict)):
                    value = json.dumps(value)
                values.append(value)

        placeholders = ', '.join(['?' for _ in values])
        field_names = ', '.join(fields)

        query = f'INSERT INTO applications ({field_names}) VALUES ({placeholders})'
        cursor.execute(query, values)

        conn.commit()
        app_id = cursor.lastrowid
        conn.close()
        return app_id

    def get_applications(self, status=None):
        conn = self.get_connection()
        cursor = conn.cursor()

        if status:
            cursor.execute('SELECT * FROM applications WHERE status = ? ORDER BY applied_at DESC', (status,))
        else:
            cursor.execute('SELECT * FROM applications ORDER BY applied_at DESC')

        applications = []
        for row in cursor.fetchall():
            app = dict(row)
            # Deserialize JSON fields
            json_fields = ['questions_asked', 'answers_provided', 'skills_required', 'skills_matched']
            for field in json_fields:
                if app.get(field):
                    try:
                        app[field] = json.loads(app[field])
                    except:
                        pass
            applications.append(app)

        conn.close()
        return applications

    def get_dashboard_stats(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Count posts this week
        cursor.execute('''
            SELECT COUNT(*) as count FROM posts
            WHERE status = 'published'
            AND datetime(published_at) >= datetime('now', '-7 days')
        ''')
        posts_this_week = cursor.fetchone()['count']

        # Count applications this week
        cursor.execute('''
            SELECT COUNT(*) as count FROM applications
            WHERE datetime(applied_at) >= datetime('now', '-7 days')
        ''')
        applications_this_week = cursor.fetchone()['count']

        # Average engagement
        cursor.execute('''
            SELECT AVG(likes + comments + shares) as avg_engagement
            FROM posts
            WHERE status = 'published'
        ''')
        avg_engagement = cursor.fetchone()['avg_engagement'] or 0

        # Interviews scheduled (mock for now)
        interviews_scheduled = 0

        conn.close()

        return {
            'posts_this_week': posts_this_week,
            'applications_this_week': applications_this_week,
            'avg_engagement': round(avg_engagement, 1),
            'interviews_scheduled': interviews_scheduled
        }

    # Settings Methods
    def set_setting(self, key, value):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, ?)
        ''', (key, value, datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def get_setting(self, key, default=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        return row['value'] if row else default

    def get_all_settings(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT key, value FROM settings')
        settings = {row['key']: row['value'] for row in cursor.fetchall()}
        conn.close()
        return settings


# Global database instance
db = DatabaseHelper()
