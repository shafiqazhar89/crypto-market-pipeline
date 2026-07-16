# Crypto Market Intelligence Pipeline

## Client Brief

Our client is a small crypto-focused business — a lean treasury or portfolio desk — making trading decisions with real money and no Bloomberg terminal. This pipeline helps them monitor which asset categories are gaining or losing momentum, track market concentration and volatility, and flag abnormal activity. Using stale or untrustworthy data here isn't a minor inconvenience: it can cause them to enter a trade at a bad price, resulting in real slippage.

> This project answers a descriptive/diagnostic question ("what is happening in the market right now?"), not a predictive one ("what will prices do?").

## Status

🚧 Phase 0 — environment & scaffold in progress.

## Stack

dlt → DuckDB → dbt (Core v1, pinned) → Dagster → Metabase, containerized with Docker/docker-compose, CI via GitHub Actions.

## Environment Setup

See `docs/PHASE0_SETUP_LOG.md` for the full environment build log.
