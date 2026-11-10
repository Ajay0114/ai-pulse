
# AI Pulse

Global AI News Intelligence Platform.

## Overview

AI Pulse discovers, collects, processes, categorizes and summarizes
AI-related news from global sources.

## Architecture

- Frontend: Next.js + TypeScript
- Backend: FastAPI + Python
- Database: PostgreSQL + pgvector
- Cache: Redis
- Background processing: Celery
- Deployment: Microsoft Azure

## Project Structure

- apps/frontend: Web application
- apps/backend: Backend API
- infrastructure: Docker and Azure configurations
- database: Database schemas and migrations
- docs: Technical documentation
- scripts: Development utilities


/mnt/d/Agents/ai-pulse/apps/backend$ source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

