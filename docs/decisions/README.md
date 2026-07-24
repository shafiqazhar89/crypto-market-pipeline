# ADR Drafts — Ready to Copy into `docs/decisions/`

Drafted from `Working_Notes.md`'s decision log (D1–D11), split out per the plan stated in that file's own header. Two decisions were deliberately **excluded** from this public set:

- **D5** (moved build to the personal ASUS TUF A15, off the company laptop) and **D6** (using a personal Claude account, not the enterprise one) — both are personal/business logistics tied to a specific employer's security policy, not technical architecture decisions a hirer or client needs to see in a portfolio repo. Moved to `Private_Learning_Log.md` instead.

Mapping from the original `Working_Notes.md` decision IDs to these ADRs:

| Working_Notes.md ID | ADR |
|---|---|
| D1 | ADR-001 |
| D2 | ADR-002 |
| D3 | ADR-003 |
| D4 | ADR-004 |
| D5, D6 | *(excluded — see `Private_Learning_Log.md`)* |
| D7 | ADR-005 |
| D8 | ADR-006 |
| D9, D10, D11 | ADR-008 (combined — same investigation, one coherent decision) |
| *(new)* | ADR-007 (dependency pinning — was implicit in the Build Brief, never had its own D-number) |

**To finish the split:** copy these eight files into your actual repo's `docs/decisions/` folder, commit via the usual branch → PR → merge workflow (this itself is a good candidate PR — "docs: promote working-notes decisions to ADRs"), then this `ADR_drafts` folder can be deleted.
