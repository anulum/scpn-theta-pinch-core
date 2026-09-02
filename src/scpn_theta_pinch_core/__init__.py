# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Theta-Pinch Core — device capability package

"""Device capability models of the SCPN theta-pinch device family.

Public surface of the ``device_configuration_model``,
``diagnostic_clock_semantics`` and ``level0_device_physics`` capabilities at
``computational_prototype`` maturity: validated parameter objects,
synthetic diagnostic and clock declarations aligned with the pinned SPO
observability catalogue, documented consistency estimates, the
sharp-boundary level-0 relations of the Scyllac review evaluated on the
validated configuration, canonical serialisation with SHA-256 digests, and
data-only pins to the SPO registries. No claim about any real machine or
diagnostic is made anywhere in this package.
"""

from __future__ import annotations

from typing import Final

from scpn_theta_pinch_core.configuration import (
    HIGH_BETA_ADVISORY_FLOOR,
    OWNED_CONFIGURATIONS,
    ConsistencyFinding,
    DeviceConfiguration,
    RegistryBinding,
    configuration_from_bytes,
    configuration_from_record,
)
from scpn_theta_pinch_core.errors import DeviceConfigurationError, DiagnosticPlanError
from scpn_theta_pinch_core.observability import (
    APPLICABLE_CANDIDATES,
    CATALOGUE_BINDING,
    CandidateProfile,
    ClockKind,
    ClockModel,
    ClockRelation,
    DeferredCandidate,
    DiagnosticChannelPlan,
    DiagnosticPlan,
    FrameKind,
    ObservabilityBinding,
    ObservabilityClass,
    ReferenceFrame,
    SemanticCarrier,
    plan_from_bytes,
    plan_from_record,
)
from scpn_theta_pinch_core.parameters import (
    MU0,
    CompressionCoil,
    PlasmaState,
)
from scpn_theta_pinch_core.physics import (
    DEUTERON_MASS_KG,
    ELEMENTARY_CHARGE_C,
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    PROTON_MASS_KG,
    SCYLLAC_LINEAR_REFERENCE,
    EndLossEstimate,
    EndLossReference,
    Level0PhysicsRecord,
    M1GrowthEstimate,
    ModelInputs,
    SharpBoundaryState,
    ToroidalEquilibrium,
    WallStabilisation,
    end_loss_estimate,
    level0_physics,
    m1_growth_estimate,
    sharp_boundary_state,
    toroidal_equilibrium,
    wall_stabilisation,
)
from scpn_theta_pinch_core.plan_envelope import (
    PlanEnvelope,
    envelope_for_plan,
    envelope_from_bytes,
    envelope_from_record,
    verify_envelope,
)

__version__: Final = "0.1.0.dev0"

__all__ = [
    "APPLICABLE_CANDIDATES",
    "CATALOGUE_BINDING",
    "DEUTERON_MASS_KG",
    "ELEMENTARY_CHARGE_C",
    "HIGH_BETA_ADVISORY_FLOOR",
    "LEVEL0_NON_CLAIMS",
    "LEVEL0_SCHEMA",
    "LEVEL0_SCHEMA_VERSION",
    "MU0",
    "OWNED_CONFIGURATIONS",
    "PROTON_MASS_KG",
    "SCYLLAC_LINEAR_REFERENCE",
    "CandidateProfile",
    "ClockKind",
    "ClockModel",
    "ClockRelation",
    "CompressionCoil",
    "ConsistencyFinding",
    "DeferredCandidate",
    "DeviceConfiguration",
    "DeviceConfigurationError",
    "DiagnosticChannelPlan",
    "DiagnosticPlan",
    "DiagnosticPlanError",
    "EndLossEstimate",
    "EndLossReference",
    "FrameKind",
    "Level0PhysicsRecord",
    "M1GrowthEstimate",
    "ModelInputs",
    "ObservabilityBinding",
    "ObservabilityClass",
    "PlanEnvelope",
    "PlasmaState",
    "ReferenceFrame",
    "RegistryBinding",
    "SemanticCarrier",
    "SharpBoundaryState",
    "ToroidalEquilibrium",
    "WallStabilisation",
    "__version__",
    "configuration_from_bytes",
    "configuration_from_record",
    "end_loss_estimate",
    "envelope_for_plan",
    "envelope_from_bytes",
    "envelope_from_record",
    "level0_physics",
    "m1_growth_estimate",
    "plan_from_bytes",
    "plan_from_record",
    "sharp_boundary_state",
    "toroidal_equilibrium",
    "verify_envelope",
    "wall_stabilisation",
]
