import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# ── Document Setup ───────────────────────────────────────────────
pdf_filename = "VendorSentinel_Visual_Presentation.pdf"
doc = SimpleDocTemplate(
    pdf_filename,
    pagesize=landscape(letter),
    rightMargin=0.5 * inch,
    leftMargin=0.5 * inch,
    topMargin=0.5 * inch,
    bottomMargin=0.5 * inch
)

# ── Color Palette (Bookish / Dark Editorial Theme) ───────────────
BG_COLOR = colors.HexColor("#0d0c0a")      # Deep charcoal background
CARD_BG = colors.HexColor("#1c1813")       # Slightly lighter brown/charcoal
GOLD_ACCENT = colors.HexColor("#dca742")   # Golden text/highlight
SOFT_IVORY = colors.HexColor("#e6e2da")    # Main body text
MUTED_TEXT = colors.HexColor("#9b978f")    # Secondary body text
BORDER_COLOR = colors.HexColor("#2f271d")  # Dark border

# ── Page Background Canvas Helper ─────────────────────────────────
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_background(page_count)
            super().showPage()
        super().save()

    def draw_background(self, page_count):
        self.saveState()
        
        # 1. Fill entire slide background with dark color
        self.setFillColor(BG_COLOR)
        self.rect(0, 0, 11 * inch, 8.5 * inch, fill=True, stroke=False)
        
        # 2. Draw golden header divider line (except on Title slide)
        if self._pageNumber > 1:
            self.setStrokeColor(BORDER_COLOR)
            self.setLineWidth(1)
            self.line(0.5 * inch, 7.5 * inch, 10.5 * inch, 7.5 * inch)
            
            # Draw golden header accent bar
            self.setFillColor(GOLD_ACCENT)
            self.rect(0.5 * inch, 7.48 * inch, 1.5 * inch, 0.04 * inch, fill=True, stroke=False)
            
            # Header Track info
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(GOLD_ACCENT)
            self.drawString(0.5 * inch, 7.65 * inch, "🛡️ VENDORSENTINEL  |  TRACK 3: WEB DATA & COMPLIANCE")
            
            # 3. Slide Footer
            self.setStrokeColor(BORDER_COLOR)
            self.line(0.5 * inch, 0.7 * inch, 10.5 * inch, 0.7 * inch)
            
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(MUTED_TEXT)
            self.drawString(0.5 * inch, 0.45 * inch, "VendorSentinel — Continuous Third-Party Risk Intelligence — Hackathon 2026")
            
            # Slide page number
            self.drawRightString(10.5 * inch, 0.45 * inch, f"{self._pageNumber} of {page_count}")
        
        self.restoreState()

# ── Styles Setup ──────────────────────────────────────────────────
styles = getSampleStyleSheet()

# Custom styles using standard built-in fonts (Times-Bold for serif headers, Helvetica for body)
title_style = ParagraphStyle(
    'TitleStyle',
    parent=styles['Normal'],
    fontName='Times-Bold',
    fontSize=36,
    leading=42,
    textColor=SOFT_IVORY,
    alignment=1, # Center
    spaceAfter=15
)

subtitle_style = ParagraphStyle(
    'SubtitleStyle',
    parent=styles['Normal'],
    fontName='Times-Italic',
    fontSize=18,
    leading=24,
    textColor=GOLD_ACCENT,
    alignment=1, # Center
    spaceAfter=25
)

author_style = ParagraphStyle(
    'AuthorStyle',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=11,
    leading=16,
    textColor=SOFT_IVORY,
    alignment=1,
    spaceAfter=5
)

meta_style = ParagraphStyle(
    'MetaStyle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=9,
    leading=14,
    textColor=GOLD_ACCENT,
    alignment=1
)

slide_header_style = ParagraphStyle(
    'SlideHeaderStyle',
    parent=styles['Normal'],
    fontName='Times-Bold',
    fontSize=22,
    leading=26,
    textColor=SOFT_IVORY,
    spaceAfter=6
)

slide_subheader_style = ParagraphStyle(
    'SlideSubheaderStyle',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=11,
    leading=15,
    textColor=MUTED_TEXT,
    spaceAfter=25
)

body_style = ParagraphStyle(
    'BodyStyle',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=10,
    leading=15,
    textColor=SOFT_IVORY
)

body_bold_style = ParagraphStyle(
    'BodyBoldStyle',
    parent=body_style,
    fontName='Helvetica-Bold',
    textColor=GOLD_ACCENT
)

card_header_style = ParagraphStyle(
    'CardHeaderStyle',
    parent=styles['Normal'],
    fontName='Times-Bold',
    fontSize=13,
    leading=17,
    textColor=GOLD_ACCENT,
    spaceAfter=6
)

card_body_style = ParagraphStyle(
    'CardBodyStyle',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9,
    leading=13,
    textColor=SOFT_IVORY
)

# ── Story Construction ────────────────────────────────────────────
story = []

# =========================================================================
# SLIDE 1: Title Slide
# =========================================================================
story.append(Spacer(1, 1.8 * inch))
story.append(Paragraph("VendorSentinel", title_style))
story.append(Paragraph("AI-Powered Third-Party Vendor Risk Intelligence Fabric", subtitle_style))
story.append(Spacer(1, 0.4 * inch))
story.append(Paragraph("🛡️ Track 3: Web Data & Compliance  |  Bright Data Hackathon 2026", meta_style))
story.append(Spacer(1, 0.2 * inch))
story.append(Paragraph("Created & Deployed by:  Hafiz Abdul Rehman", author_style))
story.append(Paragraph("Live UI:  https://vendor-sentinel.vercel.app/  &bull;  Backend API: https://vendorsentinel.onrender.com", author_style))
story.append(PageBreak())

# =========================================================================
# SLIDE 2: The Third-Party Vendor Risk Crisis
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("The Third-Party Vendor Risk Crisis", slide_header_style))
story.append(Paragraph("Modern enterprises lose millions annually due to blind spots in vendor cybersecurity.", slide_subheader_style))

# Left stats column block
stats_content = [
    [Paragraph("<b>$4.5M</b>", ParagraphStyle('HugeVal', parent=styles['Normal'], fontName='Times-Bold', fontSize=40, leading=44, textColor=GOLD_ACCENT, alignment=1))],
    [Paragraph("<b>Average Annual Cost</b><br/>of a Third-Party Data Breach", ParagraphStyle('StatSub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=SOFT_IVORY, alignment=1))],
    [Spacer(1, 10)],
    [Paragraph("🚨 <b>Critical Risk Factors</b><br/>SolarWinds credentials 'solarwinds123' lay exposed on GitHub for 13 months before exploitation. Snowflake's pre-breach client credentials circulated for weeks on hacker forums. Silent warnings are always public beforehand, but standard teams lack tools to reliably watch them.", ParagraphStyle('StatDesc', parent=body_style, fontSize=9.5, leading=14, textColor=SOFT_IVORY))]
]
t_stats = Table(stats_content, colWidths=[3.2 * inch])
t_stats.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
    ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
    ('PADDING', (0,0), (-1,-1), 16),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
]))

# Right content card
col_data = [
    [
        Paragraph("1. Outdated PDF Questionnaires", card_header_style),
        Paragraph("Traditional security teams assess vendors using annual self-attested PDF checklists. These questionnaires fail completely to capture live active credentials leaks, outages, or sudden leadership distress.", card_body_style)
    ],
    [Spacer(1, 6), ""],
    [
        Paragraph("2. The Anti-Bot Defensive Wall", card_header_style),
        Paragraph("Pastebin throws CAPTCHAs at automated requests, LinkedIn rate-limits job board scraping, and corporate trust blogs dynamically block bots. Standard tools cannot reliably capture these public warning signs.", card_body_style)
    ],
    [Spacer(1, 6), ""],
    [
        Paragraph("3. Factual Hallucinations in Standard AI", card_header_style),
        Paragraph("Generic Large Language Models generate risk assessments filled with stale statistics and fictional data. Enterprise security requirements require concrete source lineage and absolute factual provenance.", card_body_style)
    ]
]
t_col = Table(col_data, colWidths=[6.3 * inch])
t_col.setStyle(TableStyle([
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ('TOPPADDING', (0,0), (-1,-1), 0),
]))

# Combined layout
layout_table = Table([[t_stats, t_col]], colWidths=[3.4 * inch, 6.6 * inch])
layout_table.setStyle(TableStyle([
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('LEFTPADDING', (1,0), (1,0), 20),
]))
story.append(layout_table)
story.append(PageBreak())

# =========================================================================
# SLIDE 3: Track 3 Alignment: Bright Data Stack
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("📊 Track 3: Web Data & Compliance Alignment", slide_header_style))
story.append(Paragraph("Purpose-built compliance: how VendorSentinel harnesses Bright Data to satisfy security requirements.", slide_subheader_style))

# Grid Table of Track Alignment
table_data = [
    [
        Paragraph("<b>Track 3 Focus Area</b>", ParagraphStyle('TH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=GOLD_ACCENT)),
        Paragraph("<b>Bright Data Integrated Technology</b>", ParagraphStyle('TH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=GOLD_ACCENT)),
        Paragraph("<b>VendorSentinel Implementation Purpose</b>", ParagraphStyle('TH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=GOLD_ACCENT))
    ],
    [
        Paragraph("<b>Public Media & News Scrapes</b>", body_style),
        Paragraph("<b>Bright Data SERP API</b>", body_bold_style),
        Paragraph("Queries Google search engine recursively for vendor data breaches, ransomware warnings, regulatory compliance fines, and class action lawsuits.", body_style)
    ],
    [
        Paragraph("<b>Blocked/CAPTCHA Paste Sites</b>", body_style),
        Paragraph("<b>Bright Data Web Unlocker Proxy</b>", body_bold_style),
        Paragraph("Rotates residential proxies and automatically resolves Pastebin bot checks, scanning for leaked passwords, API keys, and vendor configuration strings.", body_style)
    ],
    [
        Paragraph("<b>Hiring Board Rate Limits</b>", body_style),
        Paragraph("<b>Bright Data Web Scraper API</b>", body_bold_style),
        Paragraph("Ingests recent job board postings for security engineer, incident responder, and CISO positions, tracking hiring spikes that signal internal crisis.", body_style)
    ],
    [
        Paragraph("<b>JS-Heavy Morale Pages</b>", body_style),
        Paragraph("<b>Bright Data Scraping Browser</b>", body_bold_style),
        Paragraph("Initiates remote Playwright Chromium CDP sessions to load corporate trust/posture pages, verifying security attestations and patch updates.", body_style)
    ]
]

t_align = Table(table_data, colWidths=[2.5 * inch, 2.8 * inch, 4.7 * inch])
t_align.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), CARD_BG),
    ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ('PADDING', (0,0), (-1,-1), 10),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
]))
story.append(t_align)
story.append(PageBreak())

# =========================================================================
# SLIDE 4: The Autonomous Risk Intelligence Fabric
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("The Autonomous Risk Intelligence Fabric", slide_header_style))
story.append(Paragraph("A multi-layered threat intelligence pipeline that scans continuously and reasons dynamically.", slide_subheader_style))

# 4 card grid layout
card1_content = [
    [Paragraph("📁 1. Portfolio Onboarding Hub", card_header_style)],
    [Paragraph("Security managers add vendors simply by domain and category. The SQLite WAL database registers the profiles instantly and schedules automated scan queues.", card_body_style)]
]
t_c1 = Table(card1_content, colWidths=[4.7 * inch])
t_c1.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), CARD_BG), ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 14), ('VALIGN', (0,0), (-1,-1), 'TOP')]))

card2_content = [
    [Paragraph("🔐 2. Exposed Secrets Hunting", card_header_style)],
    [Paragraph("Web Unlocker proxy routes target searches to discover exposed vendor passwords or token variables circulating on public sharing repositories and code dumps.", card_body_style)]
]
t_c2 = Table(card2_content, colWidths=[4.7 * inch])
t_c2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), CARD_BG), ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 14), ('VALIGN', (0,0), (-1,-1), 'TOP')]))

card3_content = [
    [Paragraph("📊 3. Talent Recruitment Spikes", card_header_style)],
    [Paragraph("Web Scraper API logs LinkedIn vacancy counts. Spike indicators (e.g. 400% surge in incident response recruitment) flag internal security overhaul periods.", card_body_style)]
]
t_c3 = Table(card3_content, colWidths=[4.7 * inch])
t_c3.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), CARD_BG), ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 14), ('VALIGN', (0,0), (-1,-1), 'TOP')]))

card4_content = [
    [Paragraph("🤖 4. AI Mitigation Playbooks", card_header_style)],
    [Paragraph("AI scoring synthesizes all 4 vectors to grade vendor posture (1-10) and auto-builds step-by-step plain-English playbooks for corporate cybersecurity guards.", card_body_style)]
]
t_c4 = Table(card4_content, colWidths=[4.7 * inch])
t_c4.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), CARD_BG), ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 14), ('VALIGN', (0,0), (-1,-1), 'TOP')]))

grid_c = Table([[t_c1, t_c2], [Spacer(1, 15), Spacer(1, 15)], [t_c3, t_c4]], colWidths=[4.9 * inch, 4.9 * inch])
grid_c.setStyle(TableStyle([
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('LEFTPADDING', (0,0), (-1,-1), 0),
    ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ('TOPPADDING', (0,0), (-1,-1), 0),
]))
story.append(grid_c)
story.append(PageBreak())

# =========================================================================
# SLIDE 5: Autonomous Threat Scan Pipeline
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("Autonomous Threat Scan Pipeline", slide_header_style))
story.append(Paragraph("System-wide visual data flow, showcasing concurrent collections and verification gates.", slide_subheader_style))

# Flow Table
flow_data = [
    [
        Paragraph("<b>1. Ingestion</b>", ParagraphStyle('F1', parent=styles['Normal'], fontName='Times-Bold', fontSize=14, textColor=GOLD_ACCENT, alignment=1)),
        Paragraph("<b>2. Parallel Scrape</b>", ParagraphStyle('F2', parent=styles['Normal'], fontName='Times-Bold', fontSize=14, textColor=GOLD_ACCENT, alignment=1)),
        Paragraph("<b>3. AI Synthesis</b>", ParagraphStyle('F3', parent=styles['Normal'], fontName='Times-Bold', fontSize=14, textColor=GOLD_ACCENT, alignment=1)),
        Paragraph("<b>4. Security Alert</b>", ParagraphStyle('F4', parent=styles['Normal'], fontName='Times-Bold', fontSize=14, textColor=GOLD_ACCENT, alignment=1))
    ],
    [
        Paragraph("Admin adds vendor domain, category, and data sensitivity (e.g. Okta = Critical). SQLite stores and schedules scan queue.", body_style),
        Paragraph("FastAPI concurrently spawns 4 crawling tasks via <b>asyncio.gather</b> using Bright Data SERP, Unlocker, Scraper, and Browser APIs.", body_style),
        Paragraph("All gathered evidence models feed into GPT-4o-mini to calculate exact risk scores (1-10), reasons, and action items.", body_style),
        Paragraph("If computed risk score &ge; 7.0 threshold, an automated critical warning alert is broadcasted on the admin UI stream.", body_style)
    ]
]
t_flow = Table(flow_data, colWidths=[2.4 * inch, 2.5 * inch, 2.5 * inch, 2.6 * inch])
t_flow.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (0,1), CARD_BG),
    ('BACKGROUND', (1,0), (1,1), CARD_BG),
    ('BACKGROUND', (2,0), (2,1), CARD_BG),
    ('BACKGROUND', (3,0), (3,1), CARD_BG),
    ('BOX', (0,0), (0,1), 1, BORDER_COLOR),
    ('BOX', (1,0), (1,1), 1, BORDER_COLOR),
    ('BOX', (2,0), (2,1), 1, BORDER_COLOR),
    ('BOX', (3,0), (3,1), 1, BORDER_COLOR),
    ('PADDING', (0,0), (-1,-1), 14),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
]))
story.append(Spacer(1, 0.4 * inch))
story.append(t_flow)
story.append(PageBreak())

# =========================================================================
# SLIDE 6: The Coordinated Scraper Specialists
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("The Coordinated Scraper Specialists", slide_header_style))
story.append(Paragraph("Four prompt-engineered and proxy-configured intelligence gatherers mapped to specific threat vectors.", slide_subheader_style))

specialist_data = [
    [
        Paragraph("<b>SERP API News Specialist</b>", card_header_style),
        Paragraph("Queries major search engines dynamically for keywords like `data breach`, `GDPR violation`, and `cyberattack` combined with vendor name. Standardizes unstructured news headlines into clean evidence indices.", card_body_style)
    ],
    [
        Paragraph("<b>Web Unlocker Paste Collector</b>", card_header_style),
        Paragraph("Accesses restricted paste boards and public GitHub code commit endpoints. Resolves CAPTCHAs and blocks automatically, tracking leaked credentials and database secrets related to the vendor's domain.", card_body_style)
    ],
    [
        Paragraph("<b>LinkedIn Job Board Analyst</b>", card_header_style),
        Paragraph("Scrapes active company job listings through the Bright Data dataset API. Tracks recruitment baseline and identifies sudden spikes in CISO, SOC analyst, and incident response vacancies.", card_body_style)
    ],
    [
        Paragraph("<b>Scraping Browser Posture Auditor</b>", card_header_style),
        Paragraph("Launches headless Playwright Chromium CDP sessions to load complex JavaScript-heavy trust and status blogs, verifying certification validations and recently published patch advisories.", card_body_style)
    ]
]
t_spec = Table(specialist_data, colWidths=[2.8 * inch, 7.2 * inch])
t_spec.setStyle(TableStyle([
    ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ('PADDING', (0,0), (-1,-1), 10),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('BACKGROUND', (0,0), (0,-1), CARD_BG),
]))
story.append(t_spec)
story.append(PageBreak())

# =========================================================================
# SLIDE 7: Under-the-Hood Technical Modules
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("Under-the-Hood Technical Modules", slide_header_style))
story.append(Paragraph("Highly optimized, production-ready modules driving data persistence and crawler stability.", slide_subheader_style))

# Left stats column block
stats_content_7 = [
    [Paragraph("<b>FastAPI Core</b>", card_header_style)],
    [Paragraph("Serves secure dynamic JSON API endpoints using an asynchronous event model, providing lightning-fast server routing under production Uvicorn containers.", card_body_style)],
    [Spacer(1, 10)],
    [Paragraph("💾 <b>SQLite WAL Database</b>", card_header_style)],
    [Paragraph("Leverages `aiosqlite` WAL (Write-Ahead Logging) transactions for safe, concurrent database read/write queries. Maintains stable local tables for `vendors`, `scan_results`, and `risk_scores` without heavy database instances.", card_body_style)]
]
t_stats_7 = Table(stats_content_7, colWidths=[3.2 * inch])
t_stats_7.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
    ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
    ('PADDING', (0,0), (-1,-1), 16),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
]))

# Right content card
col_data_7 = [
    [
        Paragraph("1. Windows Console Encoding Fix", card_header_style),
        Paragraph("Standard Windows shells crash (`UnicodeEncodeError`) when python prints modern emojis. We reconfigured `sys.stdout/stderr` encoding dynamically to UTF-8 at start, ensuring 100% stable terminal console audit logs.", card_body_style)
    ],
    [Spacer(1, 6), ""],
    [
        Paragraph("2. Windows Proactor Subprocess Integration", card_header_style),
        Paragraph("Playwright async connection triggers `NotImplementedError` under default SelectorEventLoop on Windows. We dynamically configure `WindowsProactorEventLoopPolicy` on win32 startup, allowing safe browser automation threads.", card_body_style)
    ],
    [Spacer(1, 6), ""],
    [
        Paragraph("3. Robust Background Task wrapping", card_header_style),
        Paragraph("Scans triggered as background tasks can hang in 'running' if uncaught exceptions occur. We wrapped `scan_single_vendor` in a bulletproof error-safe loop that guarantees table updates and saves complete audit logs.", card_body_style)
    ]
]
t_col_7 = Table(col_data_7, colWidths=[6.3 * inch])
t_col_7.setStyle(TableStyle([
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ('TOPPADDING', (0,0), (-1,-1), 0),
]))

# Combined layout
layout_table_7 = Table([[t_stats_7, t_col_7]], colWidths=[3.4 * inch, 6.6 * inch])
layout_table_7.setStyle(TableStyle([
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('LEFTPADDING', (1,0), (1,0), 20),
]))
story.append(layout_table_7)
story.append(PageBreak())

# =========================================================================
# SLIDE 8: The Cybersecurity Control Interface
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("The Cybersecurity Control Interface", slide_header_style))
story.append(Paragraph("A premium Bookish design system featuring modular components and high-tech threat radars.", slide_subheader_style))

interface_data = [
    [
        Paragraph("<b>1. Live Threat Risk Dashboard</b>", card_header_style),
        Paragraph("Presents overall portfolio count, unread alerts, and average risk rating. Renders custom-styled card grids highlighting critical, warning, and low threat vendors.", card_body_style)
    ],
    [
        Paragraph("<b>2. Automated Threat Scan Radar</b>", card_header_style),
        Paragraph("Features an infinitely spinning golden radar sweeper, concentric active wave rings, and pulsing threat blips built entirely using hardware-accelerated CSS keyframes.", card_body_style)
    ],
    [
        Paragraph("<b>3. Bright Data Nodes Status</b>", card_header_style),
        Paragraph("Integrates live status nodes with pulsing green indicator dots (`pulse-node-dot`) to prove API credentials and network connectivity directly to judges.", card_body_style)
    ],
    [
        Paragraph("<b>4. Dynamic Playbooks Panel</b>", card_header_style),
        Paragraph("Drills down into detailed vendor profiles to display AI-generated threat reasoning, evidence sources, and structured playbooks for immediate mitigation.", card_body_style)
    ]
]
t_inter = Table(interface_data, colWidths=[2.8 * inch, 7.2 * inch])
t_inter.setStyle(TableStyle([
    ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ('PADDING', (0,0), (-1,-1), 10),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('BACKGROUND', (0,0), (0,-1), CARD_BG),
]))
story.append(t_inter)
story.append(PageBreak())

# =========================================================================
# SLIDE 9: Deep Bright Data & AI/ML API Integration
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("Deep Bright Data & AI/ML API Integration", slide_header_style))
story.append(Paragraph("Normalizing global web intelligence and AI model reasoning into a single audit lifecycle.", slide_subheader_style))

integration_table = [
    [
        Paragraph("<b>System Module</b>", ParagraphStyle('IH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=GOLD_ACCENT)),
        Paragraph("<b>Technology Used</b>", ParagraphStyle('IH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=GOLD_ACCENT)),
        Paragraph("<b>Platform Operational Role</b>", ParagraphStyle('IH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=GOLD_ACCENT))
    ],
    [
        Paragraph("<b>News Aggregator</b>", body_style),
        Paragraph("<b>Bright Data SERP API</b>", body_bold_style),
        Paragraph("Crawls real-time Google results for data leaks, GDPR violations, and class action lawsuits referencing vendor names.", body_style)
    ],
    [
        Paragraph("<b>Secrets Hunter</b>", body_style),
        Paragraph("<b>Bright Data Web Unlocker</b>", body_bold_style),
        Paragraph("Bypasses bot protections on Pastebin and GitHub to search for exposed passwords, configuration variables, and API keys.", body_style)
    ],
    [
        Paragraph("<b>Talent Tracker</b>", body_style),
        Paragraph("<b>Bright Data Web Scraper API</b>", body_bold_style),
        Paragraph("Utilizes standard dataset scrapers to scan LinkedIn company pages, counting security, CISO, and incident response vacancies.", body_style)
    ],
    [
        Paragraph("<b>Posture Crawler</b>", body_style),
        Paragraph("<b>Bright Data Scraping Browser</b>", body_bold_style),
        Paragraph("Launches chromium browser CDP over websocket WSS connections to parse compliance blogs and check security patches.", body_style)
    ],
    [
        Paragraph("<b>AI Risk Analyst</b>", body_style),
        Paragraph("<b>AI/ML API (GPT-4o-mini)</b>", body_bold_style),
        Paragraph("Receives aggregated signal logs and outputs structured threat ratings, reasoning logs, and recommended actions playbooks.", body_style)
    ]
]
t_integ = Table(integration_table, colWidths=[2.2 * inch, 2.8 * inch, 5.0 * inch])
t_integ.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), CARD_BG),
    ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ('PADDING', (0,0), (-1,-1), 8),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
]))
story.append(t_integ)
story.append(PageBreak())

# =========================================================================
# SLIDE 10: Strategic Business Value & Market Scope
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("Strategic Business Value & Market Scope", slide_header_style))
story.append(Paragraph("Quantifying the commercial footprint and core enterprise monetization pathways.", slide_subheader_style))

# Left stats column block
stats_content_10 = [
    [Paragraph("<b>$4.5M</b>", ParagraphStyle('Val10', parent=styles['Normal'], fontName='Times-Bold', fontSize=32, leading=36, textColor=GOLD_ACCENT, alignment=1))],
    [Paragraph("<b>Average Cost of Breach</b>", ParagraphStyle('Label10', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=SOFT_IVORY, alignment=1))],
    [Spacer(1, 15)],
    [Paragraph("🎯 <b>Core Verticals</b>", card_header_style)],
    [Paragraph("• Finance & Enterprise Banking<br/>• Health & EMR Providers<br/>• SaaS & Cloud Infrastructure<br/>• M&A Due Diligence Auditing", ParagraphStyle('Bullet10', parent=body_style, leading=16))]
]
t_stats_10 = Table(stats_content_10, colWidths=[3.2 * inch])
t_stats_10.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
    ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
    ('PADDING', (0,0), (-1,-1), 16),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
]))

# Right content card
col_data_10 = [
    [
        Paragraph("High-Impact Operational Savings", card_header_style),
        Paragraph("• **Labor Reduction**: Shifts security compliance sweeps from weeks of manual review to seconds of automated analysis, allowing security managers to focus on direct mitigation.<br/>• **Proactive Prevention**: Identifies leaks, credentials exposure, and internal organizational distress months before standard public disclosures occur, avoiding massive breach damage.<br/>• **Continuous Attestations**: Provides corporate boards with active security health audits rather than obsolete once-a-year self-attested PDF papers.", card_body_style)
    ],
    [Spacer(1, 6), ""],
    [
        Paragraph("Monetization & Commercial Channels", card_header_style),
        Paragraph("• **Tiered SaaS Licenses**: Charged based on total active onboarded vendor counts, processed API query volume, and database sweep intervals.<br/>• **Secure API Connectors**: Standard endpoints to integrate VendorSentinel risk scores directly into enterprise BI tools like Tableau, Power BI, and ServiceNow.<br/>• **Audit Report Exports**: Premium custom fees for exporting cryptographically hashed compliance reports ready for official corporate security auditing.", card_body_style)
    ]
]
t_col_10 = Table(col_data_10, colWidths=[6.3 * inch])
t_col_10.setStyle(TableStyle([
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ('TOPPADDING', (0,0), (-1,-1), 0),
]))

# Combined layout
layout_table_10 = Table([[t_stats_10, t_col_10]], colWidths=[3.4 * inch, 6.6 * inch])
layout_table_10.setStyle(TableStyle([
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('LEFTPADDING', (1,0), (1,0), 20),
]))
story.append(layout_table_10)
story.append(PageBreak())

# =========================================================================
# SLIDE 11: Originality & Unique Selling Proposition
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("Originality & Unique Selling Proposition", slide_header_style))
story.append(Paragraph("Comparing VendorSentinel with static database scorecards and manual PDF workflows.", slide_subheader_style))

usp_table = [
    [
        Paragraph("<b>System Capability</b>", ParagraphStyle('UH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=GOLD_ACCENT)),
        Paragraph("<b>Annual PDFs</b>", ParagraphStyle('UH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=GOLD_ACCENT)),
        Paragraph("<b>Legacy Scorecards</b>", ParagraphStyle('UH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=GOLD_ACCENT)),
        Paragraph("<b>VendorSentinel Fabric</b>", ParagraphStyle('UH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=GOLD_ACCENT))
    ],
    [
        Paragraph("<b>Real-Time Monitoring</b>", body_style),
        Paragraph("❌ None, once a year only", body_style),
        Paragraph("⚠️ Delayed, relies on database index", body_style),
        Paragraph("<b>✅ Yes, continuous 6-hour sweeps</b>", body_bold_style)
    ],
    [
        Paragraph("<b>Exposed Credentials</b>", body_style),
        Paragraph("❌ None, cannot self-report", body_style),
        Paragraph("❌ Missing paste board scans", body_style),
        Paragraph("<b>✅ Yes, live Web Unlocker scans</b>", body_bold_style)
    ],
    [
        Paragraph("<b>Anti-Bot Bypassing</b>", body_style),
        Paragraph("❌ None", body_style),
        Paragraph("❌ Blocks on secure boards", body_style),
        Paragraph("<b>✅ Yes, full Bright Data stack</b>", body_bold_style)
    ],
    [
        Paragraph("<b>Mitigation Playbooks</b>", body_style),
        Paragraph("❌ None", body_style),
        Paragraph("⚠️ Generic checklist only", body_style),
        Paragraph("<b>✅ Yes, custom AI playbooks</b>", body_bold_style)
    ],
    [
        Paragraph("<b>Hiring Distress Tracking</b>", body_style),
        Paragraph("❌ None", body_style),
        Paragraph("❌ None", body_style),
        Paragraph("<b>✅ Yes, Scraper API integration</b>", body_bold_style)
    ]
]
t_usp = Table(usp_table, colWidths=[2.5 * inch, 2.3 * inch, 2.3 * inch, 2.9 * inch])
t_usp.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), CARD_BG),
    ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ('PADDING', (0,0), (-1,-1), 10),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
]))
story.append(t_usp)
story.append(PageBreak())

# =========================================================================
# SLIDE 12: Strategic Execution Roadmap
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("Strategic Execution Roadmap", slide_header_style))
story.append(Paragraph("A step-by-step scaling plan from current production MVP to enterprise-wide integrations.", slide_subheader_style))

roadmap_data = [
    [
        Paragraph("<b>Phase 1: Production MVP</b>", card_header_style),
        Paragraph("Full integration of 4 Bright Data collectors + AI scoring. Complete web UI dashboards, local WAL SQLite database layer, and public code repository push.", card_body_style)
    ],
    [
        Paragraph("<b>Phase 2: Enterprise SSO & Auth</b>", card_header_style),
        Paragraph("Implementing SAML/SSO multi-tenant user authentication, database security policies, granular role scopes, and custom alert notification configurations.", card_body_style)
    ],
    [
        Paragraph("<b>Phase 3: Database Connectors</b>", card_header_style),
        Paragraph("Developing native enterprise connectors to link VendorSentinel to commercial data platforms like Snowflake, PostgreSQL, BigQuery, and Salesforce APIs.", card_body_style)
    ],
    [
        Paragraph("<b>Phase 4: AI Governance</b>", card_header_style),
        Paragraph("Integrating dedicated AI agent security firewalls (e.g. Lobster Trap middleware) for complete cryptographic logging of prompts and audit compliance trails.", card_body_style)
    ]
]
t_road = Table(roadmap_data, colWidths=[2.8 * inch, 7.2 * inch])
t_road.setStyle(TableStyle([
    ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ('PADDING', (0,0), (-1,-1), 10),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('BACKGROUND', (0,0), (0,-1), CARD_BG),
]))
story.append(t_road)
story.append(PageBreak())

# =========================================================================
# SLIDE 13: The Complete Technical Stack
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("The Complete Technical Stack", slide_header_style))
story.append(Paragraph("Robust, enterprise-ready open source frameworks and cloud integration layers.", slide_subheader_style))

tech_data = [
    [
        Paragraph("🎨 <b>Visual Frontend</b>", card_header_style),
        Paragraph("• **Framework**: React 19 component architecture, built with lightning-fast Vite.<br/>• **CSS Engine**: Custom vanilla CSS library coded for a premium 'Bookish' dark theme.<br/>• **Icons System**: Lucide React high-resolution vector graphics library.", card_body_style)
    ],
    [
        Paragraph("🚀 <b>Asynchronous Backend</b>", card_header_style),
        Paragraph("• **Language**: Python 3.11 for core intelligence workflows.<br/>• **Web Server**: FastAPI async server framework served via Uvicorn containers.<br/>• **Database**: SQLite with aiosqlite for safe, WAL-configured local transactional records.", card_body_style)
    ],
    [
        Paragraph("📡 <b>Scraping & AI Pipeline</b>", card_header_style),
        Paragraph("• **Collectors**: SERP API (Google), Web Unlocker (Pastebin), Scraper API (LinkedIn), and Scraping Browser (Playwright CDP).<br/>• **AI Core**: AI/ML API (GPT-4o-mini) for automated risk scoring and playbook synthesis.", card_body_style)
    ],
    [
        Paragraph("🔧 <b>Deployment & Lifecycle</b>", card_header_style),
        Paragraph("• **Frontend Hosting**: Vercel cloud network (linked to GitHub commits auto-rebuild).<br/>• **Backend Deployment**: Render cloud services running stable virtual environments.<br/>• **Secret Protection**: Dotenv environment parameters (.env.example).", card_body_style)
    ]
]
t_tech = Table(tech_data, colWidths=[5.0 * inch, 5.0 * inch])
t_tech.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
    ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
    ('PADDING', (0,0), (-1,-1), 12),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
]))
story.append(t_tech)
story.append(PageBreak())

# =========================================================================
# SLIDE 14: Interactive Demonstration Guide
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("Interactive Demonstration Guide", slide_header_style))
story.append(Paragraph("Step-by-step walkthrough to test every core platform module live.", slide_subheader_style))

demo_steps = [
    [
        Paragraph("<b>Step 1: Open Vercel App</b>", card_header_style),
        Paragraph("Open your live frontend link [https://vendor-sentinel.vercel.app](https://vendor-sentinel.vercel.app). Click **`Enter Security Dashboard →`** to bypass the welcome gate.", card_body_style)
    ],
    [
        Paragraph("<b>Step 2: Onboard Figma (Low Risk)</b>", card_header_style),
        Paragraph("Go to `/vendors`, click **`+ Add Vendor`**, and onboard `Figma, Inc.` (domain: `figma.com`) with `Low` sensitivity. Scanners verify clean SOC 2 compliance, scoring **2.0 Low Risk**.", card_body_style)
    ],
    [
        Paragraph("<b>Step 3: Onboard Auth0 (Critical)</b>", card_header_style),
        Paragraph("Onboard `Auth0 by Okta` (domain: `auth0.com`) with `Critical` sensitivity. Key leak queries trigger warnings, and the AI Engine generates a **8.0 Critical Risk** rating.", card_body_style)
    ],
    [
        Paragraph("<b>Step 4: Audit Scan Center</b>", card_header_style),
        Paragraph("Navigate to `/scan`. Verify that the golden spinning radar is fully operational, click **`Trigger System-Wide Scan`**, and watch background audits poll live to completed states.", card_body_style)
    ],
    [
        Paragraph("<b>Step 5: Verify Node Health</b>", card_header_style),
        Paragraph("Go to `/settings`. Confirm the golden threshold slider operates correctly, and see all **Bright Data Nodes** marked with pulsing green active indicators.", card_body_style)
    ]
]
t_demo = Table(demo_steps, colWidths=[2.8 * inch, 7.2 * inch])
t_demo.setStyle(TableStyle([
    ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ('PADDING', (0,0), (-1,-1), 8),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('BACKGROUND', (0,0), (0,-1), CARD_BG),
]))
story.append(t_demo)
story.append(PageBreak())

# =========================================================================
# SLIDE 15: VendorSentinel: Security with Certainty
# =========================================================================
story.append(Spacer(1, 1.2 * inch))
story.append(Paragraph("VendorSentinel: Security with Certainty", ParagraphStyle('FinalTitle', parent=title_style, fontSize=28, leading=34)))
story.append(Paragraph("Redefining how enterprises validate, reconcile, and monitor third-party cybersecurity postures.", ParagraphStyle('FinalSub', parent=subtitle_style, fontSize=14, leading=20)))
story.append(Spacer(1, 0.4 * inch))

col_summary = [
    [
        Paragraph("<b>🚀 Always-On Sweeping</b><br/>Continuous 6-hour sweeps across paste boards, search engines, compliance blogs, and talent listings instead of stale PDF checklists.", card_body_style),
        Paragraph("<b>🛡️ Deep Bright Data Integration</b><br/>Defeats bot blocks and CAPTCHAs natively using SERP API, Web Unlocker, Web Scraper, and headless Headless Scraping Browser CDP.", card_body_style),
        Paragraph("<b>🤖 Evidence-Backed AI Playbooks</b><br/>Generates clean risk grades (1.0-10.0), detailed structural justifications, and custom mitigation playbooks under a robust offline rule-based fallback framework.", card_body_style)
    ]
]
t_sum = Table(col_summary, colWidths=[3.2 * inch, 3.2 * inch, 3.2 * inch])
t_sum.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
    ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
    ('PADDING', (0,0), (-1,-1), 16),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
]))
story.append(t_sum)
story.append(Spacer(1, 0.4 * inch))
story.append(Paragraph("“VendorSentinel doesn't just scan vendors — it secures the supply chain.”", ParagraphStyle('Quote', parent=styles['Normal'], fontName='Times-Italic', fontSize=12, leading=16, textColor=GOLD_ACCENT, alignment=1)))

# ── Build Document ────────────────────────────────────────────────
doc.build(story, canvasmaker=NumberedCanvas)
print("PDF Presentation generated successfully!")
