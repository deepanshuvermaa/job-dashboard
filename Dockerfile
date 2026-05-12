# ── Stage 1: Build Next.js frontend ──────────────────────────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --legacy-peer-deps

COPY frontend/ ./
ENV NEXT_PUBLIC_API_URL=RUNTIME_API_URL
RUN npm run build

# ── Stage 2: Python backend + Next.js standalone ──────────────────────────────
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

# standalone output becomes the Next.js server
COPY --from=frontend-builder /frontend/.next/standalone ./frontend/
# static files must live at frontend/.next/static (inside standalone dir)
COPY --from=frontend-builder /frontend/.next/static ./frontend/.next/static
# public assets
COPY --from=frontend-builder /frontend/public ./frontend/public

COPY start.sh ./start.sh
RUN chmod +x ./start.sh

CMD ["./start.sh"]
