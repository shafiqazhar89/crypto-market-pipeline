# ADR-006: All Structural Changes via Feature Branch → PR → Merge

**Status:** Accepted (Phase 0, Session 4 onward)

## Context

The very first commit to the repo (initial scaffold: README, `.gitignore`, setup log) went straight to `main`. Every commit since — repo scaffold, dbt init, dlt init, dependency pinning, path-portability fixes, self-healing directories — has instead gone through a feature branch, a real PR description, and a GitHub-UI merge, even working solo with no other reviewer.

## Decision

Any change that sets a structural pattern later phases build on — folder layout, project init, pipeline code, portability/reliability fixes — goes through branch → PR → merge. The PR description states what changed, why, and how it was verified (not just intent). A one-line, zero-risk factual doc correction (e.g., fixing a stale note) is the only exception, and may go straight to `main`.

## Rationale

This proves the workflow a client or hiring reviewer would actually expect from a working data engineer, and writing a real PR description forces the discipline of stating verification explicitly rather than assuming "it runs" is enough. The rule of thumb applied: ask what the blast radius of the change is — zero-risk, no reviewable content, direct to `main` is defensible; anything else earns a branch.

## Consequences

Six PRs to date follow this pattern (#1 repo scaffold, #2 dbt init, #3 dlt init, #4 dependency pinning, #5 path portability, #6 self-healing directories). `git log --graph` shows a clean history of real merge commits, not fast-forwards or squashed-away history — verified explicitly after PR #1, not assumed.
