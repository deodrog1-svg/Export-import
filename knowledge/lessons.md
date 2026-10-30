# Lessons learned

Rules and corrections from past sessions. These override the agent's
defaults. Newest first. Format:

`- YYYY-MM-DD: <lesson> (why / source)`

- 2026-10-30: For commodity trades, answer 'what tonnage?' with a tonnage x buy-price grid; past the point where fixed costs are spread, profit depends on the spread (sell - buy - logistics), not volume. (sulphur profitability)
- 2026-10-30: For bulk commodities, model per-shipment fixed costs separately; under ~100 t they dominate and small lots lose money. Producers sell in wagon lots (~60 t+). (sulphur lot-size session)
- 2026-10-30: Buying a banned country's goods through a neighbour (e.g. Kazakh sulphur via Kyrgyzstan) does not change origin; flag as circumvention risk. (sulphur lot-size session)
- 2026-10-30: Check origin-country EXPORT bans first for commodities; in 2026 KZ, RU and TR all banned sulphur exports. (sulphur session)
- 2026-10-30: Check whether the destination is already a net exporter of the product; then the import only works on price or a special grade. (Korea exports sulphur)
- 2026-10-30: User writes product names in Russian (e.g. сера = sulphur); answer in English with the Russian term. (sulphur session)
- 2026-10-30: Always run tools/landed_cost.py for cost math; never estimate totals by hand. (setup)
- 2026-10-30: Check whether the destination values goods on CIF or FOB before computing duty (US, CA, AU, NZ use FOB/transaction value). (setup)
