# Deployment Notes

## Two possible submission modes (confirm which applies)
Per the brief: *"Submit a repository or HTTPS endpoint plus an
immutable commit or container digest."* This implies two different
deployment postures:

### Mode A — Repository/commit submission
Builderr presumably clones the repo and runs the bot themselves inside
their own evaluation harness. In this mode, `src/api/server.py` may not
even be needed — the evaluator likely calls the decision function
directly rather than over HTTP. Confirm this before assuming an HTTP
server is required at all.

### Mode B — Live HTTPS endpoint
The bot needs to actually be deployed and reachable, and
`src/api/server.py` becomes the real, load-bearing implementation, not
just a local testing convenience. This mode has real operational
requirements (uptime for the full 24h evaluation window, no
crash-and-restart data loss for in-flight cycle state) that Mode A
doesn't.

**Resolve this in Phase 1 (contract verification) before assuming
either — the two modes have meaningfully different engineering
requirements, especially around state persistence and uptime.**

## If Mode B applies: state persistence considerations
`src/api/server.py`'s current in-memory `CycleTracker` would lose all
state on a crash or restart mid-run — acceptable for local testing,
**not acceptable for a real 24-hour evaluation window** if this mode
applies. Would need at minimum a periodic state snapshot to disk, or a
more robust store, before being submission-ready under Mode B.

## Container digest reproducibility
Whichever mode applies, `Dockerfile` should produce a bit-for-bit
reproducible image from a given commit — pin every dependency version
exactly (`requirements.txt` already does this), and confirm the build
is deterministic (no `:latest` base image tags, no unpinned system
package installs) before freezing a submission.
