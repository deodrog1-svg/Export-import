#!/usr/bin/env python3
"""Landed cost and profitability calculator for export/import routes.

Usage:
    python3 tools/landed_cost.py scenario.json [--json]

The scenario describes one shipment (product, quantity, buy and sell price)
and any number of routes to compare. See tools/examples/sample_scenario.json.
Only the standard library is used so it runs anywhere.
"""

import argparse
import json
import sys

# Fields that may be set on the scenario and overridden per route.
SHARED_FIELDS = (
    "quantity",
    "unit_cost",
    "sale_price_per_unit",
    "financing_rate_annual",
)


def _fees_total(fees):
    """Sum a list of {"name": str, "amount": number} or a plain number."""
    if fees is None:
        return 0.0
    if isinstance(fees, (int, float)):
        return float(fees)
    return float(sum(f.get("amount", 0) for f in fees))


def calculate_route(scenario, route):
    """Return a dict with the full cost and profit breakdown for one route."""
    params = {k: scenario.get(k) for k in SHARED_FIELDS}
    params.update({k: route[k] for k in SHARED_FIELDS if k in route})

    quantity = float(params["quantity"])
    unit_cost = float(params["unit_cost"])
    sale_price = float(params["sale_price_per_unit"])
    financing_rate = float(params.get("financing_rate_annual") or 0)

    goods_value = quantity * unit_cost
    origin_charges = _fees_total(route.get("origin_charges"))
    export_duty = goods_value * float(route.get("export_duty_rate", 0))
    fob_value = goods_value + origin_charges + export_duty

    freight = float(route.get("freight", 0))
    if "insurance" in route:
        insurance = float(route["insurance"])
    else:
        # Cargo insurance is conventionally quoted on CIF + 10%.
        insurance = (fob_value + freight) * 1.1 * float(route.get("insurance_rate", 0))
    cif_value = fob_value + freight + insurance

    duty_basis = route.get("duty_basis", "CIF").upper()
    if duty_basis not in ("CIF", "FOB"):
        raise ValueError(f"duty_basis must be CIF or FOB, got {duty_basis!r}")
    customs_value = cif_value if duty_basis == "CIF" else fob_value

    ad_valorem_duty = customs_value * float(route.get("duty_rate", 0))
    specific_duty = quantity * float(route.get("duty_per_unit", 0))
    trade_remedy = customs_value * float(route.get("additional_duty_rate", 0))
    duty = ad_valorem_duty + specific_duty + trade_remedy

    excise = customs_value * float(route.get("excise_rate", 0)) + quantity * float(
        route.get("excise_per_unit", 0)
    )

    # VAT/GST base is customs value + duties + excise in most countries;
    # routes can override with vat_base_extra for local add-ons.
    vat_base = customs_value + duty + excise + float(route.get("vat_base_extra", 0))
    vat = vat_base * float(route.get("vat_rate", 0))
    vat_recoverable = bool(route.get("vat_recoverable", True))

    destination_charges = _fees_total(route.get("destination_charges"))
    other_fees = _fees_total(route.get("other_fees"))

    # FOB-basis countries still pay the freight; it just isn't dutiable.
    landed_cost = (
        cif_value + duty + excise + destination_charges + other_fees
        + (0.0 if vat_recoverable else vat)
    )

    transit_days = float(route.get("transit_days", 0))
    payment_terms_days = float(route.get("payment_terms_days", 0))
    days_capital_tied = transit_days + payment_terms_days
    financing_cost = landed_cost * financing_rate * days_capital_tied / 365

    fx_buffer = landed_cost * float(route.get("fx_buffer_rate", 0))
    total_cost = landed_cost + financing_cost + fx_buffer

    revenue = quantity * sale_price
    gross_profit = revenue - total_cost
    margin = gross_profit / revenue if revenue else 0.0
    roi = gross_profit / total_cost if total_cost else 0.0
    profit_per_day = gross_profit / days_capital_tied if days_capital_tied else None

    return {
        "name": route.get("name", "unnamed route"),
        "mode": route.get("mode"),
        "transit_days": transit_days,
        "duty_basis": duty_basis,
        "goods_value": goods_value,
        "fob_value": fob_value,
        "freight": freight,
        "insurance": insurance,
        "cif_value": cif_value,
        "customs_value": customs_value,
        "duty": duty,
        "excise": excise,
        "vat": vat,
        "vat_recoverable": vat_recoverable,
        "destination_charges": destination_charges,
        "other_fees": other_fees,
        "landed_cost": landed_cost,
        "financing_cost": financing_cost,
        "fx_buffer": fx_buffer,
        "total_cost": total_cost,
        "cost_per_unit": total_cost / quantity if quantity else 0.0,
        "revenue": revenue,
        "gross_profit": gross_profit,
        "margin": margin,
        "roi": roi,
        "profit_per_day": profit_per_day,
        "notes": route.get("notes", ""),
    }


def compare(scenario):
    """Calculate every route and rank them by gross profit (best first)."""
    results = [calculate_route(scenario, r) for r in scenario["routes"]]
    results.sort(key=lambda r: r["gross_profit"], reverse=True)
    for rank, r in enumerate(results, 1):
        r["rank"] = rank
    return results


def _money(x, currency):
    return f"{x:,.2f} {currency}"


def format_report(scenario, results):
    currency = scenario.get("currency", "USD")
    lines = []
    title = scenario.get("product", {}).get("description", "Shipment")
    lines.append(f"# {title}: {len(results)} route(s), currency {currency}")
    lines.append("")
    header = ("Rank", "Route", "Days", "Landed", "Total cost", "Per unit",
              "Profit", "Margin", "ROI")
    rows = [header]
    for r in results:
        rows.append((
            str(r["rank"]), r["name"], f"{r['transit_days']:g}",
            f"{r['landed_cost']:,.0f}", f"{r['total_cost']:,.0f}",
            f"{r['cost_per_unit']:,.2f}", f"{r['gross_profit']:,.0f}",
            f"{r['margin']:.1%}", f"{r['roi']:.1%}",
        ))
    widths = [max(len(row[i]) for row in rows) for i in range(len(header))]
    for i, row in enumerate(rows):
        lines.append(" | ".join(c.ljust(widths[j]) for j, c in enumerate(row)))
        if i == 0:
            lines.append("-+-".join("-" * w for w in widths))
    lines.append("")

    for r in results:
        lines.append(f"## {r['rank']}. {r['name']}")
        for label, key in (
            ("Goods value", "goods_value"), ("FOB value", "fob_value"),
            ("Freight", "freight"), ("Insurance", "insurance"),
            ("CIF value", "cif_value"),
            (f"Customs value ({r['duty_basis']})", "customs_value"),
            ("Duty", "duty"), ("Excise", "excise"), ("VAT/GST", "vat"),
            ("Destination charges", "destination_charges"),
            ("Other fees", "other_fees"), ("Landed cost", "landed_cost"),
            ("Financing cost", "financing_cost"), ("FX buffer", "fx_buffer"),
            ("Total cost", "total_cost"), ("Revenue", "revenue"),
            ("Gross profit", "gross_profit"),
        ):
            lines.append(f"  {label:<26} {_money(r[key], currency)}")
        if not r["vat_recoverable"]:
            lines.append("  (VAT not recoverable: included in landed cost)")
        if r["profit_per_day"] is not None:
            lines.append(f"  {'Profit per day of capital':<26} "
                         f"{_money(r['profit_per_day'], currency)}")
        if r["notes"]:
            lines.append(f"  Notes: {r['notes']}")
        lines.append("")

    best = results[0]
    fastest = min(results, key=lambda r: r["transit_days"])
    best_margin = max(results, key=lambda r: r["margin"])
    lines.append(f"Most profitable: {best['name']} "
                 f"({_money(best['gross_profit'], currency)}, {best['margin']:.1%} margin)")
    lines.append(f"Best margin:     {best_margin['name']} ({best_margin['margin']:.1%})")
    lines.append(f"Fastest:         {fastest['name']} ({fastest['transit_days']:g} days)")
    if best["gross_profit"] <= 0:
        lines.append("WARNING: no route is profitable at this sale price.")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("scenario", help="path to scenario JSON")
    parser.add_argument("--json", action="store_true", help="print JSON instead of a report")
    args = parser.parse_args(argv)

    with open(args.scenario, encoding="utf-8") as f:
        scenario = json.load(f)
    results = compare(scenario)
    if args.json:
        json.dump(results, sys.stdout, indent=2)
        print()
    else:
        print(format_report(scenario, results))


if __name__ == "__main__":
    main()
