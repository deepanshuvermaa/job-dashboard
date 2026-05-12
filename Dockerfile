# ── Stage 1: Build Next.js frontend ──────────────────────────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --legacy-peer-deps

COPY frontend/ ./
ENV NEXT_PUBLIC_API_URL=RUNTIME_API_URL
RUN npm run build

# ── Stage 2: Python backend + serve frontend ──────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Install Node.js (to run Next.js standalone server)
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Python deps
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Backend code
COPY backend/ ./backend/

# Frontend standalone build
COPY --from=frontend-builder /frontend/.next/standalone ./frontend/
COPY --from=frontend-builder /frontend/.next/static ./frontend/.next/static
COPY --from=frontend-builder /frontend/public ./frontend/public 2>/dev/null || true

# Start script — runs backend on 8000, frontend on 3000, nginx-style proxy via caddy
# Simpler: run backend on $PORT, frontend on 3000, use backend as the public entry
COPY start.sh ./start.sh
RUN chmod +x ./start.sh

CMD ["./start.sh"]
