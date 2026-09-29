# Security & Constraints

- The evaluator "blocks arbitrary outbound network access" during
  official runs — the bot must be fully self-contained at decision
  time. Do not design any strategy that assumes a live network call
  (external price feed, external API) will succeed during the actual
  24-hour evaluation window.
- No secrets are needed for this challenge (no API keys, no real
  trading credentials) — if any ever appear necessary, stop and
  reconsider the design, since the whole point is code-only, no-funds
  submission.
- The bot never receives real trading credentials and must never be
  designed as if it might — treat any code path that assumes a real
  account/key as a design error, not a feature to build toward.
