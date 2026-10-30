#!/usr/bin/env python3
"""Noir-style pitch deck (landscape PDF) on the sulphur import opportunity.

Numbers for the Top-3 slide come from the same model as the world report
(knowledge/sessions/2026-10-30-sulphur-world-sources.json + landed_cost.py).

    python3 tools/make_pitch_deck.py [out.pdf]
"""

import json
import os
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import Paragraph

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import make_world_report as wr  # noqa: E402  (registers DejaVu fonts)

W, H = landscape(A4)
M = 18 * mm

BLACK = colors.HexColor("#0A0A0A")
CARD = colors.HexColor("#151515")
CARD_2 = colors.HexColor("#1E1E1E")
LINE = colors.HexColor("#2C2C2C")
WHITE = colors.HexColor("#F5F3EE")
GREY = colors.HexColor("#A3A09A")
DIM = colors.HexColor("#6E6B66")
SULPHUR = colors.HexColor("#E8C547")   # the one accent: sulphur yellow
RED = colors.HexColor("#D9534F")
GREEN = colors.HexColor("#5CB85C")


def style(size=11, color=WHITE, font="DV", leading=None, align=0):
    return ParagraphStyle("s", fontName=font, fontSize=size, leading=leading or size * 1.38,
                          textColor=color, alignment=align)


def para(c, text, x, y_top, w, st):
    """Draw a paragraph with its top-left corner at (x, y_top); return its height."""
    p = Paragraph(text, st)
    _, h = p.wrap(w, H)
    p.drawOn(c, x, y_top - h)
    return h


def background(c, n, total, section):
    c.setFillColor(BLACK)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    # film-grain style hairlines
    c.setStrokeColor(colors.HexColor("#101010"))
    c.setLineWidth(0.4)
    for i in range(0, int(W), 9):
        c.line(i, 0, i + 120, H)
    c.setFillColor(SULPHUR)
    c.rect(M, H - 13 * mm, 8 * mm, 0.8 * mm, stroke=0, fill=1)
    c.setFont("DV-B", 7.5)
    c.setFillColor(GREY)
    c.drawString(M + 11 * mm, H - 13.6 * mm, section.upper())
    c.drawRightString(W - M, H - 13.6 * mm, "SULPHUR · KOREA · 2026")
    c.setFillColor(DIM)
    c.setFont("DV", 7)
    c.drawString(M, 9 * mm, "Internal pitch · estimates from Oct 2026 benchmarks, not quotes · confirm before committing money")
    c.drawRightString(W - M, 9 * mm, f"{n:02d} / {total:02d}")


def title(c, kicker, text, y=H - 30 * mm):
    c.setFillColor(SULPHUR)
    c.setFont("DV-B", 8)
    c.drawString(M, y, kicker.upper())
    return y - 4 * mm - para(c, text, M, y - 3 * mm, W - 2 * M, style(25, WHITE, "DV-B", 30))


def card(c, x, y_top, w, h, fill=CARD, edge=None):
    c.setFillColor(fill)
    c.roundRect(x, y_top - h, w, h, 2.5 * mm, stroke=0, fill=1)
    if edge:
        c.setFillColor(edge)
        c.rect(x, y_top - 0.9 * mm, w, 0.9 * mm, stroke=0, fill=1)


def card_text(c, x, y_top, w, head, body, head_color=SULPHUR, size=10.2):
    h = para(c, f"<b>{head}</b>", x, y_top, w, style(11.5, head_color, "DV-B"))
    return h + 2 * mm + para(c, body, x, y_top - h - 2 * mm, w, style(size, GREY, leading=size * 1.45))


# ---------------------------------------------------------------- slides

def s_cover(c, n, t, ctx):
    c.setFillColor(BLACK)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    # big sulphur "S" glyph, cropped, as a noir motif
    c.setFillColor(colors.HexColor("#141414"))
    c.setFont("DV-B", 520)
    c.drawString(W - 175 * mm, -40 * mm, "S")
    c.setFillColor(SULPHUR)
    c.circle(W - 62 * mm, H - 58 * mm, 15 * mm, stroke=0, fill=1)
    c.setFillColor(BLACK)
    c.setFont("DV-B", 15)
    c.drawCentredString(W - 62 * mm, H - 63.5 * mm, "S")
    c.setFillColor(BLACK)
    c.setFont("DV", 6.5)
    c.drawCentredString(W - 62 * mm, H - 52 * mm, "16")
    c.setFillColor(SULPHUR)
    c.rect(M, H - 62 * mm, 14 * mm, 1.1 * mm, stroke=0, fill=1)
    c.setFont("DV-B", 8.5)
    c.drawString(M, H - 56 * mm, "INTERNAL PITCH  ·  OCTOBER 2026")
    c.setFillColor(WHITE)
    c.setFont("DV-B", 46)
    c.drawString(M, H - 86 * mm, "Sulphur.")
    c.setFont("DV-B", 22)
    c.drawString(M, H - 101 * mm, "The yellow trade into South Korea")
    c.setFillColor(GREY)
    c.setFont("DV", 11)
    c.drawString(M, H - 114 * mm, "What it is · what we can do as Kazakh & Uzbek nationals · good prices · where to buy · hidden risks")
    c.setFont("DV", 9)
    c.setFillColor(DIM)
    c.drawString(M, 22 * mm, "Сера · Sulphur · HS 2503.00")
    c.drawString(M, 17 * mm, "Prepared by Trade Advisor for the team. All prices are estimates, not supplier quotes.")


def s_what(c, n, t, ctx):
    background(c, n, t, "01 · The product")
    y = title(c, "What is sulphur (сера)?", "A by-product of oil & gas that feeds the world's fertilizer")
    facts = [
        ("Yellow element, S", "Solid at room temperature, melts at ~115 °C. Traded as <b>lump</b>, <b>granular</b> "
                              "(formed pellets), <b>liquid</b> (heated tankers) or <b>powder</b>."),
        ("Recovered, not mined", "Over 90% is <b>recovered</b> when refineries and gas plants remove it from oil and gas. "
                            "Supply follows oil & gas output, not demand."),
        ("Where it goes", "About half becomes <b>sulphuric acid → phosphate fertilizer</b>. The rest: metal leaching "
                          "(copper, nickel for batteries), chemicals, rubber vulcanization, agriculture."),
        ("How it is coded", "Customs code <b>HS 2503.00</b>. In Korea a <b>hazardous material</b> (Class 2 flammable "
                            "solid): over 100 kg needs licensed storage."),
    ]
    cw = (W - 2 * M - 3 * 6 * mm) / 4
    top = y - 6 * mm
    for i, (h, b) in enumerate(facts):
        x = M + i * (cw + 6 * mm)
        card(c, x, top, cw, 82 * mm, edge=SULPHUR if i == 0 else None)
        c.setFillColor(SULPHUR)
        c.setFont("DV-B", 22)
        c.drawString(x + 6 * mm, top - 15 * mm, f"0{i + 1}")
        card_text(c, x + 6 * mm, top - 21 * mm, cw - 12 * mm, h, b)
    para(c, "<b>Why it matters now:</b> 2026 is a supply shock. The Strait of Hormuz is effectively closed, and Russia, "
            "Kazakhstan, India and Turkey restricted exports. Prices jumped from ~$500/t in January to $800–1,000/t mid-year. "
            "Shortage creates margin, and it will not last forever.",
         M, top - 90 * mm, W - 2 * M, style(10.5, WHITE, leading=15))


def s_market(c, n, t, ctx):
    background(c, n, t, "02 · The market")
    y = title(c, "2026 price shock", "Prices spiked on war and export bans, now easing")
    pts = [("Jan 2026", 512, "pre-crisis"), ("Q2 contract", 570, "Hormuz closes"),
           ("May (Kuwait)", 765, "Russia ban extended"), ("Aug (ME peak)", 930, "record highs"),
           ("Oct spot", 765, "easing")]
    x0, y0, cw_, ch = M + 4 * mm, 38 * mm, 128 * mm, 80 * mm
    vmax = 1000
    c.setStrokeColor(LINE)
    c.setLineWidth(0.5)
    for v in (250, 500, 750, 1000):
        yy = y0 + ch * v / vmax
        c.line(x0, yy, x0 + cw_, yy)
        c.setFillColor(DIM)
        c.setFont("DV", 6.5)
        c.drawRightString(x0 - 2 * mm, yy - 1, f"${v}")
    bw = cw_ / len(pts) * 0.56
    for i, (lab, v, note) in enumerate(pts):
        bx = x0 + (i + 0.22) * cw_ / len(pts)
        c.setFillColor(SULPHUR if lab.startswith("Aug") else colors.HexColor("#8A7A3A"))
        c.roundRect(bx, y0, bw, ch * v / vmax, 1.2 * mm, stroke=0, fill=1)
        c.setFillColor(WHITE)
        c.setFont("DV-B", 9)
        c.drawCentredString(bx + bw / 2, y0 + ch * v / vmax + 2.5 * mm, f"${v}")
        c.setFillColor(GREY)
        c.setFont("DV", 7)
        c.drawCentredString(bx + bw / 2, y0 - 5 * mm, lab)
        c.setFillColor(DIM)
        c.drawCentredString(bx + bw / 2, y0 - 9 * mm, note)
    c.setFillColor(GREY)
    c.setFont("DV", 7.5)
    c.drawString(x0, y0 + ch + 6 * mm, "Middle East FOB sulphur, USD per tonne (approximate benchmarks)")

    rx = M + 150 * mm
    rw = W - M - rx
    items = [
        ("Supply is cut", "Hormuz traffic at 2–7% of normal. Russia bans exports to 31 Dec 2026. Kazakhstan suspended "
                          "exports on 27 Jun 2026. India and Turkey restrict too."),
        ("Korea is a net exporter", "S-Oil, SK and GS Caltex produce sulphur at home (~$826/t delivered locally). "
                                    "That is the price we must beat."),
        ("Direction: down", "October contracts fell $45–70 vs September. Analysts expect normalisation in 2027. "
                            "Never hold unsold stock."),
    ]
    yy = H - 52 * mm
    for h, b in items:
        card(c, rx, yy, rw, 34 * mm)
        card_text(c, rx + 6 * mm, yy - 6 * mm, rw - 12 * mm, h, b, size=9)
        yy -= 39 * mm


def s_capabilities(c, n, t, ctx):
    background(c, n, t, "03 · Our edge")
    y = title(c, "What we can do as Kazakh & Uzbek nationals", "Our passports and languages open doors others cannot")
    cols = [
        ("Kazakhstan citizens", [
            "Russian/Kazakh language: direct talks with Tengiz, Kashagan and traders",
            "Ready the day the Kazakh export ban lifts: cheapest CIS lane (~$905/t delivered)",
            "Can buy on the Turkmen commodity exchange (Kazakh buyers have before)",
            "EAEU know-how: rail, customs and transit through Kazakhstan and Russia",
        ]),
        ("Uzbekistan citizens", [
            "Uzbek exports must be made by an <b>Uzbek resident exporter</b>: an Uzbek colleague can register that company",
            "Access to Uzbekneftegaz / Mubarek (150 kt/yr granular sulphur) and the UzEx exchange",
            "Open source today: no 2026 export ban found (still to be confirmed officially)",
            "Uzbek origin pays 2% Korean duty (non-WTO): budget for it",
        ]),
        ("In South Korea (both)", [
            "Business allowed on visas <b>F-2, F-4, F-5, F-6, D-8, D-9</b>. D-2, D-10, E-9, H-2: introducer only",
            "Setup: business registration (Hometax) → customs code (UNI-PASS) → trade number (KITA, free)",
            "Chemicals: K-REACH coverage at ≥ 1 t/yr + chemical confirmation per import",
            "We already have <b>client leads</b> in Korea: demand is the hardest part",
        ]),
    ]
    cw = (W - 2 * M - 2 * 7 * mm) / 3
    top = y - 6 * mm
    for i, (h, pts) in enumerate(cols):
        x = M + i * (cw + 7 * mm)
        card(c, x, top, cw, 100 * mm, edge=SULPHUR)
        c.setFillColor(WHITE)
        c.setFont("DV-B", 13)
        c.drawString(x + 6 * mm, top - 12 * mm, h)
        yy = top - 19 * mm
        for ptxt in pts:
            c.setFillColor(SULPHUR)
            c.circle(x + 7.5 * mm, yy - 2.2 * mm, 0.9 * mm, stroke=0, fill=1)
            yy -= para(c, ptxt, x + 11 * mm, yy, cw - 17 * mm, style(10, GREY, leading=14)) + 4.5 * mm


def s_prices(c, n, t, ctx):
    background(c, n, t, "04 · Price compass")
    y = title(c, "What prices are good?", "Know three numbers before any call")
    lanes = [
        ("BUY  ·  CIS rail station (FCA), per tonne", 500, 760,
         [(500, 600, GREEN, "GOOD ≤ $600"), (600, 650, SULPHUR, "OK $600–650"), (650, 760, RED, "WALK AWAY > $680")]),
        ("SELL  ·  delivered to Korean client, per tonne", 820, 1060,
         [(820, 880, RED, "LOSS < $880"), (880, 950, SULPHUR, "THIN $880–950"), (950, 1060, GREEN, "GOOD ≥ $950")]),
    ]
    top = y - 10 * mm
    bar_w = W - 2 * M - 70 * mm
    for label, lo, hi, zones in lanes:
        c.setFillColor(WHITE)
        c.setFont("DV-B", 10)
        c.drawString(M, top, label)
        by = top - 16 * mm
        for a, b, col, txt in zones:
            x1 = M + bar_w * (a - lo) / (hi - lo)
            x2 = M + bar_w * (b - lo) / (hi - lo)
            c.setFillColor(col)
            c.rect(x1, by, x2 - x1 - 1.2, 8 * mm, stroke=0, fill=1)
            c.setFillColor(BLACK)
            c.setFont("DV-B", 8)
            c.drawCentredString((x1 + x2) / 2, by + 2.8 * mm, txt)
        c.setFillColor(DIM)
        c.setFont("DV", 7)
        c.drawString(M, by - 4.5 * mm, f"${lo}")
        c.drawRightString(M + bar_w, by - 4.5 * mm, f"${hi}")
        top -= 40 * mm
    rx = M + bar_w + 8 * mm
    rw = W - M - rx
    bench = [("$740–790", "Middle East FOB spot, 22 Oct 2026"),
             ("~$826", "Korean refiners, delivered locally (our ceiling)"),
             ("~$859", "Best import: China, delivered Busan"),
             ("$280/t", "Minimum gap sell − buy for 10% margin (containers)")]
    yy = y - 6 * mm
    for v, d in bench:
        card(c, rx, yy, rw, 22 * mm)
        c.setFillColor(SULPHUR)
        c.setFont("DV-B", 15)
        c.drawString(rx + 5 * mm, yy - 9 * mm, v)
        para(c, d, rx + 5 * mm, yy - 11.5 * mm, rw - 10 * mm, style(7.8, GREY, leading=10))
        yy -= 25 * mm
    para(c, "<b>Rule of thumb:</b> profit per tonne = sale price − buy price − ~$200 logistics (containers) or ~$125 (bulk, 3,000 t+). "
            "Every <b>$50/t</b> more from the client adds <b>~$50,000</b> per 1,000 t.",
         M, 46 * mm, bar_w, style(10, WHITE, leading=14))


def s_supply(c, n, t, ctx):
    background(c, n, t, "05 · Where to buy")
    y = title(c, "Where to look for supply", "Open today, watch closely, or avoid")
    groups = [
        ("OPEN: START HERE", GREEN, [
            ("China", "best margin, 3 days to Busan, scarce export volumes"),
            ("Japan · Taiwan", "refinery sulphur, 3–4 days, get FOB quotes"),
            ("Uzbekistan", "best CIS, rail via KZ + China, ~30 days"),
            ("Turkmenistan", "state exchange, confirmed foreign buyers in Oct 2026"),
            ("Oman · Singapore", "Oman outside Hormuz; Singapore: check true origin"),
        ]),
        ("WATCH: MAY OPEN", SULPHUR, [
            ("Kazakhstan", "export ban since 27 Jun 2026; reports of lifting unconfirmed"),
            ("Russia", "ban to 31 Dec 2026; sanctions & payment risk remain"),
            ("Gulf (UAE, Qatar, Saudi, Kuwait)", "huge supply, blocked by Hormuz crisis"),
            ("USA · Canada · Malaysia", "open but long haul, currently at a loss"),
        ]),
        ("AVOID", RED, [
            ("Iran · Belarus", "sanctions"),
            ("India · Turkey", "export restrictions in 2026"),
            ("Kyrgyzstan", "no production; Kazakh-origin stock = ban circumvention risk"),
            ("Azerbaijan", "tiny volumes, very long route"),
        ]),
    ]
    cw = (W - 2 * M - 2 * 7 * mm) / 3
    top = y - 6 * mm
    for i, (h, col, items) in enumerate(groups):
        x = M + i * (cw + 7 * mm)
        card(c, x, top, cw, 104 * mm, edge=col)
        c.setFillColor(col)
        c.setFont("DV-B", 10)
        c.drawString(x + 6 * mm, top - 11 * mm, h)
        yy = top - 18 * mm
        for name, note in items:
            yy -= para(c, f"<b><font color='#F5F3EE'>{name}</font></b><br/>{note}", x + 6 * mm, yy,
                       cw - 12 * mm, style(9.8, GREY, leading=13.5)) + 4.5 * mm


def s_top3(c, n, t, ctx):
    background(c, n, t, "06 · Best routes")
    y = title(c, "Top 3 routes by profit", "1,000 t lot, delivered Busan → client at $900/t")
    cw = (W - 2 * M - 2 * 7 * mm) / 3
    top = y - 6 * mm
    for i, r in enumerate(ctx["top"]):
        x = M + i * (cw + 7 * mm)
        cc = r["c"]
        card(c, x, top, cw, 98 * mm, edge=SULPHUR)
        c.setFillColor(SULPHUR)
        c.setFont("DV-B", 30)
        c.drawString(x + 6 * mm, top - 17 * mm, f"{i + 1}")
        c.setFillColor(WHITE)
        c.setFont("DV-B", 16)
        c.drawString(x + 18 * mm, top - 15.5 * mm, cc["country"])
        steps = [s_.strip() for s_ in cc["route"].split("->")]
        yy = top - 25 * mm
        yy -= para(c, "  →  ".join(steps), x + 6 * mm, yy, cw - 12 * mm, style(9.5, GREY, leading=13)) + 5 * mm
        stats = [("Delivered", f"{wr.usd(r['lots'][1000]['cost_per_unit'])}/t"),
                 ("Transit", f"~{cc['transit_days']:g} days"),
                 ("Profit 1,000 t", wr.usd(wr.profit(r, 1000))),
                 ("at $950/t", wr.usd(wr.profit(r, 1000, 950))),
                 ("Per year (12 × 1,000 t)", wr.usd(wr.profit(r, 1000) * 12)),
                 ("Price for 10% margin", f"{wr.usd(wr.price_for_margin(r))}/t")]
        for j, (k, v) in enumerate(stats):
            sx = x + 6 * mm + (j % 2) * (cw - 12 * mm) / 2
            sy = yy - (j // 2) * 17 * mm
            c.setFillColor(DIM)
            c.setFont("DV-B", 6.5)
            c.drawString(sx, sy - 3 * mm, k.upper())
            c.setFillColor(WHITE)
            c.setFont("DV-B", 14)
            c.drawString(sx, sy - 10 * mm, v)
    bc = ctx["best_cis"]
    if bc:
        para(c, f"<b>Best CIS lane: {bc['c']['country']}</b>: delivered {wr.usd(bc['lots'][1000]['cost_per_unit'])}/t, "
                f"{wr.usd(wr.profit(bc, 1000))} at $900/t but {wr.usd(wr.profit(bc, 1000, 950))} at $950/t. "
                f"CIS works when the client pays ≥ ~{wr.usd(wr.price_for_margin(bc))}/t.",
             M, 30 * mm, W - 2 * M, style(9.5, GREY, leading=13))


def s_risks(c, n, t, ctx):
    background(c, n, t, "07 · Подводные камни")
    y = title(c, "Hidden risks (подводные камни)", "What can sink this deal, and how we protect ourselves")
    risks = [
        ("Bans change overnight", "KZ, RU, IN, TR all restricted exports in 2026.", "Contract with force-majeure + two suppliers."),
        ("Korea makes its own", "Local refiners sell at ~$826/t.", "Win on grade, volume or reliability, not just price."),
        ("Prices are falling", "Contracts down $45–70 in Oct; 2027 normalisation.", "Back-to-back only: never stock."),
        ("Small lots lose", "1–10 t pay ~$1,200/t in fixed costs.", "Minimum 500 t per deal, or broker."),
        ("Hazmat rules", "Class 2 flammable solid; >100 kg needs licensed storage.", "Port → client direct delivery."),
        ("Chemical registration", "K-REACH at ≥ 1 t/yr; chemical confirmation each import.", "Supplier's Only Representative."),
        ("Fake origin / sanctions", "Trader stock may be Kazakh, Iranian or Russian origin.", "Check origin certificate, not seller."),
        ("Commodity scams", "Fake offers with ‘SGS’, ‘ICPO/FCO’ chains and advance fees.", "Never pay upfront; verify producer directly."),
        ("Quality disputes", "Purity, moisture, ash, acidity vary by plant.", "Spec ≥ 99.5% S + SGS inspection at loading."),
        ("Transit & freight", "Rail bans, border queues, war-risk surcharges.", "Fixed forwarder quote + insurance."),
        ("Payment risk", "Client delays or defaults.", "Letter of credit at sight from client."),
        ("Visa limits", "Some visas forbid running a business.", "Check visa; else partner company imports."),
    ]
    cols, rows = 3, 4
    cw = (W - 2 * M - (cols - 1) * 5 * mm) / cols
    ch = 25.5 * mm
    top = y - 4 * mm
    for i, (h, risk, fix) in enumerate(risks):
        x = M + (i % cols) * (cw + 5 * mm)
        yy = top - (i // cols) * (ch + 3.5 * mm)
        card(c, x, yy, cw, ch)
        c.setFillColor(RED)
        c.rect(x, yy - ch, 1.1 * mm, ch, stroke=0, fill=1)
        c.setFillColor(DIM)
        c.setFont("DV-B", 7)
        c.drawRightString(x + cw - 4 * mm, yy - 5.5 * mm, f"{i + 1:02d}")
        para(c, f"<b>{h}</b>", x + 5 * mm, yy - 3.5 * mm, cw - 15 * mm, style(9.5, WHITE, "DV-B"))
        para(c, f"{risk}<br/><font color='#E8C547'>→ {fix}</font>", x + 5 * mm, yy - 9.5 * mm, cw - 10 * mm,
             style(8.2, GREY, leading=11))


def s_plan(c, n, t, ctx):
    background(c, n, t, "08 · The plan")
    y = title(c, "How we start", "Low risk first, capital only when the numbers work")
    steps = [
        ("NOW", "Broker", "Introduce Korean clients to verified suppliers for 1–3% commission. "
                          "~$9–27k on 1,000 t. No capital, no hazmat risk."),
        ("30 DAYS", "Validate", "Get client volume, grade and current price in writing. Get FOB/FCA quotes from "
                                "China, Japan, Uzbekistan and Turkmenistan + two forwarder quotes."),
        ("60 DAYS", "First trade", "500–1,000 t in containers, back-to-back, client LC at sight, "
                                   "buy ≤ $600/t CIS or best Asian FOB."),
        ("90+ DAYS", "Scale", "Monthly contract; 3,000 t+ bulk to a fertilizer or acid plant (10–16% margin). "
                              "Ready for Kazakh supply when the ban lifts."),
    ]
    cw = (W - 2 * M - 3 * 6 * mm) / 4
    top = y - 8 * mm
    c.setStrokeColor(SULPHUR)
    c.setLineWidth(1)
    c.line(M + 6 * mm, top + 3 * mm, W - M - 6 * mm, top + 3 * mm)
    for i, (when, h, b) in enumerate(steps):
        x = M + i * (cw + 6 * mm)
        c.setFillColor(SULPHUR)
        c.circle(x + 6 * mm, top + 3 * mm, 1.8 * mm, stroke=0, fill=1)
        card(c, x, top - 4 * mm, cw, 70 * mm)
        c.setFillColor(SULPHUR)
        c.setFont("DV-B", 8)
        c.drawString(x + 6 * mm, top - 12 * mm, when)
        card_text(c, x + 6 * mm, top - 16 * mm, cw - 12 * mm, h, b, head_color=WHITE)
    card(c, M, 52 * mm, W - 2 * M, 26 * mm, fill=CARD_2, edge=SULPHUR)
    para(c, "<b>The one question that decides everything:</b> what do our Korean clients pay today, and how many tonnes per month? "
            "~1,000 t/month at ≥ $950/t = a real business. 10–50 t at a time = broker only.",
         M + 7 * mm, 46 * mm, W - 2 * M - 14 * mm, style(11, WHITE, leading=15.5))


SLIDES = [s_cover, s_what, s_market, s_capabilities, s_prices, s_supply, s_top3, s_risks, s_plan]


def build(out):
    with open(os.path.join(ROOT, "knowledge", "sessions", "2026-10-30-sulphur-world-sources.json"),
              encoding="utf-8") as f:
        rows = wr.evaluate(json.load(f))
    ranked = wr.ranked_by_profit(rows)
    ctx = {"top": ranked[:3], "best_cis": next((r for r in ranked if r["c"].get("cis")), None)}
    c = rl_canvas.Canvas(out, pagesize=(W, H))
    c.setTitle("Sulphur: the yellow trade into South Korea")
    c.setAuthor("Trade Advisor")
    for i, slide in enumerate(SLIDES, 1):
        slide(c, i, len(SLIDES), ctx)
        c.showPage()
    c.save()


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "reports", "sulphur-pitch-noir-2026-10-30.pdf")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    build(out)
    print(os.path.abspath(out))
