# ADR-004: Analytics Are Descriptive/Diagnostic, Not Predictive

**Status:** Accepted (Phase 0, Session 1)

## Context

Crypto price data invites an obvious temptation: build a price-prediction feature and claim "alpha." This needed a deliberate scope boundary before any dashboard or modeling work began.

## Decision

The flagship's analytics are explicitly **descriptive and diagnostic** — category/sector momentum, market concentration, volatility monitoring, anomaly flags, supply-event tracking — and never predict future prices.

## Rationale

Price prediction is a different discipline than data engineering, doesn't reliably work on daily OHLCV data, and an unsupported "predicts prices" claim damages credibility with both technical reviewers and business clients faster than it impresses anyone. This project is a data-engineering and reliability portfolio, not a trading-signals product.

## Consequences

A volatility-forecasting or anomaly/regime-detection ML layer is a legitimate, explicitly **deferred** (not cancelled) post-flagship extension. It's positioned to leverage the point-in-time-correct SCD2 `dim_coin` dimension for leak-free features — meaning the reliability work done in Phases 1–3 is the actual prerequisite for doing that honestly later, not wasted effort if the ML layer never happens. Revisit after Phase 8.
