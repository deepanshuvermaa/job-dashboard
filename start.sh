#!/bin/sh
# Next.js standalone server on port 3000
cd /app/frontend
HOSTNAME=0.0.0.0 PORT=3000 node server.js &

# FastAPI on Railway's $PORT
cd /app/backend
python -m uvicorn api.v2.app:app --host 0.0.0.0 --port ${PORT:-8000}
