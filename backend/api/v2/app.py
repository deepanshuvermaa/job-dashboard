"""
Unified FastAPI app — v2 auth/jobs + frontend proxy.
"""
import sys
import os
from contextlib import asynccontextmanager
from pathlib import Path

backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
import httpx


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


# ── Serve Next.js static assets directly (bypass proxy) ──────────────────────
FRONTEND_DIR = Path("/app/frontend")
STATIC_DIR = FRONTEND_DIR / ".next" / "static"
PUBLIC_DIR = FRONTEND_DIR / "public"

if STATIC_DIR.exists():
    app.mount("/_next/static", StaticFiles(directory=str(STATIC_DIR)), name="next-static")

if PUBLIC_DIR.exists():
    app.mount("/public", StaticFiles(directory=str(PUBLIC_DIR)), name="public")


# ── Proxy all page requests to Next.js on port 3000 ──────────────────────────
async def _proxy(request: Request, path: str = ""):
    url = f"http://localhost:3000/{path}"
    if request.url.query:
        url += f"?{request.url.query}"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.request(
                method=request.method,
                url=url,
                headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
                content=await request.body(),
                timeout=30,
            )
            # Don't forward transfer-encoding — causes issues
            headers = {k: v for k, v in resp.headers.items()
                       if k.lower() not in ("transfer-encoding", "content-encoding")}
            return Response(content=resp.content, status_code=resp.status_code, headers=headers)
        except Exception as e:
            return Response(content=f"Frontend unavailable: {e}".encode(), status_code=503)


@app.api_route("/", methods=["GET", "HEAD"])
async def proxy_root(request: Request):
    return await _proxy(request, "")


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def proxy_frontend(request: Request, path: str):
    return await _proxy(request, path)
