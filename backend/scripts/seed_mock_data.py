"""Seed 25 realistic mock jobs + a demo user for development."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine, SessionLocal, init_db
from models.user import User, UserProfile
from models.job import Job, JobEvaluation
import bcrypt, re, random
from datetime import datetime, timedelta, timezone

DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "demo1234"

MOCK_JOBS = [
    {"title": "Senior Backend Engineer", "company": "Stripe", "location": "San Francisco, CA", "work_mode": "hybrid", "source": "greenhouse", "category": "backend", "salary_min": 180000, "salary_max": 220000, "skills": ["Python", "Go", "PostgreSQL", "AWS", "Kubernetes"], "desc": "Build and scale payment infrastructure serving millions of businesses worldwide. You will design distributed systems that process billions of dollars in transactions.", "grade": "A", "score": 94},
    {"title": "Full Stack Developer", "company": "Vercel", "location": "Remote", "work_mode": "remote", "source": "lever", "category": "fullstack", "salary_min": 150000, "salary_max": 190000, "skills": ["React", "Next.js", "TypeScript", "Node.js", "Vercel"], "desc": "Join the team building the frontend cloud. You will work on the platform that powers millions of websites and help shape the future of web development.", "grade": "A", "score": 91},
    {"title": "Software Engineer, ML Platform", "company": "Anthropic", "location": "San Francisco, CA", "work_mode": "onsite", "source": "ashby", "category": "ai_ml", "salary_min": 200000, "salary_max": 280000, "skills": ["Python", "PyTorch", "CUDA", "Distributed Systems", "Kubernetes"], "desc": "Build the infrastructure that trains and serves our AI models. Work on large-scale distributed training systems and ML pipelines.", "grade": "A", "score": 96},
    {"title": "Frontend Engineer", "company": "Linear", "location": "Remote", "work_mode": "remote", "source": "ashby", "category": "frontend", "salary_min": 140000, "salary_max": 175000, "skills": ["React", "TypeScript", "CSS", "WebGL", "Performance"], "desc": "Create delightful user experiences in the fastest project management tool. Focus on performance, animations, and pixel-perfect UI.", "grade": "B", "score": 82},
    {"title": "Backend Engineer", "company": "Supabase", "location": "Remote", "work_mode": "remote", "source": "ashby", "category": "backend", "salary_min": 150000, "salary_max": 200000, "skills": ["PostgreSQL", "Elixir", "TypeScript", "Docker", "AWS"], "desc": "Build the open-source Firebase alternative. Work on real-time subscriptions, authentication, and database tooling at scale.", "grade": "A", "score": 89},
    {"title": "DevOps Engineer", "company": "Datadog", "location": "New York, NY", "work_mode": "hybrid", "source": "greenhouse", "category": "devops", "salary_min": 160000, "salary_max": 210000, "skills": ["Terraform", "Kubernetes", "AWS", "Python", "Go"], "desc": "Scale the monitoring platform used by thousands of engineering teams. Design infrastructure that handles petabytes of observability data daily.", "grade": "B", "score": 78},
    {"title": "Product Designer", "company": "Figma", "location": "San Francisco, CA", "work_mode": "hybrid", "source": "greenhouse", "category": "design", "salary_min": 160000, "salary_max": 200000, "skills": ["Figma", "Design Systems", "Prototyping", "User Research", "CSS"], "desc": "Design the design tool. Shape the future of collaborative design by creating features used by millions of designers worldwide.", "grade": "B", "score": 75},
    {"title": "Senior Software Engineer", "company": "Cloudflare", "location": "Austin, TX", "work_mode": "hybrid", "source": "greenhouse", "category": "backend", "salary_min": 170000, "salary_max": 220000, "skills": ["Rust", "Go", "C++", "Linux", "Networking"], "desc": "Build the network that powers 20% of the internet. Work on edge computing, CDN, and security products at massive global scale.", "grade": "B", "score": 84},
    {"title": "Data Engineer", "company": "dbt Labs", "location": "Remote", "work_mode": "remote", "source": "lever", "category": "data", "salary_min": 145000, "salary_max": 185000, "skills": ["Python", "SQL", "dbt", "Snowflake", "Airflow"], "desc": "Transform how analytics engineering works. Build the tools that enable data teams to apply software engineering best practices to analytics.", "grade": "B", "score": 80},
    {"title": "iOS Engineer", "company": "Loom", "location": "Remote", "work_mode": "remote", "source": "lever", "category": "frontend", "salary_min": 140000, "salary_max": 180000, "skills": ["Swift", "UIKit", "SwiftUI", "AVFoundation", "Core Data"], "desc": "Build the mobile video messaging experience used by millions of professionals. Focus on camera, recording, and real-time video features.", "grade": "C", "score": 65},
    {"title": "Staff Engineer, Infrastructure", "company": "Notion", "location": "San Francisco, CA", "work_mode": "hybrid", "source": "greenhouse", "category": "backend", "salary_min": 220000, "salary_max": 300000, "skills": ["Kotlin", "TypeScript", "PostgreSQL", "Redis", "AWS"], "desc": "Lead infrastructure initiatives for the productivity workspace used by millions. Design systems for real-time collaboration and data consistency.", "grade": "A", "score": 92},
    {"title": "Security Engineer", "company": "1Password", "location": "Remote", "work_mode": "remote", "source": "lever", "category": "devops", "salary_min": 150000, "salary_max": 195000, "skills": ["Go", "Rust", "Cryptography", "Kubernetes", "Threat Modeling"], "desc": "Protect the secrets of millions of users and businesses. Build security infrastructure and conduct threat analysis for the leading password manager.", "grade": "B", "score": 76},
    {"title": "Machine Learning Engineer", "company": "Hugging Face", "location": "Remote", "work_mode": "remote", "source": "lever", "category": "ai_ml", "salary_min": 160000, "salary_max": 230000, "skills": ["Python", "PyTorch", "Transformers", "NLP", "Docker"], "desc": "Democratize AI by building open-source machine learning tools. Work on model training, optimization, and the Transformers library used by thousands.", "grade": "A", "score": 88},
    {"title": "Full Stack Engineer", "company": "Cal.com", "location": "Remote", "work_mode": "remote", "source": "ashby", "category": "fullstack", "salary_min": 120000, "salary_max": 165000, "skills": ["Next.js", "TypeScript", "Prisma", "tRPC", "Tailwind"], "desc": "Build the open-source scheduling infrastructure. Create features for the calendar platform that competes with Calendly.", "grade": "C", "score": 68},
    {"title": "Senior Frontend Engineer", "company": "Miro", "location": "Amsterdam, NL", "work_mode": "hybrid", "source": "greenhouse", "category": "frontend", "salary_min": 90000, "salary_max": 130000, "skills": ["React", "TypeScript", "Canvas", "WebSocket", "Performance"], "desc": "Build the collaborative whiteboard used by 60M+ users. Focus on real-time canvas rendering, collaboration features, and performance optimization.", "grade": "C", "score": 62},
    {"title": "Platform Engineer", "company": "Railway", "location": "Remote", "work_mode": "remote", "source": "ashby", "category": "devops", "salary_min": 140000, "salary_max": 180000, "skills": ["Go", "Kubernetes", "Nix", "Rust", "gRPC"], "desc": "Build the modern cloud platform for developers. Work on deployment infrastructure, build systems, and developer experience.", "grade": "B", "score": 81},
    {"title": "Backend Engineer, Payments", "company": "Mercury", "location": "San Francisco, CA", "work_mode": "hybrid", "source": "lever", "category": "backend", "salary_min": 170000, "salary_max": 215000, "skills": ["Haskell", "PostgreSQL", "AWS", "Plaid API", "Banking"], "desc": "Build banking products for startups. Work on payment processing, ledger systems, and financial infrastructure.", "grade": "B", "score": 77},
    {"title": "Senior Software Engineer", "company": "Neon", "location": "Remote", "work_mode": "remote", "source": "ashby", "category": "backend", "salary_min": 160000, "salary_max": 210000, "skills": ["Rust", "PostgreSQL", "C", "Storage Systems", "Linux"], "desc": "Build serverless Postgres. Work on storage engines, compute separation, and the database platform powering modern applications.", "grade": "A", "score": 87},
    {"title": "Product Manager", "company": "Replit", "location": "Remote", "work_mode": "remote", "source": "ashby", "category": "product", "salary_min": 150000, "salary_max": 200000, "skills": ["AI/ML", "Developer Tools", "Product Strategy", "Data Analysis", "User Research"], "desc": "Shape the future of coding with AI. Define product strategy for the AI-powered IDE used by millions of developers and learners.", "grade": "C", "score": 60},
    {"title": "Senior SRE", "company": "PlanetScale", "location": "Remote", "work_mode": "remote", "source": "lever", "category": "devops", "salary_min": 170000, "salary_max": 220000, "skills": ["MySQL", "Vitess", "Go", "Kubernetes", "Terraform"], "desc": "Keep the serverless MySQL platform running at scale. Build reliability tooling and incident response systems for database infrastructure.", "grade": "B", "score": 79},
    {"title": "Full Stack Engineer", "company": "Zapier", "location": "Remote", "work_mode": "remote", "source": "greenhouse", "category": "fullstack", "salary_min": 140000, "salary_max": 180000, "skills": ["Python", "React", "Django", "PostgreSQL", "Redis"], "desc": "Build automation workflows that connect 6000+ apps. Work on the integration platform that saves millions of hours of manual work.", "grade": "B", "score": 74},
    {"title": "AI Engineer", "company": "ElevenLabs", "location": "Remote", "work_mode": "remote", "source": "ashby", "category": "ai_ml", "salary_min": 170000, "salary_max": 240000, "skills": ["Python", "PyTorch", "Audio Processing", "TTS", "Transformers"], "desc": "Build the most realistic AI voice technology. Work on text-to-speech models, voice cloning, and real-time audio generation.", "grade": "A", "score": 90},
    {"title": "Software Engineer, API", "company": "Plaid", "location": "San Francisco, CA", "work_mode": "hybrid", "source": "greenhouse", "category": "backend", "salary_min": 160000, "salary_max": 210000, "skills": ["Go", "Python", "PostgreSQL", "gRPC", "AWS"], "desc": "Build the financial data infrastructure that connects thousands of fintech apps to bank accounts. Design APIs at massive scale.", "grade": "B", "score": 83},
    {"title": "Frontend Engineer", "company": "Framer", "location": "Amsterdam, NL", "work_mode": "remote", "source": "lever", "category": "frontend", "salary_min": 85000, "salary_max": 125000, "skills": ["React", "TypeScript", "Canvas", "WASM", "Framer Motion"], "desc": "Build the no-code website builder that designers love. Work on the visual editor, component system, and publishing pipeline.", "grade": "C", "score": 63},
    {"title": "Senior Backend Engineer", "company": "Fly.io", "location": "Remote", "work_mode": "remote", "source": "lever", "category": "backend", "salary_min": 160000, "salary_max": 200000, "skills": ["Go", "Rust", "Firecracker", "Networking", "Linux"], "desc": "Build the edge compute platform. Work on VM orchestration, global networking, and the infrastructure that runs apps close to users.", "grade": "B", "score": 85},
]


def normalize_key(company: str, title: str) -> str:
    c = re.sub(r'[^a-z0-9]', '', company.lower())
    t = re.sub(r'[^a-z0-9]', '', title.lower())
    return f"{c}|{t}"


def seed():
    init_db()
    db = SessionLocal()
    try:
        # Check if demo user exists
        user = db.query(User).filter(User.email == DEMO_EMAIL).first()
        if user:
            print(f"Demo user already exists: {user.id}")
        else:
            user = User(
                email=DEMO_EMAIL,
                full_name="Demo User",
                password_hash=bcrypt.hashpw(DEMO_PASSWORD.encode(), bcrypt.gensalt()).decode(),
            )
            db.add(user)
            db.flush()
            profile = UserProfile(
                user_id=user.id,
                headline="Full Stack Software Engineer",
                summary="Passionate about building scalable web applications.",
                location="San Francisco, CA",
                skills=["Python", "TypeScript", "React", "Next.js", "Node.js", "PostgreSQL", "AWS", "Docker", "Kubernetes", "Go"],
                preferred_work_mode="remote",
            )
            db.add(profile)
            db.flush()
            print(f"Created demo user: {user.email} / {DEMO_PASSWORD}")

        # Check if jobs already seeded
        existing = db.query(Job).filter(Job.user_id == user.id).count()
        if existing >= 20:
            print(f"Already have {existing} jobs, skipping seed.")
            db.commit()
            return

        now = datetime.now(timezone.utc)
        for i, m in enumerate(MOCK_JOBS):
            domain = m["company"].lower().replace(" ", "").replace(".", "") + ".com"
            logo_url = f"https://logo.clearbit.com/{domain}"

            job = Job(
                user_id=user.id,
                title=m["title"],
                company=m["company"],
                company_logo_url=logo_url,
                location=m["location"],
                job_url=f"https://boards.{m['source']}.io/{domain}/jobs/{1000 + i}",
                normalized_key=normalize_key(m["company"], m["title"]),
                description_full=m["desc"],
                description_snippet=m["desc"][:300],
                salary_min=m.get("salary_min"),
                salary_max=m.get("salary_max"),
                salary_currency="USD",
                salary_period="yearly",
                employment_type="full-time",
                experience_level=random.choice(["mid", "senior"]),
                work_mode=m.get("work_mode", "remote"),
                skills_required=m.get("skills", []),
                skills_matched=m.get("skills", [])[:3],
                posted_date=now - timedelta(days=random.randint(1, 14)),
                source=m["source"],
                category=m.get("category", "other"),
                status="active",
                is_easy_apply=random.choice([True, False]),
                first_seen_at=now - timedelta(days=random.randint(1, 7)),
                last_seen_at=now - timedelta(hours=random.randint(1, 48)),
                times_seen=random.randint(1, 5),
            )
            db.add(job)
            db.flush()

            ev = JobEvaluation(
                job_id=job.id,
                user_id=user.id,
                overall_score=m["score"],
                grade=m["grade"],
                gate_pass=m["grade"] in ("A", "B", "C"),
                role_match=min(100, m["score"] + random.randint(-10, 10)),
                skills_alignment=min(100, m["score"] + random.randint(-15, 5)),
                seniority_fit=min(100, m["score"] + random.randint(-8, 12)),
                compensation=min(100, m["score"] + random.randint(-5, 10)),
                interview_likelihood=min(100, m["score"] + random.randint(-12, 8)),
                growth_potential=min(100, m["score"] + random.randint(-10, 15)),
                company_reputation=min(100, m["score"] + random.randint(-5, 10)),
                location_fit=min(100, m["score"] + random.randint(-20, 5)),
                tech_stack_match=min(100, m["score"] + random.randint(-8, 12)),
                culture_signals=min(100, m["score"] + random.randint(-15, 10)),
                reasoning=f"Strong match for {m['category']} role at {m['company']}.",
                evaluated_at=now,
            )
            db.add(ev)

        db.commit()
        print(f"Seeded {len(MOCK_JOBS)} mock jobs with evaluations.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
