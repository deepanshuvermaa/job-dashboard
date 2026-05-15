"""Run migration: add resume_data column to user_profiles"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv('../.env')
from sqlalchemy import create_engine, text

url = os.environ['DATABASE_URL'].replace('postgres://', 'postgresql://', 1)
engine = create_engine(url)

with engine.connect() as conn:
    conn.execute(text("ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS resume_data JSONB"))
    conn.commit()
    print("OK: resume_data column added")
    
    # Verify
    r = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='user_profiles'")).fetchall()
    print(f"Columns: {[row[0] for row in r]}")
