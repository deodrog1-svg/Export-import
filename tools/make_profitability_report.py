#!/usr/bin/env python3
"""Build reports/sulphur-profitability-2026-10-30.pdf: profit vs tonnage and buy price."""

import math
import os
import sys

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, SimpleDocTemplate, Spacer

sys.path.insert(0, os.path.dirname(__file__))
from landed_cost import calculate_route  # noqa: E402
from make_sulphur_report import (BOX, H1, H2, ROOT, SMALL, bullets, money, p,  # noqa: E402
                                 table)

SETTINGS = {"financing_rate_annual": 0.08}


def route(q, buy, sell, bulk=False, duty=0.02, terms=30):
    """Uzbekistan -> Busan, containers (25 t each) or bulk (>= 3,000 t). Estimates."""
    if bulk:
        freight = 105 * q
        origin = [{"name": "Docs", "amount": 1500}]
        dest = [{"name": "Bulk discharge + truck", "amount": 15 * q},
                {"name": "Broker / chemical check", "amount": 350}]
    else:
        n = math.ceil(q / 25)
        freight = 3520 * n
        origin = [{"name": "Docs", "amount": 1500}, {"name": "Bagging", "amount": 15 * q}]
        dest = [{"name": "THC + hazmat truck", "amount": 750 * n},
                {"name": "Broker / chemical check", "amount": 350}]
    return dict(unit_cost=buy, sale_price_per_unit=sell, quantity=q, origin_charges=origin,
                freight=freight, insurance_rate=0.003, duty_basis="CIF", duty_rate=duty,
                vat_rate=0.10, destination_charges=dest, transit_days=30,
                payment_terms_days=terms, fx_buffer_rate=0.01)


def calc(*args, **kw):
    return calculate_route(SETTINGS, route(*args, **kw))


def cell(x):
    return f"{money(x['gross_profit'])} ({x['margin']:.0%})"


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("DV", 7.5)
    canvas.drawString(18 * mm, 10 * mm, "Trade Advisor · Sulphur profitability · 30 Oct 2026 · "
                      "Estimates: verify before committing money")
    canvas.drawRightString(192 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build(out):
    story = [
        p("Sulphur Import: How to Make It Profitable", H1),
        p("Tonnage needed, profit by purchase price, and levers · Uzbekistan → South Korea · 30 October 2026", SMALL),
        Spacer(1, 6),
        p("<b>Bottom line.</b> Tonnage alone does not create profit. Above ~250–500 t the cost of moving "
          "each tonne stops falling (~$200/t in containers, ~$125/t in bulk). "
          "<b>Profit per tonne = sale price − buy price − logistics.</b> Target "
          "<b>500–1,000 t per deal bought at ≤ $600/t</b> in containers, or <b>3,000 t+ bought at ≤ $650/t</b> in bulk. "
          "For 10% margin the sale price must be ≥ ~$280/t above the buy price (containers) or ≥ ~$215/t (bulk).", BOX),
    ]

    story.append(p("1. Logistics + fees per tonne (excluding the sulphur itself)", H2))
    rows = [["Tonnage", "How it ships", "Cost per tonne"]]
    for q, how, bulk in ((25, "1 container", False), (100, "4 containers", False),
                         (500, "20 containers", False), (1000, "40 containers", False),
                         (3000, "Rail wagons + bulk vessel", True), (10000, "Rail wagons + bulk vessel", True)):
        x = calc(q, 0, 900, bulk=bulk)
        rows.append([f"{q:,} t", how, f"${x['total_cost'] / q:,.0f}"])
    story.append(table(rows, [30, 90, 54], money_cols=(2,)))
    story.append(p("Container cost flattens at ~$196/t from ~1,000 t. Bulk (≥ 3,000 t) cuts it to ~$125/t.", SMALL))

    story.append(p("2. Profit by tonnage and purchase price (sale price $900/t delivered)", H2))
    qs = (100, 500, 1000, 2000)
    rows = [["Buy price", *[f"{q:,} t containers" for q in qs], "3,000 t bulk"]]
    for buy in (550, 600, 650, 680):
        rows.append([f"<b>${buy}/t</b>", *[cell(calc(q, buy, 900)) for q in qs],
                     cell(calc(3000, buy, 900, bulk=True))])
    story.append(table(rows, [22, 30, 30, 32, 30, 30], money_cols=(1, 2, 3, 4, 5)))

    story.append(p("3. Minimum targets", H2))
    story.append(table([
        ["Shipping mode", "Tonnage per deal", "Max buy price", "Spread needed for 10% margin"],
        ["Containers", "500–1,000 t", "≤ $600/t", "sale ≥ buy + ~$280/t"],
        ["Bulk", "≥ 3,000 t", "≤ $650/t", "sale ≥ buy + ~$215/t"],
    ], [34, 40, 34, 66]))

    story.append(p("4. Five levers to widen the spread", H2))
    story += bullets([
        "<b>Buy cheaper ($50–130/t):</b> direct annual contract with Uzbekneftegaz / Turkmengaz instead of single "
        "exchange lots; monthly volume earns discounts; lump sulphur is usually cheaper than granular.",
        "<b>Sell to the right clients (+$50–300/t):</b> big users (fertilizer, sulphuric acid, zinc/metal plants) take "
        "3,000 t+ and unlock bulk; specialty grades (powder for agriculture/rubber, high purity, 25 kg bags) pay far more per tonne.",
        "<b>Cut costs ($15–30/t):</b> confirm 0% WTO duty instead of 2% (≈ $17/t); client letter of credit at sight "
        "removes ≈ $12/t financing; use cheap backhaul containers Central Asia → China.",
        "<b>Repeat business:</b> the same lane monthly lowers fixed costs and improves forwarder and producer prices.",
        "<b>No price risk:</b> prices are expected to fall in 2027: only buy what a client has already bought, at a fixed price (back-to-back).",
    ])

    base = calc(1000, 680, 900)
    opt = calc(1000, 600, 900, duty=0, terms=0)
    opt950 = calc(1000, 600, 950, duty=0, terms=0)
    story.append(KeepTogether([p("5. Optimised example: 1,000 t", H2), table([
        ["Case", "Cost per t", "Profit", "Margin"],
        ["Base: buy $680, duty 2%, 30-day terms, sell $900", f"${base['cost_per_unit']:,.0f}", money(base["gross_profit"]), f"{base['margin']:.1%}"],
        ["Optimised: buy $600, duty 0%, LC at sight, sell $900", f"${opt['cost_per_unit']:,.0f}", money(opt["gross_profit"]), f"{opt['margin']:.1%}"],
        ["Optimised + client pays $950/t", f"${opt950['cost_per_unit']:,.0f}", money(opt950["gross_profit"]), f"{opt950['margin']:.1%}"],
    ], [94, 26, 30, 24], money_cols=(1, 2, 3))]))

    story.append(KeepTogether([
        p("6. Suggested path", H2),
        table([
            ["Stage", "What to do", "Your money at risk"],
            ["Now", "Broker: introduce clients to suppliers for 1–3% commission (≈ $9–27k on 1,000 t)", "$0"],
            ["First trade", "500–1,000 t in containers, back-to-back, client LC, buy ≤ $600/t", "Low"],
            ["Scale", "Monthly 3,000 t+ bulk contract with a fertilizer or acid plant", "Medium, 10–16% margin"],
        ], [26, 110, 38]),
        Spacer(1, 6),
        p("<b>Next step:</b> ask your clients (1) how many tonnes per month and (2) what price they pay today. "
          "~1,000 t/month at ≥ $950/t → real business. 10–50 t at a time → broker only.", BOX),
        p("<b>Assumptions (estimates, not quotes):</b> Uzbekistan route; $3,520 per 20ft (25 t) to Busan; "
          "$750/container THC + hazmat truck; $1,500 docs + $15/t bagging; $350 broker/chemical check; bulk ≈ $105/t "
          "freight + $15/t discharge; duty 2% of CIF unless stated; VAT 10% recoverable; financing 8%/yr over "
          "30 days transit + payment terms; FX buffer 1%. Confirm with forwarder, customs broker and supplier.", SMALL),
    ]))

    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=16 * mm, bottomMargin=16 * mm,
                            title="Sulphur Profitability", author="Trade Advisor")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    out = os.path.join(ROOT, "reports", "sulphur-profitability-2026-10-30.pdf")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    build(out)
    print(os.path.abspath(out))
