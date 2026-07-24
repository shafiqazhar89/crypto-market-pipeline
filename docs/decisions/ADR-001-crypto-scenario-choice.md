# ADR-001: Crypto Market-Intelligence Scenario (CoinGecko, Daily Batch)

**Status:** Accepted (Phase 0, Session 1)

## Context

The flagship needed one scenario, evaluated against five criteria: a genuinely free live data source, a real SME-relevant business question, a natural star-schema fit, a defensible SCD2 dimension paired with a growing fact, and enough real-world messiness to be worth building reliability features against. Four candidates were scored: crypto (CoinGecko), Klang Valley logistics, an FMCG price/margin monitor, and US equities. Full comparison table and scoring in `Scenario_Decision_And_Crypto_Design.md`.

## Decision

Cryptocurrency market-intelligence pipeline. Daily **batch** snapshots (not streaming — streaming is explicitly overkill at this data volume and appears only as a Phase 8 concept demo). Primary source: CoinGecko's free Demo API.

Business framing: a lean crypto treasury/portfolio desk needs to monitor the market without a Bloomberg terminal. The dashboard answers *"which asset categories are gaining or losing momentum, how concentrated and volatile is the market, and is anything behaving abnormally"* — explicitly **descriptive and diagnostic**, never predictive of future prices (see ADR-004).

## Rationale

Crypto scored highest overall. Its fact is fully real (live market data), unlike the logistics/FMCG alternatives, whose facts would have been partly synthetic — no free real delivery-transaction or margin feed exists for those. It's a modern, in-demand domain with a rich, genuinely free, keyless-capable API. The one hard requirement — a defensible SCD2 dimension — is solvable via CoinGecko's `/coins/{id}` metadata (category tags, supply figures, rank buckets), snapshotted daily with dbt's `check` strategy.

Klang Valley logistics was the strongest runner-up (highest SME domain credibility, excellent free Malaysian government data sources) but was weaker on exactly the two criteria crypto wins on: no free real transaction-level fact, and a thinner SCD2 story. Kept as the documented fallback.

## Consequences

- A course-correction threshold is defined: let the `dim_coin` snapshot run 1–2 weeks; if no dimension attribute has changed across the top-100 universe, widen to top-250; if still static, fall back to the logistics scenario (`Scenario_Decision_And_Crypto_Design.md` §7).
- A volatility/anomaly-detection ML layer is a legitimate, explicitly deferred post-flagship extension — not a "predicts prices" product (ties to ADR-004).
