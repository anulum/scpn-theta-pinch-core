# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Theta-Pinch Core — shared synthetic fixtures of the geometry tests

"""Configurations and geometries shared by the geometry tests.

Two fixtures, and the difference between them is the point.

The *reference* pair is synthetic: round numbers chosen to exercise the
model, describing no machine.

The *anchor* pair carries the dimensions printed in section VI.A of the
Scyllac review already on file (W. E. Quinn et al., LA-UR-73-1053 (1973),
pp. 13-14) for the five-metre linear theta pinch: a main compression coil
five metres long flanked by mirror coils 16 cm long, main and mirror
coils sharing an inside diameter of 11 cm, with a quartz discharge tube
of 8.8 cm inside diameter inside them. It exists so the geometry tier can
be checked against a published arrangement the way the level-0 models are
checked against published numbers. The fields the source does not print —
the tube wall thickness, the coil wall thicknesses, the tube overhang and
the flange thickness — are declared here and marked as declared;
reproducing a printed dimension is an anchor, never a claim about the
machine.
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


#: Values printed in the Scyllac review for the five-metre linear theta pinch.
ANCHOR_COIL_RADIUS_M = 0.055
ANCHOR_COIL_LENGTH_M = 5.0
ANCHOR_TUBE_INNER_RADIUS_M = 0.044
ANCHOR_MIRROR_COIL_LENGTH_M = 0.16


def anchor_configuration() -> DeviceConfiguration:
    """Return the configuration of the printed five-metre linear theta pinch.

    The coil bore and length are the printed values; the compression field
    and the plasma pressure are declared, and do not enter the geometry.
    """
    magnetic = 3.6 * 3.6 / (2.0 * MU0)
    return DeviceConfiguration(
        identifier="theta_pinch",
        coil=CompressionCoil(
            coil_field_t=3.6,
            coil_radius_m=ANCHOR_COIL_RADIUS_M,
            coil_length_m=ANCHOR_COIL_LENGTH_M,
        ),
        plasma=PlasmaState(plasma_pressure_pa=0.85 * magnetic),
        registry=RegistryBinding(version="1.0.0", digest_sha256=REGISTRY_DIGEST),
    )


def anchor_geometry() -> DeviceGeometry:
    """Return the geometry of the printed five-metre linear theta pinch.

    The discharge-tube bore and the mirror-coil length are the printed
    values; the wall thicknesses, the tube overhang and the flange
    thickness are declared because the source does not print them.
    """
    return DeviceGeometry(
        discharge_tube_inner_radius_m=ANCHOR_TUBE_INNER_RADIUS_M,
        discharge_tube_wall_thickness_m=0.005,
        tube_extension_length_m=0.2,
        coil_wall_thickness_m=0.02,
        mirror_coil_length_m=ANCHOR_MIRROR_COIL_LENGTH_M,
        mirror_coil_wall_thickness_m=0.015,
        end_flange_thickness_m=0.02,
    )


def bits(value: float) -> bytes:
    """Return the IEEE-754 double bit pattern of a value."""
    return struct.pack("<d", value)


def stream_bits(values: list[float]) -> bytes:
    """Return the concatenated bit patterns of a float stream."""
    return b"".join(bits(value) for value in values)
