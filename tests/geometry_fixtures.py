# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Theta-Pinch Core — shared synthetic fixtures of the geometry tests

"""Synthetic configuration and geometry shared by the geometry tests.

Every value is a test fixture; none describes a real machine.
"""

from __future__ import annotations

import struct

from scpn_theta_pinch_core.configuration import DeviceConfiguration, RegistryBinding
from scpn_theta_pinch_core.geometry import DeviceGeometry
from scpn_theta_pinch_core.parameters import MU0, CompressionCoil, PlasmaState

REGISTRY_DIGEST = "786d9542ce76c56dd7748fa948b17efed6c073525e527ce90e6d5e29a2d00090"
REFERENCE_PLASMA_RADIUS_M = 0.007


def reference_configuration() -> DeviceConfiguration:
    """Return the synthetic linear theta-pinch configuration of these tests."""
    magnetic = 3.6 * 3.6 / (2.0 * MU0)
    return DeviceConfiguration(
        identifier="theta_pinch",
        coil=CompressionCoil(coil_field_t=3.6, coil_radius_m=0.08, coil_length_m=5.0),
        plasma=PlasmaState(plasma_pressure_pa=0.85 * magnetic),
        registry=RegistryBinding(version="1.0.0", digest_sha256=REGISTRY_DIGEST),
    )


def reference_geometry() -> DeviceGeometry:
    """Return the synthetic linear theta-pinch geometry of these tests."""
    return DeviceGeometry(
        discharge_tube_inner_radius_m=0.07,
        discharge_tube_wall_thickness_m=0.008,
        tube_extension_length_m=0.15,
        coil_wall_thickness_m=0.02,
        mirror_coil_length_m=0.2,
        mirror_coil_wall_thickness_m=0.015,
        end_flange_thickness_m=0.02,
    )


def bits(value: float) -> bytes:
    """Return the IEEE-754 double bit pattern of a value."""
    return struct.pack("<d", value)


def stream_bits(values: list[float]) -> bytes:
    """Return the concatenated bit patterns of a float stream."""
    return b"".join(bits(value) for value in values)
