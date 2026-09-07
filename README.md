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

## Reproduction evidence and data policy

The implementation was checked against the EPA DEGADIS 2.1 reference distribution and published EPA benchmark listings. The quantitative audit, its limits, and exact source locations are in [docs/reproduction.md](docs/reproduction.md).

This repository deliberately contains **no** third-party Fortran source, EPA input/output decks, experimental measurements, reduced observation data, or PDFs. See [docs/data-policy.md](docs/data-policy.md).

## Citation

Please cite both this software (see [CITATION.cff](CITATION.cff)) and the original model:

> Spicer, T. O., and Havens, J. A. (1989). *User’s Guide for the DEGADIS 2.1 Dense Gas Dispersion Model*. U.S. Environmental Protection Agency, EPA-450/4-89-019.

## License

The Python implementation is MIT licensed. DEGADIS is cited as the original model; the original Fortran distribution and source materials are not redistributed here.
