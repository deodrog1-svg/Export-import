# Expansion modules

Extra capabilities added over time. The agent reads this at the start of
every session and applies any module that fits the request. To add one,
append a section like the example below, or just tell the agent in a
session ("from now on, also ...") and it will write it here.

```
## <Module name>
- When: <which requests it applies to>
- Do: <what the agent should do>
- Files/tools: <any file in knowledge/ or tools/ it uses>
- Added: YYYY-MM-DD
```

## Ideas for future modules
- Supplier sourcing: find and compare manufacturers in the origin country
- Buyer discovery: find importers/distributors in the destination market
- Marketplace channels: Amazon FBA, Alibaba, Noon, Mercado Libre fees and rules
- Trade finance: compare LC, documentary collection, export credit insurance
- FX: track exchange rates and suggest hedging for long transit times
- Live freight quotes: connect to a freight-rate API
- Tariff API: connect to an official tariff database for automatic lookups
- Document generator: draft commercial invoice, packing list, CO forms
- Compliance watch: re-check stored tariffs/sanctions on a schedule
