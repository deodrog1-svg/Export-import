#!/usr/bin/env python3
"""Build reports/sulphur-cis-korea-2026-10-30.pdf from the saved scenarios."""

import json
import os
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (KeepTogether, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.dirname(__file__))
from landed_cost import calculate_route, compare  # noqa: E402

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("DV", f"{FONT_DIR}/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DV-B", f"{FONT_DIR}/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B")

NAVY = colors.HexColor("#1F3A5F")
LIGHT = colors.HexColor("#EEF2F7")
RED = colors.HexColor("#B3261E")
GREEN = colors.HexColor("#1E7B34")

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Title"], fontName="DV-B", fontSize=20, textColor=NAVY,
                    alignment=TA_LEFT, spaceAfter=4)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontName="DV-B", fontSize=13.5,
                    textColor=NAVY, spaceBefore=10, spaceAfter=5)
BODY = ParagraphStyle("B", parent=ss["Normal"], fontName="DV", fontSize=9.5, leading=13.5)
SMALL = ParagraphStyle("S", parent=BODY, fontSize=8, leading=10.5, textColor=colors.HexColor("#444444"))
CELL = ParagraphStyle("C", parent=BODY, fontSize=8.3, leading=10.5)
CELLB = ParagraphStyle("CB", parent=CELL, fontName="DV-B", textColor=colors.white)
BOX = ParagraphStyle("Box", parent=BODY, backColor=LIGHT, borderPadding=7, borderColor=NAVY,
                     borderWidth=0.6, spaceBefore=6, spaceAfter=10)


def p(text, style=BODY):
    return Paragraph(text, style)


def bullets(items):
    return [p(f"• {t}") for t in items]


def table(rows, widths, money_cols=(), bold_last=False):
    data = [[p(str(c), CELLB) for c in rows[0]]]
    for row in rows[1:]:
        data.append([p(str(c), CELL) for c in row])
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#B8C2CF")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    for c in money_cols:
        style.append(("ALIGN", (c, 1), (c, -1), "RIGHT"))
    if bold_last:
        style.append(("FONTNAME", (0, -1), (-1, -1), "DV-B"))
    t.setStyle(TableStyle(style))
    return t


def money(x):
    s = f"{abs(x):,.0f}"
    return f"−${s}" if x < 0 else f"${s}"


def load(name):
    with open(os.path.join(ROOT, "knowledge", "sessions", name), encoding="utf-8") as f:
        return json.load(f)


def short(name):
    return {"UZ": "Uzbekistan", "TM": "Turkmenistan", "KG": "Kyrgyzstan"}[name[:2]]


def lot_breakdown(s, route):
    """Per-tonne cost lines for one route of a lot scenario."""
    x = calculate_route(s, route)
    q = s["quantity"]
    return x, [
        ("Sulphur purchase price", x["goods_value"]),
        ("Export docs, certificate of origin, broker, bagging", x["fob_value"] - x["goods_value"]),
        ("Freight to Busan", x["freight"]),
        ("Cargo insurance", x["insurance"]),
        ("Korean import duty (2% of CIF)", x["duty"]),
        ("Busan port, broker, chemical check, hazmat truck", x["destination_charges"]),
        ("Financing (60 days) + FX buffer 1%", x["financing_cost"] + x["fx_buffer"]),
    ], q


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("DV", 7.5)
    canvas.setFillColor(colors.grey)
    canvas.drawString(18 * mm, 10 * mm, "Trade Advisor · Sulphur (сера) CIS → South Korea · 30 Oct 2026 · Estimates: verify before committing money")
    canvas.drawRightString(192 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build(out):
    lots = {q: load(f"2026-10-30-sulphur-{q}t.json") for q in (1, 10, 100)}
    big = load("2026-10-30-sulphur-cis-korea.json")
    story = []

    story += [
        p("Sulphur (сера) Import: CIS → South Korea", H1),
        p("Laws, routes, full cost calculation for 1 t, 10 t, 100 t and 1,000 t · prepared 30 October 2026", SMALL),
        Spacer(1, 6),
        p("<b>Bottom line.</b> Today only <b>Uzbekistan</b> and <b>Turkmenistan</b> can legally export sulphur "
          "among CIS producers; Kazakhstan and Russia have export bans, and Kyrgyzstan produces none. "
          "With 2026 prices and freight, <b>1 t and 10 t lots lose money</b> because fixed costs dominate; "
          "<b>100 t is near break-even</b>; trading starts to work at <b>~500–1,000 t in wagon lots</b> "
          "with a purchase price of <b>≤ $550–570/t</b>. Until a real quote meets that, act as a "
          "<b>commission broker</b> for your Korean clients.", BOX),
    ]

    story.append(p("1. Which countries allow export (October 2026)", H2))
    story.append(table([
        ["Country", "Status", "Verdict"],
        ["Uzbekistan", "Mubarek GPP, 150 kt/yr granulated unit. No 2026 export ban found (not yet officially confirmed).", "<font color='#1E7B34'><b>YES</b></font>, verify"],
        ["Turkmenistan", "Turkmengaz sells via State Commodity Exchange (SCRMET); Oct 2026 buyers from Türkiye, UAE, Singapore.", "<font color='#1E7B34'><b>YES</b></font>"],
        ["Kazakhstan", "Full export ban from 27 Jun 2026 (Energy Ministry), no end date; only Russia-bound exempt.", "<font color='#B3261E'><b>NO</b></font>, blocked"],
        ["Russia", "Export ban to 31 Dec 2026 (Decree 785); EAEU exempt. Sanctions/payment risk after.", "<font color='#B3261E'><b>NO</b></font>, blocked"],
        ["Kyrgyzstan", "No production. Stock is Kazakh-origin → re-export while KZ ban is in force = circumvention risk. Costliest route.", "<font color='#B3261E'><b>NO</b></font>, not recommended"],
        ["Belarus", "Naftan (US) and Mozyr (EU, 23 Jul 2026) refineries sanctioned.", "<font color='#B3261E'><b>NO</b></font>, avoid"],
        ["Azerbaijan", "Small refinery output, no export data, very long route.", "<font color='#B3261E'><b>NO</b></font>, not practical"],
    ], [28, 118, 28]))

    story.append(p("2. South Korea import rules for sulphur (HS 2503.00)", H2))
    story += bullets([
        "<b>Duty:</b> ~0–2% on CIF (basic 2%, WTO 0%); no FTA with KZ, TM, UZ, KG, RU. Confirm on UNI-PASS. 2% used in the model.",
        "<b>VAT:</b> 10% on CIF + duty, recoverable once VAT-registered.",
        "<b>Hazardous Materials Safety Act:</b> sulphur is Class 2 flammable solid, designated quantity 100 kg. "
        "Larger storage needs a licensed facility: deliver port → client directly.",
        "<b>K-REACH:</b> import ≥ 1 t/yr requires registration or coverage by the supplier's Only Representative; "
        "chemical confirmation for each import (KCMA). Sulphur's exact status still to be confirmed.",
        "<b>Market:</b> Korea is a net sulphur exporter (refinery by-product), so clients can buy locally: "
        "you must beat their current price.",
    ])

    story.append(p("3. What you can do as a Kazakhstan citizen resident in Korea", H2))
    story += bullets([
        "Visas allowing a business: <b>F-2, F-4, F-5, F-6, D-8, D-9</b>. D-2, D-10, E-9, H-2 generally cannot "
        "(act only as an introducer or change status). Confirm on HiKorea.",
        "Setup: business registration (Hometax) → customs code (UNI-PASS) → trade business number (KITA, free).",
        "Advantage: Russian language, access to Central Asian exchanges, ready for Kazakh supply when the ban ends.",
    ])

    story.append(p("4. Step-by-step route", H2))
    steps = [
        "Get written client demand: grade (lump/granular), purity, monthly volume, current price, delivery point; ideally an LOI.",
        "Register in Korea: business registration, customs code, KITA trade number.",
        "Arrange K-REACH coverage (Only Representative / letter of access) and chemical confirmation.",
        "Request a written quote and export confirmation from Uzbekneftegaz / Uzbek exchange (or register at SCRMET via a broker).",
        "Book rail: origin → Kazakhstan transit → Altynkol/Khorgos → China → Lianyungang; sea feeder to Busan.",
        "Payment back-to-back: client LC or deposit → your payment to supplier, so you never fund cargo yourself.",
        "Clear Korean customs in Busan; hazmat-licensed truck straight to the client.",
    ]
    story += [p(f"{i}. {s}") for i, s in enumerate(steps, 1)]

    story.append(p("5. Routes", H2))
    story.append(table([
        ["Route", "Path", "Days", "Per 20ft to Busan"],
        ["Uzbekistan", "Mubarek → rail via KZ → Altynkol → Lianyungang → ship to Busan", "~30", "~$3,520"],
        ["Turkmenistan", "Turkmen rail → UZ/KZ transit → Altynkol → Lianyungang → Busan", "~32", "~$3,820"],
        ["Kyrgyzstan", "Truck Bishkek → Torugart → Kashgar → China rail → Lianyungang → Busan", "~38", "~$5,220"],
        ["Caspian (TM)", "Turkmenbashi → Baku → Poti/Batumi → Suez → Busan", "~55", "~$230/t (uneconomic)"],
        ["1 t lots", "Groupage (shared freight), any of the above", "+8", "$450–520/t"],
        ["Avoid", "Iran / Bandar Abbas (sanctions, Hormuz crisis)", "-", "-"],
    ], [26, 98, 14, 36]))
    story.append(p("A 20ft container carries ~25 t of bagged sulphur. China→Busan sea leg: $378–455 per 20ft (Oct 2026).", SMALL))

    story.append(p("6. Full calculation per lot size: Uzbekistan route (cost per tonne, USD)", H2))
    cols = {}
    for q, s in lots.items():
        uz = next(r for r in s["routes"] if r["name"].startswith("UZ"))
        cols[q] = lot_breakdown(s, uz)
    labels = [name for name, _ in cols[1][1]]
    rows = [["Cost item", "1 t", "10 t", "100 t"]]
    for i, label in enumerate(labels):
        rows.append([label] + [f"{cols[q][1][i][1] / q:,.0f}" for q in (1, 10, 100)])
    rows.append(["<b>Total cost per tonne delivered</b>"] + [f"<b>{cols[q][0]['total_cost'] / q:,.0f}</b>" for q in (1, 10, 100)])
    rows.append(["Assumed sale price per tonne (ask clients)"] + [f"{lots[q]['sale_price_per_unit']:,.0f}" for q in (1, 10, 100)])
    rows.append(["<b>Profit / loss on the lot</b>"] + [f"<b>{money(cols[q][0]['gross_profit'])}</b>" for q in (1, 10, 100)])
    rows.append(["Margin"] + [f"{cols[q][0]['margin']:.1%}" for q in (1, 10, 100)])
    story.append(table(rows, [94, 26, 26, 28], money_cols=(1, 2, 3)))
    story.append(p("Purchase price assumed: 1–10 t from a distributor ($900 / $800, bagged); 100 t from producer $680 + $15/t bagging. "
                   "Financing 8%/yr for 30 days transit + 30 days payment terms.", SMALL))

    story.append(p("7. All routes compared: total cost per tonne delivered to client", H2))
    rows = [["Route", "1 t", "10 t", "100 t", "Max buy price for 10% margin (100 t)"]]
    for code in ("UZ", "TM", "KG"):
        row = [short(code)]
        for q, s in lots.items():
            r = next(r for r in s["routes"] if r["name"].startswith(code))
            row.append(f"${calculate_route(s, r)['total_cost'] / q:,.0f}")
        s = lots[100]
        r = next(r for r in s["routes"] if r["name"].startswith(code))
        lo, hi = 0.0, 3000.0
        for _ in range(50):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if calculate_route(s, {**r, "unit_cost": mid})["margin"] >= 0.10 else (lo, mid)
        row.append(f"${lo:,.0f}/t")
        rows.append(row)
    story.append(table(rows, [32, 26, 26, 26, 64], money_cols=(1, 2, 3, 4)))

    story.append(p("8. 1,000 t trial (wagon/container lots, buy $650/t, sell $900/t)", H2))
    rows = [["Route", "Days", "Cost per t", "Profit", "Margin"]]
    for r in compare(big):
        rows.append([r["name"], f"{r['transit_days']:g}", f"${r['cost_per_unit']:,.0f}",
                     money(r["gross_profit"]), f"{r['margin']:.1%}"])
    story.append(table(rows, [100, 14, 22, 22, 16], money_cols=(2, 3, 4)))
    story.append(p("Sensitivity (Turkmenistan route, 1,000 t): buy $550 → +$105k (11.7%); buy $650 → break-even; buy $750 → −$104k.", SMALL))

    story.append(p("9. Market prices (benchmarks)", H2))
    story += bullets([
        "Middle East FOB $740–790/t; CFR China granular $800–850/t (22 Oct 2026).",
        "October 2026 Middle East contracts $820–890/t FOB, $45–70 below September.",
        "Turkey Tupras domestic tender Sept 2026: $866–875/t FCA.",
        "Early 2026 was ~$500–525/t; analysts expect prices to fall in 2027: <b>never hold unsold stock</b>.",
    ])

    story.append(KeepTogether([
        p("10. Recommendation & next steps", H2),
        *bullets([
            "<b>Now:</b> work as a commission broker (1–3%) between Korean clients and large traders: no capital, no hazmat or freight risk.",
            "<b>Trade yourself</b> only with ≥ 100 t (better 500–1,000 t) and a written buy price ≤ ~$570/t, or a client price ≥ ~$1,030/t for 100 t.",
            "<b>Send the Trade Advisor:</b> your visa type; client grade, volume and current price; supplier and forwarder quotes. "
            "The model is re-run in a minute.",
            "<b>2027:</b> watch for the end of the Kazakh ban: Tengiz sulphur via China is the cheapest lane.",
        ]),
    ]))

    story.append(p("Sources (checked 30 Oct 2026)", H2))
    for s in [
        "Kazakhstan ban: petrocouncil.kz; Sulphur Magazine Sept 2026 (bcinsight.crugroup.com)",
        "Russia ban to end-2026: alta.ru/external_news/129074; news.metal.com",
        "Turkmen exchange sales: trend.az/casia/turkmenistan/4234836.html; business.com.tm",
        "Uzbekistan: yuz.uz (Uzbekneftegaz 2022 sales); caspianpost.com (Mubarek granulation)",
        "Kyrgyzstan imports: tradingeconomics.com; akipress.com/news:926519",
        "Belarus sanctions: EU 21st package, 23 Jul 2026 (lovguiden.dk / EUR-Lex)",
        "Korea tariff 2503: treayo.com/en/hs/korea/25030000 (confirm on unipass.customs.go.kr)",
        "Korea hazmat (sulphur 100 kg): kfsi.or.kr",
        "Korea trade in sulphur: oec.world",
        "Prices: chemportal.com.tr; petrolodex.com; fertilizerdaily.com",
        "China→Busan freight: sino-shipping.com",
        "Visas: kowork.kr (confirm on hikorea.go.kr)",
    ]:
        story.append(p(f"• {s}", SMALL))
    story.append(Spacer(1, 6))
    story.append(p("<b>Disclaimer:</b> purchase prices, rail freight and Korean sale prices are estimates, not quotes. "
                   "Laws and prices change; confirm with a licensed Korean customs broker and freight forwarder "
                   "before committing money.", SMALL))

    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=16 * mm, bottomMargin=16 * mm,
                            title="Sulphur Import CIS to South Korea", author="Trade Advisor")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    out = os.path.join(ROOT, "reports", "sulphur-cis-korea-2026-10-30.pdf")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    build(out)
    print(os.path.abspath(out))
