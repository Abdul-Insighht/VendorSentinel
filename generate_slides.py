import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

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

# ── Color Palette (Bookish / Light Editorial Theme) ──────────────
BG_COLOR = colors.HexColor("#f5f2eb")      # Soft light cream background
CARD_BG = colors.HexColor("#faf8f2")       # Lighter ivory for cards
NAVY_BLUE = colors.HexColor("#0d2c54")     # Deep navy blue for headings
GOLD_ACCENT = colors.HexColor("#a9843d")   # Ochre / Golden brown highlight
SOFT_BLACK = colors.HexColor("#2a2a2a")    # Primary body text color
MUTED_TEXT = colors.HexColor("#6e6c64")    # Secondary/muted body text color
BORDER_COLOR = colors.HexColor("#dcd8cd")  # Light elegant border
CRIMSON = colors.HexColor("#a83232")       # Crimson red for critical highlights

# ── Page Background Canvas Helper ─────────────────────────────────
# We define a custom canvas class to draw backgrounds dynamically on each page
from reportlab.pdfgen import canvas
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
        
        # 1. Fill entire slide background with light cream color
        self.setFillColor(BG_COLOR)
        self.rect(0, 0, 11 * inch, 8.5 * inch, fill=True, stroke=False)
        
        # 2. Page 1: draw vertical golden bar on left edge
        if self._pageNumber == 1:
            self.setFillColor(GOLD_ACCENT)
            self.rect(0, 0, 0.3 * inch, 8.5 * inch, fill=True, stroke=False)
            
        # 3. Subsequent slides: draw elegant headers and footers
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
            
            # Slide Footer
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

title_style = ParagraphStyle(
    'TitleStyle',
    parent=styles['Normal'],
    fontName='Times-Bold',
    fontSize=36,
    leading=42,
    textColor=NAVY_BLUE,
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
    textColor=SOFT_BLACK,
    alignment=1,
    spaceAfter=5
)

meta_style = ParagraphStyle(
    'MetaStyle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=9,
    leading=14,
    textColor=NAVY_BLUE,
    alignment=1
)

slide_header_style = ParagraphStyle(
    'SlideHeaderStyle',
    parent=styles['Normal'],
    fontName='Times-Bold',
    fontSize=22,
    leading=26,
    textColor=NAVY_BLUE,
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
    fontSize=9,
    leading=13.5,
    textColor=SOFT_BLACK
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
    fontSize=12,
    leading=16,
    textColor=GOLD_ACCENT,
    spaceAfter=6
)

card_body_style = ParagraphStyle(
    'CardBodyStyle',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=8.5,
    leading=12.5,
    textColor=SOFT_BLACK
)

table_header_style = ParagraphStyle(
    'TableHeaderStyle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=9,
    textColor=colors.white,
    alignment=0
)

# ── Story Construction ────────────────────────────────────────────
story = []

# =========================================================================
# SLIDE 1: Title Slide
# =========================================================================
story.append(Spacer(1, 1.8 * inch))
story.append(Paragraph("VendorSentinel", title_style))
story.append(Paragraph("Always-On AI-Powered Third-Party Vendor Risk Intelligence", subtitle_style))
story.append(Spacer(1, 0.4 * inch))
story.append(Paragraph("🛡️ Track 3: Web Data & Compliance  |  Bright Data Hackathon 2026", meta_style))
story.append(Spacer(1, 0.2 * inch))
story.append(Paragraph("Created & Deployed by:  Hafiz Abdul Rehman", author_style))
story.append(Paragraph("Live UI:  https://vendor-sentinel.vercel.app/  &bull;  Backend API: https://vendorsentinel.onrender.com", author_style))
story.append(PageBreak())

# =========================================================================
# SLIDE 2: The Enterprise Data Quality & Vendor Risk Crisis
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("The Third-Party Vendor Risk Crisis", slide_header_style))
story.append(Paragraph("Outdated assessment models expose modern enterprises to silent, catastrophic supply-chain threats.", slide_subheader_style))

# Left stats column block
stats_content = [
    [Paragraph("<b>$4.5M</b>", ParagraphStyle('HugeVal', parent=styles['Normal'], fontName='Times-Bold', fontSize=36, leading=40, textColor=colors.white, alignment=1))],
    [Paragraph("<b>Average Cost of a Breach</b><br/>IBM Cost of a Data Breach Report", ParagraphStyle('StatSub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=13, textColor=colors.white, alignment=1))],
    [Spacer(1, 10)],
    [Paragraph("🚨 <b>Verifiable Case Studies</b><br/>In 2021, the SolarWinds supply chain attack compromised over 18,000 organizations including the US Treasury. Their database credentials lay exposed on public GitHub as 'solarwinds123' for thirteen months completely unnoticed. In 2024, the Snowflake breach exposed data from 165 major enterprises (including AT&T, Ticketmaster, and Santander Bank). The fault sat entirely at the vendor level, but the financial damage landed squarely on their customers.", ParagraphStyle('StatDesc', parent=body_style, fontSize=8.5, leading=12.5, textColor=SOFT_BLACK))]
]
t_stats = Table(stats_content, colWidths=[3.3 * inch])
t_stats.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,1), CRIMSON),
    ('BACKGROUND', (0,3), (-1,3), CARD_BG),
    ('BOX', (0,3), (-1,3), 1, BORDER_COLOR),
    ('PADDING', (0,0), (-1,1), 12),
    ('PADDING', (0,2), (-1,2), 0),
    ('PADDING', (0,3), (-1,3), 12),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
]))

# Right content card
col_data = [
    [
        [Paragraph("The Vulnerability Problem", card_header_style),
         Paragraph("Every modern enterprise outsources critical parts of its infrastructure to third-party vendors. Your payment processors hold credit card databases, cloud providers house sensitive customer records, and authentication providers govern corporate login directories. These vendors sit at the core of your security posture, yet security administrators possess zero real-time visibility into their daily operational health.", card_body_style)]
    ],
    [Spacer(1, 6)],
    [
        [Paragraph("The Signal Paradox", card_header_style),
         Paragraph("Major supply-chain breaches never happen without warning. Factual signals are always public beforehand—scattered across paste boards, code repositories, and job vacancies. SolarWinds had its public credentials leaked, Snowflake's customer session keys circulated on forums weeks prior, and corporate hiring spikes occurred. Nobody was systematically watching.", card_body_style)]
    ],
    [Spacer(1, 6)],
    [
        [Paragraph("The Obsolete Checklists", card_header_style),
         Paragraph("The current standard security solution is a self-attested PDF questionnaire sent once a year. The vendor simply checks 'Yes, we are secure' and files it away. In 2026, this static method is completely inadequate to detect live threats, configuration gaps, and active leakage cycles.", card_body_style)]
    ]
]
t_col = Table(col_data, colWidths=[6.3 * inch])
t_col.setStyle(TableStyle([
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ('TOPPADDING', (0,0), (-1,-1), 0),
]))

# Combined layout
layout_table = Table([[t_stats, t_col]], colWidths=[3.5 * inch, 6.5 * inch])
layout_table.setStyle(TableStyle([
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('LEFTPADDING', (1,0), (1,0), 16),
]))
story.append(layout_table)
story.append(PageBreak())

# =========================================================================
# SLIDE 3: The Technical Barriers
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("The Technical Barriers to Vendor Audits", slide_header_style))
story.append(Paragraph("Why manual security monitoring and standard scripts fail to protect corporate ecosystems.", slide_subheader_style))

barrier_data = [
    [
        Paragraph("<b>CAPTCAs & IP Bans</b>", card_header_style),
        Paragraph("Public sharing platforms like Pastebin and GitHub actively protect their data from scrapers. Standard automated scrapers are instantly blocked by CAPTCHAs, dynamic browser challenges, and IP address bans.", card_body_style)
    ],
    [
        Paragraph("<b>Rate Limits & Scraper Blocks</b>", card_header_style),
        Paragraph("Hiring platforms like LinkedIn enforce strict rate limits and dynamically check requests for bot behavior, making it technically impossible for a standard script to monitor even a small portfolio of vendors.", card_body_style)
    ],
    [
        Paragraph("<b>JavaScript Rendering Walls</b>", card_header_style),
        Paragraph("Morale review platforms and trust blogs utilize heavy JavaScript frameworks that render data dynamically. Standard HTTP clients only fetch static raw HTML, completely missing the actual content text.", card_body_style)
    ],
    [
        Paragraph("<b>Scale & Bandwidth Overload</b>", card_header_style),
        Paragraph("Even if a security team attempted manual daily check loops across 50 vendors on these platforms, the sheer operational overhead and time required would completely overwhelm their analytical bandwidth.", card_body_style)
    ]
]
t_bar = Table(barrier_data, colWidths=[2.8 * inch, 7.2 * inch])
t_bar.setStyle(TableStyle([
    ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ('PADDING', (0,0), (-1,-1), 10),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('BACKGROUND', (0,0), (0,-1), CARD_BG),
]))
story.append(t_bar)
story.append(PageBreak())

# =========================================================================
# SLIDE 4: The Solution: Bright Data Powered Pipeline
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("The Solution: Bright Data Powered Pipeline", slide_header_style))
story.append(Paragraph("Defeating anti-bot shields to construct an automated third-party risk intelligence pipeline.", slide_subheader_style))

sol_col1 = [
    [Paragraph("<b>Bright Data Infrastructure</b>", card_header_style)],
    [Paragraph("VendorSentinel completely solves these technical barriers by leveraging Bright Data's global proxy and browser automation network. Bright Data provides the only enterprise infrastructure capable of reliably bypassing bot protections, resolving CAPTCHAs, and fetching JavaScript-heavy pages at scale. The system runs fully autonomously—checking every registered vendor across 4 signal dimensions every 6 hours, storing findings, and feeding them to our AI agent.", card_body_style)]
]
t_sc1 = Table(sol_col1, colWidths=[4.7 * inch])
t_sc1.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), CARD_BG), ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 16), ('VALIGN', (0,0), (-1,-1), 'TOP')]))

sol_col2 = [
    [Paragraph("<b>The Four Signal Dimensions</b>", card_header_style)],
    [Paragraph("• **Signal One (News & Media)**: Utilizes Bright Data SERP API to index search results for published breaches, regulatory fines, and GDPR class action lawsuits.<br/>• **Signal Two (Exposed Leaks)**: Employs Web Unlocker to search public code repos and Pastebin for domain password/API key exposures.<br/>• **Signal Three (Hiring Spikes)**: Integrates Web Scraper API to track security recruitment spikes on LinkedIn.<br/>• **Signal Four (Reputation checks)**: Runs Scraping Browser CDP to crawl posture patches and employee reviews.", card_body_style)]
]
t_sc2 = Table(sol_col2, colWidths=[4.7 * inch])
t_sc2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), CARD_BG), ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR), ('PADDING', (0,0), (-1,-1), 16), ('VALIGN', (0,0), (-1,-1), 'TOP')]))

story.append(Table([[t_sc1, t_sc2]], colWidths=[5.0 * inch, 5.0 * inch], style=[('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0)]))
story.append(PageBreak())

# =========================================================================
# SLIDE 5: Signal One — News & Public Media Monitoring
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("Signal One — News & Public Media Monitoring", slide_header_style))
story.append(Paragraph("Indexing global search engine queries in real-time for security-relevant public disclosures.", slide_subheader_style))

# Left stats column block
stats_content_5 = [
    [Paragraph("<b>SERP API</b>", ParagraphStyle('Val5', parent=styles['Normal'], fontName='Times-Bold', fontSize=28, leading=32, textColor=GOLD_ACCENT, alignment=1))],
    [Paragraph("<b>Real-Time Search Results</b>", ParagraphStyle('Label5', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=MUTED_TEXT, alignment=1))],
    [Spacer(1, 15)],
    [Paragraph("🔑 <b>Indexed Keywords</b>", card_header_style)],
    [Paragraph("• 'data breach'<br/>• 'ransomware attack'<br/>• 'security incident'<br/>• 'regulatory fine'<br/>• 'GDPR violation'<br/>• 'class action'", ParagraphStyle('Bullet5', parent=body_style, leading=15))]
]
t_stats_5 = Table(stats_content_5, colWidths=[3.2 * inch])
t_stats_5.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
    ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
    ('PADDING', (0,0), (-1,-1), 16),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
]))

# Right content card
col_data_5 = [
    [
        [Paragraph("Operational Framework", card_header_style),
         Paragraph("The first layer of defense uses Bright Data's **SERP API** to query Google, Bing, and major search engines dynamically for each onboarded vendor. By combining the vendor's company name with threat keywords (GDPR violation, ransomware, data leak, lawsuit), it parses organic search items in real-time and normalizes them into structured JSON arrays containing title, publish date, snippet, and source link.", card_body_style)]
    ],
    [Spacer(1, 6)],
    [
        [Paragraph("Impact & Severity Classification", card_header_style),
         Paragraph("This layer catches anything that has already reached the public domain. It verifies headlines, publication dates, and legal source URLs. The system automatically classifies threat severity based on keyword categories—for instance, 'ransomware' or 'cyberattack' matches trigger critical ratings, while 'patch' or 'vulnerability' issues trigger warning flags, providing a complete baseline check.", card_body_style)]
    ]
]
t_col_5 = Table(col_data_5, colWidths=[6.3 * inch])
t_col_5.setStyle(TableStyle([
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ('TOPPADDING', (0,0), (-1,-1), 0),
]))

# Combined layout
layout_table_5 = Table([[t_stats_5, t_col_5]], colWidths=[3.4 * inch, 6.6 * inch])
layout_table_5.setStyle(TableStyle([
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('LEFTPADDING', (1,0), (1,0), 20),
]))
story.append(layout_table_5)
story.append(PageBreak())

# =========================================================================
# SLIDE 6: Signal Two — Credential Leak Detection
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("Signal Two — Credential Leak Detection", slide_header_style))
story.append(Paragraph("Scraping public paste boards and public GitHub code commit endpoints for exposed data.", slide_subheader_style))

leak_data = [
    [
        Paragraph("<b>Bypassing Anti-Bot Blocks</b>", card_header_style),
        Paragraph("Public repositories and paste boards aggressively block automated crawler requests with CAPTCHAs, IP bans, and browser fingerprinting. Bright Data **Web Unlocker** proxy handles all this transparently: it automatically rotates residential IP addresses, solves CAPTCHAs, and handles challenges to return full raw HTML text.", card_body_style)
    ],
    [
        Paragraph("<b>Target Search Query</b>", card_header_style),
        Paragraph("VendorSentinel queries these secure sites searching for vendor-specific leak patterns. It combines the vendor's primary domain name with keywords like `password`, `api_key`, `token`, `secret`, and private key blocks (`-----BEGIN RSA PRIVATE KEY-----`).", card_body_style)
    ],
    [
        Paragraph("<b>Critical Alerts & Verification</b>", card_header_style),
        Paragraph("If any search results match these patterns alongside a vendor's domain name, it indicates direct exposure of active authentication secrets and is flagged as a critical-priority risk. This provides a powerful, proactive warning of potential breach conditions.", card_body_style)
    ],
    [
        Paragraph("<b>Ethical & Legal Compliance</b>", card_header_style),
        Paragraph("This scanning process is entirely legal and compliant. Every piece of code or text scanned is already publicly visible on the open web. The system simply automates in real-time what a manual security analyst would do—catching exposures in days instead of months.", card_body_style)
    ]
]
t_leak = Table(leak_data, colWidths=[2.8 * inch, 7.2 * inch])
t_leak.setStyle(TableStyle([
    ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ('PADDING', (0,0), (-1,-1), 10),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('BACKGROUND', (0,0), (0,-1), CARD_BG),
]))
story.append(t_leak)
story.append(PageBreak())

# =========================================================================
# SLIDE 7: Signal Three — Hiring Distress Detection
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("Signal Three — Hiring Distress Detection", slide_header_style))
story.append(Paragraph("Tracking LinkedIn security recruitment metrics to uncover silent internal crisis periods.", slide_subheader_style))

# Left stats column block
stats_content_7 = [
    [Paragraph("<b>Web Scraper API</b>", ParagraphStyle('Val7', parent=styles['Normal'], fontName='Times-Bold', fontSize=28, leading=32, textColor=GOLD_ACCENT, alignment=1))],
    [Paragraph("<b>LinkedIn Job Board Aggregator</b>", ParagraphStyle('Label7', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=MUTED_TEXT, alignment=1))],
    [Spacer(1, 15)],
    [Paragraph("🚀 <b>Tracked Roles</b>", card_header_style)],
    [Paragraph("• 'CISO' / Security Director<br/>• Incident Response Engineer<br/>• SOC Security Analyst<br/>• Threat Intelligence Analyst<br/>• Application Security Architect", ParagraphStyle('Bullet7', parent=body_style, leading=15))]
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
        [Paragraph("LinkedIn Datasets Scrapes", card_header_style),
         Paragraph("When an enterprise is quietly dealing with a serious security failure or a breach, one of the most reliable early warning indicators is a sudden, urgent spike in security recruitment. Bright Data's **Web Scraper API** provides robust, pre-built scrapers for LinkedIn company pages. We query the vendor's job board to fetch recent job listings, avoiding custom scrapers.", card_body_style)]
    ],
    [Spacer(1, 6)],
    [
        [Paragraph("Hiring Spike Analytics", card_header_style),
         Paragraph("The system filters job listings for security-specific roles and calculates the baseline volume against the previous 30 days. An abnormal recruitment spike (e.g. 5 vacancies last month vs 15 vacancies now) is flagged. This represents an active attempt to rebuild threat mitigation teams, providing a clear signal of security concerns weeks before any public news.", card_body_style)]
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
# SLIDE 8: Signal Four — Vendor Health & Reputation
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("Signal Four — Vendor Health & Reputation", slide_header_style))
story.append(Paragraph("Crawling Glassdoor morale ratings and corporate trust blogs via Playwright CDP.", slide_subheader_style))

reput_data = [
    [
        Paragraph("<b>Playwright CDP Connection</b>", card_header_style),
        Paragraph("The fourth layer utilizes Bright Data's **Scraping Browser**, a full Playwright-based browser that natively handles JS-heavy pages, dynamically rendering content and transparently handling anti-bot scripts.", card_body_style)
    ],
    [
        Paragraph("<b>Glassdoor Employee Reviews</b>", card_header_style),
        Paragraph("We crawl the vendor's Glassdoor reviews looking for language clusters indicating organizational chaos. We filter for terms like 'mass layoffs', 'leadership departures', and 'restructuring' which correlate with corporate distress.", card_body_style)
    ],
    [
        Paragraph("<b>Corporate Security Blogs</b>", card_header_style),
        Paragraph("The system crawls the vendor's own security and engineering blogs. A sudden, unusual increase in security advisory posts or defensive updates suggests they are actively remediating an unpublicized threat.", card_body_style)
    ],
    [
        Paragraph("<b>Morale & Posture Analysis</b>", card_header_style),
        Paragraph("None of these signals is conclusive on its own. But when a vendor shows negative reviews, an unusual security hiring surge, and a flurry of defensive blog posts in a 30-day window, the combination creates a clear warning pattern.", card_body_style)
    ]
]
t_reput = Table(reput_data, colWidths=[2.8 * inch, 7.2 * inch])
t_reput.setStyle(TableStyle([
    ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ('PADDING', (0,0), (-1,-1), 10),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('BACKGROUND', (0,0), (0,-1), CARD_BG),
]))
story.append(t_reput)
story.append(PageBreak())

# =========================================================================
# SLIDE 9: The AI Risk Scoring Engine
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("The AI Risk Scoring Engine", slide_header_style))
story.append(Paragraph("Harnessing Claude via MCP to synthesize raw web signals into evidence-backed audits.", slide_subheader_style))

# Left stats column block
stats_content_9 = [
    [Paragraph("<b>GPT-4o-mini</b>", ParagraphStyle('Val9', parent=styles['Normal'], fontName='Times-Bold', fontSize=28, leading=32, textColor=GOLD_ACCENT, alignment=1))],
    [Paragraph("<b>Generative AI Scoring Engine</b>", ParagraphStyle('Label9', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=MUTED_TEXT, alignment=1))],
    [Spacer(1, 15)],
    [Paragraph("🧠 <b>AI Output Elements</b>", card_header_style)],
    [Paragraph("• **Risk Score (1-10)**<br/>• **Risk Level (Low-Critical)**<br/>• **Detailed Reasoning Logs**<br/>• **Mitigation Playbooks**", ParagraphStyle('Bullet9', parent=body_style, leading=15))]
]
t_stats_9 = Table(stats_content_9, colWidths=[3.2 * inch])
t_stats_9.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
    ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
    ('PADDING', (0,0), (-1,-1), 16),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
]))

# Right content card
col_data_9 = [
    [
        [Paragraph("Multi-Source AI Synthesis", card_header_style),
         Paragraph("After all 4 signal vectors are collected, they are normalized and passed to the **AI Scoring Engine** (GPT-4o-mini). Instead of simple rule-based metrics, the AI reasons over the combined signals, weighs their severities, and delivers a structured, evidence-backed report. It provides a numeric risk score (1.0-10.0), a plain-English explanation, and a step-by-step mitigation playbook for the security team.", card_body_style)]
    ],
    [Spacer(1, 6)],
    [
        [Paragraph("Example AI Output Report", card_header_style),
         Paragraph("*'This vendor scores 8.2 out of 10. Three signals are contributing to this score. First, a string matching the vendor domain combined with the word \"api_key\" was found on Pastebin on May 22nd. Second, the vendor has posted eleven security job openings in the past two weeks, a 450% spike. Third, fourteen Glassdoor reviews contain language related to sudden leadership changes. Recommended action: contact relationship manager immediately andBegin qualifying an alternative vendor.'*", card_body_style)]
    ]
]
t_col_9 = Table(col_data_9, colWidths=[6.3 * inch])
t_col_9.setStyle(TableStyle([
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ('TOPPADDING', (0,0), (-1,-1), 0),
]))

# Combined layout
layout_table_9 = Table([[t_stats_9, t_col_9]], colWidths=[3.4 * inch, 6.6 * inch])
layout_table_9.setStyle(TableStyle([
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('LEFTPADDING', (1,0), (1,0), 20),
]))
story.append(layout_table_9)
story.append(PageBreak())

# =========================================================================
# SLIDE 10: Strategic Business Value & Market Scope
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("Strategic Business Value & Market Scope", slide_header_style))
story.append(Paragraph("Enterprise market potential, capital risk mitigation, and SaaS monetization channels.", slide_subheader_style))

# Grid Table of Business value
business_grid = [
    [
        Paragraph("<b>Monetization Channel</b>", table_header_style),
        Paragraph("<b>Operational Implementation</b>", table_header_style),
        Paragraph("<b>Commercial Enterprise Value</b>", table_header_style)
    ],
    [
        Paragraph("<b>SaaS Subscription</b>", body_bold_style),
        Paragraph("Monthly tier licenses based on active vendor counts and database scan intervals.", body_style),
        Paragraph("Enables predictable annual recurring revenue (ARR) from small to enterprise clients.", body_style)
    ],
    [
        Paragraph("<b>Secure BI APIs</b>", body_bold_style),
        Paragraph("Dedicated endpoints to integrate risk scores into tools like Power BI or ServiceNow.", body_style),
        Paragraph("Drives deep ecosystem integration, increasing product stickiness and enterprise scaling.", body_style)
    ],
    [
        Paragraph("<b>Audit Report Exports</b>", body_bold_style),
        Paragraph("Cryptographically signed compliance reports ready for external board audits.", body_style),
        Paragraph("Provides transactional revenue channels, capturing extra value from audit cycles.", body_style)
    ]
]
t_biz = Table(business_grid, colWidths=[2.2 * inch, 3.8 * inch, 4.0 * inch])
t_biz.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), NAVY_BLUE),
    ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ('PADDING', (0,0), (-1,-1), 10),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
]))
story.append(t_biz)
story.append(PageBreak())

# =========================================================================
# SLIDE 11: Originality & Unique Selling Proposition (USP)
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("Originality & Unique Selling Proposition", slide_header_style))
story.append(Paragraph("Comparing VendorSentinel to legacy checklists and static security database products.", slide_subheader_style))

compare_data = [
    [
        Paragraph("<b>Dynamic Web Crawling</b>", card_header_style),
        Paragraph("Conventional database products (e.g. BitSight, SecurityScorecard costing $50k-$200k/year) rely on static, historical registries that fail to perform real-time monitoring. VendorSentinel runs continuous 6-hour sweeps across the live web.", card_body_style)
    ],
    [
        Paragraph("<b>Deep Anti-Bot Bypassing</b>", card_header_style),
        Paragraph("Standard compliance tools cannot reliably bypass anti-bot shields. VendorSentinel harnesses Bright Data's global proxy and automation networks to defeat CAPTCHAs, rate limits, and JS rendering blocks.", card_body_style)
    ],
    [
        Paragraph("<b>Factual AI Integrity</b>", card_header_style),
        Paragraph("Standard LLMs frequently hallucinate metrics. Our AI Scoring Engine uses structured prompts and aggregates normalized evidence logs, creating audit trails with full facts provenance.", card_body_style)
    ],
    [
        Paragraph("<b>Evidence Playbooks</b>", card_header_style),
        Paragraph("Instead of generic dashboards, the system delivers structured reasoning summaries and custom-compiled playbooks indicating the exact mitigation steps required.", card_body_style)
    ]
]
t_comp = Table(compare_data, colWidths=[2.8 * inch, 7.2 * inch])
t_comp.setStyle(TableStyle([
    ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ('PADDING', (0,0), (-1,-1), 10),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('BACKGROUND', (0,0), (0,-1), CARD_BG),
]))
story.append(t_comp)
story.append(PageBreak())

# =========================================================================
# SLIDE 12: Strategic Execution Roadmap
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("Strategic Execution Roadmap", slide_header_style))
story.append(Paragraph("A 4-phase scaling plan from current production MVP to full enterprise integrations.", slide_subheader_style))

roadmap_table = [
    [
        Paragraph("<b>Phase</b>", table_header_style),
        Paragraph("<b>Execution Targets</b>", table_header_style),
        Paragraph("<b>Technical Milestones</b>", table_header_style)
    ],
    [
        Paragraph("<b>Phase 1: Production MVP</b>", body_bold_style),
        Paragraph("Complete implementation of 4 Bright Data collectors + FastAPI async backend + React 19 UI dashboard.", body_style),
        Paragraph("Fully deployed on Vercel/Render, dynamic radar, node status health checker, and SQLite WAL database.", body_style)
    ],
    [
        Paragraph("<b>Phase 2: SSO & Granular Auth</b>", body_bold_style),
        Paragraph("granular security boundaries, multi-tenant directory authentication, and customizable alert rules.", body_style),
        Paragraph("SAML/OAuth SSO integration, multi-tenant databases partition, and Slack/Teams webhooks integration.", body_style)
    ],
    [
        Paragraph("<b>Phase 3: DB Connectors</b>", body_bold_style),
        Paragraph("Developing native enterprise connectors to pull vendor lists automatically from cloud sources.", body_style),
        Paragraph("Connectors to Snowflake, BigQuery, and Salesforce APIs to maintain dynamic, live vendor pipelines.", body_style)
    ],
    [
        Paragraph("<b>Phase 4: AI Governance</b>", body_bold_style),
        Paragraph("Granular AI model governance and cryptographic audit trail logging.", body_style),
        Paragraph("Integration with dedicated prompt firewalls (e.g. Lobster Trap) for cryptographic audit trails.", body_style)
    ]
]
t_road = Table(roadmap_table, colWidths=[2.2 * inch, 3.8 * inch, 4.0 * inch])
t_road.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), NAVY_BLUE),
    ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ('PADDING', (0,0), (-1,-1), 10),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
]))
story.append(t_road)
story.append(PageBreak())

# =========================================================================
# SLIDE 13: The Complete Technical Stack
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("The Complete Technical Stack", slide_header_style))
story.append(Paragraph("Enterprise-ready open source frameworks and cloud integration layers.", slide_subheader_style))

# Left stats column block
stats_content_13 = [
    [Paragraph("<b>Language & Hosting</b>", card_header_style)],
    [Paragraph("• Language: Python 3.11<br/>• Server: FastAPI Async served by Uvicorn<br/>• DB: SQLite WAL (aiosqlite)<br/>• Host: Render.com Container", ParagraphStyle('TechL', parent=body_style, leading=16))],
    [Spacer(1, 15)],
    [Paragraph("🎨 <b>Frontend Engine</b>", card_header_style)],
    [Paragraph("• Framework: React 19<br/>• Styling: Custom Vanilla CSS<br/>• Bundler: Vite<br/>• Host: Vercel Cloud Network", ParagraphStyle('TechR', parent=body_style, leading=16))]
]
t_stats_13 = Table(stats_content_13, colWidths=[3.2 * inch])
t_stats_13.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), CARD_BG),
    ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
    ('PADDING', (0,0), (-1,-1), 16),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
]))

# Right content card
col_data_13 = [
    [
        [Paragraph("Bright Data Pipeline Layer", card_header_style),
         Paragraph("• **SERP API**: Queries Google and Bing search engine results to index public media news.<br/>• **Web Unlocker**: Bypasses bot protections and CAPTCHAs to scan Pastebin.<br/>• **Web Scraper API**: Pulls structured LinkedIn job board listings without custom code.<br/>• **Scraping Browser**: Headless Playwright Chromium CDP sessions to audit compliance blogs.", card_body_style)]
    ],
    [Spacer(1, 6)],
    [
        [Paragraph("AI & Security Governance", card_header_style),
         Paragraph("• **AI/ML API**: GPT-4o-mini chat completion endpoints to generate structured assessments.<br/>• **Environment Protection**: Dotenv environment variables (.env.example) safeguarding API keys.<br/>• **Windows Loop Policy**: Custom Proactor loop policy handling win32 subprocess limitations.", card_body_style)]
    ]
]
t_col_13 = Table(col_data_13, colWidths=[6.3 * inch])
t_col_13.setStyle(TableStyle([
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ('TOPPADDING', (0,0), (-1,-1), 0),
]))

# Combined layout
layout_table_13 = Table([[t_stats_13, t_col_13]], colWidths=[3.4 * inch, 6.6 * inch])
layout_table_13.setStyle(TableStyle([
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('LEFTPADDING', (1,0), (1,0), 20),
]))
story.append(layout_table_13)
story.append(PageBreak())

# =========================================================================
# SLIDE 14: Interactive Demonstration Guide
# =========================================================================
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("Interactive Demonstration Guide", slide_header_style))
story.append(Paragraph("Step-by-step walkthrough to test every platform module live.", slide_subheader_style))

demo_steps = [
    [
        Paragraph("<b>1. Open Welcome Gate</b>", card_header_style),
        Paragraph("Navigate to your live URL [https://vendor-sentinel.vercel.app](https://vendor-sentinel.vercel.app). Read the problem brief, and click **`Enter Security Dashboard →`** to bypass the gate.", card_body_style)
    ],
    [
        Paragraph("<b>2. Onboard Figma (Low Risk)</b>", card_header_style),
        Paragraph("Go to `/vendors`, click **`+ Add Vendor`**, and onboard `Figma, Inc.` (domain: `figma.com`) with `Low` sensitivity. Scanners verify clean compliance audit playbooks, scoring **2.0 Low Risk**.", card_body_style)
    ],
    [
        Paragraph("<b>3. Onboard Auth0 (Critical)</b>", card_header_style),
        Paragraph("Onboard `Auth0 by Okta` (domain: `auth0.com`) with `Critical` sensitivity. Exposed credential scans match warnings on paste boards, and the AI Engine generates a **8.0 Critical Risk** rating.", card_body_style)
    ],
    [
        Paragraph("<b>4. Run Threat sweeps</b>", card_header_style),
        Paragraph("Navigate to `/scan`. Verify the spinning golden radar sweeper, concentric active wave rings, and pulsing threat blips. Trigger a scan and watch history records compile and poll live.", card_body_style)
    ],
    [
        Paragraph("<b>5. Verify Node Health</b>", card_header_style),
        Paragraph("Navigate to `/settings`. Verify the golden threshold slider operates correctly, and see all **Bright Data Nodes** marked with pulsing green active indicators.", card_body_style)
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
        Paragraph("<b>🛡️ Deep Bright Data Integration</b><br/>Defeats bot blocks and CAPTCHAs natively using SERP API, Web Unlocker, Web Scraper, and Scraping Browser.", card_body_style),
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
