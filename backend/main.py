"""
TAFA V1 — Technical + Fundamental Stock Screener API
FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers import watchlist, config, screener, tracking, health
from .services.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    print("[TAFA] Initializing database...")
    init_db()
    print("[TAFA] Starting background scheduler (every 30 min)...")
    start_scheduler()
    print("[TAFA] Ready!")

    yield

    # Shutdown
    print("[TAFA] Shutting down scheduler...")
    stop_scheduler()


app = FastAPI(
    title="Technical + Fundamental Stock Screener API",
    version="0.1.0",
    lifespan=lifespan,
)

import os

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

# CORS — allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(watchlist.router)
app.include_router(config.router)
app.include_router(screener.router)
app.include_router(tracking.router)
app.include_router(health.router)
