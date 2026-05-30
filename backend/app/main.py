"""
VendorSentinel — Main Application Entry Point
Wires up routers, middleware, lifecycle hooks, and optional periodic scanning.
"""
import sys
import asyncio
# ── Force stdout/stderr to use UTF-8 to prevent unicode/emoji encoding crashes on Windows consoles ──
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# ── Set ProactorEventLoopPolicy on Windows to support async subprocesses (required by Playwright) ──
if sys.platform == 'win32':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app import database as db
from app.routers import vendors, scans, dashboard, reports

# ── Logging ──────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("vendorsentinel")

# ── Optional scanner + scheduler imports ─────────────────────────
_scanner = None
try:
    from app.services import scanner as _scanner  # type: ignore[import-untyped]
    logger.info("Scanner module loaded successfully")
except ImportError:
    logger.warning(
        "Scanner module not available — scan endpoints will return 503 "
        "until dependencies are installed."
    )

_scheduler = None
try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore[import-untyped]
    _scheduler = AsyncIOScheduler()
    logger.info("APScheduler loaded — periodic scans enabled")
except ImportError:
    logger.info("APScheduler not installed — periodic scans disabled")


# ── Lifespan (startup / shutdown) ────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager.

    * **Startup**: initialise the database, and optionally schedule periodic
      full scans via APScheduler.
    * **Shutdown**: gracefully stop the scheduler (if running).
    """
    # ── startup ──
    logger.info("Starting VendorSentinel API …")
    await db.init_db()

    if _scheduler is not None and _scanner is not None:
        _scheduler.add_job(
            _scanner.run_full_scan,
            "interval",
            hours=settings.scan_interval_hours,
            id="periodic_full_scan",
            replace_existing=True,
        )
        _scheduler.start()
        logger.info(
            "Periodic scan scheduled every %d hour(s)",
            settings.scan_interval_hours,
        )

    yield  # ← app is serving requests

    # ── shutdown ──
    if _scheduler is not None and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down")
    logger.info("VendorSentinel API stopped")


# ── FastAPI app ──────────────────────────────────────────────────
app = FastAPI(
    title="VendorSentinel API",
    description=(
        "Real-time third-party vendor risk monitoring platform. "
        "Continuously scans the web for security incidents, data breaches, "
        "compliance issues, and financial instability signals across your "
        "vendor ecosystem."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,  # e.g. http://localhost:5173
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "*",  # permissive for development — tighten in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────
app.include_router(vendors.router)
app.include_router(scans.router)
app.include_router(dashboard.router)
app.include_router(reports.router)


# ── Root & Health ────────────────────────────────────────────────
@app.get("/", tags=["Root"], summary="Welcome")
async def root() -> dict:
    """Landing page — confirms the API is reachable."""
    return {
        "name": "VendorSentinel API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
    }


@app.get("/api/health", tags=["Health"], summary="Health check")
async def health_check() -> dict:
    """Lightweight liveness probe for load-balancers and orchestrators."""
    return {"status": "healthy"}
