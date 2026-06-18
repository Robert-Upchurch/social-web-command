"""
Social & Web Command — Operations Manual (PDF)
Full page-by-page, feature-by-feature reference with screenshots.
"""
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table,
    TableStyle, KeepTogether, KeepInFrame
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas as canvas_mod
from reportlab.graphics.shapes import Drawing, Rect
from PIL import Image as PILImage

# ---------- SWATCH HELPER ----------
def swatch(hex_color, size=10):
    """Small filled colored square used as an icon-replacement in tables."""
    d = Drawing(size + 2, size + 2)
    r = Rect(1, 1, size, size, rx=2, ry=2)
    r.fillColor = colors.HexColor(hex_color)
    r.strokeColor = colors.HexColor("#00000000")  # no stroke
    r.strokeWidth = 0
    d.add(r)
    return d

# ---------- PATHS ----------
ROOT = "/home/user/workspace/social-web-command"
SHOTS = os.path.join(ROOT, "manual-shots")
OUT = os.path.join(ROOT, "Social_Web_Command_Operations_Manual.pdf")

# ---------- POSEIDON BRAND COLORS ----------
C_BG       = colors.HexColor("#0b0b0d")
C_PANEL    = colors.HexColor("#141416")
C_PANEL2   = colors.HexColor("#1b1b1f")
C_LINE     = colors.HexColor("#27272a")
C_TXT      = colors.HexColor("#1c1d22")    # body text on white pages
C_MUTED    = colors.HexColor("#6b6f78")
C_ACCENT   = colors.HexColor("#dc2626")
C_ACCENTD  = colors.HexColor("#991b1b")
C_GREEN    = colors.HexColor("#16a34a")
C_AMBER    = colors.HexColor("#d97706")
C_BLUE     = colors.HexColor("#0284c7")
C_GREY     = colors.HexColor("#9aa0aa")
C_PAGEBG   = colors.HexColor("#fafafa")
C_CARDBG   = colors.HexColor("#ffffff")
C_BORDER   = colors.HexColor("#e3e5ea")

# ---------- STYLES ----------
styles = getSampleStyleSheet()

def style(name, **kw):
    base = dict(name=name, fontName="Helvetica", textColor=C_TXT, leading=14)
    base.update(kw)
    return ParagraphStyle(**base)

s_h0       = style("h0",     fontName="Helvetica-Bold", fontSize=36, leading=42, textColor=colors.white, alignment=TA_LEFT)
s_h0sub    = style("h0sub",  fontName="Helvetica",      fontSize=13, leading=18, textColor=colors.HexColor("#c2c2c2"))
s_h1       = style("h1",     fontName="Helvetica-Bold", fontSize=22, leading=28, textColor=C_ACCENT, spaceBefore=0, spaceAfter=4)
s_h1sub    = style("h1sub",  fontName="Helvetica",      fontSize=11, leading=15, textColor=C_MUTED, spaceAfter=10)
s_h2       = style("h2",     fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=C_TXT, spaceBefore=8, spaceAfter=4)
s_h3       = style("h3",     fontName="Helvetica-Bold", fontSize=10, leading=14, textColor=C_ACCENT, spaceBefore=4, spaceAfter=2)
s_body     = style("body",   fontName="Helvetica",      fontSize=9.5, leading=13.5, textColor=C_TXT, spaceAfter=4)
s_small    = style("small",  fontName="Helvetica",      fontSize=8.5, leading=12, textColor=C_MUTED)
s_caption  = style("caption",fontName="Helvetica-Oblique", fontSize=8.5, leading=11, textColor=C_MUTED, alignment=TA_CENTER, spaceBefore=4, spaceAfter=8)
s_kpilabel = style("kpilbl", fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=C_MUTED)
s_kpival   = style("kpival", fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=C_TXT)
s_toc      = style("toc",    fontName="Helvetica",      fontSize=10.5, leading=18, textColor=C_TXT)
s_tocnum   = style("tocnum", fontName="Helvetica-Bold", fontSize=10.5, leading=18, textColor=C_ACCENT)
s_pageno   = style("pageno", fontName="Helvetica",      fontSize=9, textColor=C_MUTED, alignment=TA_RIGHT)
s_ribbon   = style("ribbon", fontName="Helvetica-Bold", fontSize=8.5, textColor=colors.white, alignment=TA_CENTER)

# ---------- PAGE TEMPLATE WITH FOOTER ----------
def draw_page_frame(canv, doc):
    page = canv.getPageNumber()
    # cover & TOC handled separately — pages 1-2 get no footer
    if page <= 2:
        return
    w, h = LETTER
    # top thin red rule
    canv.setStrokeColor(C_ACCENT)
    canv.setLineWidth(2)
    canv.line(0.5*inch, h - 0.5*inch, w - 0.5*inch, h - 0.5*inch)
    # header text
    canv.setFont("Helvetica-Bold", 8.5)
    canv.setFillColor(C_ACCENT)
    canv.drawString(0.5*inch, h - 0.4*inch, "POSEIDON  ·  SOCIAL & WEB COMMAND")
    canv.setFont("Helvetica", 8.5)
    canv.setFillColor(C_MUTED)
    canv.drawRightString(w - 0.5*inch, h - 0.4*inch, "Operations Manual  ·  v0.9")
    # footer
    canv.setStrokeColor(C_BORDER)
    canv.setLineWidth(0.5)
    canv.line(0.5*inch, 0.55*inch, w - 0.5*inch, 0.55*inch)
    canv.setFont("Helvetica", 8)
    canv.setFillColor(C_MUTED)
    canv.drawString(0.5*inch, 0.4*inch, "© 2026 CTI Group Worldwide Services, Inc.  ·  Confidential")
    canv.drawRightString(w - 0.5*inch, 0.4*inch, f"Page {page}")

# ---------- HELPERS ----------
def fit_image(img_path, max_w_pts, max_h_pts):
    """Return an Image flowable scaled to fit max bounds, preserving aspect ratio."""
    pil = PILImage.open(img_path)
    iw, ih = pil.size
    ratio = min(max_w_pts / iw, max_h_pts / ih)
    return Image(img_path, width=iw * ratio, height=ih * ratio)

def section_header(title, subtitle):
    return [
        Paragraph(title, s_h1),
        Paragraph(subtitle, s_h1sub),
    ]

def bullet_list(items, style_used=None):
    style_used = style_used or s_body
    out = []
    for it in items:
        out.append(Paragraph(f"<b style='color:#dc2626'>▸</b>&nbsp;&nbsp;{it}", style_used))
    return out

def kv_table(rows, col_widths=None):
    col_widths = col_widths or [1.6*inch, 5.0*inch]
    # Wrap raw strings in Paragraph so long values wrap within the column.
    wrapped_rows = []
    for r in rows:
        if len(r) == 2:
            k, v = r
            k_p = k if hasattr(k, "wrap") else Paragraph(f"<b>{k}</b>", s_body)
            v_p = v if hasattr(v, "wrap") else Paragraph(str(v), s_body)
            wrapped_rows.append([k_p, v_p])
        else:
            wrapped_rows.append(r)
    t = Table(wrapped_rows, colWidths=col_widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("TEXTCOLOR", (0,0), (0,-1), C_ACCENT),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("TEXTCOLOR", (1,0), (-1,-1), C_TXT),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LINEBELOW", (0,0), (-1,-2), 0.4, C_BORDER),
    ]))
    return t

# ---------- COVER PAGE ----------
def cover_page():
    """Painted cover (Poseidon dark)."""
    class Cover(Image):
        def __init__(self): pass
        def wrap(self, *_): return (0,0)
        def drawOn(self, c, *_): pass
    # we'll do the cover as a single canvas draw via a custom Flowable
    return []

def render_cover(canv, doc):
    w, h = LETTER
    # dark background
    canv.setFillColor(C_BG)
    canv.rect(0, 0, w, h, stroke=0, fill=1)
    # red diagonal stripe
    canv.setFillColor(C_ACCENT)
    canv.rect(0, h - 0.9*inch, w, 0.18*inch, stroke=0, fill=1)
    # trident emblem (simplified)
    canv.setStrokeColor(C_ACCENT)
    canv.setLineWidth(3)
    cx, cy = w/2, h - 2.6*inch
    canv.line(cx, cy - 0.6*inch, cx, cy + 0.7*inch)
    canv.line(cx - 0.45*inch, cy + 0.35*inch, cx, cy + 0.7*inch)
    canv.line(cx + 0.45*inch, cy + 0.35*inch, cx, cy + 0.7*inch)
    canv.arc(cx - 0.7*inch, cy - 0.2*inch, cx + 0.7*inch, cy + 0.5*inch, 200, 140)
    # POSEIDON brand
    canv.setFillColor(colors.white)
    canv.setFont("Helvetica-Bold", 13)
    canv.drawCentredString(cx, cy - 0.95*inch, "POSEIDON")
    canv.setFillColor(C_ACCENT)
    canv.setFont("Helvetica-Bold", 8.5)
    canv.drawCentredString(cx, cy - 1.12*inch, "C O M M A N D    C E N T E R    ·    V 6")
    # Title block
    canv.setFillColor(colors.white)
    canv.setFont("Helvetica-Bold", 44)
    canv.drawString(0.8*inch, 4.0*inch, "Social & Web")
    canv.drawString(0.8*inch, 3.4*inch, "Command")
    # accent rule under title
    canv.setStrokeColor(C_ACCENT)
    canv.setLineWidth(4)
    canv.line(0.8*inch, 3.2*inch, 3.5*inch, 3.2*inch)
    # subtitle
    canv.setFillColor(colors.HexColor("#c2c2c2"))
    canv.setFont("Helvetica", 16)
    canv.drawString(0.8*inch, 2.85*inch, "Operations Manual")
    canv.setFont("Helvetica", 11)
    canv.setFillColor(C_GREY)
    canv.drawString(0.8*inch, 2.55*inch, "Page-by-page reference for the Poseidon v6 hub")
    canv.drawString(0.8*inch, 2.35*inch, "covering content ops, web analytics, engagement, ROI,")
    canv.drawString(0.8*inch, 2.15*inch, "prospects, and brand workspaces.")
    # meta block
    canv.setFillColor(colors.HexColor("#1b1b1f"))
    canv.rect(0.8*inch, 1.0*inch, 6.9*inch, 0.85*inch, stroke=0, fill=1)
    canv.setStrokeColor(C_ACCENT)
    canv.setLineWidth(1)
    canv.line(0.8*inch, 1.0*inch, 0.8*inch, 1.85*inch)
    canv.setFillColor(colors.white)
    canv.setFont("Helvetica-Bold", 9)
    canv.drawString(1.0*inch, 1.55*inch, "PREPARED FOR")
    canv.drawString(3.4*inch, 1.55*inch, "VERSION")
    canv.drawString(5.4*inch, 1.55*inch, "DATE")
    canv.setFont("Helvetica", 10)
    canv.setFillColor(colors.HexColor("#c2c2c2"))
    canv.drawString(1.0*inch, 1.30*inch, "Robert Upchurch · CTI Group")
    canv.drawString(3.4*inch, 1.30*inch, "v0.9 · Phase 1")
    canv.drawString(5.4*inch, 1.30*inch, "June 18, 2026")
    # footer
    canv.setFillColor(C_GREY)
    canv.setFont("Helvetica", 8.5)
    canv.drawString(0.8*inch, 0.5*inch, "© 2026 CTI Group Worldwide Services, Inc.   ·   Confidential — Internal Use Only")
    canv.drawRightString(w - 0.8*inch, 0.5*inch, "robert-upchurch.github.io/social-web-command")

# ---------- BUILD ----------
doc = SimpleDocTemplate(
    OUT, pagesize=LETTER,
    leftMargin=0.55*inch, rightMargin=0.55*inch,
    topMargin=0.75*inch, bottomMargin=0.75*inch,
    title="Social & Web Command — Operations Manual",
    author="Perplexity Computer",
)

# We use a custom first-page handler for the cover, then draw_page_frame for the rest.
def on_first_page(canv, doc):
    render_cover(canv, doc)

def on_later_pages(canv, doc):
    draw_page_frame(canv, doc)

# Content frame width = 7.4 inches
CW = 7.4 * inch
PAGE_USABLE_H = 9.0 * inch  # rough

story = []

# ===== COVER (blank flowable — page is fully painted in on_first_page) =====
story.append(Spacer(1, PAGE_USABLE_H))
story.append(PageBreak())

# ===== TABLE OF CONTENTS =====
story.append(Spacer(1, 0.2*inch))
story.append(Paragraph("Table of Contents", s_h1))
story.append(Paragraph("Operations Manual · v0.9 · Phase 1", s_h1sub))
story.append(Spacer(1, 8))

toc_rows = [
    ("01", "Welcome & Quick Start", "3"),
    ("02", "Interface Anatomy", "5"),
    ("03", "Executive Overview", "8"),
    ("04", "Web Analytics", "10"),
    ("05", "Content Calendar", "12"),
    ("06", "Script & Video Library", "14"),
    ("07", "Engagement Inbox", "16"),
    ("08", "Spend & ROI Analytics", "18"),
    ("09", "Landing Pages & UTM", "20"),
    ("10", "Prospect Intelligence", "21"),
    ("11", "Presentation Vault", "22"),
    ("12", "Brand Workspaces", "23"),
    ("13", "Settings & Integrations", "24"),
    ("14", "Themes & Personalization", "26"),
    ("15", "Data Management", "28"),
    ("16", "Roles & Permissions (RBAC)", "29"),
    ("17", "Integration Roadmap", "30"),
    ("18", "Troubleshooting & FAQ", "31"),
]
toc_table = Table(
    [[Paragraph(f"<font color='#dc2626'><b>{n}</b></font>", s_toc),
      Paragraph(f"<b>{t}</b>", s_toc),
      Paragraph(f"<font color='#8a8a92'>{p}</font>", s_toc)] for n,t,p in toc_rows],
    colWidths=[0.5*inch, 5.9*inch, 0.7*inch],
)
toc_table.setStyle(TableStyle([
    ("LINEBELOW", (0,0), (-1,-2), 0.4, C_BORDER),
    ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ("TOPPADDING", (0,0), (-1,-1), 7),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("ALIGN", (2,0), (2,-1), "RIGHT"),
]))
story.append(toc_table)
story.append(Spacer(1, 0.3*inch))
story.append(Paragraph(
    "<b>Live URL:</b> &nbsp;<font color='#0284c7'>https://robert-upchurch.github.io/social-web-command/</font>",
    s_body))
story.append(Paragraph(
    "<b>Built for:</b> &nbsp;Robert Upchurch · CTI Group Worldwide Services, Inc.",
    s_body))
story.append(Paragraph(
    "<b>Design system:</b> &nbsp;Mirrors Poseidon v6 Command Center · all five themes supported",
    s_body))

# ============================================================
# CHAPTER 01 — WELCOME & QUICK START
# ============================================================
story += section_header(
    "01 · Welcome & Quick Start",
    "Your unified cockpit for social media planning, paid campaigns, and continuous web analytics"
)
story.append(Paragraph(
    "Social & Web Command is the operating layer that sits across every CTI Group brand "
    "and every CTI Group web property. It replaces fragmented spreadsheets, scattered content "
    "calendars, and per-platform dashboards with one Poseidon-styled hub.",
    s_body
))
story.append(Paragraph("What it does", s_h2))
story += bullet_list([
    "<b>Plans every post</b> across Instagram, Facebook, TikTok, YouTube, LinkedIn, X, Pinterest, and Adobe Express",
    "<b>Houses every script and every video</b> from internal hosts, Adobe Express, YouTube, Vimeo, and TikTok",
    "<b>Monitors every web property</b> — cti-usa.com, j1.cti-usa.com, uniformsnumberone.com, baronpromotions.com, ctimarinetravel.com, ctiproperties.com",
    "<b>Tracks paid spend, leads, and ROI</b> across all platforms and campaigns",
    "<b>Routes engagement</b> from every platform into one unified inbox",
    "<b>Connects social activity to sales pipeline</b> through landing pages, UTMs, and prospect records",
])

story.append(Paragraph("Six brands. One workspace.", s_h2))
brand_rows = [
    [swatch("#6b6f78"), "All Brands",                  "Aggregate view across every operating unit"],
    [swatch("#0284c7"), "UNO (Uniforms Number One)",  "Hospitality, marine, and corporate uniform line"],
    [swatch("#d97706"), "Baron Promotions",            "Promotional products & trade-show services"],
    [swatch("#0ea5e9"), "CTI Marine Travel",           "Cruise crew recruitment and travel logistics"],
    [swatch("#dc2626"), "CTI Group",                   "Corporate brand and umbrella entity"],
    [swatch("#16a34a"), "CTI Properties",              "Real estate, dormitory, and tenant operations"],
    [swatch("#7c3aed"), "J1 Division",                 "J-1 visa sponsorship and exchange program"],
]
bt = Table(brand_rows, colWidths=[0.4*inch, 2.1*inch, 4.9*inch])
bt.setStyle(TableStyle([
    ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
    ("FONTSIZE", (0,0), (-1,-1), 9.5),
    ("TEXTCOLOR", (1,0), (1,-1), C_ACCENT),
    ("FONTNAME", (1,0), (1,-1), "Helvetica-Bold"),
    ("TEXTCOLOR", (2,0), (2,-1), C_TXT),
    ("ALIGN", (0,0), (0,-1), "CENTER"),
    ("VALIGN", (0,0), (0,-1), "MIDDLE"),
    ("VALIGN", (1,0), (-1,-1), "MIDDLE"),
    ("LINEBELOW", (0,0), (-1,-2), 0.4, C_BORDER),
    ("TOPPADDING", (0,0), (-1,-1), 7),
    ("BOTTOMPADDING", (0,0), (-1,-1), 7),
]))
story.append(bt)

story.append(PageBreak())

# Quick start
story += section_header(
    "Quick Start · 60-Second Tour",
    "Five things to try the first time you open the hub"
)
qs = [
    ("Open the hub",       "Visit <font color='#0284c7'>robert-upchurch.github.io/social-web-command</font> on any device. No login required for Phase 1."),
    ("Pick your theme",    "Use the five color swatches in the top bar to switch between Midnight (default), Daylight, Harbor, Contrast, or Marine."),
    ("Filter by brand",    "Click any brand chip near the top of each page — every chart, list, and KPI re-filters instantly. Use the All Brands chip for the executive roll-up."),
    ("Schedule something", "Open the Calendar, click <b>+ New Content</b>, fill the form. The post lands on its date and can be dragged to any other day."),
    ("Try Web Analytics",  "Click 📊 Web Analytics in the left rail. You'll see six site cards — one per CTI property — with pageviews, uptime, and sparkline trends ready for live data."),
]
for i, (h, b) in enumerate(qs, 1):
    story.append(Paragraph(f"<b>Step {i} — {h}</b>", s_h3))
    story.append(Paragraph(b, s_body))
    story.append(Spacer(1, 4))

story.append(Spacer(1, 8))
story.append(Paragraph("Important: where your data lives right now", s_h2))
story.append(Paragraph(
    "Phase 1 stores everything in your browser's local storage. That means data is "
    "<b>per-device</b> and <b>per-browser</b> — Robert's laptop, Robert's phone, and a "
    "team member's PC each have their own copy until Phase 2 introduces a shared backend. "
    "Use the <b>Export JSON</b> button (right rail or Settings) to back up or move data, "
    "and <b>Import JSON</b> to restore it.",
    s_body
))

story.append(PageBreak())

# ============================================================
# CHAPTER 02 — INTERFACE ANATOMY
# ============================================================
story += section_header(
    "02 · Interface Anatomy",
    "Every part of the screen, named and explained"
)
story.append(fit_image(os.path.join(SHOTS, "01-overview.png"), CW, 4.2*inch))
story.append(Paragraph("The Executive Overview, showing every interface zone.", s_caption))

zones = [
    ("Top bar",      "The persistent 56-pixel header. Holds the Poseidon trident, the global search field, the five-theme switcher, status pills, and your user avatar."),
    ("Left sidebar", "Your hub navigation. Eleven routes organized into five groups: Command, Content Ops, Performance, Sales Intel, and System."),
    ("Main panel",   "The active page. Re-renders instantly whenever you click a nav item or switch brands."),
    ("Right rail",   "Always-on situational awareness: items awaiting approval, fresh engagement alerts, today's top-performing campaign, and quick-action buttons."),
    ("Status strip", "The thin bottom bar. Shows build version, last-save timestamp, RBAC phase, record count, and copyright."),
]
story.append(kv_table([(z[0], z[1]) for z in zones]))
story.append(PageBreak())

# Top bar close-up
story.append(Paragraph("Top Bar — close-up", s_h2))
story.append(fit_image(os.path.join(SHOTS, "cu-topbar.png"), CW, 0.9*inch))
story.append(Spacer(1, 6))
story.append(kv_table([
    ("Trident + brand",  "Identifies the hub. Clicking it returns you to the Executive Overview."),
    ("Search field",     "Phase 1: visual placeholder. Phase 2: global search across content, scripts, landing pages, and prospects."),
    ("Theme switcher",   "Five swatches — Midnight, Daylight, Harbor, Contrast, Marine. Selection persists in your browser."),
    ("Status pills",     "Live build indicator and version stamp."),
    ("Avatar",           "Your initials. Phase 2: tied to Microsoft SSO identity."),
]))

# Sidebar close-up
story.append(Spacer(1, 10))
story.append(Paragraph("Sidebar — close-up", s_h2))
story.append(fit_image(os.path.join(SHOTS, "cu-sidebar.png"), 2.6*inch, 5.4*inch))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "Each item shows its current status as a colored badge: <b><font color='#16a34a'>LIVE</font></b> (functional today), "
    "<b><font color='#dc2626'>NEW</font></b> (new in this build), or a placeholder pill (planned for later phases). "
    "The active route is marked with a red left border and a tinted background.",
    s_body
))

story.append(PageBreak())

# Brand switcher + KPI ribbon + right rail + strip
story.append(Paragraph("Brand Switcher", s_h2))
story.append(fit_image(os.path.join(SHOTS, "cu-brand-switcher.png"), CW, 0.7*inch))
story.append(Paragraph(
    "Appears at the top of every brand-aware page. Click any chip to filter all content, KPIs, "
    "and tables on that page. <b>All Brands</b> shows the unfiltered roll-up.",
    s_body
))

story.append(Spacer(1, 10))
story.append(Paragraph("KPI Ribbon", s_h2))
story.append(fit_image(os.path.join(SHOTS, "cu-kpi-row.png"), CW, 1.2*inch))
story.append(Paragraph(
    "Four headline metrics tuned to the current page and the current brand filter. Each KPI shows "
    "a label, the value in large type, and a contextual delta or supporting metric.",
    s_body
))

story.append(Spacer(1, 10))
story.append(Paragraph("Right Rail", s_h2))
story.append(fit_image(os.path.join(SHOTS, "cu-rightbar.png"), 2.8*inch, 5.0*inch))
story.append(Paragraph(
    "Four sections, always visible on screens 1280px and wider: <b>Awaiting Approval</b> "
    "(content in review state), <b>Alerts</b> (new or escalated engagement items), "
    "<b>Today's Top Mover</b> (best-performing campaign by leads), and "
    "<b>Quick Actions</b> (+ New Content · Export JSON · Import JSON).",
    s_body
))

story.append(Spacer(1, 10))
story.append(Paragraph("Status Strip", s_h2))
story.append(fit_image(os.path.join(SHOTS, "cu-strip.png"), CW, 0.45*inch))
story.append(Paragraph(
    "Quiet system telemetry. The dot turns amber when changes are unsaved. The record counter "
    "reflects how many content, video, script, landing-page, prospect, and presentation items "
    "are currently in your local store.",
    s_body
))

story.append(PageBreak())

# ============================================================
# CHAPTER 03 — EXECUTIVE OVERVIEW
# ============================================================
story += section_header(
    "03 · Executive Overview",
    "Your daily-first-thing-in-the-morning page"
)
story.append(fit_image(os.path.join(SHOTS, "01-overview.png"), CW, 4.2*inch))
story.append(Paragraph("Default landing view, all brands selected.", s_caption))

story.append(Paragraph("What you see", s_h2))
story += bullet_list([
    "<b>Scheduled This Week</b> — count of content with status = Scheduled",
    "<b>Published This Month</b> — count with status = Published, plus delta versus the prior period",
    "<b>Awaiting Approval</b> — count with status = Review, surfaced as the most-urgent action item",
    "<b>Spend This Week</b> — total ad spend, with CPC and CPL micro-metrics",
    "<b>Brand-by-Brand Reach</b> — horizontal bar chart, one row per brand, sorted by impressions",
    "<b>Platform Mix</b> — distribution of content across Instagram, TikTok, YouTube, LinkedIn, Facebook, X, Pinterest",
    "<b>Top Performing Content</b> — published items, ranked, with brand badges",
    "<b>Best Performing Platform by Brand</b> — table showing which platform each brand wins on",
    "<b>Recent Performance Trend</b> — seven-day spark bar at the bottom of the page",
])

story.append(PageBreak())

story.append(Paragraph("Filtered to a single brand", s_h2))
story.append(fit_image(os.path.join(SHOTS, "16-brand-j1-filtered.png"), CW, 4.2*inch))
story.append(Paragraph("Same Executive Overview, filtered to J1 Division only.", s_caption))
story.append(Paragraph(
    "Click any brand chip to refilter every chart, KPI, and table. The filter persists as you navigate "
    "between pages — switch to Calendar, Engagement, or ROI and they'll all stay scoped to that brand "
    "until you return to <b>All Brands</b>.",
    s_body
))

story.append(PageBreak())

# ============================================================
# CHAPTER 04 — WEB ANALYTICS
# ============================================================
story += section_header(
    "04 · Web Analytics",
    "Continuous monitoring for every CTI Group web property"
)
story.append(fit_image(os.path.join(SHOTS, "02-web-analytics.png"), CW, 4.4*inch))
story.append(Paragraph("Web Analytics page with all six monitored properties.", s_caption))

story.append(Paragraph("What the page tracks per site", s_h2))
story.append(kv_table([
    ("Pageviews 30D",   "Total page views over the last 30 days"),
    ("Uptime",          "Percentage uptime, last 30 days — green when ≥ 99.9 %"),
    ("Avg Page Load",   "Median load time in seconds. Target is under 2.0 s"),
    ("Top Page",        "Highest-traffic landing path on that property"),
    ("14-day spark",    "Visual trend of daily traffic"),
    ("Health badge",    "HEALTHY (green) · WATCH (amber) · DOWN (red)"),
]))

story.append(Spacer(1, 10))
story.append(Paragraph("Per-site card — close-up", s_h2))
story.append(fit_image(os.path.join(SHOTS, "cu-site-card.png"), 4.0*inch, 3.5*inch))

story.append(PageBreak())

story.append(Paragraph("Going live with real data", s_h2))
story.append(Paragraph(
    "The page is fully wired to display live data — only the connection is pending. You have three options "
    "for activation, in order of effort:",
    s_body
))

go_live = [
    ("Looker Studio embed",
     "<b>Easiest path.</b> Build (or open existing) Looker Studio reports for each site, copy the embed URL, "
     "and paste it into the embed slot at the bottom of the Web Analytics page. Live data inside the hub, "
     "no API setup. Recommended starting point."),
    ("GA4 Property ID per site",
     "<b>Native path.</b> Drop each site's GA4 Property ID into Settings or Add Site. Phase 2 backend reads "
     "directly from the GA4 Data API on a schedule — currently every 6 hours — and refreshes the cards "
     "without any embed."),
    ("Search Console + Uptime monitor",
     "<b>Bonus paths.</b> Connect Search Console for impression, click, and query data, and UptimeRobot "
     "(or similar) for real uptime monitoring rather than the placeholder value."),
]
for h, b in go_live:
    story.append(Paragraph(h, s_h3))
    story.append(Paragraph(b, s_body))
    story.append(Spacer(1, 4))

story.append(Spacer(1, 6))
story.append(Paragraph("Add Site dialog", s_h2))
story.append(fit_image(os.path.join(SHOTS, "14-modal-add-site.png"), CW, 4.4*inch))
story.append(Paragraph(
    "Click <b>+ Add Site</b> in the Web Analytics header to register a new property. Fields: domain, brand, "
    "GA4 Property ID, Search Console URL, and an optional Looker Studio embed URL.",
    s_caption
))

story.append(PageBreak())

# ============================================================
# CHAPTER 05 — CONTENT CALENDAR
# ============================================================
story += section_header(
    "05 · Content Calendar",
    "Drag-and-drop scheduling across every brand and every platform"
)
story.append(fit_image(os.path.join(SHOTS, "03-calendar.png"), CW, 4.4*inch))
story.append(Paragraph("Month view, with color-coded status events.", s_caption))

story.append(Paragraph("Status color legend", s_h2))
status_rows = [
    [swatch("#6b6f78"), "Draft",     "Idea or working copy. Not yet sent to anyone."],
    [swatch("#d97706"), "Review",    "Sent for approval. Surfaces in Right Rail and Awaiting Approval KPI."],
    [swatch("#0284c7"), "Approved",  "Approved but not yet scheduled to a platform."],
    [swatch("#dc2626"), "Scheduled", "Has a date and time. Default state for normal publishing."],
    [swatch("#16a34a"), "Published", "Already live on the platform."],
]
st = Table(status_rows, colWidths=[0.4*inch, 1.0*inch, 6.0*inch])
st.setStyle(TableStyle([
    ("FONTSIZE", (0,0), (-1,-1), 10),
    ("FONTNAME", (1,0), (1,-1), "Helvetica-Bold"),
    ("TEXTCOLOR", (1,0), (1,-1), C_ACCENT),
    ("ALIGN", (0,0), (0,-1), "CENTER"),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("LINEBELOW", (0,0), (-1,-2), 0.4, C_BORDER),
    ("TOPPADDING", (0,0), (-1,-1), 6),
    ("BOTTOMPADDING", (0,0), (-1,-1), 6),
]))
story.append(st)

story.append(PageBreak())

story.append(Paragraph("How to use it", s_h2))
story += bullet_list([
    "<b>Navigate months</b> — use the ‹ Prev / Today / Next › buttons at the top right.",
    "<b>Create content</b> — click <b>+ New Content</b> (header) or use the right rail. The New Content modal opens.",
    "<b>Edit content</b> — click any event chip directly. Same modal, pre-filled.",
    "<b>Reschedule</b> — drag any event from one day to another. Saves automatically.",
    "<b>Filter brand</b> — use the brand switcher above the month. Only that brand's events render.",
    "<b>Today is highlighted</b> — a red border marks today's date so you never lose your place.",
])

story.append(Spacer(1, 10))
story.append(Paragraph("New Content dialog", s_h2))
story.append(fit_image(os.path.join(SHOTS, "13-modal-new-content.png"), CW, 5.0*inch))
story.append(Paragraph("Every field that defines a content item. Used to create new posts and edit existing ones.", s_caption))

story.append(PageBreak())

# Calendar fields
story.append(Paragraph("Field reference — New Content modal", s_h2))
fields = [
    ("Title",           "Short headline. Required."),
    ("Brand",           "Which of the six brands this belongs to."),
    ("Campaign",        "Optional. Ties the post to a campaign so spend and ROI roll up correctly."),
    ("Platform",        "Instagram, Facebook, TikTok, YouTube, LinkedIn, X, Pinterest, or Adobe Express."),
    ("Content Type",    "Reel, Short, Carousel, Story, Long-form Video, Static Post, or Live."),
    ("Scheduled Date",  "The calendar day. Can be changed later by drag-and-drop."),
    ("Time",            "Local time of publishing."),
    ("Status",          "Idea, Draft, Ready for Review, Approved, Scheduled, Published, Paused, Archived."),
    ("Owner",           "Person responsible. Used for assignment and right-rail display."),
    ("CTA",             "Call-to-action text used in copy (e.g. <i>Apply Now</i>, <i>Shop Now</i>)."),
    ("Landing Page",    "Tie this content to a landing page so UTMs and conversions are tracked."),
    ("Paid?",           "Organic or Paid. Paid posts also appear in Spend & ROI."),
]
story.append(kv_table(fields))

story.append(PageBreak())

# ============================================================
# CHAPTER 06 — SCRIPT & VIDEO LIBRARY
# ============================================================
story += section_header(
    "06 · Script & Video Library",
    "Centralized asset library across Adobe Express, YouTube, Vimeo, TikTok, and internal hosts"
)
story.append(fit_image(os.path.join(SHOTS, "04-library-videos.png"), CW, 4.4*inch))
story.append(Paragraph("Videos tab — grid of every video asset across all brands.", s_caption))

story.append(Paragraph("Per-video card", s_h2))
story.append(fit_image(os.path.join(SHOTS, "cu-video-card.png"), 2.2*inch, 2.0*inch))
story.append(Spacer(1, 6))
story.append(kv_table([
    ("Thumbnail",         "Visual preview. In Phase 2, replaces emoji with an actual frame grab."),
    ("Host badge",        "Top-right pill — INTERNAL · ADOBE EXPRESS · YOUTUBE · VIMEO · TIKTOK · FACEBOOK · INSTAGRAM."),
    ("Title",             "Asset name."),
    ("Brand",             "Owning brand."),
    ("Duration",          "Length in mm:ss."),
]))

story.append(PageBreak())

story.append(Paragraph("Scripts tab", s_h2))
story.append(fit_image(os.path.join(SHOTS, "05-library-scripts.png"), CW, 4.4*inch))
story.append(Paragraph("Scripts table — versioned, brand-tagged, and linked to videos and posts.", s_caption))

story.append(Paragraph("How scripts and videos connect", s_h2))
story.append(Paragraph(
    "Each script has a version number, a hook, a body, a CTA, and hashtag set. When a script "
    "is used in a video shoot, the resulting video links back to the script ID, and when a "
    "post is created from that video, the post inherits the same script and brand. This chain — "
    "<b>script → video → post → landing page → conversion</b> — is what makes the ROI page in Chapter 08 work.",
    s_body
))

story.append(Spacer(1, 8))
story.append(Paragraph("Importing from third-party hosts", s_h2))
import_rows = [
    ("Adobe Express",  "Phase 1: manual entry via + Add Asset. Phase 2: direct OAuth import via Creative SDK."),
    ("YouTube",        "Phase 1: paste URL. Phase 2: live import via the connected YouTube Data API (Poseidon)."),
    ("Vimeo",          "Phase 1: paste URL. Phase 2: Vimeo OAuth import."),
    ("TikTok / Instagram / Facebook", "Phase 1: link content URL. Phase 2: pull through Meta + TikTok Business APIs."),
    ("Internal host",  "Local file upload — coming in Phase 2 backend."),
]
story.append(kv_table(import_rows))

story.append(PageBreak())

# ============================================================
# CHAPTER 07 — ENGAGEMENT INBOX
# ============================================================
story += section_header(
    "07 · Engagement Inbox",
    "Every comment, DM, and reply across every platform — one feed"
)
story.append(fit_image(os.path.join(SHOTS, "06-engagement.png"), CW, 4.4*inch))
story.append(Paragraph("Unified engagement inbox with status, priority, and per-platform icons.", s_caption))

story.append(Paragraph("Status pipeline", s_h2))
story.append(kv_table([
    ("NEW",        "Just arrived. No one has touched it yet. Surfaces in Right Rail Alerts."),
    ("ASSIGNED",   "Routed to a team member. Owner is named on the row."),
    ("RESPONDED",  "A reply has been sent. Closes the loop."),
    ("ESCALATED",  "Negative, sensitive, or high-priority. Surfaced to Robert by default."),
    ("CLOSED",     "Archived. Excluded from active counts."),
]))

story.append(Spacer(1, 10))
story.append(Paragraph("Single item — close-up", s_h2))
story.append(fit_image(os.path.join(SHOTS, "cu-inbox-item.png"), CW, 1.0*inch))

story.append(PageBreak())

story.append(Paragraph("Per-item actions", s_h2))
story += bullet_list([
    "<b>Reply</b> — opens the response composer (Phase 2 publishes back to the source platform)",
    "<b>Assign</b> — hand off to a team member by role",
    "<b>Escalate</b> — flag for leadership review",
    "<b>Close</b> — archive once resolved",
])

story.append(Spacer(1, 6))
story.append(Paragraph("Filters", s_h2))
story.append(Paragraph(
    "Filter by <b>Status</b>, <b>Platform</b>, and <b>Priority</b>. Combine with the brand switcher "
    "to focus on (for example) <i>all high-priority new comments on the J1 Division's Instagram</i>.",
    s_body
))

story.append(Spacer(1, 10))
story.append(Paragraph("Going live with engagement", s_h2))
story.append(Paragraph(
    "Phase 1 displays a representative sample. Real-time engagement ingestion requires platform-side "
    "API approvals — Meta Business (Instagram + Facebook), YouTube Data API (already connected via "
    "Poseidon), TikTok Business API, and LinkedIn Marketing API. Approval timelines vary by platform "
    "but typically run two to six weeks per network. YouTube is the fastest path to first live data.",
    s_body
))

story.append(PageBreak())

# ============================================================
# CHAPTER 08 — SPEND & ROI
# ============================================================
story += section_header(
    "08 · Spend & ROI Analytics",
    "Where the money goes and what comes back"
)
story.append(fit_image(os.path.join(SHOTS, "07-roi.png"), CW, 4.4*inch))
story.append(Paragraph("Funnel + campaign table.", s_caption))

story.append(Paragraph("Headline KPIs", s_h2))
story.append(kv_table([
    ("Total Spend",  "Sum of paid spend for the current brand filter and time window."),
    ("Impressions",  "Plus CPM (cost per thousand impressions)."),
    ("Clicks",       "Plus CTR (click-through rate) and CPC (cost per click)."),
    ("Leads",        "Plus CPL (cost per lead) and Conv (conversion-from-click rate)."),
]))

story.append(PageBreak())

story.append(Paragraph("Conversion Funnel", s_h2))
story.append(Paragraph(
    "Four-stage funnel — Impressions → Clicks → Leads → Conversions — rendered as proportional bars. "
    "Drop-off between stages is the diagnostic: a wide drop from Impressions to Clicks signals weak "
    "creative or wrong audience; a drop from Clicks to Leads points to the landing page; a drop from "
    "Leads to Conversions usually means the offer or follow-up flow.",
    s_body
))

story.append(Spacer(1, 8))
story.append(Paragraph("Campaign-Level table", s_h2))
story.append(Paragraph(
    "One row per platform-per-campaign combination, showing Campaign, Brand, Platform, Spend, "
    "Impressions, Clicks, Leads, and a computed CPL. Click any row in Phase 2 to drill into "
    "the per-creative breakdown.",
    s_body
))

story.append(Spacer(1, 8))
story.append(Paragraph("How spend gets in", s_h2))
story += bullet_list([
    "<b>Phase 1</b>: manual <b>+ Log Spend</b> entries or JSON import",
    "<b>Phase 2</b>: nightly pull from Meta Ads, Google Ads, TikTok Ads, and LinkedIn Ads APIs",
    "<b>Phase 2</b>: optional CSV upload for any platform without an API integration",
])

story.append(PageBreak())

# ============================================================
# CHAPTER 09 — LANDING PAGES
# ============================================================
story += section_header(
    "09 · Landing Pages & UTM Tracking",
    "The bridge between social content and measurable outcomes"
)
story.append(fit_image(os.path.join(SHOTS, "08-landing.png"), CW, 4.4*inch))
story.append(Paragraph("Landing-page registry with visits, conversions, and computed conversion rate.", s_caption))

story.append(Paragraph("What a landing-page record holds", s_h2))
story.append(kv_table([
    ("Name",         "Human-readable label (e.g. <i>J1 Apply</i>)."),
    ("Brand",        "Owning brand."),
    ("URL",          "Public destination URL — clickable."),
    ("CTA",          "Call-to-action shown on associated content."),
    ("UTM string",   "Pre-built UTM parameters appended to the URL for source/medium/campaign tracking."),
    ("Visits",       "Total inbound visits."),
    ("Conversions",  "Total completed actions (form, signup, purchase)."),
    ("Status",       "Active / Paused / Archived."),
]))

story.append(Spacer(1, 8))
story.append(Paragraph("UTM builder", s_h2))
story.append(Paragraph(
    "Phase 1 supplies static UTM strings; Phase 2 adds a guided builder that constructs them from "
    "brand, platform, campaign, content type, and date — keeping UTMs consistent across the organization.",
    s_body
))

story.append(PageBreak())

# ============================================================
# CHAPTER 10 — PROSPECTS
# ============================================================
story += section_header(
    "10 · Prospect & Client Intelligence",
    "Target accounts and pipeline tied to campaigns"
)
story.append(fit_image(os.path.join(SHOTS, "09-prospects.png"), CW, 4.4*inch))
story.append(Paragraph("Prospect table with pipeline value, deal stage, and last contact.", s_caption))

story.append(Paragraph("Pipeline stages", s_h2))
story.append(kv_table([
    ("Discovery",    "Initial research and outreach phase."),
    ("Qualified",    "Fit confirmed; conversation in motion."),
    ("Proposal",     "Formal proposal sent."),
    ("Negotiation",  "Terms in active discussion."),
    ("Closed Won",   "Deal signed. Counted in won-deals KPI."),
    ("Closed Lost",  "Lost — recorded for win-rate calculations."),
]))

story.append(Spacer(1, 8))
story.append(Paragraph("Connecting prospects to campaigns", s_h2))
story.append(Paragraph(
    "Each prospect carries a target brand. Phase 2 introduces direct linkage between Prospects and "
    "Campaigns so you can see exactly which campaigns generated which deals — closing the loop "
    "from social impression to revenue. Import-from-Zoho is one click in Phase 2 (Zoho CRM connector "
    "is already wired into Poseidon).",
    s_body
))

story.append(PageBreak())

# ============================================================
# CHAPTER 11 — PRESENTATIONS
# ============================================================
story += section_header(
    "11 · Presentation Vault",
    "Versioned decks tied to prospects, audiences, and campaigns"
)
story.append(fit_image(os.path.join(SHOTS, "10-presentations.png"), CW, 4.4*inch))
story.append(Paragraph("Vault grid — every deck with version, audience, presenter, and last-used date.", s_caption))

story.append(Paragraph("Per-deck fields", s_h2))
story.append(kv_table([
    ("Title",      "Deck name."),
    ("Brand",      "Owning brand."),
    ("Version",    "v1.0, v2.1, v3.2, etc. — keeps revision history clean."),
    ("Audience",   "Who the deck was built for (Carnival/Disney, University Partners, etc.)."),
    ("Presenter",  "Who delivered or will deliver it."),
    ("Last Used",  "Date the deck was last presented."),
    ("Campaign",   "Optional — ties the deck to a marketing campaign."),
    ("File",       "Phase 2 — synced from OneDrive / SharePoint via existing Poseidon connectors."),
]))

story.append(PageBreak())

# ============================================================
# CHAPTER 12 — BRAND WORKSPACES
# ============================================================
story += section_header(
    "12 · Brand Workspaces",
    "Per-brand drill-down view"
)
story.append(fit_image(os.path.join(SHOTS, "11-brands.png"), CW, 4.4*inch))
story.append(Paragraph("Six brand tiles, one card per operating brand.", s_caption))

story.append(Paragraph("Per-card metrics", s_h2))
story.append(kv_table([
    ("Content",    "How many content items this brand has scheduled or published."),
    ("Landing",    "How many landing pages this brand owns."),
    ("Prospects",  "Pipeline depth — count of active prospects targeted at this brand."),
    ("Spend",      "Total paid spend on this brand to date."),
]))
story.append(Paragraph(
    "<b>Click any tile</b> to instantly set that brand as the active filter and jump to the Executive Overview "
    "scoped to it.",
    s_body
))

story.append(PageBreak())

# ============================================================
# CHAPTER 13 — SETTINGS & INTEGRATIONS
# ============================================================
story += section_header(
    "13 · Settings & Integrations",
    "Where you wire the hub to the rest of your stack"
)
story.append(fit_image(os.path.join(SHOTS, "12-settings.png"), CW, 4.4*inch))
story.append(Paragraph("Settings page — RBAC roles, integrations status, and data tools.", s_caption))

story.append(Paragraph("Integrations panel — status legend", s_h2))
story.append(kv_table([
    ("🟡 Pending",         "Connection planned for Phase 2 or later."),
    ("🔵 Available",       "Connector exists in Poseidon — drop-in once Phase 2 backend ships."),
    ("🟢 Connected",       "Actively passing live data (Phase 2+)."),
    ("🔴 Error",           "Connection broken or quota exhausted."),
]))

story.append(PageBreak())

story.append(Paragraph("Integration inventory", s_h2))
ints = [
    ("Meta Business",            "Phase 2",   "Instagram + Facebook publishing, comments, ads"),
    ("YouTube Data API",         "Available", "Already connected in Poseidon — videos, comments, analytics"),
    ("TikTok Business API",      "Phase 2",   "Publishing, ad spend, engagement"),
    ("X / Twitter API",          "Phase 2",   "Requires paid API tier"),
    ("LinkedIn Marketing API",   "Phase 2",   "Company-page publishing, sponsored content"),
    ("Adobe Express",            "Phase 1+",  "Manual upload today; OAuth import in Phase 2"),
    ("GA4 + Search Console",     "Phase 1+",  "Looker embed today; native API in Phase 2"),
    ("UptimeRobot or equivalent","Phase 2",   "Real uptime data per site"),
    ("Zoho CRM",                 "Available", "Connector wired into Poseidon — pulls prospect records"),
    ("OneDrive / SharePoint",    "Available", "Connector wired into Poseidon — for Presentation Vault"),
    ("Microsoft Teams",          "Available", "Connector wired into Poseidon — for engagement-routing alerts"),
    ("Microsoft To-Do",          "Available", "Connector wired into Poseidon — for approval-task creation"),
]
it = Table(
    [["Integration", "Status", "Purpose"]] + ints,
    colWidths=[1.9*inch, 1.4*inch, 4.1*inch]
)
it.setStyle(TableStyle([
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 9),
    ("BACKGROUND", (0,0), (-1,0), C_ACCENT),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("TEXTCOLOR", (0,1), (0,-1), C_TXT),
    ("FONTNAME", (0,1), (0,-1), "Helvetica-Bold"),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("LINEBELOW", (0,0), (-1,-1), 0.4, C_BORDER),
    ("TOPPADDING", (0,0), (-1,-1), 6),
    ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ("LEFTPADDING", (0,0), (-1,-1), 8),
    ("RIGHTPADDING", (0,0), (-1,-1), 8),
]))
story.append(it)

story.append(PageBreak())

# ============================================================
# CHAPTER 14 — THEMES
# ============================================================
story += section_header(
    "14 · Themes & Personalization",
    "Five themes — every user picks their own"
)
story.append(Paragraph(
    "The hub mirrors Poseidon's exact five-theme system. The current theme is stored in your browser, "
    "so each user can run the look they prefer. Switching takes one click in the top bar.",
    s_body
))

# 2x2 grid of theme screenshots
def theme_grid_row(left_path, left_label, right_path, right_label):
    img_l = fit_image(left_path, 3.5*inch, 2.3*inch)
    img_r = fit_image(right_path, 3.5*inch, 2.3*inch)
    cap_l = Paragraph(f"<b>{left_label}</b>", s_caption)
    cap_r = Paragraph(f"<b>{right_label}</b>", s_caption)
    t = Table([[img_l, img_r], [cap_l, cap_r]], colWidths=[3.65*inch, 3.65*inch])
    t.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    return t

# Midnight (default) — already shown earlier; pair with Daylight
story.append(theme_grid_row(
    os.path.join(SHOTS, "01-overview.png"), "Midnight — default, dark red",
    os.path.join(SHOTS, "15-theme-light.png"), "Daylight — light, red accent"
))
story.append(theme_grid_row(
    os.path.join(SHOTS, "15-theme-harbor.png"), "Harbor — light, teal accent",
    os.path.join(SHOTS, "15-theme-marine.png"), "Marine — light, navy blue accent"
))

story.append(PageBreak())

story.append(Paragraph("Contrast theme", s_h2))
story.append(fit_image(os.path.join(SHOTS, "15-theme-contrast.png"), CW, 4.4*inch))
story.append(Paragraph("Contrast — pure black, maximum accessibility, high-contrast red.", s_caption))

story.append(Paragraph("How to switch themes", s_h2))
story += bullet_list([
    "Click any of the five color swatches in the top right of the top bar.",
    "Your selection is saved to local storage and persists across sessions and pages.",
    "All charts, badges, KPIs, and tables re-color automatically — no reload required.",
])

story.append(PageBreak())

# ============================================================
# CHAPTER 15 — DATA MANAGEMENT
# ============================================================
story += section_header(
    "15 · Data Management",
    "Backup, restore, reset, wipe"
)
story.append(Paragraph(
    "Phase 1 stores everything in your browser's local storage. That makes it instant and "
    "private to your device — but you are also responsible for backups. The hub provides four "
    "data controls, all reachable from Settings or the right rail.",
    s_body
))
story.append(Paragraph("Controls", s_h2))
story.append(kv_table([
    ("Export JSON",   "Downloads a complete snapshot of your hub data as a .json file. Includes content, scripts, videos, landing pages, prospects, presentations, engagement, spend, sites, and campaigns."),
    ("Import JSON",   "Replaces your current data with the contents of a .json file. Use this to restore a backup or load data onto a new device."),
    ("Reset to Demo", "Wipes your local data and reloads the seed dataset. Useful for trying things out without consequences."),
    ("Wipe Data",     "Empties every list. No demo data. Confirmation prompt before it runs."),
], col_widths=[1.4*inch, 5.2*inch]))

story.append(Spacer(1, 8))
story.append(Paragraph("Recommended habit", s_h2))
story.append(Paragraph(
    "While Phase 1 is in use, click <b>Export JSON</b> at the end of each workday until Phase 2 "
    "ships. Drop the file into OneDrive — your file lives alongside all your other CTI documents "
    "and is automatically version-historied by OneDrive.",
    s_body
))

story.append(PageBreak())

# ============================================================
# CHAPTER 16 — RBAC
# ============================================================
story += section_header(
    "16 · Roles & Permissions (RBAC)",
    "Who can see and do what — Phase 2 ships full enforcement"
)
story.append(Paragraph(
    "Phase 1 ships the role catalog as a visual reference. Phase 2 wires real enforcement to Microsoft "
    "SSO (same identity provider as Poseidon Command), with row-level rules applied to every page.",
    s_body
))

roles = [
    ("Super Admin",         "Everything. System-wide configuration, user roles, integration credentials."),
    ("Executive Reviewer",  "Read-only on all brands. Approve or reject content. Cannot create."),
    ("Brand Manager",       "Full create/edit on a single brand. Approves content for that brand only."),
    ("Content Producer",    "Creates and edits content, scripts, and videos. Cannot publish or change spend."),
    ("Scheduler",           "Drag-and-drop calendar only. Cannot create new content or change status above Approved."),
    ("Analyst",             "Read-only across the hub. Exports allowed."),
    ("Sales / Outreach",    "Full access on Prospects, Presentations, and Landing Pages. Read-only elsewhere."),
]
rt = Table([["Role", "Permissions"]] + roles, colWidths=[2.0*inch, 5.4*inch])
rt.setStyle(TableStyle([
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 9.5),
    ("BACKGROUND", (0,0), (-1,0), C_ACCENT),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("TEXTCOLOR", (0,1), (0,-1), C_ACCENT),
    ("FONTNAME", (0,1), (0,-1), "Helvetica-Bold"),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("LINEBELOW", (0,0), (-1,-1), 0.4, C_BORDER),
    ("TOPPADDING", (0,0), (-1,-1), 7),
    ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ("LEFTPADDING", (0,0), (-1,-1), 8),
    ("RIGHTPADDING", (0,0), (-1,-1), 8),
]))
story.append(rt)

story.append(PageBreak())

# ============================================================
# CHAPTER 17 — ROADMAP
# ============================================================
story += section_header(
    "17 · Integration Roadmap",
    "Where this hub is going — phase by phase"
)

phases = [
    ("Phase 1 — Internal Command Center",  "Shipped today",  [
        "Single-file static hub, deployable anywhere",
        "Eleven routes, six brand workspaces, five themes",
        "Drag-and-drop calendar, library, prospects, presentations, engagement, ROI",
        "Web Analytics screen scaffolded with Looker-Studio embed slot",
        "Browser-local storage with JSON export/import",
    ]),
    ("Phase 2 — Live Backend + Web Analytics", "Next milestone",  [
        "Postgres or SQLite backend with multi-user editing",
        "Microsoft SSO authentication tied to existing CTI M365 tenant",
        "RBAC enforcement using the seven Phase 1 role definitions",
        "Native GA4 + Search Console API pulls per site",
        "YouTube Data API ingestion (already connected via Poseidon)",
        "OneDrive sync for Presentation Vault",
        "Zoho CRM import for Prospects",
    ]),
    ("Phase 3 — Direct Social APIs",       "After Phase 2",  [
        "Meta Business publishing for Instagram + Facebook",
        "TikTok Business API for ad spend and engagement",
        "LinkedIn Marketing API for sponsored content",
        "Direct comment-ingestion across all connected networks",
        "Automated nightly spend pull from every connected platform",
    ]),
    ("Phase 4 — Attribution & AI",         "Long horizon",   [
        "Full UTM-level attribution from impression to closed-won",
        "AI-assisted script drafting using the Poseidon agent network",
        "Automated thumbnail and caption generation",
        "Anomaly alerts on traffic, spend, or engagement spikes",
        "Predictive scheduling recommendations",
    ]),
]
for name, when, items in phases:
    story.append(Paragraph(f"<b>{name}</b>   <font color='#8a8a92' size=9>· {when}</font>", s_h2))
    for it in items:
        story.append(Paragraph(f"<font color='#dc2626'>▸</font>&nbsp;&nbsp;{it}", s_body))
    story.append(Spacer(1, 8))

story.append(PageBreak())

# ============================================================
# CHAPTER 18 — TROUBLESHOOTING
# ============================================================
story += section_header(
    "18 · Troubleshooting & FAQ",
    "Quick answers to the questions you'll have in the first week"
)

faqs = [
    ("My data disappeared after switching browsers — why?",
     "Phase 1 uses browser local storage. Each browser on each device has its own copy. "
     "Use Export JSON on the device that has the data, then Import JSON on the new browser. "
     "Phase 2 introduces a shared backend so this stops being a concern."),
    ("Why is the Web Analytics page showing demo numbers?",
     "The screen is wired but the data source is not yet connected. Drop in a Looker Studio "
     "embed URL (easiest) or wait for Phase 2 native GA4 integration."),
    ("Can I edit content directly from the calendar?",
     "Yes. Click any event chip and the New Content modal opens with that item's fields pre-filled. "
     "You can also drag the chip to a different date to reschedule, or change the status field in "
     "the modal to move it through the workflow."),
    ("How do I share the hub with a teammate?",
     "Send them the live URL. Phase 1 is publicly accessible but unauthenticated — fine for internal "
     "team review while we wait for Phase 2 SSO. After Phase 2, access is restricted to your M365 tenant."),
    ("Will switching themes affect what my team sees?",
     "No. Theme preference is per-user. Robert can run Midnight while a brand manager runs Daylight — "
     "the underlying data is identical."),
    ("How do I add a new brand?",
     "Phase 1: edit the BRANDS array in the source HTML. Phase 2: add via Settings → Brands."),
    ("Where do I report a bug or request a feature?",
     "Open a new task in Perplexity Computer and reference the manual section. Robert's Perplexity "
     "workspace is where all hub iteration runs."),
    ("Is it mobile-friendly?",
     "Yes — the layout collapses cleanly to tablet and phone. The right rail hides below 1280 px, "
     "the sidebar collapses to icons below 980 px. Drag-and-drop on the calendar requires a "
     "touch-capable browser; use the modal for status changes on mobile."),
]
for q, a in faqs:
    story.append(Paragraph(f"<b>{q}</b>", s_h3))
    story.append(Paragraph(a, s_body))
    story.append(Spacer(1, 4))

story.append(PageBreak())

# CLOSING PAGE
story.append(Spacer(1, 1.6*inch))
story.append(Paragraph(
    "<font color='#dc2626' size=20><b>Built on Poseidon v6.</b></font>",
    s_h1
))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "<font size=12>Designed and built for CTI Group Worldwide Services, Inc.</font>",
    s_body
))
story.append(Spacer(1, 18))
story.append(Paragraph("Live URL", s_h3))
story.append(Paragraph("<font color='#0284c7'>https://robert-upchurch.github.io/social-web-command/</font>", s_body))
story.append(Spacer(1, 8))
story.append(Paragraph("Repository", s_h3))
story.append(Paragraph("<font color='#0284c7'>github.com/Robert-Upchurch/social-web-command</font>", s_body))
story.append(Spacer(1, 8))
story.append(Paragraph("Manual version", s_h3))
story.append(Paragraph("v0.9 · June 18, 2026 · Phase 1 reference", s_body))

# BUILD
doc.build(story, onFirstPage=on_first_page, onLaterPages=on_later_pages)
print("PDF written:", OUT)
print("Pages: built")
import subprocess
result = subprocess.run(['pdfinfo', OUT], capture_output=True, text=True)
print(result.stdout)
