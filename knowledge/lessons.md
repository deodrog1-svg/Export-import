# Lessons learned

Rules and corrections from past sessions. These override the agent's
defaults. Newest first. Format:

`- YYYY-MM-DD: <lesson> (why / source)`

- 2026-10-30: Check origin-country EXPORT bans first for commodities; in 2026 KZ, RU and TR all banned sulphur exports. (sulphur session)
- 2026-10-30: Check whether the destination is already a net exporter of the product; then the import only works on price or a special grade. (Korea exports sulphur)
- 2026-10-30: User writes product names in Russian (e.g. сера = sulphur); answer in English with the Russian term. (sulphur session)
- 2026-10-30: Always run tools/landed_cost.py for cost math; never estimate totals by hand. (setup)
- 2026-10-30: Check whether the destination values goods on CIF or FOB before computing duty (US, CA, AU, NZ use FOB/transaction value). (setup)
