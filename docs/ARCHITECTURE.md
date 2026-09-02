<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Theta Pinch Core — Architecture
-->

# Architecture

## Purpose and evidence state

`SCPN-THETA-PINCH-CORE` is the device-family owner for theta-pinch systems
in the SCPN Reactor Systems Research Group portfolio. The
repository owns three implemented capabilities at
`computational_prototype` in `src/scpn_theta_pinch_core/`: the device
configuration model (design record ADR 0002, evidence record
`VALIDATION.md#device-configuration-model`), the diagnostic and
clock semantics model (design record ADR 0003, evidence record
`VALIDATION.md#diagnostic-and-clock-semantics`) and the level-0
device physics (design record ADR 0005, evidence record
`VALIDATION.md#level-0-device-physics`; owned domain
`analytic_device_physics_models`, disjoint from solver mathematics). Every other
section below describes boundaries and contracts. The claim inventory is
empty; capability and claim inventories are generated and drift-checked.

## The five-surface boundary

1. **Governing confinement physics** — the `theta_pinch`
   (azimuthal-current pinch, `self_magnetic` registry family): a
   fast-rising axial field induces an azimuthal plasma current; the
   resulting radial Lorentz force implodes the column against the axial
   field, heating by shock and adiabatic compression. Confinement is
   radial and transient; the open-ended geometry's axial end loss sets the
   confinement time and is a first-class device declaration. The Z-pinch
   (axial current, azimuthal field — the exact role reversal), the dense
   plasma focus, and closed-field devices fail this sharing test and are
   excluded. The FRC uses theta-pinch-class programming for formation, but
   FRC physics belongs to its own owner; this repository owns the theta
   pinch as a compression device.
2. **Primary driver and energy delivery** — fast capacitor banks
   discharging into a single-turn (or segmented) compression coil around
   the discharge tube, with preionisation systems preparing the fill
   plasma; optional bias-field circuits are configuration facets.
3. **Plant and shot lifecycle** — single-shot pulsed lifecycle:
   preionisation, main-bank trigger, radial implosion and shock heating,
   adiabatic compression plateau, end-loss-dominated decay, and
   disassembly. Device-level hazard semantics cover coil/insulator
   failure, restrike, and bank faults.
4. **Diagnostic, reference-frame, and clock model** — radial-profile
   conventions in the coil midplane, end-loss instrumentation, excluded-
   flux and interferometric compression measurements, and nanosecond-to-
   microsecond shot-relative clock identities.
5. **Solver, evidence, and control-contract boundary** — versioned seams
   towards `SCPN-FUSION-CORE`, review-only semantics towards
   `SCPN-PHASE-ORCHESTRATOR`, and the device-owned CONTROL adapter
   specification towards `SCPN-CONTROL`.

## Position in the SCPN ecosystem

```text
SCPN-THETA-PINCH-CORE (device truth: compression policy, end-loss
                       semantics, pulsed lifecycle, safety envelope,
                       adapter spec)
   │  optional versioned solver seams (none active)
   ├──────────────► SCPN-FUSION-CORE      (solver mathematics, evidence)
   │  typed review-only semantics
   ├──────────────► SCPN-PHASE-ORCHESTRATOR (semantics, comparability)
   │  device-owned adapter (specification only; no implementation)
   ├──────────────► SCPN-CONTROL          (admission; sole ControlAction author)
   │  derived portfolio descriptor (not_federated)
   └──────────────► SCPN-STUDIO           (catalogue, evidence UI, gating)

SCPN-CONTROL ──admitted ControlAction──► independent machine protection
                                          (final veto) ─► plant actuators
```

## Repository layout

| Path | Role |
|---|---|
| `reactor-domain.json` | portable source of project identity and contracts |
| `studio/portfolio-descriptor.json` | derived Studio descriptor, `not_federated` |
| `capability-inventory.json` | generated inventory of the three implemented capabilities |
| `src/scpn_theta_pinch_core/physics/` | level-0 device physics (Scyllac sharp-boundary relations, composed record) |
| `rust/` | optional native kernels (`scpn-theta-pinch-rs`), bit-exact with the Python floor |
| `benchmarks/` | standard-conformant benchmark and committed local artefact |
| `docs/CONTROL_ADAPTER_SPECIFICATION.md` | device-owned adapter contract |
| `docs/THREAT_MODEL.md` | assets, trust boundaries, misuse paths |
| `docs/adr/0001-repository-boundary.md` | boundary decision record |
| `tools/` | validators, derivation tools, preflight orchestrator |
| `tests/` | statement- and branch-complete tests for `src/` and `tools/`, native parity tests |
| `.github/workflows/` | read-only CI definitions (no publication) |

## Contract surfaces and versioning

- `reactor-domain.json` follows schema `scpn.reactor-domain.v1`; unknown
  schemas are rejected by consumers.
- The Studio descriptor is derived deterministically and embeds the
  manifest's SHA-256; manual edits are detected as drift.
- The CONTROL adapter contract is specification-only at `0.1.0-spec`.
- SPO binding is fixed to reactor registry `1.0.0`, digest
  `786d9542ce76c56dd7748fa948b17efed6c073525e527ce90e6d5e29a2d00090`.

## What would change this architecture

Acceptance of a FUSION solver seam through the family migration gate,
ratification of an SPO `ControlIntent`-class contract, or Studio federation
after a real capability passes producer and consumer gates — each recorded
as a versioned contract change in a new ADR.
