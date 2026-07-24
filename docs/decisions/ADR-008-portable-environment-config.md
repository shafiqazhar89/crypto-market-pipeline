# ADR-008: Environment-Specific Local Configuration via Environment Variables

**Status:** Accepted (Phase 0, Session 5 — found via the continuity check)

## Context

Also found during the Phase 0 continuity check (cloning the repo fresh into a throwaway `continuity-test` directory). Two related bugs:

1. Both `~/.dbt/profiles.yml` and `dlt/rest_api_pipeline.py` hardcoded the absolute filesystem path of one specific clone. `~/.dbt/profiles.yml` is a single file per user account, keyed by dbt **profile name** rather than by directory — so a second clone of the same repo silently read and wrote the *original* clone's real database. `dbt debug` reported "All checks passed" while connected to entirely the wrong data — a false-positive pass, and a genuine data-corruption risk had a `dbt build` run instead of just a connection check.
2. Separately, `.duckdb/` (correctly gitignored, since it holds a binary database file) never exists on a truly fresh clone, and neither DuckDB nor the `dbt-duckdb` adapter creates a missing parent directory — `dbt debug` failed with a plain filesystem "No such file or directory" error until this was handled.

## Decision

1. The DuckDB path in `profiles.yml` and the destination path in the dlt pipeline script are both read from environment variables — `env_var('CRYPTO_PIPELINE_DUCKDB_PATH_DEV' / '_PROD')` in dbt, `os.environ[...]` in Python — set per-machine in `~/.bashrc`. Never hardcoded, even as an absolute path.
2. `dev` and `prod` use **separate** variables, never a shared one.
3. The dlt ingestion script self-heals its own output directory (`os.makedirs(os.path.dirname(path), exist_ok=True)`) rather than depending on a documented manual setup step.

## Rationale

Environment variables decouple "where's the file" from "who's invoking the tool and from what directory" — a property that matters again once Dagster (Phase 4) becomes a third invoker with its own working directory, one that neither a hardcoded path nor a directory-relative path would reliably survive. Keeping `dev`/`prod` on separate variables preserves the safety net a mistyped `--target prod` is supposed to trip — collapsing them would let a typo silently read/write the wrong environment's data instead of failing loudly. Self-healing directory creation means a client, hirer, or future machine cloning this repo never depends on an undocumented prerequisite; `dbt-duckdb` itself still can't self-heal a missing directory, but since ingestion always runs before transformation in this pipeline, the directory exists by the time dbt needs it.

## Consequences

PR #5 (`fix/portable-duckdb-path`) and PR #6 (`fix/self-healing-directories`). Full setup steps for a new machine — the `profiles.yml` template and the four `.bashrc` lines required — are documented in `PHASE0_SETUP_LOG.md` §12 and `Phase0_Step_By_Step_Guide.md` §8–10.1. This also corrected an earlier overclaim in the project's operating notes that recovery was "`git clone && docker-compose up`, nothing more" — it isn't; a short, now-documented per-machine setup is genuinely required first.
