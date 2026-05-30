import asyncio
import sqlite3
import os
import json
import uuid
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vendorsentinel.db")

async def seed_data():
    print(f"[SEED] Seeding database at {DB_PATH}...")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check if database has vendors already
    try:
        cursor.execute("SELECT COUNT(*) as count FROM vendors")
        count = cursor.fetchone()["count"]
        if count > 0:
            print("[WARN] Database already contains vendor records. Skipping seed.")
            conn.close()
            return
    except sqlite3.OperationalError:
        print("[WARN] Tables do not exist. Please initialize database first.")
        conn.close()
        return

    # Generate dates
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    two_days_ago = now - timedelta(days=2)
    three_days_ago = now - timedelta(days=3)

    # 1. Insert Vendors
    vendors = [
        {
            "id": 1,
            "name": "Slack Technologies",
            "domain": "slack.com",
            "website_url": "https://slack.com",
            "category": "communication",
            "data_sensitivity": "high",
            "description": "Enterprise instant messaging and collaboration platform. Handles internal employee communications and file sharing.",
            "risk_score": 3.2,
            "risk_level": "medium",
            "last_scanned": yesterday.isoformat()
        },
        {
            "id": 2,
            "name": "Acme Corp",
            "domain": "acme.com",
            "website_url": "https://acme.com",
            "category": "saas",
            "data_sensitivity": "critical",
            "description": "Core SaaS provider for billing workflow and customer records management. Accesses sensitive customer PII.",
            "risk_score": 8.5,
            "risk_level": "critical",
            "last_scanned": now.isoformat()
        },
        {
            "id": 3,
            "name": "Stripe",
            "domain": "stripe.com",
            "website_url": "https://stripe.com",
            "category": "payment",
            "data_sensitivity": "critical",
            "description": "Primary payment gateway and financial processing vendor. Handles PCI-DSS credit card transactions.",
            "risk_score": 1.2,
            "risk_level": "low",
            "last_scanned": yesterday.isoformat()
        }
    ]

    for v in vendors:
        cursor.execute(
            """INSERT INTO vendors (id, name, domain, website_url, category, data_sensitivity, description, risk_score, risk_level, last_scanned)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (v["id"], v["name"], v["domain"], v["website_url"], v["category"], v["data_sensitivity"], v["description"], v["risk_score"], v["risk_level"], v["last_scanned"])
        )
    
    # 2. Insert Scan History
    scan_id_1 = str(uuid.uuid4())
    scan_id_2 = str(uuid.uuid4())
    
    scans = [
        {
            "scan_id": scan_id_1,
            "status": "completed",
            "vendors_scanned": 3,
            "total_signals_found": 8,
            "started_at": yesterday.isoformat(),
            "completed_at": (yesterday + timedelta(minutes=1)).isoformat()
        },
        {
            "scan_id": scan_id_2,
            "status": "completed",
            "vendors_scanned": 1,
            "total_signals_found": 4,
            "started_at": now.isoformat(),
            "completed_at": (now + timedelta(minutes=1)).isoformat()
        }
    ]
    
    for s in scans:
        cursor.execute(
            """INSERT INTO scan_history (scan_id, status, vendors_scanned, total_signals_found, started_at, completed_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (s["scan_id"], s["status"], s["vendors_scanned"], s["total_signals_found"], s["started_at"], s["completed_at"])
        )

    # 3. Insert Scan Results (Signals)
    signals = [
        # Slack yesterday signals
        {
            "vendor_id": 1,
            "scan_id": scan_id_1,
            "signal_type": "news_media",
            "severity": "medium",
            "title": "Slack experiences minor service outage impacting connection speeds",
            "description": "Slack Technologies experienced a 45-minute service outage yesterday causing elevated message delivery latency globally.",
            "source_url": "https://techcrunch.com/slack-outage-report",
            "raw_data": {"articles_matched": 1, "provider": "techcrunch"}
        },
        {
            "vendor_id": 1,
            "scan_id": scan_id_1,
            "signal_type": "hiring_distress",
            "severity": "low",
            "title": "Slack posts active openings for security engineers",
            "description": "Found 2 active job listings on LinkedIn for security roles: 'Senior Incident Response Engineer' and 'Security Compliance Specialist'.",
            "source_url": "https://linkedin.com/jobs/slack",
            "raw_data": {"listings_found": 2, "roles": ["Senior Incident Response Engineer", "Security Compliance Specialist"]}
        },
        # Acme yesterday signals
        {
            "vendor_id": 2,
            "scan_id": scan_id_1,
            "signal_type": "news_media",
            "severity": "critical",
            "title": "Ransomware gang claims cyberattack on SaaS provider Acme Corp",
            "description": "The LockBit ransomware syndicate has added Acme Corp to its leak site, claiming to have exfiltrated over 10GB of customer billing records and PII.",
            "source_url": "https://krebsonsecurity.com/acme-corp-ransomware",
            "raw_data": {"source": "LockBit Leak Site", "file_count": 450, "size_gb": 10}
        },
        {
            "vendor_id": 2,
            "scan_id": scan_id_1,
            "signal_type": "credential_leak",
            "severity": "critical",
            "title": "Pastebin credential leak: Acme database admin password exposed",
            "description": "A public raw paste on pastebin.com was found containing db connection credentials matching the acme.com domain: 'DB_USER=acme_admin_prod; DB_PASS=********'.",
            "source_url": "https://pastebin.com/raw/u83Hd72f",
            "raw_data": {"site": "pastebin.com", "exposed_variables": ["DB_USER", "DB_PASS"]}
        },
        {
            "vendor_id": 2,
            "scan_id": scan_id_1,
            "signal_type": "hiring_distress",
            "severity": "high",
            "title": "Sudden spike in high-level security job openings at Acme Corp",
            "description": "LinkedIn scraper detected a sudden surge in emergency postings: CISO, SOC Lead, and Security Architect within the last 48 hours.",
            "source_url": "https://linkedin.com/jobs/acme",
            "raw_data": {"surge_detected": True, "openings_count": 3, "roles": ["CISO", "SOC Lead", "Security Architect"]}
        },
        {
            "vendor_id": 2,
            "scan_id": scan_id_1,
            "signal_type": "vendor_health",
            "severity": "high",
            "title": "Glassdoor reviews flag severe organizational instability and IT cuts",
            "description": "Recent Glassdoor employee reviews mention severe budget cuts in IT compliance departments and leadership attrition.",
            "source_url": "https://glassdoor.com/reviews/acme-corp",
            "raw_data": {"ratings_average": 2.1, "mention_keywords": ["layoffs", "IT budget", "compliance cuts"]}
        },
        # Stripe yesterday signals
        {
            "vendor_id": 3,
            "scan_id": scan_id_1,
            "signal_type": "news_media",
            "severity": "low",
            "title": "Stripe launches new AI-billing API features",
            "description": "Stripe announced general availability of its new automated AI invoice matching suite.",
            "source_url": "https://stripe.com/newsroom",
            "raw_data": {"announcement": True}
        }
    ]

    for sig in signals:
        cursor.execute(
            """INSERT INTO scan_results (vendor_id, scan_id, signal_type, severity, title, description, source_url, raw_data)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (sig["vendor_id"], sig["scan_id"], sig["signal_type"], sig["severity"], sig["title"], sig["description"], sig["source_url"], json.dumps(sig["raw_data"]))
        )

    # 4. Insert Risk Scores
    scores = [
        # Slack scores
        {
            "vendor_id": 1,
            "scan_id": scan_id_1,
            "score": 3.2,
            "risk_level": "medium",
            "ai_reasoning": "Slack is exhibiting mild security indicators. The minor outage and ongoing standard security recruitment are normal operational behaviors and do not represent a systemic compromise.",
            "recommended_actions": "1. Standard continuous monitoring of public media.\n2. Ensure employee communications sensitivity matches data handling guidelines.",
            "signal_summary": {"news": 1, "hiring": 1}
        },
        # Stripe scores
        {
            "vendor_id": 3,
            "scan_id": scan_id_1,
            "score": 1.2,
            "risk_level": "low",
            "ai_reasoning": "Stripe exhibits an outstanding risk profile. No threat signals, database leaks, or corporate distress markers were identified.",
            "recommended_actions": "1. Maintain standard monthly audit schedule.",
            "signal_summary": {"news": 1}
        },
        # Acme yesterday scores
        {
            "vendor_id": 2,
            "scan_id": scan_id_1,
            "score": 8.5,
            "risk_level": "critical",
            "ai_reasoning": "Acme Corp is undergoing a severe security crisis. The verified LockBit ransomware exfiltration, public exposure of production db credentials on Pastebin, and sudden emergency hiring of a CISO strongly indicate an active, uncontained breach.",
            "recommended_actions": "1. Halt non-essential data transfers to Acme Corp immediately.\n2. Force rotate all API keys and integrations shared with Acme.\n3. Request verified incident response report from Acme CISO.",
            "signal_summary": {"news": 1, "credentials": 1, "hiring": 1, "health": 1}
        }
    ]

    for sc in scores:
        cursor.execute(
            """INSERT INTO risk_scores (vendor_id, scan_id, score, risk_level, ai_reasoning, recommended_actions, signal_summary)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (sc["vendor_id"], sc["scan_id"], sc["score"], sc["risk_level"], sc["ai_reasoning"], sc["recommended_actions"], json.dumps(sc["signal_summary"]))
        )

    # 5. Insert Alerts
    alerts = [
        {
            "vendor_id": 2,
            "scan_id": scan_id_1,
            "alert_type": "high_risk",
            "severity": "critical",
            "title": "CRITICAL BREACH: Acme Corp ransomware attack",
            "message": "Vendor 'Acme Corp' scored 8.5/10 (Critical Risk). A verified ransomware breach has exfiltrated 10GB of customer billing PII, and production database passwords were leaked publicly.",
            "is_read": 0
        }
    ]

    for al in alerts:
        cursor.execute(
            """INSERT INTO alerts (vendor_id, scan_id, alert_type, severity, title, message, is_read)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (al["vendor_id"], al["scan_id"], al["alert_type"], al["severity"], al["title"], al["message"], al["is_read"])
        )

    conn.commit()
    conn.close()
    print("[OK] Database seeded successfully with Slack, Stripe, and Acme Corp profiles.")

if __name__ == "__main__":
    asyncio.run(seed_data())
