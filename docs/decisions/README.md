ADR - architecture decision record is document that record one decision on why, what, alternatives considered for a decision. Decisions get numbered file here is because in working_notes.md it did not capture what we are actually weigh. It got numbered standalone files for permanence and discoverability.

## Index

| ADR | Title | Summary |
|---|---|---|
| [ADR-001](ADR-001-crypto-scenario-choice.md) | Crypto Market-Intelligence Scenario | CoinGecko, daily batch — chosen for a fully real fact and a defensible SCD2 dimension. |
| [ADR-002](ADR-002-ubuntu-24-04-lts.md) | Ubuntu 24.04 LTS, Not 26.04 | Ecosystem maturity over bleeding-edge; supported to 2029. |
| [ADR-003](ADR-003-docker-desktop.md) | Docker Desktop, Not Native Docker-in-WSL | Simpler setup for a solo dev; native Docker is the fallback. |
| [ADR-004](ADR-004-descriptive-not-predictive-scope.md) | Descriptive/Diagnostic Analytics Scope | No price prediction — momentum, concentration, volatility, anomaly detection only. |
| [ADR-005](ADR-005-dbt-core-v1-not-fusion.md) | dbt Core v1.x, Not Fusion | Fusion's DuckDB adapter was still public beta at build time. |
| [ADR-006](ADR-006-branch-pr-workflow.md) | Feature Branch → PR → Merge for Structural Changes | Proves the workflow a client/reviewer would expect, even solo. |
| [ADR-007](ADR-007-dependency-pinning.md) | Dependencies Snapshotted via `uv pip freeze` | Found missing during the Phase 0 continuity check — a fresh clone had nothing to install from. |
| [ADR-008](ADR-008-portable-environment-config.md) | Portable Environment-Specific Configuration | Env vars for DuckDB paths, separate dev/prod, self-healing directories — fixed a real cross-clone data-corruption bug. |
