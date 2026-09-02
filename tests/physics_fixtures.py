# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Theta-Pinch Core — shared synthetic fixtures of the physics tests

"""Synthetic configurations and inputs shared by the level-0 physics tests.

Every value is a test fixture; none describes a real machine. The
"Scyllac-like" operating point reproduces the order of magnitude of the
1973 review's stated parameters (B ~ 3.6 T, n ~ 2.5e22 m^-3, beta 0.85)
only so that the source's printed numbers can serve as anchors.
"""

from __future__ import annotations

import struct

from scpn_theta_pinch_core.configuration import DeviceConfiguration, RegistryBinding
from scpn_theta_pinch_core.parameters import MU0, CompressionCoil, PlasmaState
from scpn_theta_pinch_core.physics import (
    DEUTERON_MASS_KG,
    SCYLLAC_LINEAR_REFERENCE,
    ModelInputs,
)

REGISTRY_DIGEST = "786d9542ce76c56dd7748fa948b17efed6c073525e527ce90e6d5e29a2d00090"


def configuration(
    field_t: float = 3.6,
    beta: float = 0.85,
    coil_radius_m: float = 0.08,
    coil_length_m: float = 5.0,
) -> DeviceConfiguration:
    """Return a synthetic configuration at the requested beta."""
    magnetic = field_t * field_t / (2.0 * MU0)
    return DeviceConfiguration(
        identifier="theta_pinch",
        coil=CompressionCoil(
            coil_field_t=field_t,
            coil_radius_m=coil_radius_m,
            coil_length_m=coil_length_m,
        ),
        plasma=PlasmaState(plasma_pressure_pa=beta * magnetic),
        registry=RegistryBinding(version="1.0.0", digest_sha256=REGISTRY_DIGEST),
    )


def inputs(
    ion_density_per_m3: float = 2.5e22,
    plasma_radius_m: float = 0.007,
    major_radius_m: float = 2.375,
    helical_wavenumber_per_m: float = 19.0,
    l1_field_ratio: float = 0.08,
    l0_field_ratio: float = 0.08,
) -> ModelInputs:
    """Return synthetic model inputs (Scyllac 5-m sector orders of magnitude)."""
    return ModelInputs(
        ion_mass_kg=DEUTERON_MASS_KG,
        ion_density_per_m3=ion_density_per_m3,
        plasma_radius_m=plasma_radius_m,
        major_radius_m=major_radius_m,
        helical_wavenumber_per_m=helical_wavenumber_per_m,
        l1_field_ratio=l1_field_ratio,
        l0_field_ratio=l0_field_ratio,
        end_loss_reference=SCYLLAC_LINEAR_REFERENCE,
    )


def bits(value: float) -> bytes:
    """Return the IEEE-754 double bit pattern of a value."""
    return struct.pack("<d", value)
