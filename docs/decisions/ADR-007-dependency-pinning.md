# ADR-007: Dependencies Snapshotted via `uv pip freeze`, Committed to the Repo

**Status:** Accepted (Phase 0, Session 5 — found via the continuity check)

## Context

Core tools (`dlt`, `dbt-core`, `dbt-duckdb`, `dagster`, `dagster-dbt`, `dagster-duckdb`) were originally installed with a single `uv pip install ...` command back in Session 4, and never captured to a file. This surfaced as a real bug during the Phase 0 continuity check: cloning the repo fresh into a throwaway directory produced a venv with none of these tools installed — `dbt`, `dlt`, and `dagster` genuinely did not exist, not because anything was broken, but because nothing had ever recorded what to install.

## Decision

`uv pip freeze > requirements.txt`, committed to the repo, immediately after any dependency change — not deferred, not left as a remembered one-off command.

## Rationale

A dependency manifest is the reproducibility floor everything else sits on. The same "pin explicit versions, never rely on `latest`/an unrecorded state" reasoning behind ADR-002 (Ubuntu 24.04) and ADR-005 (dbt Core v1.x, pinned) applies here at the Python-environment level, not just the OS/tool-version level.

## Consequences

PR #4 (`chore/pin-dependencies`). Two things worth verifying, not assuming, when re-freezing in future: which venv is actually active in the current shell (activation is per-shell-session, not per-directory — `cd`-ing elsewhere doesn't switch it, so freezing from the wrong shell silently produces an empty or wrong-package list), and that the resulting file isn't suspiciously short (`wc -l requirements.txt` should land in the 50–150+ range given dlt/dbt/dagster's transitive dependency trees).
