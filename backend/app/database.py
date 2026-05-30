"""
VendorSentinel Database Layer
SQLite with aiosqlite for async operations.
"""
import aiosqlite
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vendorsentinel.db")


async def get_db():
    """Get database connection."""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db():
    """Initialize database tables."""
    db = await get_db()
    try:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS vendors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                domain TEXT NOT NULL,
                website_url TEXT DEFAULT '',
                category TEXT DEFAULT 'general',
                data_sensitivity TEXT DEFAULT 'medium',
                description TEXT DEFAULT '',
                logo_url TEXT DEFAULT '',
                risk_score REAL DEFAULT 0.0,
                risk_level TEXT DEFAULT 'unknown',
                last_scanned TEXT DEFAULT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS scan_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor_id INTEGER NOT NULL,
                scan_id TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                severity TEXT DEFAULT 'info',
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                source_url TEXT DEFAULT '',
                raw_data TEXT DEFAULT '{}',
                found_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS risk_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor_id INTEGER NOT NULL,
                scan_id TEXT NOT NULL,
                score REAL NOT NULL,
                risk_level TEXT NOT NULL,
                ai_reasoning TEXT DEFAULT '',
                recommended_actions TEXT DEFAULT '',
                signal_summary TEXT DEFAULT '{}',
                scored_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor_id INTEGER NOT NULL,
                scan_id TEXT DEFAULT '',
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT DEFAULT '',
                is_read INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id TEXT NOT NULL UNIQUE,
                status TEXT DEFAULT 'running',
                vendors_scanned INTEGER DEFAULT 0,
                total_signals_found INTEGER DEFAULT 0,
                started_at TEXT DEFAULT (datetime('now')),
                completed_at TEXT DEFAULT NULL,
                error_log TEXT DEFAULT ''
            );

            CREATE INDEX IF NOT EXISTS idx_scan_results_vendor ON scan_results(vendor_id);
            CREATE INDEX IF NOT EXISTS idx_scan_results_scan ON scan_results(scan_id);
            CREATE INDEX IF NOT EXISTS idx_risk_scores_vendor ON risk_scores(vendor_id);
            CREATE INDEX IF NOT EXISTS idx_alerts_vendor ON alerts(vendor_id);
        """)
        await db.commit()
        print("[OK] Database tables initialized successfully")

        # ── Auto-seed demo data if the vendors table is empty ──
        cursor = await db.execute("SELECT COUNT(*) as count FROM vendors")
        row = await cursor.fetchone()
        if row["count"] == 0:
            print("[INFO] Empty database detected — seeding demo data...")
            try:
                from app.seed import seed_data
                await db.close()       # seed.py uses its own sync connection
                await seed_data()
            except Exception as exc:
                print(f"[WARN] Seeding failed: {exc}")
        else:
            print(f"[OK] Database already has {row['count']} vendors")
            await db.close()
            return

    finally:
        try:
            await db.close()
        except Exception:
            pass  # already closed


# ═══════════════════════════════════════════════════════════════
# Vendor CRUD
# ═══════════════════════════════════════════════════════════════

async def create_vendor(name: str, domain: str, website_url: str = "",
                        category: str = "general", data_sensitivity: str = "medium",
                        description: str = "") -> dict:
    db = await get_db()
    try:
        cursor = await db.execute(
            """INSERT INTO vendors (name, domain, website_url, category, data_sensitivity, description)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (name, domain, website_url, category, data_sensitivity, description)
        )
        await db.commit()
        vendor_id = cursor.lastrowid
        return await get_vendor(vendor_id)
    finally:
        await db.close()


async def get_vendor(vendor_id: int) -> dict | None:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM vendors WHERE id = ?", (vendor_id,))
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        await db.close()


async def get_all_vendors() -> list[dict]:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM vendors ORDER BY risk_score DESC")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


async def update_vendor(vendor_id: int, **kwargs) -> dict | None:
    db = await get_db()
    try:
        set_parts = []
        values = []
        for key, value in kwargs.items():
            if key in ("name", "domain", "website_url", "category", "data_sensitivity",
                       "description", "risk_score", "risk_level", "last_scanned", "logo_url"):
                set_parts.append(f"{key} = ?")
                values.append(value)
        if not set_parts:
            return await get_vendor(vendor_id)
        set_parts.append("updated_at = datetime('now')")
        values.append(vendor_id)
        await db.execute(
            f"UPDATE vendors SET {', '.join(set_parts)} WHERE id = ?",
            values
        )
        await db.commit()
        return await get_vendor(vendor_id)
    finally:
        await db.close()


async def delete_vendor(vendor_id: int) -> bool:
    db = await get_db()
    try:
        cursor = await db.execute("DELETE FROM vendors WHERE id = ?", (vendor_id,))
        await db.commit()
        return cursor.rowcount > 0
    finally:
        await db.close()


# ═══════════════════════════════════════════════════════════════
# Scan Results
# ═══════════════════════════════════════════════════════════════

async def save_scan_result(vendor_id: int, scan_id: str, signal_type: str,
                           severity: str, title: str, description: str = "",
                           source_url: str = "", raw_data: dict = None) -> int:
    db = await get_db()
    try:
        cursor = await db.execute(
            """INSERT INTO scan_results (vendor_id, scan_id, signal_type, severity, title, description, source_url, raw_data)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (vendor_id, scan_id, signal_type, severity, title, description, source_url,
             json.dumps(raw_data or {}))
        )
        await db.commit()
        return cursor.lastrowid
    finally:
        await db.close()


async def get_scan_results(vendor_id: int, scan_id: str = None) -> list[dict]:
    db = await get_db()
    try:
        if scan_id:
            cursor = await db.execute(
                "SELECT * FROM scan_results WHERE vendor_id = ? AND scan_id = ? ORDER BY found_at DESC",
                (vendor_id, scan_id)
            )
        else:
            cursor = await db.execute(
                "SELECT * FROM scan_results WHERE vendor_id = ? ORDER BY found_at DESC LIMIT 100",
                (vendor_id,)
            )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


async def get_latest_scan_results_all() -> list[dict]:
    """Get the latest scan results for all vendors."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT sr.*, v.name as vendor_name FROM scan_results sr
               JOIN vendors v ON sr.vendor_id = v.id
               ORDER BY sr.found_at DESC LIMIT 200"""
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


# ═══════════════════════════════════════════════════════════════
# Risk Scores
# ═══════════════════════════════════════════════════════════════

async def save_risk_score(vendor_id: int, scan_id: str, score: float,
                          risk_level: str, ai_reasoning: str = "",
                          recommended_actions: str = "", signal_summary: dict = None) -> int:
    db = await get_db()
    try:
        cursor = await db.execute(
            """INSERT INTO risk_scores (vendor_id, scan_id, score, risk_level, ai_reasoning, recommended_actions, signal_summary)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (vendor_id, scan_id, score, risk_level, ai_reasoning, recommended_actions,
             json.dumps(signal_summary or {}))
        )
        # Also update vendor's current risk score
        await db.execute(
            "UPDATE vendors SET risk_score = ?, risk_level = ?, last_scanned = datetime('now') WHERE id = ?",
            (score, risk_level, vendor_id)
        )
        await db.commit()
        return cursor.lastrowid
    finally:
        await db.close()


async def get_risk_history(vendor_id: int, limit: int = 30) -> list[dict]:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM risk_scores WHERE vendor_id = ? ORDER BY scored_at DESC LIMIT ?",
            (vendor_id, limit)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


# ═══════════════════════════════════════════════════════════════
# Alerts
# ═══════════════════════════════════════════════════════════════

async def create_alert(vendor_id: int, scan_id: str, alert_type: str,
                       severity: str, title: str, message: str = "") -> int:
    db = await get_db()
    try:
        cursor = await db.execute(
            """INSERT INTO alerts (vendor_id, scan_id, alert_type, severity, title, message)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (vendor_id, scan_id, alert_type, severity, title, message)
        )
        await db.commit()
        return cursor.lastrowid
    finally:
        await db.close()


async def get_recent_alerts(limit: int = 50) -> list[dict]:
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT a.*, v.name as vendor_name FROM alerts a
               JOIN vendors v ON a.vendor_id = v.id
               ORDER BY a.created_at DESC LIMIT ?""",
            (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


async def mark_alert_read(alert_id: int):
    db = await get_db()
    try:
        await db.execute("UPDATE alerts SET is_read = 1 WHERE id = ?", (alert_id,))
        await db.commit()
    finally:
        await db.close()


# ═══════════════════════════════════════════════════════════════
# Scan History
# ═══════════════════════════════════════════════════════════════

async def create_scan_record(scan_id: str) -> None:
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO scan_history (scan_id) VALUES (?)", (scan_id,)
        )
        await db.commit()
    finally:
        await db.close()


async def update_scan_record(scan_id: str, **kwargs) -> None:
    db = await get_db()
    try:
        set_parts = []
        values = []
        for key, value in kwargs.items():
            if key in ("status", "vendors_scanned", "total_signals_found", "completed_at", "error_log"):
                set_parts.append(f"{key} = ?")
                values.append(value)
        if set_parts:
            values.append(scan_id)
            await db.execute(
                f"UPDATE scan_history SET {', '.join(set_parts)} WHERE scan_id = ?",
                values
            )
            await db.commit()
    finally:
        await db.close()


async def get_scan_history(limit: int = 20) -> list[dict]:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM scan_history ORDER BY started_at DESC LIMIT ?", (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


# ═══════════════════════════════════════════════════════════════
# Dashboard Stats
# ═══════════════════════════════════════════════════════════════

async def get_dashboard_stats() -> dict:
    db = await get_db()
    try:
        # Total vendors
        cursor = await db.execute("SELECT COUNT(*) as count FROM vendors")
        total_vendors = (await cursor.fetchone())["count"]

        # Risk distribution
        cursor = await db.execute("""
            SELECT risk_level, COUNT(*) as count FROM vendors
            WHERE risk_level != 'unknown'
            GROUP BY risk_level
        """)
        risk_dist = {row["risk_level"]: row["count"] for row in await cursor.fetchall()}

        # Average risk score
        cursor = await db.execute("SELECT AVG(risk_score) as avg FROM vendors WHERE risk_score > 0")
        row = await cursor.fetchone()
        avg_score = round(row["avg"], 1) if row["avg"] else 0.0

        # Critical vendors
        cursor = await db.execute("SELECT COUNT(*) as count FROM vendors WHERE risk_score >= 7.0")
        critical_count = (await cursor.fetchone())["count"]

        # Total signals (last scan)
        cursor = await db.execute(
            "SELECT COUNT(*) as count FROM scan_results WHERE scan_id = (SELECT scan_id FROM scan_history ORDER BY started_at DESC LIMIT 1)"
        )
        total_signals = (await cursor.fetchone())["count"]

        # Unread alerts
        cursor = await db.execute("SELECT COUNT(*) as count FROM alerts WHERE is_read = 0")
        unread_alerts = (await cursor.fetchone())["count"]

        return {
            "total_vendors": total_vendors,
            "risk_distribution": risk_dist,
            "average_risk_score": avg_score,
            "critical_vendors": critical_count,
            "total_signals": total_signals,
            "unread_alerts": unread_alerts
        }
    finally:
        await db.close()
