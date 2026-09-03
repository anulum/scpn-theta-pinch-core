<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Theta Pinch Core — ADR 0007
-->

# ADR 0007 — Consume the shared geometry kernels instead of carrying copies

Status: accepted (2026-09-03). Landed together with ADR 0006: this
repository never carried a geometry substrate of its own and never will.

## Context

The family-independent geometry substrate — deterministic unit circle,
cylinder and annular-tube tessellation, the closed-mesh contract with its
measures and canonical bytes, and the STL/GLB serialisers — lives once in
the research group's shared kernel library `scpn-reactor-kernels` (its ADR
0002, kernels `geometry_unit_circle`, `geometry_mesh_contract`,
`geometry_primitives`, `geometry_exports`), where its accuracy, closure,
convergence and native parity are proven. The pilot family landed that
substrate first and then moved it into the library; this family starts on
the library, so no third copy is created and no parity is re-proven here.

## Decision

1. The repository declares `scpn-reactor-kernels` as its one runtime
   dependency, pinned to a commit object of the library's public
   repository (`pyproject.toml`, `dependencies`); no release of the
   library exists yet, so the commit is the exact identity. The pinned
   commit is the one that introduced the geometry kernels, the same commit
   the other geometry consumers carry.
2. The manifest carries the pin as an optional `kernel_library` block:
   distribution, version, `source_commit`, `inventory_sha256` (the SHA-256
   of the library's generated `kernel-inventory.json` at that commit) and
   the sorted identifiers of the kernels consumed. The validator enforces
   every field exactly; a contract test proves that the manifest, the
   `pyproject.toml` dependency, the installed package version and the CI
   install steps agree on one commit.
3. `src/scpn_theta_pinch_core/geometry/` holds device truth only:
   `device.py` (the mechanical envelope), `model.py` (composition of the
   seven bodies on the library's primitives; the mesh type of every body
   is the library's `TriangleMesh`) and `export.py` (device-side
   provenance `glb_extras` handed to the library's serialisers). The
   library's segment refusal is re-raised as `DeviceGeometryError` with
   its message. Library symbols are not re-exported for consumers to
   import through this package.
4. The native crate `scpn-theta-pinch-rs` carries physics only and is
   unchanged. Parity of the device model is proven against the library's
   native module (`scpn_reactor_kernels_native`): every vertex coordinate,
   face index, volume and area of the seven bodies agrees bit for bit with
   the library's native tessellation and measures, so the consumer
   inherits the library's bit-exactness.
5. The 3D-model benchmark measures the library's Python floor (through the
   validated device build) against the library's native kernels.
6. The manifest adds the excluded domain
   `shared_physics_geometry_and_numerics_kernels` owned by
   `SCPN-REACTOR-KERNELS`, mirroring the library's exclusion of device
   truth.

## Consequences

Evidence maturity stays `computational_prototype`; the claims inventory
stays empty. `VALIDATION.md#device-3d-model` lists what this repository
exercises and points at the library's evidence for the kernels
themselves. A change of the library pin is a governed data change of this
repository (manifest, descriptor and inventory regeneration, envelope
fixture re-pin, SPO re-intake). Continuous integration installs the
package so that the pinned library resolves in the static-policy, test and
pre-commit jobs, and additionally builds the library's native module in
the native job so the parity file never silently skips there.
