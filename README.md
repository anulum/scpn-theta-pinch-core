<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Theta Pinch Core — README
-->

# SCPN Theta Pinch Core

Governed device-family repository for theta-pinch fusion systems within the
SCPN Reactor Systems Research Group. This repository is the designated
owner of device-level truth for the `theta_pinch` configuration of the SCPN
Phase Orchestrator reactor registry (azimuthal-current pinch).

**Evidence maturity: `computational_prototype`** (per-capability; ADR 0002).
One capability is implemented: the device configuration model — validated
parameter objects with documented consistency estimates, canonical
serialisation, and a data-only SPO registry pin (`src/scpn_theta_pinch_core/`,
evidence: `VALIDATION.md#device-configuration-model`). No parameter set
describes any real machine; the claim inventory is empty and verified by
the domain validator.

## Scope

This repository owns, for the theta-pinch device family:

- the device boundary: plant and experiment truth, shot lifecycle, and
  configuration policy for linear devices in which a fast-rising axial
  magnetic field, driven by a single-turn coil around the discharge tube,
  induces an azimuthal plasma current whose interaction with the axial
  field radially implodes and compresses the column;
- implosion-heating and adiabatic-compression semantics at device level
  (shock formation, end-loss timescales of the open-ended geometry) as
  configuration facets;
- diagnostic semantics, reference frames, and clock identity declarations;
- actuator-response model boundaries and the declared safety envelope;
- the device-owned CONTROL adapter specification;
- the binding to the SCPN Phase Orchestrator reactor registry
  (version `1.0.0`, digest
  `786d9542ce76c56dd7748fa948b17efed6c073525e527ce90e6d5e29a2d00090`);
- the machine-readable domain manifest `reactor-domain.json` and the derived
  Studio portfolio descriptor (integration state `not_federated`).

## Explicit exclusions

- **Axial-current Z-pinch devices** (current/field roles reversed):
  `SCPN-Z-PINCH-CORE`.
- **FRC equilibrium, transport, and stability physics**: `SCPN-FRC-CORE` —
  theta-pinch-class programming appears there only as an FRC formation
  facet; this repository owns the theta pinch as a compression device in
  its own right.
- **Dense plasma focus**: `SCPN-DENSE-PLASMA-FOCUS-CORE`.
- **Solver mathematics and validation evidence**: `SCPN-FUSION-CORE` until
  an exact surface passes the reactor family migration gate; no solver code
  exists in, or was copied into, this repository.
- **Typed signal semantics and comparability**: `SCPN-PHASE-ORCHESTRATOR`
  (review-only output; never actuation).
- **Control admission and action formation**: `SCPN-CONTROL` is the sole
  software authority that forms an admitted `ControlAction`.
- **Machine protection**: independent systems retain the final veto.
- **Portfolio presentation, identity, entitlement, and execution gating**:
  `SCPN-STUDIO`.

## Non-claims

This repository is not machine-ready, not safety-certified, and not
reactor-ready. It contains no implemented solver, no controller, no
benchmark result, no experimental correlation, no dataset, and no published
artefact, and no parameter set describes or validates any real machine. Coil-geometry and fuel-cycle choices are configuration
facets, not separate claims. No capability has reached any
evidence-maturity state beyond `computational_prototype`.

## Architecture

The five-surface boundary and the position of this repository in the SCPN
ecosystem are defined in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and
fixed by
[`docs/adr/0001-repository-boundary.md`](docs/adr/0001-repository-boundary.md).
The threat model is in [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md); the
CONTROL adapter contract is in
[`docs/CONTROL_ADAPTER_SPECIFICATION.md`](docs/CONTROL_ADAPTER_SPECIFICATION.md).

## Validation

Every gate currently active in this repository is listed in
[`VALIDATION.md`](VALIDATION.md). The local sequence is:

```bash
make lint        # ruff check + ruff format --check
make typecheck   # mypy --strict tools tests
make test        # pytest with 100 % statement and branch coverage on tools/
make validate    # domain manifest, descriptor, and inventory checks
make preflight   # the full fail-closed gate sequence
```

## Security

See [`SECURITY.md`](SECURITY.md) for the supported states and the private
reporting route (protoscience@anulum.li).

## Licensing

AGPL-3.0-or-later for the public repository, with a commercial licence
available (see [`NOTICE.md`](NOTICE.md)). Licence texts are under
[`LICENSES/`](LICENSES/); machine-readable licensing metadata follows
REUSE 3.x (`REUSE.toml`).

## Citation

Citation metadata is provided in [`CITATION.cff`](CITATION.cff). No release,
version, or DOI exists yet; cite the repository state you inspected.
