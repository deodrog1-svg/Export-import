#!/usr/bin/env python3
"""Premium PDF: sulphur delivered cost to South Korea from every source country.

Reads knowledge/sessions/2026-10-30-sulphur-world-sources.json (one object per
country, written by the trade-advisor agent), runs every country through
tools/landed_cost.py for 100 t and 1,000 t lots, and writes
reports/sulphur-world-sources-2026-10-30.pdf.

    python3 tools/make_world_report.py [sources.json] [out.pdf]
"""

import json
import math
import os
import sys

from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, NextPageTemplate,
                                PageBreak, PageTemplate, Paragraph, Spacer, Table,
                                TableStyle)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from landed_cost import calculate_route  # noqa: E402

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("DV", f"{FONT_DIR}/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DV-B", f"{FONT_DIR}/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DV-L", f"{FONT_DIR}/DejaVuSans.ttf"))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B")

# Palette: deep navy + champagne gold, recessive greys, reserved status colors.
NAVY = colors.HexColor("#0E1B2C")
NAVY_2 = colors.HexColor("#16283F")
GOLD = colors.HexColor("#C9A45C")
GOLD_SOFT = colors.HexColor("#E9DCC0")
INK = colors.HexColor("#1B1F24")
INK_2 = colors.HexColor("#5A6472")
INK_3 = colors.HexColor("#8C95A1")
HAIR = colors.HexColor("#E1E0D9")
PAPER = colors.HexColor("#FBFAF7")
ROW = colors.HexColor("#F4F1EA")
STATUS = {
    "open": ("#0CA30C", "OPEN"),
    "disrupted": ("#FAB219", "DISRUPTED"),
    "banned": ("#D03B3B", "BANNED"),
    "sanctioned": ("#D03B3B", "SANCTIONED"),
    "benchmark": ("#8C95A1", "BENCHMARK"),
}

SALE_PRICE = 900          # assumed delivered sale price to Korean client, USD/t
LOTS = (100, 1000)
CONTAINER_T = 25          # bagged sulphur per 20ft
DOCS = 1500               # export docs, certificate of origin, broker (per shipment)
BAGGING = 15              # USD/t to bag bulk sulphur for containers
DEST_PER_CONTAINER = 750  # Busan THC/D-O + hazmat truck to client
BROKER_KR = 350           # Korean customs broker + chemical confirmation
SETTINGS = {"financing_rate_annual": 0.08}

W, H = A4
M = 16 * mm


def st(name, **kw):
    base = dict(fontName="DV", fontSize=9, leading=12.5, textColor=INK)
    base.update(kw)
    return ParagraphStyle(name, **base)


S = {
    "h1": st("h1", fontName="DV-B", fontSize=17, leading=21, textColor=NAVY, spaceAfter=2),
    "kicker": st("k", fontName="DV-B", fontSize=7.5, leading=10, textColor=GOLD, spaceAfter=3),
    "lead": st("lead", fontSize=10, leading=14.5, textColor=INK_2, spaceAfter=8),
    "body": st("body"),
    "small": st("small", fontSize=7.4, leading=10, textColor=INK_2),
    "cell": st("cell", fontSize=7.6, leading=9.6),
    "cellr": st("cellr", fontSize=7.6, leading=9.6, alignment=2),
    "cellb": st("cellb", fontName="DV-B", fontSize=7.6, leading=9.6),
    "head": st("head", fontName="DV-B", fontSize=7, leading=9, textColor=GOLD_SOFT),
    "headr": st("headr", fontName="DV-B", fontSize=7, leading=9, textColor=GOLD_SOFT, alignment=2),
    "card_t": st("ct", fontName="DV-B", fontSize=10.5, leading=13, textColor=NAVY),
    "card": st("c", fontSize=7.6, leading=10.2, textColor=INK),
}


def P(t, s="body"):
    return Paragraph(t, S[s])


def pct(x):
    s = f"{x:.0%}"
    return "0%" if s == "-0%" else s.replace("-", "−")


def usd(x, dec=0):
    s = f"{abs(x):,.{dec}f}"
    return f"−${s}" if x < 0 else f"${s}"


# ---------------------------------------------------------------- calculation

def route_for(c, q):
    n = math.ceil(q / CONTAINER_T)
    domestic = c.get("status") == "benchmark"
    origin = [] if domestic else [{"name": "Export docs, CO, broker", "amount": DOCS},
                                  {"name": "Bagging", "amount": BAGGING * q}]
    return {
        "name": c["country"],
        "quantity": q,
        "unit_cost": (c["buy_price_usd_t"] or 0) + (c.get("extra_origin_cost_usd_t") or 0),
        "sale_price_per_unit": SALE_PRICE,
        "origin_charges": origin,
        "freight": (c.get("freight_per_20ft_usd") or 0) * n,
        "insurance_rate": 0 if domestic else 0.003,
        "duty_basis": "CIF",
        "duty_rate": 0 if domestic else (c.get("korea_duty_rate") or 0),
        "vat_rate": 0.10,
        "destination_charges": [{"name": "Truck to client" if domestic else "Busan THC + hazmat truck",
                                 "amount": (500 if domestic else DEST_PER_CONTAINER) * n},
                                {"name": "Broker + chemical check", "amount": 0 if domestic else BROKER_KR}],
        "transit_days": c.get("transit_days") or 0,
        "payment_terms_days": 30,
        "fx_buffer_rate": 0 if domestic else 0.01,
    }


def evaluate(countries):
    rows = []
    for c in countries:
        if c.get("buy_price_usd_t") is None:
            rows.append({"c": c, "lots": None})
            continue
        lots = {q: calculate_route(SETTINGS, route_for(c, q)) for q in LOTS}
        rows.append({"c": c, "lots": lots})
    priced = [r for r in rows if r["lots"]]
    priced.sort(key=lambda r: r["lots"][1000]["cost_per_unit"])
    return priced + [r for r in rows if not r["lots"]]


# ---------------------------------------------------------------- page chrome

def cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, W, H, stroke=0, fill=1)
    # subtle contour lines
    canvas.setStrokeColor(NAVY_2)
    canvas.setLineWidth(0.6)
    for i in range(14):
        r = 60 * mm + i * 9 * mm
        canvas.circle(W + 10 * mm, H * 0.62, r, stroke=1, fill=0)
    canvas.setFillColor(GOLD)
    canvas.rect(M, H - 52 * mm, 14 * mm, 1.2 * mm, stroke=0, fill=1)
    canvas.setFont("DV-B", 8.5)
    canvas.drawString(M, H - 46 * mm, "TRADE ADVISOR  ·  MARKET INTELLIGENCE REPORT")
    canvas.setFillColor(colors.white)
    canvas.setFont("DV-B", 34)
    canvas.drawString(M, H - 78 * mm, "Sulphur to")
    canvas.drawString(M, H - 92 * mm, "South Korea")
    canvas.setFont("DV-L", 15)
    canvas.setFillColor(GOLD_SOFT)
    canvas.drawString(M, H - 106 * mm, "Delivered cost from every source country")
    canvas.setFont("DV", 9)
    canvas.setFillColor(INK_3)
    canvas.drawString(M, H - 116 * mm, "HS 2503.00  ·  delivered Busan → client  ·  100 t and 1,000 t lots  ·  30 October 2026")

    # KPI tiles
    k = doc.kpis
    tile_w = (W - 2 * M - 2 * 6 * mm) / 3
    y = 62 * mm
    for i, (label, value, note) in enumerate(k):
        x = M + i * (tile_w + 6 * mm)
        canvas.setFillColor(NAVY_2)
        canvas.roundRect(x, y, tile_w, 38 * mm, 3 * mm, stroke=0, fill=1)
        canvas.setFillColor(GOLD)
        canvas.rect(x, y + 38 * mm - 1.1 * mm, tile_w, 1.1 * mm, stroke=0, fill=1)
        canvas.setFont("DV-B", 7)
        canvas.drawString(x + 5 * mm, y + 30 * mm, label.upper())
        canvas.setFillColor(colors.white)
        canvas.setFont("DV-B", 19)
        canvas.drawString(x + 5 * mm, y + 17 * mm, value)
        canvas.setFont("DV", 7.5)
        canvas.setFillColor(GOLD_SOFT)
        for j, line in enumerate(note.split("\n")):
            canvas.drawString(x + 5 * mm, y + 10 * mm - j * 3.6 * mm, line)

    canvas.setFillColor(INK_3)
    canvas.setFont("DV", 7)
    canvas.drawString(M, 22 * mm, "Prepared for a Kazakhstan-national trader resident in South Korea. Estimates built from "
                      "October 2026 benchmarks, not supplier quotes.")
    canvas.drawString(M, 18 * mm, "Verify with a licensed Korean customs broker, freight forwarder and supplier before committing money.")
    canvas.restoreState()


def inner(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(PAPER)
    canvas.rect(0, 0, W, H, stroke=0, fill=1)
    canvas.setFillColor(NAVY)
    canvas.rect(0, H - 11 * mm, W, 11 * mm, stroke=0, fill=1)
    canvas.setFillColor(GOLD)
    canvas.rect(0, H - 11 * mm - 0.8 * mm, W, 0.8 * mm, stroke=0, fill=1)
    canvas.setFont("DV-B", 7.5)
    canvas.drawString(M, H - 7 * mm, "TRADE ADVISOR")
    canvas.setFillColor(GOLD_SOFT)
    canvas.setFont("DV", 7.5)
    canvas.drawRightString(W - M, H - 7 * mm, "Sulphur to South Korea  ·  Delivered cost by source country  ·  Oct 2026")
    canvas.setStrokeColor(HAIR)
    canvas.setLineWidth(0.5)
    canvas.line(M, 13 * mm, W - M, 13 * mm)
    canvas.setFillColor(INK_3)
    canvas.setFont("DV", 7)
    canvas.drawString(M, 9 * mm, "Estimates, not quotes. Prices, bans and freight change; confirm before committing money.")
    canvas.drawRightString(W - M, 9 * mm, f"{doc.page:02d}")
    canvas.restoreState()


# ---------------------------------------------------------------- components

def pill(status):
    hexc, label = STATUS.get(status, ("#8C95A1", status.upper()))
    t = Table([[Paragraph(f"<font color='{'#0b0b0b' if status == 'disrupted' else '#ffffff'}'><b>{label}</b></font>",
                          st("p", fontSize=6, leading=7.5, alignment=1))]],
              colWidths=[17.5 * mm], rowHeights=[4.4 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(hexc)),
        ("ROUNDEDCORNERS", [2, 2, 2, 2]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING", (0, 0), (-1, -1), 1), ("RIGHTPADDING", (0, 0), (-1, -1), 1),
    ]))
    return t


def section(kicker, title, lead=None):
    out = [P(kicker.upper(), "kicker"), P(title, "h1")]
    if lead:
        out.append(P(lead, "lead"))
    else:
        out.append(Spacer(1, 6))
    return out


def bar_chart(rows, width):
    """Horizontal bars: delivered cost per tonne (1,000 t), colored by status, sale line."""
    data = [r for r in rows if r["lots"]]
    bar_h, gap, left, right_pad, top = 3.4 * mm, 1.5 * mm, 40 * mm, 16 * mm, 8 * mm
    height = top + len(data) * (bar_h + gap) + 10 * mm
    d = Drawing(width, height)
    vmax = max(max(r["lots"][1000]["cost_per_unit"] for r in data), SALE_PRICE) * 1.05
    plot_w = width - left - right_pad

    def x(v):
        return left + plot_w * v / vmax

    # gridlines
    step = 200
    for v in range(0, int(vmax) + 1, step):
        d.add(Line(x(v), 8 * mm, x(v), height - top + 2 * mm, strokeColor=HAIR, strokeWidth=0.4))
        d.add(String(x(v), 4 * mm, f"${v:,}", fontName="DV", fontSize=6.5, fillColor=INK_3, textAnchor="middle"))
    y = height - top
    for r in data:
        y -= bar_h + gap
        c = r["c"]
        v = r["lots"][1000]["cost_per_unit"]
        hexc = STATUS.get(c["status"], ("#8C95A1",))[0]
        d.add(String(left - 2.5 * mm, y + 1.3 * mm, c["country"], fontName="DV", fontSize=7.2,
                     fillColor=INK, textAnchor="end"))
        d.add(Rect(left, y, x(v) - left, bar_h, rx=1.2, ry=1.2, fillColor=colors.HexColor(hexc),
                   strokeColor=PAPER, strokeWidth=1))
        d.add(String(x(v) + 1.8 * mm, y + 1.3 * mm, usd(v), fontName="DV-B", fontSize=7,
                     fillColor=INK))
    # sale-price reference line
    d.add(Line(x(SALE_PRICE), 8 * mm, x(SALE_PRICE), height - top + 3 * mm,
               strokeColor=NAVY, strokeWidth=1, strokeDashArray=[2, 2]))
    d.add(String(x(SALE_PRICE), height - top + 4.2 * mm, f"Assumed sale price ${SALE_PRICE}/t",
                 fontName="DV-B", fontSize=6.8, fillColor=NAVY, textAnchor="middle"))
    return d


def legend():
    cells = []
    for key in ("open", "disrupted", "banned", "benchmark"):
        hexc, label = STATUS[key]
        cells += [Table([[""]], colWidths=[3 * mm], rowHeights=[3 * mm],
                        style=[("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(hexc)),
                               ("ROUNDEDCORNERS", [1, 1, 1, 1])]),
                  P(label.title() if key != "banned" else "Banned / sanctioned", "small")]
    t = Table([cells], colWidths=[4 * mm, 22 * mm, 4 * mm, 24 * mm, 4 * mm, 34 * mm, 4 * mm, 26 * mm])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 1)]))
    return t


def ranking_table(rows):
    head = ["#", "Country", "Status", "Route to Busan", "Days", "Buy $/t", "Freight $/t",
            "100 t $/t", "1,000 t $/t", "Margin*"]
    data = [[P(h, "headr" if i >= 4 else "head") for i, h in enumerate(head)]]
    styles = []
    for i, r in enumerate(rows, 1):
        c = r["c"]
        if r["lots"]:
            a, b = r["lots"][100], r["lots"][1000]
            nums = [f"{c['transit_days']:g}", usd(c["buy_price_usd_t"]),
                    usd(c["freight_per_20ft_usd"] / CONTAINER_T), usd(a["cost_per_unit"]),
                    f"<b>{usd(b['cost_per_unit'])}</b>", pct(b["margin"])]
        else:
            nums = [f"{c.get('transit_days') or 0:g}", "n/a", "-", "-", "-", "-"]
        data.append([P(str(i), "cell"), P(f"<b>{c['country']}</b>", "cell"), pill(c["status"]),
                     P(c.get("route", ""), "cell")] + [P(n, "cellr") for n in nums])
        if c["status"] not in ("open", "benchmark"):
            styles.append(("TEXTCOLOR", (0, i), (-1, i), INK_3))
    widths = [6, 27, 19, 46, 9, 13, 14, 15, 16, 13]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("LINEBELOW", (0, 0), (-1, 0), 1, GOLD),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW]),
        ("LINEBELOW", (0, 1), (-1, -1), 0.3, HAIR),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ] + styles))
    return t


def breakdown_table(r):
    """Per-tonne cost stack for one country at 1,000 t."""
    x = r["lots"][1000]
    q = 1000
    lines = [
        ("Purchase", x["goods_value"]),
        ("Origin fees + bagging", x["fob_value"] - x["goods_value"]),
        ("Freight", x["freight"]),
        ("Insurance", x["insurance"]),
        ("Korean duty", x["duty"]),
        ("Busan + delivery", x["destination_charges"]),
        ("Finance + FX", x["financing_cost"] + x["fx_buffer"]),
    ]
    data = [[P(k, "card"), P(usd(v / q), "cellr")] for k, v in lines]
    data.append([P("<b>Delivered</b>", "card"), P(f"<b>{usd(x['cost_per_unit'])}</b>", "cellr")])
    t = Table(data, colWidths=[31 * mm, 17 * mm])
    t.setStyle(TableStyle([
        ("LINEABOVE", (0, -1), (-1, -1), 0.8, GOLD),
        ("TOPPADDING", (0, 0), (-1, -1), 1.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t


def card(r, width):
    c = r["c"]
    conf = {"high": "High", "medium": "Medium", "low": "Low"}.get(c.get("confidence"), "-")
    left = [
        Table([[P(c["country"], "card_t"), pill(c["status"])]], colWidths=[width - 48 * mm - 30 * mm, 20 * mm],
              style=[("LEFTPADDING", (0, 0), (-1, -1), 0), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]),
        Spacer(1, 2),
        P(f"<font color='#5A6472'>{c.get('status_note', '')}</font>", "card"),
        Spacer(1, 3),
        P(f"<b>Route:</b> {c.get('route', '')} ({c.get('mode', '')}, ~{c.get('transit_days', 0):g} days)", "card"),
        P(f"<b>Buy:</b> {usd(c['buy_price_usd_t']) + '/t ' + c.get('buy_basis', '') if c.get('buy_price_usd_t') else 'n/a'}"
          f"  ·  <b>Freight:</b> {usd(c.get('freight_per_20ft_usd') or 0)}/20ft"
          f"  ·  <b>Duty:</b> {(c.get('korea_duty_rate') or 0):.0%} ({c.get('fta') or 'no FTA'})", "card"),
        P(f"<b>Confidence:</b> {conf}", "card"),
    ]
    right = breakdown_table(r) if r["lots"] else P("No price available", "small")
    t = Table([[left, right]], colWidths=[width - 52 * mm, 52 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.4, HAIR),
        ("LINEBEFORE", (0, 0), (0, -1), 2.2, colors.HexColor(STATUS.get(c["status"], ("#8C95A1",))[0])),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ]))
    return KeepTogether([t, Spacer(1, 5)])


def callout(text):
    t = Table([[P(text, "body")]], colWidths=[W - 2 * M])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("LINEBEFORE", (0, 0), (0, -1), 2.5, GOLD),
        ("BOX", (0, 0), (-1, -1), 0.4, HAIR),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    return t


# ---------------------------------------------------------------- document

def build(src, out):
    with open(src, encoding="utf-8") as f:
        countries = json.load(f)
    rows = evaluate(countries)
    importable = [r for r in rows if r["lots"] and r["c"]["status"] == "open"]
    best = importable[0] if importable else None
    best_cis = next((r for r in importable if r["c"].get("cis")), None)
    n_open = sum(1 for r in rows if r["c"]["status"] == "open" and r["lots"])
    n_total = sum(1 for r in rows if r["c"]["status"] != "benchmark" and r["lots"])

    doc = BaseDocTemplate(out, pagesize=A4, title="Sulphur to South Korea: delivered cost by country",
                          author="Trade Advisor", leftMargin=M, rightMargin=M,
                          topMargin=18 * mm, bottomMargin=18 * mm)
    doc.kpis = [
        ("Cheapest open source", best["c"]["country"] if best else "-",
         f"{usd(best['lots'][1000]['cost_per_unit'])}/t delivered\n1,000 t lot" if best else ""),
        ("Best CIS source", best_cis["c"]["country"] if best_cis else "-",
         f"{usd(best_cis['lots'][1000]['cost_per_unit'])}/t delivered\n1,000 t lot" if best_cis else ""),
        ("Countries open now", f"{n_open} of {n_total}", "others banned, sanctioned\nor disrupted (Oct 2026)"),
    ]
    frame = Frame(M, 18 * mm, W - 2 * M, H - 36 * mm, id="f", leftPadding=0, rightPadding=0)
    doc.addPageTemplates([PageTemplate("cover", frames=[frame], onPage=cover),
                          PageTemplate("inner", frames=[frame], onPage=inner)])

    story = [NextPageTemplate("inner"), PageBreak()]

    # Executive summary
    story += section("01 · Executive summary", "Where to buy, and what it costs delivered",
                     "Every realistic sulphur source was costed the same way: purchase price at origin, "
                     "export fees and bagging, freight to Busan in 20ft containers (25 t each), insurance, "
                     "Korean duty, port and hazmat delivery, financing and an FX buffer.")
    summary = []
    if best:
        b = best["lots"][1000]
        summary.append(f"<b>Cheapest legal source today: {best['c']['country']}</b> at <b>{usd(b['cost_per_unit'])}/t</b> "
                       f"delivered for 1,000 t ({b['margin']:.0%} margin at ${SALE_PRICE}/t).")
    if best_cis:
        b = best_cis["lots"][1000]
        summary.append(f"<b>Best CIS source: {best_cis['c']['country']}</b> at <b>{usd(b['cost_per_unit'])}/t</b> "
                       f"({b['margin']:.0%} margin).")
    bench = next((r for r in rows if r["c"]["status"] == "benchmark" and r["lots"]), None)
    if bench:
        summary.append(f"<b>Korean domestic benchmark ({bench['c']['country']}):</b> "
                       f"{usd(bench['lots'][1000]['cost_per_unit'])}/t, which is what your clients can already get locally.")
    summary.append(f"Only <b>{n_open} of {n_total}</b> priced source countries are open; the rest are under export bans, "
                   "sanctions or shipping disruption (marked in grey in the tables).")
    story.append(callout("<br/><br/>".join(summary)))
    story.append(Spacer(1, 10))

    story += section("02 · Comparison", "Delivered cost per tonne, 1,000 t lot",
                     f"Bars to the left of the dashed line are below the assumed ${SALE_PRICE}/t sale price; "
                     "the gap is your gross profit per tonne.")
    story.append(bar_chart(rows, W - 2 * M))
    story.append(Spacer(1, 3))
    story.append(legend())

    story.append(PageBreak())
    story += section("03 · Ranking", "Every country, ranked by delivered cost",
                     "Cost per tonne delivered to the client in Korea, ex-VAT (VAT is recoverable). "
                     f"*Margin at 1,000 t and an assumed sale price of ${SALE_PRICE}/t.")
    story.append(ranking_table(rows))

    story.append(PageBreak())
    story += section("04 · Country profiles", "Route, status and cost stack per country",
                     "Cost stack per tonne at 1,000 t. The coloured edge shows the export status.")
    for r in rows:
        story.append(card(r, W - 2 * M))

    story.append(PageBreak())
    story += section("05 · Method & sources", "How the numbers were built")
    method = [
        f"Lot sizes {', '.join(f'{q:,} t' for q in LOTS)}; 20ft containers of {CONTAINER_T} t bagged sulphur.",
        f"Origin: export documents, certificate of origin and broker ${DOCS:,} per shipment; bagging ${BAGGING}/t.",
        "Insurance 0.3% of (FOB + freight) × 110%. Korean duty on CIF: 0% WTO rate for WTO members and FTA partners; 2% basic rate for non-WTO origins (UZ, TM, AZ, BY, IR, IQ).",
        f"Korea: Busan THC/D-O + hazmat-licensed truck ${DEST_PER_CONTAINER} per container; customs broker + "
        f"chemical confirmation ${BROKER_KR} per shipment. VAT 10% recoverable, so excluded from cost.",
        "Financing 8%/yr on landed cost over transit + 30 days payment terms; FX buffer 1%.",
        "Purchase prices and freight are October 2026 benchmarks and estimates, not supplier quotes. "
        "Bulk vessel shipments (3,000 t+) are roughly $70/t cheaper than containers.",
        "Hazardous-material rules: sulphur is a Class 2 flammable solid in Korea (designated quantity 100 kg); "
        "deliver from port straight to a licensed client site. K-REACH coverage needed at ≥ 1 t/yr.",
    ]
    for m_ in method:
        story.append(P(f"•  {m_}", "body"))
        story.append(Spacer(1, 2))
    story.append(Spacer(1, 8))
    story.append(P("SOURCES BY COUNTRY", "kicker"))
    for r in rows:
        srcs = r["c"].get("sources") or []
        if srcs:
            story.append(P(f"<b>{r['c']['country']}:</b> " + " · ".join(srcs[:4]), "small"))
            story.append(Spacer(1, 1.5))

    doc.build(story)


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        ROOT, "knowledge", "sessions", "2026-10-30-sulphur-world-sources.json")
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        ROOT, "reports", "sulphur-world-sources-2026-10-30.pdf")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    build(src, out)
    print(os.path.abspath(out))
