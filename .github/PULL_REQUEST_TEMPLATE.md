## What changed

## Which phase (see PROJECT_PLAN.md)

## Backtest impact (required for any strategy change)
- [ ] Full replay run attached: median / best / worst / flat % / hit-target %
- [ ] Stressed run (2-cent adverse execution) attached alongside baseline
- [ ] Flat rate is still 100% — a strategy change that reduces flat rate
      below 100% should not be merged regardless of median improvement

## Checklist
- [ ] Tests pass locally (`make check`)
- [ ] No outbound network dependency introduced
- [ ] Docs updated if the contract understanding changed
