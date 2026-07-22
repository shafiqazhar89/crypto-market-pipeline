# Phase 0 — Environment Setup Log

> Chronological record of every command run to stand up the dev environment on the personal ASUS TUF A15.
> This is the seed for the repo's `README.md` "Environment" section — copy the relevant parts over when we scaffold the repo.

---

## 1. WSL2 + Ubuntu 24.04

Run in **PowerShell, as Administrator**:
```powershell
wsl --install -d Ubuntu-24.04
```
Reboot when prompted. On first launch, Ubuntu prompts for a UNIX username/password — used `shafiq`.

**Verify:**
```bash
pwd                # -> /home/shafiq
uname -a           # -> ...microsoft-standard-WSL2...
```
```powershell
wsl -l -v          # -> Ubuntu-24.04  Running  2
```

## 2. Update packages

```bash
sudo apt update && sudo apt upgrade -y
```

## 3. Docker Desktop

- Downloaded from `https://www.docker.com/products/docker-desktop/` (Windows AMD64)
- Installed with **"Use WSL 2 instead of Hyper-V"** checked
- Docker Desktop → Settings → Resources → WSL Integration → enabled `Ubuntu-24.04` → Apply & Restart

**Verify (from inside Ubuntu):**
```bash
docker --version
docker compose version
docker run hello-world
```
> Note: `docker` commands only work while Docker Desktop is running on Windows — it injects the CLI into WSL live.

## 4. VS Code + WSL extension

- Installed VS Code on Windows from `https://code.visualstudio.com/`
- Installed the **WSL** extension (by Microsoft) from the Extensions panel
- Launched connected into WSL from the Ubuntu terminal:
```bash
code .
```
Bottom-left of VS Code should show `WSL: Ubuntu-24.04`.

## 5. Confirm Python

```bash
python3 --version   # -> Python 3.12.3
which python3        # -> /usr/bin/python3
```

## 6. Project directory

```bash
mkdir ~/crypto-market-pipeline
cd ~/crypto-market-pipeline
pwd                  # -> /home/shafiq/crypto-market-pipeline
```

## 7. Install `uv` (Python package/env manager)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env    # if `source ~/.bashrc` doesn't pick it up
uv --version
```

## 8. Create + activate the virtual environment

```bash
uv venv --python 3.12
source .venv/bin/activate
```
Prompt changes to `(crypto-market-pipeline)` when active.

## 9. Install core tools (all at once — see D7 below)

```bash
uv pip install "dlt[duckdb]" dbt-core dbt-duckdb dagster dagster-dbt dagster-duckdb
```

**Verify:**
```bash
dlt --version        # -> 1.29.0
dbt --version         # -> Core 1.11.12, duckdb plugin 1.10.1
dagster --version     # -> 1.13.13
```

> **D7 note:** installed `dbt-core` (Python, v1.x), **not** the Fusion distribution — Fusion is still Beta and its DuckDB adapter is still public beta. Pinned `dbt-core==1.11.12`. Revisit at Fusion GA *and* DuckDB adapter GA.

## 10. Git identity

```bash
git config --global user.name "muhammad.shafiq.azhar"
git config --global user.email "shafiqazhar89@gmail.com"
```

## 11. SSH key for GitHub

```bash
ssh-keygen -t ed25519 -C "shafiqazhar89@gmail.com"
# accepted default path (~/.ssh/id_ed25519), set a passphrase
```

**Start the agent and load the key** — note the `$` matters, `eval "$(ssh-agent -s)"` not `eval "(ssh-agent -s)"`:
```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

**Verify the key loaded:**
```bash
ssh-add -l
```

**Get the public key to paste into GitHub:**
```bash
cat ~/.ssh/id_ed25519.pub
```
Added under GitHub → Settings → SSH and GPG keys → New SSH key.

**Test the connection:**
```bash
ssh -T git@github.com
```
Ran and authenticated successfully — `Hi shafiqazhar89! You've successfully authenticated, but GitHub does not provide shell access.` (Session 3.)

## 12. Portable DuckDB path (dbt + dlt)

> Found during the Phase 0 continuity check: both `~/.dbt/profiles.yml` and `dlt/rest_api_pipeline.py` originally hardcoded an absolute path (`/home/shafiq/crypto-market-pipeline/.duckdb/...`). Since `~/.dbt/profiles.yml` is a single file shared by every dbt project on the machine (keyed by profile name, not directory), any second clone of this repo silently read/wrote into the *original* clone's database — a real data-corruption risk, not just a portability nit. Fixed by moving the path into environment variables, resolved outside the repo (see PR #4, #5).

**`~/.dbt/profiles.yml` — never committed to git (standard dbt convention: per-machine, can hold credentials). Recreate this on any new machine:**
```yaml
crypto_market_pipeline:
  outputs:
    dev:
      type: duckdb
      path: "{{ env_var('CRYPTO_PIPELINE_DUCKDB_PATH_DEV') }}"
      threads: 1
    prod:
      type: duckdb
      path: "{{ env_var('CRYPTO_PIPELINE_DUCKDB_PATH_PROD') }}"
      threads: 4
  target: dev
```

**`~/.bashrc` — add these two lines (values are per-clone; below is this machine's original clone):**
```bash
export CRYPTO_PIPELINE_DUCKDB_PATH_DEV=/home/shafiq/crypto-market-pipeline/.duckdb/dev.duckdb
export CRYPTO_PIPELINE_DUCKDB_PATH_PROD=/home/shafiq/crypto-market-pipeline/.duckdb/prod.duckdb
```
Then `source ~/.bashrc`.

**dlt side:** `dlt/rest_api_pipeline.py` reads the same dev var directly — `os.environ["CRYPTO_PIPELINE_DUCKDB_PATH_DEV"]`. Ingestion always targets `dev`, never `prod`.

**Verify:**
```bash
env | grep CRYPTO_PIPELINE
dbt debug   # "Connection: path:" should show the value from the env var, not a literal hardcoded string
```

**Why two separate vars instead of one:** collapsing `dev`/`prod` onto a single var means a mistyped `--target prod` silently reads/writes `dev`'s file instead of failing or hitting an isolated one. Cheap to keep them separate now.

---

## Pro-tips picked up this session (also copied to Working_Notes.md §4)

- **Redact secrets, not identifiers.** Never share private key files (`id_ed25519`, no `.pub`), passphrases, API keys, `.env` contents, or `.dlt/secrets.toml`. Public keys, fingerprints, usernames, and version strings are safe and often necessary to share for debugging.
- **`eval "$(...)"` vs `eval "(...)"`** — the `$` triggers command substitution (capture and run the *output* of the command). Without it, bash just treats `(...)` as a subshell — nothing gets exported to your current shell. Easy typo, easy to miss because it doesn't error loudly.
- **Docker's CLI in WSL only exists while Docker Desktop is running on Windows** — if `docker` commands suddenly say "not found," check Docker Desktop is open first before debugging anything else.

## Pro-tips picked up this session — continuity-check debugging (Phase 0 closeout)

- **An install command typed once and never captured to a file is invisible to `git clone`.** `uv pip install "dlt[duckdb]" dbt-core dbt-duckdb dagster ...` back in Session 4 was never snapshotted — a fresh clone had nowhere to learn what to install (`dbt: command not found`, not because dbt was broken, but because nothing had installed it). Fix: `uv pip freeze > requirements.txt`, commit it, and treat "did I capture this in a file" as part of finishing any install step, not an afterthought.
- **`uv pip freeze` captures whatever venv is *currently active* in your shell — not whatever venv "should" be active.** Venv activation is per-shell-session, not per-directory: `cd`-ing into a different project does **not** switch venvs. Freezing from the wrong one silently produces an empty or wrong-package list. Always check the prompt's `(venv-name)` matches the project you're actually freezing before running it.
- **`~/.dbt/profiles.yml` is a single global file per user account, keyed by *profile name* — not by directory.** Two separate clones of the same repo (same `profile:` name in `dbt_project.yml`) read the exact same entry in that one file, regardless of which directory you're standing in. A hardcoded absolute path there means every clone silently reads/writes the *same physical database file* — a real data-corruption risk (a `dbt build` from a throwaway test clone would have written into the original project's real, already-verified data), not just a portability nit.
- **"All checks passed" / "connection ok" is not proof `dbt debug` connected to the right database — read the printed `path:` line.** A green check can be a silent wrong-target success, which is worse than an outright failure because it doesn't announce itself. Always compare the printed path against where you actually expect it to point.
- **Fix pattern for machine-specific values: move them out of files that travel with the repo (or are shared globally) and into environment variables.** `env_var('NAME')` in `profiles.yml`, `os.environ["NAME"]` in Python, values set in `~/.bashrc` (not committed — same handling as secrets, even though these particular values aren't sensitive). This also survives a third invoker later (Dagster in Phase 4) that has its own working directory neither dlt's nor dbt's relative-path assumptions would account for.
- **Don't collapse `dev`/`prod` config onto a single shared variable "for simplicity."** It quietly removes the safety net a mistyped `--target prod` is supposed to trip — instead of failing loudly or hitting an isolated file, it silently reads/writes `dev`'s data. Keep them separate; it costs one extra line.
- **`source ~/.bashrc` does not unset variables that were set manually in the current shell session outside the file.** `env | grep X` reflects live shell state, which can silently diverge from what's actually saved on disk. Treat the file itself as the source of truth (`grep VAR ~/.bashrc`), and `unset` stale in-session variables explicitly rather than assuming a re-source clears everything.
- **A "fresh clone" continuity test only proves anything if you verify you're actually operating on the fresh clone's own tooling/state at each step** — mixing up which venv or which directory a command runs against defeats the point of the test before it's even started.
