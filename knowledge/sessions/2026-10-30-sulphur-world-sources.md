# 2026-10-30: Sulphur (сера, HS 2503) world sources -> South Korea (Busan)

**Question:** country-by-country dataset of every realistic sulphur source for Korea (status, price, route, freight per 20ft, duty).
**Output:** sessions/2026-10-30-sulphur-world-sources.json (25 objects; Korea domestic = status "benchmark").

**Status (2026-10-30)**
- Open: Oman, China, Japan, Taiwan, Singapore, Malaysia, Canada, USA, Turkmenistan, Uzbekistan, Azerbaijan (no volume), Indonesia (importer, not a source)
- Disrupted (Hormuz/Red Sea): UAE, Qatar, Kuwait, Iraq, Saudi Arabia
- Banned: Kazakhstan, Russia (300 kt low-grade quota), India (informal), Turkey (Q2-Q3, Q4 unconfirmed), Kyrgyzstan (KZ-origin stock)
- Sanctioned: Iran, Belarus

**Calculator check** (tools/make_world_report.py evaluate -> landed_cost.py; sell $900 delivered, 1,000 t, containers, ALL ESTIMATES): landed cost/t KR domestic ~826, China ~859, Japan ~881, Taiwan ~889, Singapore ~904, KZ ~905, UZ ~913, Oman ~924, TM ~926, US ~938, Canada ~944, Gulf inside-Hormuz 1,050-1,094.
=> At current prices, importing barely beats or loses to Korean refiners. Only nearby Asia (China/Japan/Taiwan) clears a thin margin; Korean domestic supply is cheapest.

**Corrections:** Korea duty 0% for WTO members (was 2% blanket). CRU "FOB Japan/Korea $310-320" is sulphuric acid.

**Open questions:** Kazakh ban status (CRU conflicting line on 4 Aug lifting); Turkey Q4; Korean domestic refiner contract price (get a quote from S-Oil/SK/GS distributors); live container quotes; 편익관세 coverage for UZ/TM; HS 2503 lines in UAE CEPA / India CEPA.
