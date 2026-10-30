---
name: trade
description: Plan an export/import trade - laws, step-by-step route, costs and the most profitable option - using the trade-advisor agent, then save what it learned. Use when the user asks about exporting, importing, tariffs, customs, shipping routes or trade profitability.
---

1. Delegate the request to the `trade-advisor` agent. Pass the user's full
   request, plus anything from this conversation the agent needs (product,
   countries, quantities, prices, preferences, corrections the user made).
2. Show the user the agent's answer, keeping its structure: summary,
   legality, step-by-step route, cost & profit table, risks, sources,
   confidence.
3. If the user corrects something or states a preference, send it back to
   the agent (or write it to `knowledge/lessons.md` / `knowledge/user-profile.md`
   yourself) so it is remembered.
4. Commit and push the files the agent changed under `knowledge/`, so the
   learning survives this session:
   `git add knowledge && git commit -m "Trade advisor: learn <topic>" && git push`
