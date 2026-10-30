# Export-Import project

This repo holds **Trade Advisor**, an agent for export/import law, routes,
costs and profitability between any countries.

- Agent: `.claude/agents/trade-advisor.md`
- Entry point: the `/trade` skill (`.claude/skills/trade/SKILL.md`)
- Memory: `knowledge/` (read `knowledge/INDEX.md` first)
- Calculator: `tools/landed_cost.py` (tests: `python3 -m unittest discover -s tests`)

## Rules
- Any export/import/tariff/customs/shipping/profitability question goes to
  the `trade-advisor` agent.
- When the user corrects the agent or states a business preference, record
  it in `knowledge/lessons.md` or `knowledge/user-profile.md`.
- Sessions run in ephemeral containers: commit and push `knowledge/`
  changes at the end of every trade session or the learning is lost.
- New capabilities go in `knowledge/modules.md` (behavior) and `tools/`
  (code, with tests in `tests/`).
