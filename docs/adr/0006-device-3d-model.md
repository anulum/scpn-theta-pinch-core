<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Theta Pinch Core — ADR 0006
-->

# ADR 0006 — Device 3D model: validated geometry, deterministic tessellation, open exports

Status: accepted (2026-09-03). Adds the fourth implemented capability,
`device_3d_model`, at `computational_prototype`.

## Context

The device repository owns device geometry (ADR 0001 boundary: plant and
experiment truth, configuration policy). Until this record the repository
carried the compression coil and the plasma state as numbers only; there
was no mechanical envelope and no way to present, measure or hand a design
to downstream tooling. A three-dimensional model of the device is the
substrate for every later engineering lane (surface loading, neutronics
geometry, magnet and pulsed-power layouts) and for portfolio
presentation. It must be regenerated exactly from the validated records,
must not depend on a heavy CAD kernel to run in every gate, and must never
overstate what an analytic surface is.

## Decision

1. A new owned domain `device_geometry_and_3d_model` is declared in
   `reactor-domain.json`: device-owned geometry parameters and the 3D
   model derived from them. It is disjoint from solver mathematics (no
   equation is solved), from portfolio presentation (the exported files
   are an offer, `docs/DEVICE_3D_MODEL_CONTRACT.md`; STUDIO decides the
   viewer and the federation) and from any engineering lane (no property
   is carried).
2. `DeviceGeometry` (`src/scpn_theta_pinch_core/geometry/device.py`)
   carries the linear theta-pinch mechanical envelope — discharge-tube
   bore and wall, tube overhang beyond the coils, main-coil wall, mirror-
   coil length and wall, end-flange thickness — with fail-closed
   positivity, canonical bytes, a SHA-256 digest and a strict record
   parser. The coil bore radius and the coil length are NOT repeated: they
   are the validated configuration's `coil_radius_m` and `coil_length_m`,
   so one number has one home. The layout follows section VI.A (pp. 13-14)
   of the Scyllac review already on file for ADR 0005 (W. E. Quinn et al.,
   LA-UR-73-1053 (1973)): a straight theta pinch whose main compression
   coil is flanked by mirror coils of their own bank, main and mirror
   coils sharing one bore, with a discharge tube of smaller bore inside
   them. Parameter sets are declared by the caller. The repository's own
   reference fixtures are synthetic; one anchor fixture carries the
   dimensions the source prints (coil bore 11 cm, mirror-coil length 16 cm,
   tube bore 8.8 cm, coil length five metres) so the tier can be checked
   against a published arrangement, exactly as the level-0 models are
   checked against published numbers. Reproducing a printed dimension is
   an anchor; no claim about that machine follows from it.
3. The model is tier G1: analytic bodies (solid cylinders and annular
   tubes) tessellated into closed, outward-oriented triangle meshes with
   fixed vertex and face order. Seven bodies in a fixed order: discharge
   tube, main compression coil, upstream and downstream mirror coils,
   upstream and downstream end flanges, and the plasma column (the
   declared column radius of the level-0 models extruded over the main
   coil — an analytic surface, not an equilibrium boundary). B-rep CAD
   (tier G2) is a separate, later decision.
4. The unit circle, the tessellation primitives, the closed-mesh contract
   and the serialisers are consumed from the shared kernel library, not
   implemented here; see ADR 0007 for that decision and its pin.
5. `DeviceModel3D` (`scpn.theta-pinch-3d-model.v1` `1.0.0`) records both
   source digests, the declared plasma radius, the segment count, the
   units and axis convention (metre, right-handed, z along the device axis
   increasing downstream, origin at the upstream face of the main coil),
   every body summary and fixed non-claims; its canonical digest
   identifies the exact model, and one reference digest (segments = 8) is
   pinned in the tests as an immutability fixture.
6. Build invariants are checked against the configuration and fail closed,
   never clamped: the discharge tube must fit inside the shared coil bore,
   the plasma column must be strictly inside the tube bore and its radius
   strictly positive, and the segment count must satisfy the library's
   rule (its refusal is re-raised as `DeviceGeometryError` with the
   library's message).
7. Exports are pure serialisations of the validated meshes: binary STL
   (all bodies) and glTF 2.0 binary (GLB) per the Khronos specification,
   one named node per body, float32 storage as the container requires, and
   document `extras` carrying the schema, both digests, the model digest,
   the plasma radius, the segment count, the units and the non-claims.
8. A standard-conformant benchmark (`benchmarks/device_model_3d.py`) times
   one full device tessellation with measures per generated face on both
   backends of the pinned library; the local artefact is committed and
   labelled non-isolated.

## Simplifications recorded on purpose

The end flanges are plain closing discs of the tube outer diameter: in a
real assembly the tube passes through its end hardware. Coil slots, feed
plates, ports, diagnostics, supports and the tube-to-flange seal are not
modelled. The mirror coils are drawn as plain tubes abutting the main coil
and sharing its bore; their field shaping is a physics matter and lives
in the level-0 models, not in this geometry.

## Consequences

Evidence maturity stays `computational_prototype`; the claims inventory
stays empty. `VALIDATION.md#device-3d-model` states what is exercised
(device geometry branches, model composition and placement identities,
volume convergence to the analytic bodies, export layouts read back at
specification level, native parity against the library's module) and what
is not claimed (no CAD solid, no equilibrium boundary, no material, load,
field or neutronic quantity, no real machine). The manifest change alters
`manifest_sha256` inside the plan envelope, so the envelope fixture is
regenerated from the public surface and re-pinned; the plan bytes and
`plan_sha256` are unchanged. The exported GLB and its node contract are
offered to the portfolio layer; federation state remains `not_federated`
until its gates run.
