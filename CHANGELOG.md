# Changelog

## 0.1.3 — 2026-09-12

- Add a checked `SourceLedger` adapter for an explicitly resolved directed
  gas-jet source plane to the existing JETPLU initial-state interface.
- Preserve the JETPLU core equations and legacy vertical route; reject liquid,
  unbalanced, or non-directed source states before they enter the adapter.
- Document the two-dimensional wind--vertical scope: this adapter does not
  create a yawed three-dimensional receptor field.

## 0.1.2 — 2026-09-12

- Add validated, JSON-serialisable `SourceLedger`/`SourceState` input handoff.
- Add explicit conversion from a resolved ledger to DEGADIS source tables.
- Reject unresolved liquid source states rather than treating them as gas-only.

## 0.1.1 — 2026-09-09

- Add an optional LH2PoolX adapter that converts qualified quasi-steady pool
  source terms to the original DEGADIS ground-source table.
- Refuse confined-pool and unresolved-inventory inputs rather than silently
  treating them as a stationary ground source.

## 0.1.0 — 2026-09-07

- First public release of the legacy DEGADIS 2.1 Python reimplementation.
- Separates the original-model route from non-public DEGALI/LH2 research extensions.
- Records reproducibility evidence without redistributing EPA reference material or experimental data.
