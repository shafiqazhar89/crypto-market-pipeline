# ADR-002: Ubuntu 24.04 LTS, Not 26.04

**Status:** Accepted (Phase 0, Session 1)

## Context

WSL2 needed a distro choice. Ubuntu 26.04 existed at build time but had only recently released (~April 2026).

## Decision

Ubuntu **24.04 LTS**, not the newer 26.04.

## Rationale

Ecosystem maturity. Tooling, documentation, and community troubleshooting (Stack Overflow, GitHub issues) target 24.04 first; 26.04 is too new for a project already depending on this many interlocking tools (dlt, dbt, dagster, Docker Desktop's WSL integration). 24.04 is supported until 2029 — plenty of runway. The problem-solving budget for this project should go toward dlt/dbt/dagster/reliability concepts, not "does tool X even run on brand-new OS Y."

This is the same "boring is a feature" reasoning applied consistently elsewhere in this project — see ADR-005 (dbt Core v1.x over Fusion).

## Consequences

No practical downside identified. Revisit only if a specific required tool needs a newer kernel or userspace than 24.04 provides.
