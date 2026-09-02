<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Theta Pinch Core — ADR 0005
-->

# ADR 0005 — Level-0 device physics: the Scyllac sharp-boundary relations with native parity

Status: accepted (2026-09-02). Adds the third implemented capability,
`level0_device_physics`, at `computational_prototype`.

## Context

Until this record the repository carried no physics beyond the magnetic
pressure and the beta invariant of the configuration model. Every device
manifest excludes `solver_mathematics_and_validation_evidence` (owner
SCPN-FUSION-CORE), and no FUSION seam covers the theta-pinch family. The
device owner therefore needs its own bounded, exercised, published physics:
closed-form relations from the device's own literature, evaluated on the
validated configuration, without solving any equation. One open-access
source carries a complete, internally consistent set of such relations
with printed reference numbers: the 1973 review of the Scyllac theta-pinch
experiments (W. E. Quinn et al., LA-UR-73-1053, OSTI 4460392).

## Decision

1. A new owned domain `analytic_device_physics_models` is declared in
   `reactor-domain.json`: device-owned closed-form and 0-D models from the
   device literature. It is disjoint from solver mathematics: no solver
   code is copied, no equilibrium, stability, compression or transport
   equation is solved, and no FUSION seam is implied or consumed.
2. Four models, each with its published form cited in the module
   docstring, live one per module under `src/scpn_theta_pinch_core/physics/`:
   the sharp-boundary state (beta, equal-species ion temperature, Alfvén
   speed and end-to-centre propagation time; Quinn 1973 p. 14), the
   `l = 1, 0` Scyllac toroidal equilibrium (p. 2, eqs. 3 and 7; only
   dimensionless quantities and the force ratio are reported so the
   source's unit system never enters), the `m = 1` growth estimate with
   the wall-stabilisation condition (eqs. 4, 6 and the condition derived
   from eq. 6), and the empirical end-loss scaling `tau ∝ L / T_i^(1/2)`
   normalised to the linear Scyllac point (p. 16, Table I). A composed
   `Level0PhysicsRecord` serialises canonically with a SHA-256 digest and
   carries fixed non-claims.
3. Two typographical ambiguities of the scanned source are resolved by
   the source's own numbers and recorded in the evidence record: the
   excursion definitions are implemented as quotients because only that
   form reproduces Fig. 2 (required field-ratio product −0.0059 against
   the measured −0.0064), and the wall condition is implemented as
   derived from eq. (6) because only that form reproduces the worked
   example `a/b = 0.4`.
4. Inputs the configuration does not carry (ion mass and density, plasma
   radius, major radius, helical wavenumber, the two field ratios, the
   end-loss normalisation point) are declared explicitly in
   `ModelInputs`; nothing is defaulted silently.
5. Native kernels (`rust/`, crate `scpn-theta-pinch-rs`, optional
   distribution `scpn-theta-pinch-native` via maturin) mirror every
   evaluation with identical operation order using only `+ - * /` and
   `sqrt` (the fourth root as `sqrt(sqrt(x))`); parity tests compare
   float64 bit patterns, never tolerances. The pure-Python floor remains
   the public API and the default.
6. Performance numbers follow the ecosystem benchmark standard; the local
   artefact is committed and labelled non-isolated.

## Consequences

Evidence maturity stays `computational_prototype`; the claims inventory
stays empty. VALIDATION states per model what is exercised and what is
not claimed; the anchors reproduce numbers printed in the source, which is
not a correlation with data. Adiabatic-compression and implosion models
are out of scope until a source is on file. The family's 3D model waits
for the shared kernel library pin so that no third copy of the geometry
substrate is created. The manifest change alters `manifest_sha256` inside
the plan envelope, so the envelope fixture is regenerated from the public
surface and re-pinned; the plan bytes and `plan_sha256` are unchanged.
