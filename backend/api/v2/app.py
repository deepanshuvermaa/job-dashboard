"""
Unified FastAPI app — v2 auth/jobs + legacy wrappers.
"""
import sys
import os
from contextlib import asynccontextmanager

backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    from core.database import init_db
    init_db()
    yield


app = FastAPI(title="JobFlow", version="3.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── IMPORTANT: Legacy routes FIRST (they have specific paths like /api/jobs/search) ──
from api.v2.legacy import router as legacy_router
app.include_router(legacy_router)

# ── Auth routes ──
from api.v2.auth import router as auth_router
app.include_router(auth_router)

# ── V2 jobs routes LAST (contains /api/jobs/{job_id} wildcard) ──
from api.v2.jobs import router as jobs_router
app.include_router(jobs_router)


@app.get("/health")
def health():
    return {"status": "ok", "version": "3.0.0"}
