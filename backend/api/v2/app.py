"""
Unified FastAPI app — v2 auth/jobs.
Legacy routes only loaded when ENABLE_LEGACY=true (local dev only).
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
    try:
        from core.database import init_db
        init_db()
        print("[DB] Tables ready")
    except Exception as e:
        print(f"[DB] WARNING: init_db failed: {e}")
    yield


app = FastAPI(title="JobFlow", version="3.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Legacy routes (SQLite + Selenium) — only in local dev
if os.getenv("ENABLE_LEGACY", "true").lower() == "true":
    try:
        from api.v2.legacy import router as legacy_router
        app.include_router(legacy_router)
    except Exception as e:
        print(f"[WARN] Legacy router not loaded: {e}")

from api.v2.auth import router as auth_router
app.include_router(auth_router)

from api.v2.jobs import router as jobs_router
app.include_router(jobs_router)


@app.get("/health")
def health():
    return {"status": "ok", "version": "3.0.0"}


# ── Proxy all non-API requests to Next.js frontend on port 3000 ──
import httpx
from fastapi import Request
from fastapi.responses import Response

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def proxy_frontend(request: Request, path: str):
    frontend_url = f"http://localhost:3000/{path}"
    params = str(request.url.query)
    if params:
        frontend_url += f"?{params}"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.request(
                method=request.method,
                url=frontend_url,
                headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
                content=await request.body(),
                timeout=30,
            )
            return Response(content=resp.content, status_code=resp.status_code,
                            headers=dict(resp.headers))
        except Exception:
            return Response(content=b"Frontend not available", status_code=503)
