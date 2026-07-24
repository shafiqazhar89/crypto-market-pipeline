# ADR-003: Docker Desktop, Not Native Docker-in-WSL

**Status:** Accepted (Phase 0, Session 1)

## Context

A container runtime was needed inside WSL2 on Windows 11. Two options: Docker Desktop (GUI app on Windows, injects its CLI into WSL) or installing Docker Engine natively inside the Ubuntu distro.

## Decision

**Docker Desktop**, not native Docker-in-Ubuntu.

## Rationale

Simpler to set up and toggle for a solo developer: GUI, automatic WSL integration per-distro, a tray icon to start/stop. Free for personal, non-enterprise use. Native Docker Engine inside Ubuntu is the documented fallback if Docker Desktop's licensing terms or a future corporate policy make it impractical.

## Consequences

Docker Desktop must be running on the Windows host for `docker`/`docker compose` commands to resolve inside WSL at all — if they suddenly report "command not found," the first check is always "is Docker Desktop open," not a deeper environment investigation (documented gotcha, hit and resolved during this build). Revisit if licensing terms change materially, or if a future employer/client environment blocks Docker Desktop specifically (the Accenture machine did — see the machine-independence operating notes).
