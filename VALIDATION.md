<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Theta Pinch Core — VALIDATION
-->

# Validation

Every gate currently active in this repository, with its exact scope,
followed by the evidence record of each implemented capability.

## Local gates

| Gate | Command | Scope |
|---|---|---|
| Lint | `ruff check .` | all Python under `src/`, `tools/`, `tests/` and `benchmarks/` |
| Format | `ruff format --check .` | same scope |
| Typing | `mypy --strict src tools tests benchmarks` | zero errors, strict mode |
| Tests + coverage | `pytest -q --cov=src --cov=tools --cov-branch --cov-fail-under=100` | 100 % statement and branch coverage of `src/` and `tools/` |
| Domain manifest | `python3 tools/validate_reactor_domain.py reactor-domain.json` | schema, registry version/digest, exact configuration set, capability inventory shape and ceiling rule, safety boundary |
| Studio descriptor | `python3 tools/derive_studio_descriptor.py --check` | committed descriptor byte-identical to a fresh derivation |
| Capability inventory | `python3 tools/generate_capability_inventory.py --check` | committed inventory byte-identical to a fresh generation |
| Licensing | `reuse lint` | REUSE 3.x compliance of the full tree |
| Workflow lint | `actionlint` | all files under `.github/workflows/` |
| Workflow modularity | `python3 tools/audit_workflows.py` | distributed workflow inventory: single ownership per job, coordinator/gate contract, action pinning, size ceilings |
| Native kernels | `make rust` (`cargo fmt --check`, `cargo clippy --all-targets --features python -- -D warnings`, `cargo test` in `rust/`) | formatting, lints with warnings denied, kernel unit tests |
| Native parity | `pytest -q tests/test_physics_native_parity.py` | bit-exact float64 agreement of every native kernel with the Python floor (skipped hermetically when the optional native module is absent) |
| Documentation | `python3 tools/preflight.py --only docs` | UTF-8 readability and relative-link integrity of every Markdown file |
| Orchestrated | `python3 tools/preflight.py` | fail-closed run of all gates above |

## Workflow gates

Definitions are present in-repository; they run on the hosted platform
only once a remote exists under separate owner authority.

The hosted surface is modular: `ci.yml` is a coordinator that carries
only trigger policy, two reusable-workflow calls, and one stable
fail-closed `gate` job aggregating every category (failure,
cancellation, and unexpected skips all fail the gate). Every job is
declared and owned exactly once in the versioned inventory
`.github/workflow-inventory.json`, which the workflow-modularity guard
verifies locally and in hosted CI.

| Workflow | Purpose |
|---|---|
| `ci.yml` | coordinator and stable required gate |
| `reusable-static-policy.yml` | lint, format, typing, domain policy, workflow guard |
| `reusable-tests.yml` | tests with complete statement and branch coverage; native crate gates, parity and benchmark smoke |
| `pre-commit.yml` | exact pre-commit parity |
| `codeql.yml` | Python code scanning |
| `security-audit.yml` | secrets, dependency, licence, and workflow policy |
| `docs.yml` | strict documentation and link validation, no deployment |
| `sbom.yml` | reproducible dependency inventory, no release |
| `scorecard.yml` | read-only supply-chain analysis |

## Shared ecosystem gate

From the monorepo root:

```bash
python3 agentic-shared/scripts/repository_tier0_scaffold_audit.py \
  03_CODE/SCPN-THETA-PINCH-CORE --json
```

proves the Tier-0 local-scaffold machine profile (required and forbidden
paths, Git/remote boundary, workflow pins and permissions, badge non-claims,
JSON integrity, defensive ignore rules).

## Device configuration model

Evidence record of the `device_configuration_model` capability
(`computational_prototype`; design record: `docs/adr/0002-device-configuration-model.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- Validated frozen parameter objects (`CompressionCoil`, `PlasmaState`,
  `DeviceConfiguration`) rejecting non-finite values, non-positive
  extents, and a declared beta above one (radial pressure balance is a
  hard invariant) — every rejection branch is tested.
- The magnetic-pressure relation `p_B = B^2 / (2 mu0)` as a documented
  derived quantity, with an advisory finding for beta below one half
  (theta pinches characteristically operate at high beta; Ribe, Rev.
  Mod. Phys. 47 (1975) 7), reported and never clamped.
- Canonical serialisation (sorted keys, NaN/infinity rejected on both
  emit and parse), SHA-256 digest identity, and a strict round-trip
  parser that refuses unknown fields.
- A data-only pin equality check binding the model to the SPO reactor
  registry version and digest declared in `reactor-domain.json`.

Bounded claims — what is NOT claimed:

- No parameter set describes, approximates, or validates any real
  machine; every exercised parameter set is a synthetic test fixture.
- The estimates are advisory regime checks, not equilibrium, stability,
  or end-loss results; no benchmark, dataset, solver, controller, or
  experimental correlation exists in this repository.

## Diagnostic and clock semantics

Evidence record of the `diagnostic_clock_semantics` capability
(`computational_prototype`; design record: `docs/adr/0003-diagnostic-clock-semantics.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- Validated frozen declaration objects (`ClockModel`,
  `DiagnosticChannelPlan`, `DeferredCandidate`, `DiagnosticPlan`)
  rejecting catalogue misalignment: inapplicable candidates,
  inadmissible carriers, evidence-vocabulary mismatches, incompatible
  clock kinds, Nyquist violations, unresolvable event-timing bounds,
  and incomplete candidate coverage — every rejection branch is tested.
- A data-only pin (`ObservabilityBinding`) to the SPO
  observability-profile catalogue release `1.0.0`
  (`d70c0de696534e5a77066ef8420cf7ca17bc4d7321984b0ac83523dbc1dce609`),
  bound in turn to reactor registry `1.0.0`; a plan pinned to any other
  release is rejected.
- A reference plan mirroring canonical practice with synthetic
  declarations: bank waveform event train, rotational-mode probe array, synthetic oscillator, each bound to its clock domain.
- Documented advisory band and timing checks with their sources stated
  in the code: rotational/wobble instability bands of 0.1–10 MHz and microsecond bank timing (Ribe 1975); findings are reported, never clamped.
- Canonical serialisation (sorted keys, NaN/infinity rejected on both
  emit and parse), SHA-256 digest identity, and a strict round-trip
  parser that refuses unknown fields.

Bounded claims — what is NOT claimed:

- No channel describes a real diagnostic, measurement, or facility;
  every plan is a synthetic declaration of HOW evidence slots would be
  bound, marked `synthetic=True` by hard invariant.
- No SPO semantic-profile ingress is declared; the profile registry
  `ingress_state` for this device family remains `not_declared`, and
  no adapter, producer, or handoff exists in this repository.

### Portable plan envelope

The `diagnostic_clock_semantics` capability additionally exercises a
producer-owned portable envelope
(`src/scpn_theta_pinch_core/plan_envelope.py`,
`scpn.reactor-diagnostic-plan-envelope.v1` version `1.0.0`): one
canonically serialised object carrying the exact project identity and
owned configurations, the capability and its maturity, the
synthetic/review-only/non-actuating statements, both SPO registry pins,
the SHA-256 digest of the inner canonical plan, the producer revision,
and fixed no-observation/no-control non-claims. The committed immutable
fixture (`tests/data/plan_envelope_fixture.json`, byte hash pinned in
the tests) is verified together with positive, tamper, wrong-project,
wrong-configuration, registry-drift, duplicate-member, and non-finite
rejection paths, all under the 100 % coverage gate. The envelope claims
nothing beyond the enveloped synthetic declaration.

### Typed frames, clock relations, and acquisition geometry

The deepened model adds typed reference frames (per-repository allowed
`FrameKind` subset; every noncyclic `coordinate_frame` binding must
reference a declared frame), clock synchronisation relations
(synthetic offset/uncertainty BOUNDS between declared non-simulation
clocks with an explicit method statement — no correlation evidence is
claimed and no clock is mapped to physical wall time), and per-channel
acquisition windows and element counts with device-cited advisory
scales. Both decoders are hardened per the SPO intake architecture:
recursive exact-key refusal in every nested entry, duplicate-member
refusal, and byte-canonical refusal (a document that is not exactly
canonical bytes is rejected). The envelope is `1.1.0`, adding
`manifest_sha256` — the SHA-256 of the committed canonical
`reactor-domain.json` — verified in tests against the committed file.
All declarations remain synthetic; nothing here observes or controls
anything.

### Signal inventories, frame transformations, and clock topology

The depth slice (envelope `1.2.0`; a `1.1.0` document is refused by the
`1.2.0` codec and vice versa — no defaults, no cross-version coercion;
`1.1.0` remains historical custody at the consumer) adds three typed
declaration surfaces, every branch under the 100 % statement-and-branch
gate:

- A per-channel **signal inventory** (`SignalDeclaration`: identifier,
  quantity, unit, role, description). Hard rules: non-empty, unique and
  sorted; exactly one `carrier`; a `timing_marker` in `"s"` exactly for
  event-relative channels and forbidden otherwise; numerical-only
  channels declare a single `phase`/`rad` carrier. Quantity and unit are
  declared tokens — no SI or UCUM validation is performed or claimed —
  and no declaration creates or overrides a candidate, carrier,
  observation, or phase: the candidate profile stays authoritative. An
  advisory flags a multi-element cyclic array without an amplitude
  signal.
- **Frame transformations** (`FrameTransformation`): the frame kinds this
  repository may declare admit no transformation pair, so the
  transformation tuple must be empty and a second frame — which could
  never be connected — is refused. The model, its admissibility table
  and its declaration-only semantics (`evidence_claimed` always `False`)
  are shared with the portfolio.
- A **clock topology** (`ClockDomain`, `ClockTopology`): every physical
  clock in exactly one domain, the simulation clock in none; a domain
  holding a facility clock is rooted there, otherwise at its shot-event
  epoch; every non-root member declares a relation to its root; every
  non-reference root declares a relation to the reference root (star);
  relations must not form a cycle. The reference plan declares one
  domain (`clk_facility` root, `clk_shot` member); multi-domain rules
  are exercised by test-constructed plans. Scopes are declarations;
  `mapping_state` stays `unmapped`.

## Level-0 device physics

Evidence record of the `level0_device_physics` capability
(`computational_prototype`; design record: `docs/adr/0005-level0-device-physics.md`).
Source: W. E. Quinn et al., "Review of Scyllac theta-pinch experiments",
LA-UR-73-1053 (1973), OSTI 4460392 (open access).

What is exercised, all under the 100 % statement-and-branch coverage gate
(`src/scpn_theta_pinch_core/physics/`):

- **Sharp-boundary state** (`balance.py`): `beta = p / (B^2 / 2 mu0)` from
  the configuration, the equal-species ion temperature `T = p / (2 n e)`,
  the Alfvén speed `B / sqrt(mu0 n m_i)` and the end-to-centre propagation
  time `(L/2) / v_A` at a declared density and ion mass; `beta = 1`
  (allowed by the configuration) is refused by every sharp-boundary model,
  never clamped. Tests verify the closed forms and the `m_i^-1/2`, `n^-1/2`
  scalings.
- **Scyllac `l = 1, 0` toroidal equilibrium** (`toroidal_equilibrium.py`;
  source p. 2, eqs. 3 and 7): the excursions `delta_1`, `delta_0`, their
  product against the required `-2 / ((3 - 2 beta) h^2 a R)`, the balance
  ratio (unity at equilibrium, tested to `1e-12`), the required
  field-ratio product and the auxiliary field ratio of eq. (3). Anchor:
  the 5-m sector point of Fig. 2 (beta 0.85, a 0.7 cm, R 2.375 m,
  h 0.19 /cm) yields a required product of −0.0059 against the measured
  −0.0064 and the plotted sharp-boundary value ≈ −0.0065; the quotient
  forms of the excursions are the ones that reproduce it, which resolves
  the scan's typographical ambiguity, with a declared 10 % tolerance.
- **`m = 1` growth estimate and wall stabilisation** (`stability.py`;
  eqs. 4 and 6; the wall condition derived from eq. 6): the three terms,
  the bracket, the growth rate `h v_A sqrt(bracket)` with a stable
  disposition when the bracket is non-positive, and the reduced eq. (4)
  estimate. Anchors: the source's worked example `a = 3 cm, beta = 0.8,
  h a = 0.13 → a/b = 0.4` is reproduced to `0.40 ± 0.01` (0.399); with the
  source's stated orders of magnitude for the 5-m sector (B ~ 3.6 T,
  n ~ 2.5e22 m^-3, beta 0.85, equal field ratios with product 0.0064) the
  growth rate lands within a factor of two of the source's calculated
  1.0 MHz (the source does not print every input of its own calculation,
  so no tighter statement is made); the growth rate is exactly zero at the
  wall-stabilisation boundary.
- **End-loss scaling** (`end_loss.py`; p. 16 and Table I): `tau ∝ L /
  T_i^(1/2)` normalised to the linear Scyllac point (5 m, 2.7 keV,
  11.5 μs); the Table I rows for Scylla IV-1 (2.13 μs) and Scylla IV-3
  (9.67 μs) are reproduced within 1 % (the table's own rounding); the
  scaling exponents are exact.
- A composed `Level0PhysicsRecord` (`scpn.theta-pinch-level0-physics.v1`
  `1.0.0`) with canonical bytes, SHA-256 digest and fixed non-claims, built
  from the validated configuration and explicit `ModelInputs`; every input
  rejects non-positive and non-finite values; a plasma radius not smaller
  than the coil radius is refused.
- **Native parity**: the Rust crate in `rust/` mirrors every kernel with
  identical operation order; `tests/test_physics_native_parity.py`
  compares float64 bit patterns over a 36-point state grid plus the
  equilibrium, growth, wall and end-loss inputs.
- **Benchmark**: `benchmarks/level0_physics.py` per the ecosystem
  benchmark standard; results in `docs/benchmarks.md` and the committed
  local artefact `benchmarks/results/level0_physics.local.json`.

Bounded claims — what is NOT claimed:

- Every number is a closed-form evaluation of a 1973 sharp-boundary model
  on a synthetic configuration; no equilibrium, stability, compression or
  transport equation is solved, and no eigenvalue problem exists here.
- The anchors reproduce numbers printed in the source; they are not
  correlations with experimental data, and the growth-rate anchor is an
  order-of-magnitude reproduction by design.
- No adiabatic-compression, implosion-heating, yield, gain, reactivity or
  confinement statement is made; the end-loss scaling is an empirical
  three-device fit that the source itself contrasts with two disagreeing
  theoretical models.
- No value describes, approximates or validates any real machine; the
  benchmark measures per-point evaluation cost of two implementations of
  the same closed forms, not physics.
- Maturity stays `computational_prototype`.

## Device 3D model

Evidence record of the `device_3d_model` capability
(`computational_prototype`; design records: `docs/adr/0006-device-3d-model.md`
and `docs/adr/0007-shared-geometry-kernels.md`; consumer contract:
`docs/DEVICE_3D_MODEL_CONTRACT.md`).

The unit circle, the tessellation primitives, the closed-mesh contract and
the STL/GLB serialisers are consumed from the shared kernel library
`scpn-reactor-kernels`, pinned in the manifest (`kernel_library`: commit
object and kernel-inventory digest) and in `pyproject.toml`; their evidence
(polynomial accuracy against `libm`, exact polygon-prism identities,
quadratic convergence, closure and orientation, export layouts, native
parity) is the library's, at its `VALIDATION.md#geometry-kernels`. What
this repository exercises, all under the coverage gate
(`src/scpn_theta_pinch_core/geometry/`):

- **Device geometry** (`DeviceGeometry`): seven SI parameters of the linear
  theta-pinch envelope (discharge-tube bore and wall, tube overhang, main
  coil wall, mirror-coil length and wall, end-flange thickness) with
  fail-closed positivity, canonical bytes, SHA-256 digest and a strict
  parser refusing unknown fields and non-finite literals; every rejection
  branch is tested. The coil bore radius and the coil length are not
  repeated here: they are the validated configuration's `coil_radius_m`
  and `coil_length_m`. The layout is the qualitative arrangement of the
  linear theta pinch described in section VI.A (pp. 13-14) of the Scyllac
  review already on file for the level-0 models (W. E. Quinn et al.,
  LA-UR-73-1053 (1973)): a straight theta pinch whose main compression
  coil is flanked by mirror coils of their own bank, main and mirror coils
  sharing one bore, with a discharge tube of smaller bore inside them. The
  reference fixtures are synthetic; one anchor fixture carries the printed
  dimensions (coil bore 11 cm, coil length five metres, mirror-coil length
  16 cm, tube bore 8.8 cm) and a test proves the model reproduces every one
  of them. Reproducing a printed dimension is an anchor, never a claim
  about that machine.
- **Kernel library pin**: the manifest block `kernel_library` is validated
  field by field (distribution, version, 40-hex source commit, 64-hex
  inventory digest, sorted unique kernel identifiers, no other field); a
  contract test proves the manifest, the `pyproject.toml` dependency, the
  installed library version and the CI install steps name one commit.
- **Device model** (`DeviceModel3D`, `scpn.theta-pinch-3d-model.v1`
  `1.0.0`): seven bodies in the fixed order with declared roles and
  materials; the mirror coils abut the main coil with no gap and no
  overlap and share its bore; the tube overhangs both mirror coils by the
  declared extension and each flange caps one tube end; the plasma column
  lies inside the tube bore over the main coil; convergence of every body
  volume to its analytic cylinder or tube; refusal of a tube wider than
  the coil bore, of a column not inside the tube bore, and of a
  non-positive column radius (the library's segment refusal is re-raised
  under `DeviceGeometryError`); the fixed body inventory; determinism (two
  builds equal, digests equal); canonical bytes and one pinned reference
  digest (segments = 8) as an immutability fixture.
- **Exports**: the device-side provenance record (`glb_extras`: schema,
  both source digests, model digest, plasma radius, segment count, units,
  non-claims) is exactly what the library's GLB carries as document
  `extras`; the bytes are proven identical to the library serialisers
  called directly; the binary STL and glTF 2.0 binary layouts are read
  back with minimal specification-level readers; determinism of the bytes;
  the file writers.
- **Native parity**: `tests/test_geometry_native_parity.py` builds the
  seven device bodies on the library's Python floor and compares float64
  bit patterns of every vertex coordinate, the face index streams, the
  signed volume and the surface area against the library's native module
  (`scpn_reactor_kernels_native`); the consumer inherits the library's
  parity rather than re-proving the kernels. The crate in `rust/` carries
  physics only and is unchanged by this capability.
- **Benchmark**: `benchmarks/device_model_3d.py` per the ecosystem
  benchmark standard, measuring the library's Python floor (through the
  validated device build) against the library's native kernels; results in
  `docs/benchmarks.md` and the committed local artefact
  `benchmarks/results/device_model_3d.local.json`.

Bounded claims — what is NOT claimed:

- The bodies are analytic surfaces of a synthetic design: no B-rep solid,
  no equilibrium boundary, no engineering model. The plasma body is the
  declared column radius of the sharp-boundary models extruded over the
  main coil, not a computed plasma boundary.
- The end flanges are plain closing discs of the tube outer diameter; the
  feed-through hardware of a real assembly is not modelled, and neither
  are coil slots, feed plates, ports, diagnostics or supports.
- No material property, load, field, thermal or neutronic quantity is
  carried; the material tokens are declarations only.
- The tessellation is exact only as an inscribed polygonal prism: every
  volume and area is below the analytic value by the declared deficit, and
  that deficit is measured, not assumed.
- No value describes, approximates or validates any real machine; the
  benchmark measures tessellation cost of two implementations of the same
  kernels, not physics.
- Maturity stays `computational_prototype`.
