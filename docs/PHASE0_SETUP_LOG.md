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

---

## Pro-tips picked up this session (also copied to Working_Notes.md §4)

- **Redact secrets, not identifiers.** Never share private key files (`id_ed25519`, no `.pub`), passphrases, API keys, `.env` contents, or `.dlt/secrets.toml`. Public keys, fingerprints, usernames, and version strings are safe and often necessary to share for debugging.
- **`eval "$(...)"` vs `eval "(...)"`** — the `$` triggers command substitution (capture and run the *output* of the command). Without it, bash just treats `(...)` as a subshell — nothing gets exported to your current shell. Easy typo, easy to miss because it doesn't error loudly.
- **Docker's CLI in WSL only exists while Docker Desktop is running on Windows** — if `docker` commands suddenly say "not found," check Docker Desktop is open first before debugging anything else.
