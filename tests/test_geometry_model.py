# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Theta-Pinch Core — device 3D model tests

"""Body inventory, placement, invariants, record identity and the pinned digest."""

from __future__ import annotations

import dataclasses
import hashlib
import json
import math

import pytest

from geometry_fixtures import (
    REFERENCE_PLASMA_RADIUS_M,
    reference_configuration,
    reference_geometry,
)
from scpn_theta_pinch_core.errors import DeviceGeometryError
from scpn_theta_pinch_core.geometry import (
    BODY_NAMES,
    MODEL_NON_CLAIMS,
    MODEL_SCHEMA,
    MODEL_SCHEMA_VERSION,
    MODEL_UNITS,
    DeviceGeometry,
    DeviceModel3D,
    build_device_model,
)
from scpn_theta_pinch_core.parameters import CompressionCoil

REFERENCE_MODEL_SHA256 = (
    "a4edd9e59ef8de93855e7ab445f9f25318a2099854bf7e1dad5cda2c4602d603"
)


def reference_model(segments: int = 16) -> DeviceModel3D:
    """Build the reference model of these tests at a segment count."""
    return build_device_model(
        reference_configuration(),
        reference_geometry(),
        REFERENCE_PLASMA_RADIUS_M,
        segments,
    )


def test_bodies_roles_and_materials() -> None:
    """Seven bodies in the fixed order with the declared roles and materials."""
    model = reference_model()
    assert tuple(mesh.name for mesh in model.meshes) == BODY_NAMES
    assert [mesh.role for mesh in model.meshes] == [
        "vacuum_boundary",
        "coil",
        "coil",
        "coil",
        "vacuum_boundary",
        "vacuum_boundary",
        "plasma",
    ]
    assert [mesh.material_identifier for mesh in model.meshes] == [
        "discharge_tube_insulator",
        "coil_conductor",
        "coil_conductor",
        "coil_conductor",
        "flange_wall",
        "flange_wall",
        "plasma",
    ]
    for mesh in model.meshes:
        assert mesh.signed_volume_m3() > 0.0


def test_mirror_coils_abut_the_main_coil_and_share_its_bore() -> None:
    """The mirror coils touch the main coil ends with no gap and no overlap."""
    geometry = reference_geometry()
    coil = reference_configuration().coil
    _, main, upstream, downstream, _, _, _ = reference_model().meshes
    assert main.bounding_box()[0][2] == 0.0
    assert main.bounding_box()[1][2] == coil.coil_length_m
    assert upstream.bounding_box()[1][2] == main.bounding_box()[0][2]
    assert downstream.bounding_box()[0][2] == main.bounding_box()[1][2]
    assert upstream.bounding_box()[0][2] == -geometry.mirror_coil_length_m
    assert (
        downstream.bounding_box()[1][2]
        == coil.coil_length_m + geometry.mirror_coil_length_m
    )
    for coil_mesh, thickness in (
        (main, geometry.coil_wall_thickness_m),
        (upstream, geometry.mirror_coil_wall_thickness_m),
        (downstream, geometry.mirror_coil_wall_thickness_m),
    ):
        assert coil_mesh.bounding_box()[1][0] == coil.coil_radius_m + thickness


def test_tube_spans_every_coil_and_the_flanges_close_it() -> None:
    """The tube overhangs both mirror coils and each flange caps one end."""
    geometry = reference_geometry()
    tube, _, upstream_coil, downstream_coil, upstream, downstream, _ = (
        reference_model().meshes
    )
    tube_low = tube.bounding_box()[0][2]
    tube_high = tube.bounding_box()[1][2]
    assert tube_low == pytest.approx(
        upstream_coil.bounding_box()[0][2] - geometry.tube_extension_length_m
    )
    assert tube_high == pytest.approx(
        downstream_coil.bounding_box()[1][2] + geometry.tube_extension_length_m
    )
    assert upstream.bounding_box()[1][2] == tube_low
    assert downstream.bounding_box()[0][2] == tube_high
    assert upstream.bounding_box()[0][2] == pytest.approx(
        tube_low - geometry.end_flange_thickness_m
    )
    assert downstream.bounding_box()[1][2] == pytest.approx(
        tube_high + geometry.end_flange_thickness_m
    )
    assert upstream.bounding_box()[1][0] == geometry.discharge_tube_outer_radius_m
    assert downstream.bounding_box()[1][0] == geometry.discharge_tube_outer_radius_m


def test_plasma_column_lies_inside_the_tube_over_the_main_coil() -> None:
    """The plasma body is the declared column inside the tube bore."""
    geometry = reference_geometry()
    coil = reference_configuration().coil
    plasma = reference_model().meshes[-1]
    low, high = plasma.bounding_box()
    assert low[2] == 0.0
    assert high[2] == coil.coil_length_m
    assert high[0] == REFERENCE_PLASMA_RADIUS_M
    assert high[0] < geometry.discharge_tube_inner_radius_m


def test_volumes_follow_the_analytic_bodies() -> None:
    """Each body volume converges on the analytic cylinder or tube volume."""
    model = reference_model(1024)
    tube_span = 5.0 + 2.0 * (0.2 + 0.15)
    analytic = [
        math.pi * (0.078**2 - 0.07**2) * tube_span,
        math.pi * (0.1**2 - 0.08**2) * 5.0,
        math.pi * (0.095**2 - 0.08**2) * 0.2,
        math.pi * (0.095**2 - 0.08**2) * 0.2,
        math.pi * 0.078**2 * 0.02,
        math.pi * 0.078**2 * 0.02,
        math.pi * REFERENCE_PLASMA_RADIUS_M**2 * 5.0,
    ]
    for mesh, exact in zip(model.meshes, analytic, strict=True):
        assert 0.0 < (exact - mesh.signed_volume_m3()) / exact < 1.0e-5


def test_record_identity_and_pinned_digest() -> None:
    """The canonical record is sorted JSON and the reference digest is pinned."""
    configuration = reference_configuration()
    geometry = reference_geometry()
    model = build_device_model(configuration, geometry, REFERENCE_PLASMA_RADIUS_M, 8)
    record = model.to_record()
    assert record["schema"] == MODEL_SCHEMA
    assert record["schema_version"] == MODEL_SCHEMA_VERSION
    assert record["units"] == MODEL_UNITS
    assert record["non_claims"] == list(MODEL_NON_CLAIMS)
    assert record["configuration_digest_sha256"] == configuration.digest_sha256()
    assert record["geometry_digest_sha256"] == geometry.digest_sha256()
    assert record["plasma_radius_m"] == REFERENCE_PLASMA_RADIUS_M
    assert record["segments"] == 8
    assert [body["name"] for body in record["bodies"]] == list(BODY_NAMES)
    data = model.canonical_bytes()
    assert json.loads(data) == record
    assert model.digest_sha256() == hashlib.sha256(data).hexdigest()
    assert model.digest_sha256() == REFERENCE_MODEL_SHA256


def test_model_is_deterministic() -> None:
    """Two builds of the same inputs are equal and share every digest."""
    first = reference_model(32)
    second = reference_model(32)
    assert first == second
    assert first.digest_sha256() == second.digest_sha256()
    assert [m.digest_sha256() for m in first.meshes] == [
        m.digest_sha256() for m in second.meshes
    ]


def test_tube_must_fit_the_coil_bore() -> None:
    """A tube wider than the shared coil bore is refused."""
    geometry = dataclasses.replace(
        reference_geometry(), discharge_tube_wall_thickness_m=0.02
    )
    with pytest.raises(DeviceGeometryError, match="discharge_tube_outer_radius_m"):
        build_device_model(
            reference_configuration(), geometry, REFERENCE_PLASMA_RADIUS_M, 8
        )
    tube = reference_geometry()
    assert isinstance(tube, DeviceGeometry)
    flush = dataclasses.replace(
        reference_configuration(),
        coil=CompressionCoil(
            coil_field_t=3.6,
            coil_radius_m=tube.discharge_tube_outer_radius_m,
            coil_length_m=5.0,
        ),
    )
    built = build_device_model(flush, tube, REFERENCE_PLASMA_RADIUS_M, 8)
    assert built.meshes[0].bounding_box()[1][0] == tube.discharge_tube_outer_radius_m


def test_plasma_column_must_fit_the_tube_bore() -> None:
    """A column as wide as the tube bore is refused."""
    with pytest.raises(DeviceGeometryError, match="plasma_radius_m"):
        build_device_model(reference_configuration(), reference_geometry(), 0.07, 8)


@pytest.mark.parametrize("radius", [0.0, -0.001, math.nan, math.inf])
def test_plasma_radius_must_be_finite_and_positive(radius: float) -> None:
    """A non-finite or non-positive column radius fails closed."""
    with pytest.raises(DeviceGeometryError, match="plasma_radius_m"):
        build_device_model(reference_configuration(), reference_geometry(), radius, 8)


def test_invalid_segments_are_refused_before_tessellation() -> None:
    """The segment rule is checked first."""
    with pytest.raises(DeviceGeometryError, match="multiple"):
        build_device_model(
            reference_configuration(),
            reference_geometry(),
            REFERENCE_PLASMA_RADIUS_M,
            20,
        )


def test_a_wider_coil_bore_admits_the_same_tube() -> None:
    """The bore comes from the configuration, not from the geometry record."""
    configuration = dataclasses.replace(
        reference_configuration(),
        coil=CompressionCoil(coil_field_t=3.6, coil_radius_m=0.2, coil_length_m=5.0),
    )
    geometry = reference_geometry()
    model = build_device_model(configuration, geometry, REFERENCE_PLASMA_RADIUS_M, 8)
    assert model.meshes[1].bounding_box()[1][0] == 0.2 + geometry.coil_wall_thickness_m
    assert model.meshes[0] == reference_model(8).meshes[0]


def test_body_inventory_is_enforced() -> None:
    """A model with the wrong bodies or order is refused."""
    model = reference_model(8)
    with pytest.raises(DeviceGeometryError, match="bodies must be exactly"):
        DeviceModel3D(
            configuration_digest_sha256=model.configuration_digest_sha256,
            geometry_digest_sha256=model.geometry_digest_sha256,
            plasma_radius_m=model.plasma_radius_m,
            segments=8,
            meshes=model.meshes[::-1],
        )
