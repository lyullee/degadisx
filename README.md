# DEGADISx

**DEGADISx** is a Python reimplementation of the U.S. EPA **DEGADIS 2.1** dense-gas dispersion model. Its public interface deliberately retains the legacy DEGADIS thermodynamic and numerical route; it is not an LH2 extension and does not contain DEGALI research modules.

## Scope

DEGADISx provides the original model's ground-level steady and transient routes, pressurised-jet route, deck readers, and bridge from jet touchdown to the ground-level model. It is intended for transparent reproduction, software inspection, and research use. It is not a substitute for site-specific consequence-model selection or safety engineering review.

## Install

```bash
pip install degadisx
```

From a checkout:

```bash
pip install .
degadisx --help
```

For a separately qualified LH2 pool source term, install the optional adapter:

```bash
pip install "lh2poolx @ git+https://github.com/lyullee/lh2poolx.git"
```

`degadisx.lh2pool.source_table_from_lh2pool()` converts declared LH2PoolX
time-window terms into the original ground-source-table convention. It refuses
confined or non-equilibrium terms; it does not add an LH2 pool or jet-impact
model to the reproduced DEGADIS physics.

## Reproduction evidence and data policy

The implementation was checked against the EPA DEGADIS 2.1 reference distribution and published EPA benchmark listings. The quantitative audit, its limits, and exact source locations are in [docs/reproduction.md](docs/reproduction.md).

This repository deliberately contains **no** third-party Fortran source, EPA input/output decks, experimental measurements, reduced observation data, or PDFs. See [docs/data-policy.md](docs/data-policy.md).

## Source-ledger handoff

Version 0.1.2 adds `degadisx.SourceLedger` and `SourceState`, a model-neutral
record for a resolved source-plane state. The adapter converts H2 contaminant
rate and mass fraction into DEGADIS source-table rows while preserving area
and time history. It rejects unresolved liquid fractions: flash, impact,
droplet, and pool-inventory physics must be resolved upstream before the
ground-layer route is started.

## Directed JETPLU source handoff

Version 0.1.3 also exposes
`SourceLedger.to_directed_jet_initial_conditions()`. It converts one resolved,
single-phase gas source-plane record into the existing JETPLU initial state;
callers then run the normal JETPLU driver with that state. The adapter checks
the declared H2/total-flow mass balance and rejects remaining liquid. It does
not modify the JETPLU equations or the historical vertical `SETJET` route.

The directed entry is a two-dimensional wind--vertical calculation. A yawed
horizontal release or a cross-axis wind component is not converted into a
three-dimensional fixed-receptor prediction by this interface.

## Citation

Please cite both this software (see [CITATION.cff](CITATION.cff)) and the original model:

> Spicer, T. O., and Havens, J. A. (1989). *User’s Guide for the DEGADIS 2.1 Dense Gas Dispersion Model*. U.S. Environmental Protection Agency, EPA-450/4-89-019.

## License

The Python implementation is MIT licensed. DEGADIS is cited as the original model; the original Fortran distribution and source materials are not redistributed here.
