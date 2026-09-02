# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Theta-Pinch Core — level-0 device physics package

"""Level-0 device physics of the theta-pinch family.

The sharp-boundary relations of the Scyllac review (Quinn et al. 1973)
evaluated on the validated device configuration: the operating state
(beta, ion temperature, Alfvén speed, end propagation time), the
``l = 1, 0`` toroidal equilibrium, the ``m = 1`` growth-rate estimate with
its wall-stabilisation condition, and the empirical end-loss scaling.
Every function is a closed-form evaluation; no equation is solved and no
value describes a real machine. Design record: ADR 0005.
"""

from __future__ import annotations

from scpn_theta_pinch_core.physics.balance import (
    DEUTERON_MASS_KG,
    ELEMENTARY_CHARGE_C,
    PROTON_MASS_KG,
    SharpBoundaryState,
    require_sharp_boundary_beta,
    sharp_boundary_state,
)
from scpn_theta_pinch_core.physics.end_loss import (
    SCYLLAC_LINEAR_REFERENCE,
    EndLossEstimate,
    EndLossReference,
    end_loss_estimate,
)
from scpn_theta_pinch_core.physics.level0 import (
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    Level0PhysicsRecord,
    ModelInputs,
    level0_physics,
)
from scpn_theta_pinch_core.physics.stability import (
    M1GrowthEstimate,
    WallStabilisation,
    m1_growth_estimate,
    wall_stabilisation,
)
from scpn_theta_pinch_core.physics.toroidal_equilibrium import (
    ToroidalEquilibrium,
    toroidal_equilibrium,
)

__all__ = [
    "DEUTERON_MASS_KG",
    "ELEMENTARY_CHARGE_C",
    "LEVEL0_NON_CLAIMS",
    "LEVEL0_SCHEMA",
    "LEVEL0_SCHEMA_VERSION",
    "PROTON_MASS_KG",
    "SCYLLAC_LINEAR_REFERENCE",
    "EndLossEstimate",
    "EndLossReference",
    "Level0PhysicsRecord",
    "M1GrowthEstimate",
    "ModelInputs",
    "SharpBoundaryState",
    "ToroidalEquilibrium",
    "WallStabilisation",
    "end_loss_estimate",
    "level0_physics",
    "m1_growth_estimate",
    "require_sharp_boundary_beta",
    "sharp_boundary_state",
    "toroidal_equilibrium",
    "wall_stabilisation",
]
