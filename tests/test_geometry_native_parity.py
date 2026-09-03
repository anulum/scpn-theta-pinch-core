# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Theta-Pinch Core — device model parity against the library's native kernels

"""Bit-exact parity of the device model against the pinned library's native kernels.

The device model is composed on the Python floor of the shared kernel
library; this file proves that every body it builds agrees bit for bit
with the library's native tessellation and mesh measures, so the consumer
inherits the library's parity rather than re-proving the kernels. Skipped
hermetically when the library's optional native module is absent; when
present, every vertex coordinate, face index and measure is compared by
float64 bit pattern, never by tolerance. All inputs are synthetic.
"""

from __future__ import annotations

import pytest

from geometry_fixtures import (
    REFERENCE_PLASMA_RADIUS_M,
    bits,
    reference_configuration,
    reference_geometry,
    stream_bits,
)
from scpn_theta_pinch_core.geometry import build_device_model

native = pytest.importorskip("scpn_reactor_kernels_native")


def native_bodies(segments: int) -> list[tuple[list[float], list[int]]]:
    """Tessellate the seven device bodies through the library's native kernels."""
    geometry = reference_geometry()
    coil = reference_configuration().coil
    coil_radius = coil.coil_radius_m
    coil_length = coil.coil_length_m
    tube_outer = geometry.discharge_tube_outer_radius_m
    z_tube_low = 0.0 - geometry.mirror_coil_length_m - geometry.tube_extension_length_m
    z_tube_high = (
        coil_length + geometry.mirror_coil_length_m + geometry.tube_extension_length_m
    )
    streams = (
        native.tessellate_annular_tube(
            geometry.discharge_tube_inner_radius_m,
            tube_outer,
            z_tube_low,
            z_tube_high,
            segments,
        ),
        native.tessellate_annular_tube(
            coil_radius,
            coil_radius + geometry.coil_wall_thickness_m,
            0.0,
            coil_length,
            segments,
        ),
        native.tessellate_annular_tube(
            coil_radius,
            coil_radius + geometry.mirror_coil_wall_thickness_m,
            0.0 - geometry.mirror_coil_length_m,
            0.0,
            segments,
        ),
        native.tessellate_annular_tube(
            coil_radius,
            coil_radius + geometry.mirror_coil_wall_thickness_m,
            coil_length,
            coil_length + geometry.mirror_coil_length_m,
            segments,
        ),
        native.tessellate_cylinder(
            tube_outer,
            z_tube_low - geometry.end_flange_thickness_m,
            z_tube_low,
            segments,
        ),
        native.tessellate_cylinder(
            tube_outer,
            z_tube_high,
            z_tube_high + geometry.end_flange_thickness_m,
            segments,
        ),
        native.tessellate_cylinder(
            REFERENCE_PLASMA_RADIUS_M, 0.0, coil_length, segments
        ),
    )
    return [(list(vertices), list(faces)) for vertices, faces in streams]


@pytest.mark.parametrize("segments", [8, 32, 64])
def test_every_body_is_bit_exact_with_the_library_native_kernels(
    segments: int,
) -> None:
    """Vertices, faces, volume and area of all seven bodies agree bit for bit."""
    model = build_device_model(
        reference_configuration(),
        reference_geometry(),
        REFERENCE_PLASMA_RADIUS_M,
        segments,
    )
    bodies = native_bodies(segments)
    for mesh, (vertices, faces) in zip(model.meshes, bodies, strict=True):
        floor = [c for v in mesh.vertices for c in v]
        assert stream_bits(floor) == stream_bits(vertices)
        assert [i for f in mesh.faces for i in f] == faces
        volume = native.mesh_volume(vertices, faces)
        assert bits(volume) == bits(mesh.signed_volume_m3())
        assert bits(native.mesh_area(vertices, faces)) == bits(mesh.surface_area_m2())
