<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Theta Pinch Core — ADR 0008
-->

# ADR 0008 — Device CAD model: B-rep solids and a deterministic STEP export on the pinned CAD kernels

Status: accepted (2026-09-03). Adds the fifth implemented capability,
`device_cad_model`, at `computational_prototype`.

## Context

The tier-G1 model (ADR 0006, ADR 0007) produces analytic triangle meshes:
enough for viewing, volumes and simple CSG neutronics, but not an
engineering solid — no fillets, no ports, no STEP for CAD tooling, and no
B-rep a volume mesher can consume. The research group's tier-G2 lane
defines the next rung: B-rep solids of the SAME seven bodies built by the
pinned third-party OpenCASCADE kernel through the shared kernel library's
`cad` group, a normalised deterministic STEP export, and a faceting
checked against the tier-G1 mesh.

## Decision

1. `src/scpn_theta_pinch_core/geometry/cad.py` builds the seven bodies
   with the library's B-rep constructors (`cylinder_solid_brep`,
   `annular_tube_brep`) at the same names, roles, material tokens and
   extents as `build_device_model`, assembles them into the library's
   `BrepAssembly`, exports the normalised STEP bytes and facets every
   body. The record `DeviceModelCAD`
   (`scpn.theta-pinch-cad-model.v1`, version `1.0.0`) carries the units
   and axis convention of the tier-G1 record, both source digests, the
   declared plasma radius, the declared deflections and the reference mesh
   segment count, the back-end versions, the assembly manifest, the STEP
   digest and the per-body evidence; canonical bytes and the SHA-256
   digest follow the tier-G1 pattern.
2. The per-body evidence is the shared library's (`cad_evidence`, the
   library's ADR 0009), not this repository's: the checks are statements
   about a solid, a mesh and a bound, and none of them is device
   knowledge. What this module owns is the schema identity, the
   composition of the seven bodies, this family's build invariants and its
   non-claims. The evidence is fail-closed by construction — every body's
   B-rep volume and surface area must agree with the analytic closed form
   within `1e-9` relative, the faceted volume's deficit must stay within
   the declared bound `2 d / r` at the body's smallest circular radius,
   and the faceted volume must agree with the tier-G1 mesh at the declared
   segment count within the exact polygon-deficit bound
   `1 - (n / 2 pi) sin(2 pi / n)`. A violated bound raises the library's
   `CadError`, which the build re-raises as `DeviceGeometryError`;
   nothing is clamped.
3. The kernel library pin moves to the commit carrying the `cad` group,
   its body-evidence kernel and the bounding-box correction below. The
   library's `cad` extra is NOT a dependency of this package: every other
   capability works without a B-rep kernel, so declaring it as one would
   overstate what the package needs and would pull a roughly one-gigabyte
   back-end into every environment that installs it. It is an optional
   extra here too — `[project.optional-dependencies] cad` naming the same
   commit — and only the two CI jobs that need it install it: the coverage
   job, because the CAD module is covered like every other module, and the
   `cad` job. A contract test proves the plain dependency and the extra
   name one commit. The manifest's
   `kernel_library` block records the new source commit, the inventory
   digest at that commit and the consumed kernel identifiers (four CAD
   kernels plus the four geometry kernels; `cad_volume_mesh` and
   `cad_placement` are not consumed by this family and are not listed).
4. Evidence class, per the library's ADR 0006: OpenCASCADE is a pinned
   third-party numerical kernel, not the bit-exact floor; determinism of
   the STEP bytes is claimed within one pinned back-end environment only
   (the record carries the versions), never across back-end versions. The
   pinned reference digest of the record in the tests is bound to those
   versions; a back-end bump re-pins it as a governed data change.
5. `geometry/export.py` gains `write_step`, which writes exactly the
   digested bytes the record carries, so the exported file and the record
   cannot diverge. The consumer contract document gains the STEP section.
6. The manifest gains the capability `device_cad_model`
   (`computational_prototype`, `VALIDATION.md#device-cad-model`); the
   descriptor, the inventory and the envelope fixture are regenerated;
   the CI gains a `cad` job that installs the pinned library with the
   extra — and, before it, the system library the mesher's wheel links
   against, without which the extra cannot even be imported on a hosted
   image — then runs the CAD tests and a benchmark smoke.
7. The anchor fixture is exercised at this tier too: a test proves that
   every dimension the filed Scyllac review prints for the five-metre
   linear theta pinch — the coil bore and length, the discharge-tube bore
   and the mirror-coil length — appears in the built solids. Reproducing a
   printed dimension is an anchor, not a claim about that machine.

## Consequences

Evidence maturity stays `computational_prototype`; the claims inventory
stays empty; no material property, load, field or neutronic quantity is
carried by any body. The STEP file is an export of the record, never its
source; a STEP file is not an engineering model.

This family's build found a defect in the shared library and the fix is
part of the pin in item 3: the B-rep bounding box was taken from the
kernel's optimal box, which consults an attached triangulation when one
exists, so a body's recorded box — and every assembly manifest digest
taken after a faceting — depended on whether the faceting had run. The
assembly-level placement checks in this repository's tests are read from
those boxes, and they reported two bodies that meet face to face as a
deflection apart. The library now takes the box from the geometry alone.

The end flanges remain closing discs of the tube outer diameter, as at
tier G1: the tube passes through its end hardware in a real assembly, and
that simplification is a property of both tiers, stated in the non-claims.
