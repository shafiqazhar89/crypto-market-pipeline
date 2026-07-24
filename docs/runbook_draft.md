# Runbook — Crypto Market Pipeline

> Operational reference: how to run this thing and what to do when it breaks. Distinct from `PHASE0_SETUP_LOG.md`/`Phase0_Step_By_Step_Guide.md`, which are historical build narratives — this is meant to stay current and be useful to someone (including future you) who didn't watch it get built.

## Cold start on a new machine

Verified end-to-end via the Phase 0 continuity check (clone into a throwaway directory, stand up from nothing):

1. `git clone <repo-url>`
2. `uv venv --python 3.12 && source .venv/bin/activate && uv pip install -r requirements.txt`
3. Recreate `~/.dbt/profiles.yml` from the template in `PHASE0_SETUP_LOG.md` §12 (never committed to git — per-machine, dbt convention).
4. Set `CRYPTO_PIPELINE_DUCKDB_PATH_DEV` / `CRYPTO_PIPELINE_DUCKDB_PATH_PROD` in `~/.bashrc`, pointing at this clone's own path. `source ~/.bashrc`.
5. Recreate `dlt/.dlt/secrets.toml` with a real CoinGecko Demo API key (never committed).
6. `cd dlt && python rest_api_pipeline.py` — lands the daily snapshot into `raw.coins_markets`. The output directory self-heals; no manual `mkdir` needed.
7. `cd ../dbt_project/crypto_market_pipeline && dbt debug` — expect "All checks passed!" against this clone's own isolated database file.
8. `docker compose up` (currently a no-op placeholder — populate once Phase 4+ services are defined).

## What to check first when the daily pull fails

*(Seed only — flesh this section out for real starting Phase 3, once failure injection and recovery are actually built and tested, not guessed at.)*

- [ ] Is Docker Desktop running on the Windows host? (`docker` commands silently disappear from WSL if not — check this before anything deeper.)
- [ ] Is it a CoinGecko API issue (rate limit hit, outage, an unannounced schema change) or a local environment issue (env vars unset this session, secrets file missing/rotated, wrong venv active)?
- [ ] `env | grep CRYPTO_PIPELINE` — are both path variables actually set in this shell?
- [ ] Check the load log / Elementary report (once Phase 5 exists) before assuming it's a code bug.

## Known, deliberately-deferred gaps (not bugs — don't "fix" these prematurely)

- The REST API resource uses dlt's fallback single-page paginator. Correct today (250 rows = exactly one page), but implicit rather than explicit — make it explicit once pagination genuinely matters (e.g., pulling more than one page).
- CoinGecko's `roi` field returns empty/null for every row in this load and isn't type-inferred as a result. Real API messiness — this is exactly what Phase 3's schema-drift handling exists to address properly, not something to patch around now.

## Recovery target — what "disposable machine" actually requires

Corrected from an earlier overclaim: recovery is **not** literally zero-touch (`git clone && docker-compose up` alone). It's steps 1–7 above, all of which are now documented rather than tribal knowledge. Step 8 is the only step expected to eventually be the *entire* remaining manual step, once services are containerized.
