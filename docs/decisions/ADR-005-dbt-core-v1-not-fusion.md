# ADR-005: dbt Core v1.x, Not the Fusion Distribution

**Status:** Accepted (Phase 0, Session 2)

## Context

dbt Labs' newer "Fusion" distribution existed at build time, but was still in Beta — and critically, its DuckDB adapter (the entire warehouse for this project) was still in public beta specifically, independent of Fusion's own overall maturity.

## Decision

Pin `dbt-core==1.11.12` (the stable v1.x line), not Fusion.

## Rationale

Same ecosystem-maturity logic as ADR-002 (Ubuntu 24.04 over 26.04), applied to dbt specifically. v1 is stable and universally documented across tutorials, Stack Overflow, and the dbt Community Slack. Fusion's DuckDB adapter being in public beta was disqualifying on its own — this project's entire warehouse layer would be riding a beta component, directly undermining the reliability story the flagship is meant to demonstrate.

## Consequences

Two independent conditions must both be met before revisiting: Fusion reaching **GA**, *and* the DuckDB adapter specifically reaching **GA** (not just Fusion overall). Pin the exact version explicitly (`dbt-core==1.11.12`), never ride `latest` — this is the same principle enforced project-wide (see ADR-007, dependency pinning) applied at the framework level.
