# Trade Advisor: export/import agent

A Claude Code agent that plans trades between any two countries:

- **Laws**: export controls, sanctions, import licenses, standards, documents
- **Classification**: HS code and national tariff line
- **Taxes**: MFN vs. free-trade-agreement duty, anti-dumping, VAT/GST, excise
- **Routes**: step-by-step process plus sea/air/rail/road options
- **Costs**: researched freight, fees and taxes with sources and dates
- **Profit**: ranks every option by profit, margin, ROI and speed
- **Learning**: saves what it learns to `knowledge/` and reuses it next time

## How to use

In Claude Code, inside this repo:

```
/trade I want to export 5,000 kg of roasted coffee from Colombia to Germany or Japan. Which is more profitable?
```

or just ask any trade question; `CLAUDE.md` routes it to the agent.

## How it learns

Each session, the agent reads `knowledge/` first (profile, lessons, saved
countries/products/routes) and writes new facts, corrections and a session
log back. Every fact carries a source and a `verified:` date so stale data
gets re-checked. Commit `knowledge/` after each session.

Teach it directly, e.g. "remember our margin target is 30%" or "from now on
also check Amazon FBA fees", and it records that in `lessons.md`,
`user-profile.md` or `modules.md`.

## How to expand it

- **New behavior**: add a section to `knowledge/modules.md` (ideas listed there).
- **New calculations**: extend `tools/landed_cost.py` and add tests in `tests/`.
- **New data sources**: add them to `knowledge/sources.md`, or connect an MCP
  server (tariff API, freight quotes) and mention it in `modules.md`.

## Calculator

```
python3 tools/landed_cost.py tools/examples/sample_scenario.json
python3 tools/landed_cost.py scenario.json --json
python3 -m unittest discover -s tests
```

Supports CIF or FOB duty basis, ad-valorem/specific/anti-dumping duties,
excise, recoverable or non-recoverable VAT, itemized fees, insurance,
financing cost of transit + payment terms, and an FX buffer.

## Important

Tariffs, sanctions and freight rates change often. The agent cites sources
and states its confidence, but confirm with a licensed customs broker or
freight forwarder before committing money. It will not help evade duties,
sanctions or export controls.
