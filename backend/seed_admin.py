"""Seed admin user on startup if not exists."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import SessionLocal, engine
from models.base import Base
import models  # noqa
import bcrypt
from models.user import User, UserProfile

ADMIN_EMAIL = "deepanshuverma966@gmail.com"
ADMIN_PASSWORD = "Dv12062001@"
ADMIN_NAME = "Deepanshu Verma"

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == ADMIN_EMAIL).first():
            user = User(
                email=ADMIN_EMAIL,
                full_name=ADMIN_NAME,
                password_hash=bcrypt.hashpw(ADMIN_PASSWORD.encode(), bcrypt.gensalt()).decode(),
            )
            db.add(user)
            db.flush()
            db.add(UserProfile(user_id=user.id))
            db.commit()
            print(f"[SEED] Admin user created: {ADMIN_EMAIL}")
        else:
            print(f"[SEED] Admin user already exists: {ADMIN_EMAIL}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
