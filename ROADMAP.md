<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Theta Pinch Core — ROADMAP
-->

# Roadmap

Planned work and implemented capability are kept strictly separate. Anything
listed under "Planned" carries no implementation, no code, and no claim in
this repository until it appears in the capability inventory with evidence.

## Implemented (repository infrastructure, not reactor capability)

- Domain manifest (`reactor-domain.json`) with validator.
- Derived Studio portfolio descriptor (`not_federated`) with drift check.
- Generated capability inventory (truthfully empty) with drift check.
- CONTROL adapter specification (contract only, no implementation).
- Local and workflow gate definitions (lint, typing, tests, coverage,
  REUSE, security audit, SBOM, documentation checks).

- **Device configuration model** (landed 2026-08-31) — validated
  compression-coil and plasma objects for `theta_pinch` with the hard
  pressure-balance invariant (beta <= 1), the magnetic-pressure
  relation `B^2 / (2 mu0)`, a high-beta regime advisory (Ribe 1975),
  canonical digests, and the SPO registry data pin;
  `computational_prototype` (ADR 0002,
  `VALIDATION.md#device-configuration-model`). Preionisation classes
  and field-rise envelopes remain future work under the same
  capability.
- **Diagnostic and clock semantics** (landed 2026-08-31) — synthetic
  diagnostic-channel and clock declarations aligned fail-closed with the
  pinned SPO observability-profile catalogue (release `1.0.0`): candidate
  applicability, carrier admissibility, exact evidence vocabularies,
  clock-kind compatibility, Nyquist and event-timing bounds, canonical
  digests; the reference plan mirrors canonical practice
  (bank waveform event train, rotational-mode probe array, synthetic oscillator); `computational_prototype` (ADR 0003,
  `VALIDATION.md#diagnostic-and-clock-semantics`). No ingress is
  declared; the SPO semantic-profile state remains `not_declared`.
- **Level-0 device physics** (landed 2026-09-02) — the sharp-boundary
  relations of the 1973 Scyllac review evaluated on the validated
  configuration: operating state (beta, ion temperature, Alfvén speed,
  end propagation time), `l = 1, 0` toroidal equilibrium, `m = 1` growth
  estimate with wall stabilisation, empirical end-loss scaling; a
  canonical `Level0PhysicsRecord`, optional native kernels bit-exact with
  the Python floor, and a standard-conformant benchmark;
  `computational_prototype` (ADR 0005,
  `VALIDATION.md#level-0-device-physics`). Follow-ups under the same
  capability: adiabatic-compression and implosion-heating relations once
  a source is on file; the family's 3D model once the shared kernel
  library can be pinned.

## Planned (no implementation exists; ordering is not a commitment)
1. **Safety-envelope declaration** — machine-readable operational envelope
   (bank, coil stress, repetition bounds) consumed by the CONTROL adapter
   contract.
2. **CONTROL adapter implementation** — device-owned adapter against the
   published specification, with replay fixtures and HIL evidence,
   targeting `control_research_ready` only after replay and HIL
   acceptance.
3. **Solver seam consumption** — versioned consumption of exact
   `SCPN-FUSION-CORE` seams for implosion and compression surfaces,
   strictly after the family migration gate proves exact replacement; no
   solver code is copied.
4. **Facility-data correlation** — preregistered acceptance contracts
   against identified facility or published experimental data, targeting
   `experiment_correlated` per capability.

## Not planned in this repository

Axial-current Z-pinches, the dense plasma focus, FRC physics, closed-field
and open-field magnetic systems, inertial and magneto-inertial systems,
generic controller mathematics, machine-protection logic, and any direct
actuation path.
