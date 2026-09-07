# Reproduction audit

## What was checked

DEGADISx was audited against a locally obtained EPA DEGADIS 2.1 reference distribution and its published benchmark listings. The audit has two distinct layers:

1. **Reference executable versus EPA listings.** Five EPA examples were replayed: B9 steady, B9 transient, EX1, EX2, and EX3. The steady and jet/listing cases reproduced all non-timestamp listing lines. The transient B9 listing had eight differences confined to seventh-significant-digit numerical formatting.
2. **Python implementation versus source-built reference executable.** Input-deck scalars and density-table values matched exactly; scalar thermodynamic and closure checks differed only at floating-point round-off. At driver level, the original adaptive integration and loose tolerance conventions produce documented non-bitwise differences: step sequences were within 6e-10 relative for the DEG1 check, and representative profile/handoff values within 1e-6. Some full-driver concentration outputs differed by up to about 3%, depending on quantity, because the original implementation intentionally retains coarse internal tolerances (including `ADDHEAT` settings).

These are reproduction checks, not experimental validation. No claim is made that all outputs are bit-identical or that the software is valid outside the original model's assumptions.

## Materials not redistributed

The reference Fortran code, EPA example input decks, EPA output listings, compiled executables, and all third-party data were used only in the local audit. They are excluded from this repository and its source/wheel distributions. A user wishing to repeat the independent oracle comparison must obtain the materials from their original rightsholder/source.

## Primary sources

- Spicer, T. O., and Havens, J. A. (1989). *User’s Guide for the DEGADIS 2.1 Dense Gas Dispersion Model*. U.S. EPA, EPA-450/4-89-019.
- U.S. EPA Support Center for Regulatory Atmospheric Modeling (SCRAM), historical **DEGADIS 2.1** distribution and example materials. Access path: https://www.epa.gov/scram.

The citation is retained for provenance. The source files themselves are not supplied by DEGADISx.
