# FAQ / Working Notes

**Q: Is this a "predict BTC price" challenge?**
A: Not primarily. The scoring rewards generating volume while
preserving capital — a bot that's directionally right but trades
rarely, or one that trades often but bleeds fees, both underperform a
bot that finds many small, cheap, high-confidence, complete cycles.

**Q: Does the bot need to be fast (low-latency infrastructure)?**
A: The evaluator itself imposes a fixed 250ms decision-to-fill delay
regardless of how fast the bot responds — so there's no reward for
being faster than that, and no visible penalty for being a bit slower
as long as the bot responds within whatever timeout the real contract
specifies (unconfirmed exact timeout — check the real evaluator contract).

**Q: What happens if the bot returns an invalid or malformed response?**
A: Unconfirmed against the working brief — flagged as an open question
in `docs/data_schema.md`. Don't assume it's treated as a harmless HOLD
until verified.

**Q: Can the bot use any live external data (e.g., a live BTC price
feed) during the real evaluation?**
A: No — the evaluator "blocks arbitrary outbound network access" during
official runs. All the bot ever gets is what's in the `/decide` request
itself (including the `reference` block's causal BTC data).

**Q: Why does the house bot's own benchmark never cross $1,000?**
A: Genuinely unclear from the page alone — but the research findings
(fee curve shape, execution realism) suggest it's a hard, real
constraint, not a bug in the house bot. Treat improving on it as the
actual open problem this project is solving, not a formality.
