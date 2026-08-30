<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Theta Pinch Core — ADR 0001: repository boundary
-->

# ADR 0001 — Repository boundary and ownership

**Status:** accepted (2026-08-30)  
**Deciders:** project owner; SCPN Reactor Systems Research Group standard

## Context

The SCPN reactor portfolio assigns every built-in configuration of the SCPN
Phase Orchestrator reactor registry (version `1.0.0`, 32 configurations) to
exactly one device-family repository. The theta pinch shares the
`self_magnetic` registry family with the Z-pinch variants and the dense
plasma focus, and its programming style reappears in FRC formation; a
boundary decision was needed on all three edges.

## Decision

1. `SCPN-THETA-PINCH-CORE` owns exactly one registry configuration:
   `theta_pinch` (azimuthal-current pinch).
2. The repository owns device-level truth only: compression-device
   configuration policy (coil and preionisation classes, bias-field
   facets), pulsed lifecycle semantics with end-loss declarations, radial
   compression diagnostic and clock declarations, actuator-response model
   boundaries, the safety-envelope declaration, and the device-owned
   CONTROL adapter specification.
3. FRC physics stays with `SCPN-FRC-CORE`: theta-pinch-class field
   programming there is a formation facet of a different confinement
   object. This repository owns the theta pinch as a radial-compression
   device with open-ended axial loss.
4. Solver mathematics remains in `SCPN-FUSION-CORE` until an exact surface
   passes the family migration gate. No solver code is copied here.
5. Typed semantics remain in `SCPN-PHASE-ORCHESTRATOR` (review-only).
   Admission and `ControlAction` formation remain exclusively in
   `SCPN-CONTROL`. Machine protection remains independent with the final
   veto. Presentation remains in `SCPN-STUDIO`; this project is
   `not_federated`.
6. The repository starts, and remains until evidenced otherwise, at
   `architecture_only` with empty capability and claim inventories.

## Alternatives considered

- **One repository for Z- and theta pinches** (both self-magnetic linear
  pulsed devices): rejected — the current/field roles are exactly
  reversed, producing different instability structure (the theta pinch
  avoids the Z-pinch kink channel but pays with axial end loss), different
  drivers (compression coil versus electrode current), and different
  diagnostics (surfaces 1, 2, and 4).
- **Folding the theta pinch into the FRC repository** (shared programming
  heritage): rejected — the confinement objects differ; merging would blur
  the FRC/compression boundary the portfolio map keeps explicit.
- **Absorbing solver code at scaffold time**: rejected — violates the
  migration gate.

## Consequences

- Downstream consumers get one stable identity for the theta-pinch
  configuration and a manifest to bind against.
- The validator fails on any capability or claim entry while maturity is
  `architecture_only`.
- Boundary changes require a portfolio-level map change first; a future
  ADR records any such change here.
