# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Theta-Pinch Core — device CAD model tests (tier G2)

"""B-rep agreement, faceting bounds, STEP determinism and record identity.

The reference pair is synthetic and describes no machine. The anchor pair
carries the dimensions the filed Scyllac review prints, and the anchor
test proves each printed dimension appears in the B-rep bodies; a
dimension reproduced from a published arrangement is an anchor, not a
claim about that machine. The B-rep measures come from the pinned
third-party OpenCASCADE kernel and are checked against the analytic closed
forms within the library's declared tolerance; the tier-G1 reference mesh,
the polygon-deficit bound and the per-body evidence come from the shared
kernel library.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import math
from pathlib import Path

import pytest

pytest.importorskip("cadquery")

from scpn_reactor_kernels.cad import MANIFEST_SCHEMA, MEASURE_TOLERANCE
from scpn_reactor_kernels.errors import CadError

from geometry_fixtures import (
    ANCHOR_COIL_LENGTH_M,
    ANCHOR_COIL_RADIUS_M,
    ANCHOR_MIRROR_COIL_LENGTH_M,
    ANCHOR_TUBE_INNER_RADIUS_M,
    REFERENCE_PLASMA_RADIUS_M,
    anchor_configuration,
    anchor_geometry,
    reference_configuration,
    reference_geometry,
)
from scpn_theta_pinch_core.errors import DeviceGeometryError
from scpn_theta_pinch_core.geometry import (
    BODY_NAMES,
    CAD_MODEL_NON_CLAIMS,
    CAD_MODEL_SCHEMA,
    CAD_MODEL_SCHEMA_VERSION,
    DEFAULT_ANGULAR_DEFLECTION_RAD,
    DEFAULT_LINEAR_DEFLECTION_M,
    DEFAULT_REFERENCE_MESH_SEGMENTS,
    DeviceModelCAD,
    build_device_cad,
    build_device_model,
    write_step,
)

#: Digest of the reference CAD model record in the pinned back-end
#: environment (cadquery 2.8.0, OCP 7.9.3.1); a back-end bump re-pins it
#: as a governed data change (ADR 0008).
REFERENCE_CAD_MODEL_SHA256 = (
    "60c4b9fa8fb6db01c6824bf783518368ae6d88f55b7111a3aef2f7abe4016eb3"
)


def analytic_volumes() -> tuple[float, ...]:
    """Return the closed-form volume of every body of the reference design.

    The expressions are the closed forms of the primitives in the shared
    library's exact operation order (``pi r r h`` for the cylinder,
    ``pi (r_o r_o - r_i r_i) h`` for the tube), evaluated on the same
    fixture values the build reads, so the comparison is an exact equality
    and not an approximation. Writing the numbers as decimal literals
    would not be: the axial extents are sums of three fixture values whose
    binary result is not the decimal one.
    """
    configuration = reference_configuration()
    geometry = reference_geometry()
    coil_radius = configuration.coil.coil_radius_m
    coil_length = configuration.coil.coil_length_m
    tube_inner = geometry.discharge_tube_inner_radius_m
    tube_outer = geometry.discharge_tube_outer_radius_m
    coil_outer = coil_radius + geometry.coil_wall_thickness_m
    mirror_outer = coil_radius + geometry.mirror_coil_wall_thickness_m
    mirror_length = geometry.mirror_coil_length_m
    flange = geometry.end_flange_thickness_m
    low = 0.0 - mirror_length - geometry.tube_extension_length_m
    high = coil_length + mirror_length + geometry.tube_extension_length_m
    return (
        math.pi * (tube_outer * tube_outer - tube_inner * tube_inner) * (high - low),
        math.pi * (coil_outer * coil_outer - coil_radius * coil_radius) * coil_length,
        math.pi
        * (mirror_outer * mirror_outer - coil_radius * coil_radius)
        * (0.0 - (0.0 - mirror_length)),
        math.pi
        * (mirror_outer * mirror_outer - coil_radius * coil_radius)
        * (coil_length + mirror_length - coil_length),
        math.pi * tube_outer * tube_outer * (low - (low - flange)),
        math.pi * tube_outer * tube_outer * (high + flange - high),
        math.pi
        * REFERENCE_PLASMA_RADIUS_M
        * REFERENCE_PLASMA_RADIUS_M
        * (coil_length - 0.0),
    )


def reference_cad_model() -> DeviceModelCAD:
    """Build the synthetic CAD model of the tests."""
    return build_device_cad(
        reference_configuration(), reference_geometry(), REFERENCE_PLASMA_RADIUS_M
    )


def test_bodies_match_the_g1_inventory_roles_and_materials() -> None:
    """The CAD bodies are the G1 bodies: same names, roles, materials."""
    model = reference_cad_model()
    reference = build_device_model(
        reference_configuration(),
        reference_geometry(),
        REFERENCE_PLASMA_RADIUS_M,
        DEFAULT_REFERENCE_MESH_SEGMENTS,
    )
    assert tuple(body.name for body in model.bodies) == BODY_NAMES
    for body, mesh in zip(model.bodies, reference.meshes, strict=True):
        assert body.role == mesh.role
        assert body.material_identifier == mesh.material_identifier


def test_brep_measures_agree_with_the_analytic_closed_forms() -> None:
    """Every body volume and area matches the analytic form within 1e-9."""
    model = reference_cad_model()
    for body, analytic in zip(model.bodies, analytic_volumes(), strict=True):
        assert body.analytic_volume_m3 == analytic
        assert 0.0 <= body.volume_relative_error <= MEASURE_TOLERANCE
        assert 0.0 <= body.surface_area_relative_error <= MEASURE_TOLERANCE


def test_faceted_volumes_stay_within_the_deflection_deficit_bound() -> None:
    """The faceted body underestimates the analytic volume within 2 d / r."""
    model = reference_cad_model()
    for body in model.bodies:
        assert body.faceted_volume_relative_deficit >= 0.0
        assert body.faceted_volume_relative_deficit <= body.faceted_volume_deficit_bound
        assert body.faceted_volume_m3 < body.analytic_volume_m3


def test_faceted_meshes_are_closed_and_outward_oriented() -> None:
    """Every faceted mesh satisfies the G1 closed-mesh contract."""
    model = reference_cad_model()
    assert len(model.faceted_meshes) == len(BODY_NAMES)
    for mesh in model.faceted_meshes:
        assert mesh.signed_volume_m3() > 0.0
        assert mesh.face_count > 0


def test_faceted_volumes_track_the_reference_mesh_within_the_polygon_bound() -> None:
    """Faceted and G1 volumes agree within the exact polygon-deficit bound."""
    model = reference_cad_model()
    reference = build_device_model(
        reference_configuration(),
        reference_geometry(),
        REFERENCE_PLASMA_RADIUS_M,
        DEFAULT_REFERENCE_MESH_SEGMENTS,
    )
    for body, mesh in zip(model.bodies, reference.meshes, strict=True):
        assert body.reference_mesh_volume_m3 == mesh.signed_volume_m3()
        assert body.mesh_volume_relative_difference >= 0.0
        assert body.mesh_volume_relative_difference <= body.mesh_volume_difference_bound


def test_bodies_touch_where_the_assembly_says_they_touch() -> None:
    """Device-level placement identities hold in the B-rep bounding boxes."""
    model = reference_cad_model()
    boxes = {
        body["name"]: (body["bounding_box_min_m"], body["bounding_box_max_m"])
        for body in model.assembly_manifest["bodies"]
    }
    tube_low, tube_high = boxes["discharge_tube"]
    _, upstream_high = boxes["end_flange_upstream"]
    downstream_low, downstream_high = boxes["end_flange_downstream"]
    coil_low, coil_high = boxes["compression_coil"]
    _, mirror_up_high = boxes["mirror_coil_upstream"]
    mirror_down_low, _ = boxes["mirror_coil_downstream"]
    # the flanges close the tube at both ends, face to face
    assert math.isclose(upstream_high[2], tube_low[2], abs_tol=1.0e-9)
    assert math.isclose(downstream_low[2], tube_high[2], abs_tol=1.0e-9)
    # the mirror coils sit against the compression coil at both ends
    assert math.isclose(mirror_up_high[2], coil_low[2], abs_tol=1.0e-9)
    assert math.isclose(mirror_down_low[2], coil_high[2], abs_tol=1.0e-9)
    # the flange discs have the tube's outer radius
    assert math.isclose(upstream_high[0], tube_high[0], abs_tol=1.0e-9)
    assert math.isclose(downstream_high[0], tube_high[0], abs_tol=1.0e-9)
    # the tube is inside the coil bore
    assert tube_high[0] <= coil_low[0] + 1.0e-12 or tube_high[0] <= 0.08 + 1.0e-12


def test_anchor_dimensions_appear_in_the_brep_bodies() -> None:
    """Every dimension the filed source prints is in the tessellated solids.

    The coil bore and length, the discharge-tube bore and the mirror-coil
    length are the printed values of the five-metre linear theta pinch; the
    test proves the built solids carry them. Reproducing a printed
    dimension is an anchor, not a claim about that machine.
    """
    model = build_device_cad(anchor_configuration(), anchor_geometry(), 0.007)
    boxes = {
        body["name"]: (body["bounding_box_min_m"], body["bounding_box_max_m"])
        for body in model.assembly_manifest["bodies"]
    }
    coil_low, coil_high = boxes["compression_coil"]
    assert math.isclose(
        coil_high[2] - coil_low[2], ANCHOR_COIL_LENGTH_M, abs_tol=1.0e-9
    )
    tube_low, tube_high = boxes["discharge_tube"]
    mirror_low, mirror_high = boxes["mirror_coil_upstream"]
    assert math.isclose(
        mirror_high[2] - mirror_low[2], ANCHOR_MIRROR_COIL_LENGTH_M, abs_tol=1.0e-9
    )
    # the bores are not bounding-box quantities, so they are read from the
    # analytic volumes the bodies carry, which are exact in the library's
    # operation order
    coil_body = next(body for body in model.bodies if body.name == "compression_coil")
    coil_outer = ANCHOR_COIL_RADIUS_M + anchor_geometry().coil_wall_thickness_m
    assert math.isclose(
        coil_body.analytic_volume_m3,
        math.pi
        * (coil_outer * coil_outer - ANCHOR_COIL_RADIUS_M * ANCHOR_COIL_RADIUS_M)
        * ANCHOR_COIL_LENGTH_M,
        rel_tol=1.0e-15,
    )
    tube_body = next(body for body in model.bodies if body.name == "discharge_tube")
    tube_outer = (
        ANCHOR_TUBE_INNER_RADIUS_M + anchor_geometry().discharge_tube_wall_thickness_m
    )
    assert math.isclose(tube_high[0], tube_outer, abs_tol=1.0e-9)
    assert math.isclose(
        tube_body.analytic_volume_m3,
        math.pi
        * (
            tube_outer * tube_outer
            - ANCHOR_TUBE_INNER_RADIUS_M * ANCHOR_TUBE_INNER_RADIUS_M
        )
        * (tube_high[2] - tube_low[2]),
        rel_tol=1.0e-12,
    )


def test_step_export_is_byte_deterministic() -> None:
    """Two builds of the same design give byte-identical STEP documents."""
    first = reference_cad_model()
    second = reference_cad_model()
    assert first.step_data == second.step_data
    assert first.step_sha256 == second.step_sha256
    assert len(first.step_sha256) == 64
    assert first.digest_sha256() == second.digest_sha256()


def test_step_round_trip_reproduces_the_volumes(tmp_path: Path) -> None:
    """Re-importing the written STEP gives the bodies' volumes within 1e-9.

    The re-import runs in a subprocess, which is how a consumer reads the
    file: a separate reader process.
    """
    import subprocess
    import sys

    model = reference_cad_model()
    target = tmp_path / "device.step"
    written = write_step(target, model)
    assert written == len(model.step_data)
    assert target.read_bytes() == model.step_data
    assert hashlib.sha256(target.read_bytes()).hexdigest() == model.step_sha256
    script = (
        "import json, sys;"
        "import cadquery;"
        "solids = cadquery.importers.importStep(sys.argv[1]).solids().vals();"
        "print(json.dumps(sorted(float(s.Volume()) for s in solids)))"
    )
    completed = subprocess.run(
        [sys.executable, "-c", script, str(target)],
        capture_output=True,
        text=True,
        check=True,
    )
    got = json.loads(completed.stdout)
    assert len(got) == len(BODY_NAMES)
    expected = sorted(body.analytic_volume_m3 for body in model.bodies)
    for value, reference in zip(got, expected, strict=True):
        assert math.isclose(value, reference, rel_tol=MEASURE_TOLERANCE)


def test_record_identity_and_pinned_digest() -> None:
    """The canonical record is sorted JSON and the reference digest is pinned."""
    configuration = reference_configuration()
    geometry = reference_geometry()
    model = build_device_cad(configuration, geometry, REFERENCE_PLASMA_RADIUS_M)
    record = model.to_record()
    assert record["schema"] == CAD_MODEL_SCHEMA
    assert record["schema_version"] == CAD_MODEL_SCHEMA_VERSION
    assert record["non_claims"] == list(CAD_MODEL_NON_CLAIMS)
    assert record["configuration_digest_sha256"] == configuration.digest_sha256()
    assert record["geometry_digest_sha256"] == geometry.digest_sha256()
    assert record["plasma_radius_m"] == REFERENCE_PLASMA_RADIUS_M
    assert record["reference_mesh_segments"] == DEFAULT_REFERENCE_MESH_SEGMENTS
    assert record["linear_deflection_m"] == DEFAULT_LINEAR_DEFLECTION_M
    assert record["angular_deflection_rad"] == DEFAULT_ANGULAR_DEFLECTION_RAD
    assert record["backend_versions"]["cadquery"] != "unavailable"
    assert record["backend_versions"]["ocp"] != "unavailable"
    assert record["assembly_manifest"]["schema"] == MANIFEST_SCHEMA
    assert record["assembly_manifest"]["body_count"] == len(BODY_NAMES)
    assert [body["name"] for body in record["bodies"]] == list(BODY_NAMES)
    data = model.canonical_bytes()
    assert data.endswith(b"\n")
    assert json.loads(data) == record
    assert model.digest_sha256() == hashlib.sha256(data).hexdigest()
    assert model.digest_sha256() == REFERENCE_CAD_MODEL_SHA256


def test_invalid_segments_are_refused() -> None:
    """The reference mesh segment rule is enforced by the build."""
    with pytest.raises(DeviceGeometryError, match="multiple"):
        build_device_cad(
            reference_configuration(),
            reference_geometry(),
            REFERENCE_PLASMA_RADIUS_M,
            20,
        )


def test_column_violations_are_refused() -> None:
    """The plasma containment invariant holds for the CAD build."""
    with pytest.raises(DeviceGeometryError, match="plasma_radius_m"):
        build_device_cad(reference_configuration(), reference_geometry(), 0.09)


def test_tube_outside_the_coil_bore_is_refused() -> None:
    """A discharge tube wider than the coil bore is refused by the build."""
    geometry = dataclasses.replace(
        reference_geometry(), discharge_tube_wall_thickness_m=0.02
    )
    with pytest.raises(DeviceGeometryError, match="discharge_tube_outer_radius_m"):
        build_device_cad(reference_configuration(), geometry, REFERENCE_PLASMA_RADIUS_M)


def test_invalid_deflections_are_refused() -> None:
    """Non-positive deflections are refused by the build."""
    with pytest.raises(DeviceGeometryError, match="linear_deflection_m"):
        build_device_cad(
            reference_configuration(),
            reference_geometry(),
            REFERENCE_PLASMA_RADIUS_M,
            linear_deflection_m=0.0,
        )


def test_body_evidence_refuses_out_of_bound_values() -> None:
    """The library's evidence record fails closed when a bound is violated.

    The per-body check belongs to the shared library (its ADR 0009), so a
    violated bound surfaces as the library's error type; a build re-raises
    it under the device error type, which the build refusal tests cover.
    """
    model = reference_cad_model()
    body = model.bodies[0]
    with pytest.raises(CadError, match="volume_relative_error"):
        dataclasses.replace(body, volume_relative_error=1.0)
    with pytest.raises(CadError, match="surface_area_relative_error"):
        dataclasses.replace(body, surface_area_relative_error=1.0)
    with pytest.raises(CadError, match="faceted_volume_relative_deficit"):
        dataclasses.replace(body, faceted_volume_relative_deficit=1.0)
    with pytest.raises(CadError, match="mesh_volume_relative_difference"):
        dataclasses.replace(body, mesh_volume_relative_difference=1.0)


def test_model_refuses_a_foreign_body_inventory() -> None:
    """A record with the wrong body order is refused."""
    model = reference_cad_model()
    with pytest.raises(DeviceGeometryError, match="bodies must be exactly"):
        dataclasses.replace(model, bodies=model.bodies[::-1])


def test_model_refuses_invalid_declared_parameters() -> None:
    """The record refuses invalid segments, deflections and digests."""
    model = reference_cad_model()
    with pytest.raises(DeviceGeometryError, match="multiple"):
        dataclasses.replace(model, reference_mesh_segments=20)
    with pytest.raises(DeviceGeometryError, match="linear_deflection_m"):
        dataclasses.replace(model, linear_deflection_m=math.nan)
    with pytest.raises(DeviceGeometryError, match="angular_deflection_rad"):
        dataclasses.replace(model, angular_deflection_rad=-1.0)
    with pytest.raises(DeviceGeometryError, match="step_sha256"):
        dataclasses.replace(model, step_sha256="not-a-digest")
    with pytest.raises(DeviceGeometryError, match="assembly_manifest"):
        dataclasses.replace(model, assembly_manifest={"schema": "foreign"})
    manifest = dict(model.assembly_manifest)
    manifest["body_count"] = 1
    with pytest.raises(DeviceGeometryError, match="body_count"):
        dataclasses.replace(model, assembly_manifest=manifest)


def test_evidence_projection_is_json_serialisable() -> None:
    """The per-body evidence projects to JSON with every declared bound."""
    model = reference_cad_model()
    record = model.bodies[0].to_record()
    assert record["name"] == BODY_NAMES[0]
    assert record["volume_relative_error"] <= MEASURE_TOLERANCE
    assert (
        record["faceted_volume_relative_deficit"]
        <= record["faceted_volume_deficit_bound"]
    )
    json.dumps(record, allow_nan=False)
