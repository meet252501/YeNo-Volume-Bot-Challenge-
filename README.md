# YeNo Volume Bot

Builderr.ai challenge — **YeNo volume bots** (sponsored by YeNo)
Status: Open · Free to enter · Rolling qualification
Prize: $500 first prize + possible additional YeNo rewards/pilot opportunities

## What this is

A trading agent for YeNo's BTC five-minute Up/Down prediction markets.
The goal is **not** "predict price direction well" — it's generate at
least $1,000 in completed trading volume from a $10 simulated starting
balance within a 24-hour window, while preserving capital, paying real
fees, and finishing completely flat. Submitted as code only — no real
money, no real trading account, ever.

As of the challenge page snapshot this project is built from (2026-09-22
benchmark), **no submitted or reference bot has qualified**. Builderr's
own house bot best run was $943 across 30 replay paths — under $1,000.
This is a genuinely unsolved problem at time of writing, not a template
to fill in.

## Repo layout

See `PROJECT_PLAN.md` for the phased build order and `AGENTS.md` for
build instructions aimed at an autonomous coding agent. Full doc index:

```
yeno-volume-bot/
├── README.md                    ← you are here
├── AGENTS.md                     ← entry point for autonomous build agents
├── PROJECT_PLAN.md                ← phased plan, milestones
├── TODO.md / NOTES.md / CHANGELOG.md
├── CONTRIBUTING.md / SECURITY.md / LICENSE
├── docs/
│   ├── challenge_brief_summary.md   ← condensed rules, gates, scoring
│   ├── RESEARCH.md                   ← prediction-market microstructure, fee research
│   ├── architecture.md                ← system design
│   ├── data_schema.md                  ← /decide request/response contract
│   ├── scoring_and_gates.md             ← qualification + ranking rules mapped to checks
│   ├── learning_harness.md               ← strategy iteration loop
│   ├── SUBMISSION.md / glossary.md / faq.md / risk_register.md
│   └── algorithms/
│       ├── decision_algorithm.md          ← HOLD/BUY/SELL core logic
│       ├── fee_model.md                    ← exact fee math
│       ├── execution_model.md               ← latency, later-book, partial fills
│       ├── risk_management.md                ← sizing, drawdown control
│       ├── cycle_accounting.md                ← what counts as eligible volume
│       ├── backtesting_algorithm.md            ← replay methodology
│       └── market_regime_selection.md           ← when to trade vs. sit out
├── src/                            ← bot implementation
├── tests/                          ← unit + golden fixture tests
├── scripts/                        ← backtest runner, replay downloader
└── data/                           ← replay paths, sample requests (gitignored except samples)
```

## Quick start

```bash
make dev-install
make backtest        # run against local replay data
make check           # lint + tests
```

## Status

Planning + scaffold stage. See `TODO.md`.
