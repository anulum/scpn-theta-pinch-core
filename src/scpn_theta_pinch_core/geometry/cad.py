# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Theta-Pinch Core — device CAD model record (tier G2)

"""Tier-G2 device CAD model: B-rep solids of one validated design.

The model composes the validated configuration (compression coil), the
validated device geometry (discharge tube, mirror coils, end flanges) and
the declared plasma radius of the level-0 models into the same seven named
bodies as the tier-G1 model (:func:`build_device_model`), built as exact
B-rep solids of revolution by the pinned third-party OpenCASCADE kernel
through the shared kernel library (``scpn_reactor_kernels.cad``, kernels
``cad_brep_solids``, ``cad_step_export``, ``cad_faceting``,
``cad_evidence``).

OpenCASCADE is not the bit-exact floor: every body is checked fail-closed
by the library's evidence kernel against its analytic closed form (volume
and surface area within the library's declared relative tolerance
``1e-9``), the faceted B-rep volume is checked against the declared
deflection deficit bound and against the tier-G1 mesh at the declared
reference segment count within the exact polygon-deficit bound, and the
STEP export is the library's normalised deterministic writer. This module
owns only what is device knowledge: the schema identity, the composition
of the seven bodies, the build invariants of this family and its
non-claims. The canonical record carries the schema identity, the units
and axis convention, both source digests, the declared plasma radius, the
declared deflections and reference segment count, the back-end versions,
the assembly manifest, the STEP digest and the per-body evidence; the
SHA-256 of that record identifies the exact model. No body carries an
engineering property and no value describes a real machine.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Any, Final

from scpn_reactor_kernels.cad import (
    MANIFEST_SCHEMA,
    BodyEvidence,
    BrepAssembly,
    annular_tube_brep,
    assembly_evidence,
    backend_versions,
    cylinder_solid_brep,
    facet_assembly,
)
from scpn_reactor_kernels.cad import (
    step_bytes as _normalised_step_bytes,
)
from scpn_reactor_kernels.cad import (
    step_sha256 as _step_bytes_sha256,
)
from scpn_reactor_kernels.errors import CadError, GeometryError
from scpn_reactor_kernels.geometry import TriangleMesh, require_segments

from scpn_theta_pinch_core.configuration import DeviceConfiguration
from scpn_theta_pinch_core.errors import DeviceGeometryError
from scpn_theta_pinch_core.geometry.device import DeviceGeometry
from scpn_theta_pinch_core.geometry.model import (
    BODY_COMPRESSION_COIL,
    BODY_DISCHARGE_TUBE,
    BODY_END_FLANGE_DOWNSTREAM,
    BODY_END_FLANGE_UPSTREAM,
    BODY_MIRROR_COIL_DOWNSTREAM,
    BODY_MIRROR_COIL_UPSTREAM,
    BODY_NAMES,
    BODY_PLASMA_COLUMN,
    MATERIAL_COIL_CONDUCTOR,
    MATERIAL_DISCHARGE_TUBE_INSULATOR,
    MATERIAL_FLANGE_WALL,
    MATERIAL_PLASMA,
    MODEL_UNITS,
    ROLE_COIL,
    ROLE_PLASMA,
    ROLE_VACUUM_BOUNDARY,
    build_device_model,
)

CAD_MODEL_SCHEMA: Final = "scpn.theta-pinch-cad-model.v1"
CAD_MODEL_SCHEMA_VERSION: Final = "1.0.0"
CAD_MODEL_NON_CLAIMS: Final = (
    "B-rep solids of the same declared design, built by the pinned "
    "third-party OpenCASCADE kernel and checked against the analytic closed "
    "forms; not an engineering model",
    "no material property, load, field or neutronic quantity is carried",
    "the end flanges are closing discs; tube feed-through hardware is not modelled",
    "STEP bytes are deterministic only within one pinned back-end "
    "environment; identity across OpenCASCADE or gmsh versions is not claimed",
    "a dimension reproduced from a published arrangement is an anchor,"
    " not a claim about that machine",
)

#: Reference segment count of the tier-G1 mesh the faceted B-rep is
#: compared against.
DEFAULT_REFERENCE_MESH_SEGMENTS: Final = 8
#: Declared mesher deflections of the reference record.
DEFAULT_LINEAR_DEFLECTION_M: Final = 1.0e-4
DEFAULT_ANGULAR_DEFLECTION_RAD: Final = 0.1


@dataclass(frozen=True, slots=True)
class DeviceModelCAD:
    """The B-rep device model of one configuration and geometry.

    Parameters
    ----------
    configuration_digest_sha256
        Digest of the validated configuration the model was built from.
    geometry_digest_sha256
        Digest of the validated geometry the model was built from.
    plasma_radius_m
        Declared plasma column radius the plasma body was built from.
    reference_mesh_segments
        Segment count of the tier-G1 reference mesh of the comparison.
    linear_deflection_m, angular_deflection_rad
        Declared mesher deflections of the faceting evidence.
    backend_versions
        Versions of the pinned CAD back-ends (``cadquery``, ``ocp``,
        ``gmsh``) as reported by the library.
    assembly_manifest
        The library's B-rep assembly manifest record.
    step_sha256
        SHA-256 of the normalised STEP export of the assembly.
    bodies
        Per-body evidence in the fixed order of :data:`BODY_NAMES`, as
        checked by the library's evidence kernel.
    step_data
        The normalised STEP bytes (the digested export).
    faceted_meshes
        The faceted closed meshes, one per body, in the fixed order.

    Raises
    ------
    DeviceGeometryError
        If the body inventory differs from :data:`BODY_NAMES`, the segment
        rule or the deflection rule is violated, the manifest is foreign,
        or the STEP digest is not a 64-hex value.
    """

    configuration_digest_sha256: str
    geometry_digest_sha256: str
    plasma_radius_m: float
    reference_mesh_segments: int
    linear_deflection_m: float
    angular_deflection_rad: float
    backend_versions: dict[str, str]
    assembly_manifest: dict[str, Any]
    step_sha256: str
    bodies: tuple[BodyEvidence, ...]
    step_data: bytes = field(compare=False, repr=False)
    faceted_meshes: tuple[TriangleMesh, ...] = field(
        compare=False, repr=False, default=()
    )

    def __post_init__(self) -> None:
        """Validate the model inventory and declared parameters.

        Raises
        ------
        DeviceGeometryError
            If any invariant fails.
        """
        names = tuple(body.name for body in self.bodies)
        if names != BODY_NAMES:
            raise DeviceGeometryError(
                f"bodies: bodies must be exactly {BODY_NAMES!r} in order, got {names!r}"
            )
        try:
            require_segments(self.reference_mesh_segments)
        except GeometryError as exc:
            raise DeviceGeometryError(str(exc)) from exc
        for name, value in (
            ("linear_deflection_m", self.linear_deflection_m),
            ("angular_deflection_rad", self.angular_deflection_rad),
        ):
            if not math.isfinite(value) or value <= 0.0:
                raise DeviceGeometryError(
                    f"{name}: must be finite and strictly positive, got {value!r}"
                )
        if self.assembly_manifest.get("schema") != MANIFEST_SCHEMA:
            raise DeviceGeometryError(
                f"assembly_manifest.schema: must be {MANIFEST_SCHEMA!r}"
            )
        if self.assembly_manifest.get("body_count") != len(BODY_NAMES):
            raise DeviceGeometryError(
                f"assembly_manifest.body_count: must be {len(BODY_NAMES)}, got "
                f"{self.assembly_manifest.get('body_count')!r}"
            )
        if len(self.step_sha256) != 64 or not all(
            character in "0123456789abcdef" for character in self.step_sha256
        ):
            raise DeviceGeometryError(
                "step_sha256: must be 64 lowercase hexadecimal characters"
            )

    def to_record(self) -> dict[str, Any]:
        """Project the model to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            Schema identity, units, non-claims, source digests, the plasma
            radius, the declared deflections and reference segment count,
            back-end versions, the assembly manifest, the STEP digest and
            every body evidence.
        """
        return {
            "schema": CAD_MODEL_SCHEMA,
            "schema_version": CAD_MODEL_SCHEMA_VERSION,
            "units": dict(MODEL_UNITS),
            "non_claims": list(CAD_MODEL_NON_CLAIMS),
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "geometry_digest_sha256": self.geometry_digest_sha256,
            "plasma_radius_m": self.plasma_radius_m,
            "reference_mesh_segments": self.reference_mesh_segments,
            "linear_deflection_m": self.linear_deflection_m,
            "angular_deflection_rad": self.angular_deflection_rad,
            "backend_versions": dict(self.backend_versions),
            "assembly_manifest": self.assembly_manifest,
            "step_sha256": self.step_sha256,
            "bodies": [body.to_record() for body in self.bodies],
        }

    def canonical_bytes(self) -> bytes:
        """Serialise the record canonically.

        Returns
        -------
        bytes
            UTF-8 JSON with sorted keys, minimal separators, and a
            trailing newline; NaN and infinity are never emitted.
        """
        text = json.dumps(
            self.to_record(), sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        return (text + "\n").encode("utf-8")

    def digest_sha256(self) -> str:
        """Identify the exact model record.

        Returns
        -------
        str
            SHA-256 digest of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def build_device_cad(
    configuration: DeviceConfiguration,
    geometry: DeviceGeometry,
    plasma_radius_m: float,
    segments: int = DEFAULT_REFERENCE_MESH_SEGMENTS,
    linear_deflection_m: float = DEFAULT_LINEAR_DEFLECTION_M,
    angular_deflection_rad: float = DEFAULT_ANGULAR_DEFLECTION_RAD,
) -> DeviceModelCAD:
    """Build the B-rep device model of a validated design.

    Parameters
    ----------
    configuration
        Validated theta-pinch configuration (compression coil).
    geometry
        Validated device geometry (discharge tube, coil walls, mirror
        coils, end flanges).
    plasma_radius_m
        Declared plasma column radius ``a``, the quantity the level-0
        models take; strictly positive and smaller than the tube bore.
    segments
        Segment count of the tier-G1 reference mesh of the faceting
        comparison; at least 8, multiple of 8.
    linear_deflection_m
        Largest chord distance of the faceting to the true surface;
        strictly positive.
    angular_deflection_rad
        Largest angle between adjacent facet normals; strictly positive.

    Returns
    -------
    DeviceModelCAD
        The composed, fail-closed checked model with its STEP export.

    Raises
    ------
    DeviceGeometryError
        If the segment count is invalid, the discharge tube does not fit
        the coil bore, the plasma column is not inside the tube, a
        deflection is invalid, or a body violates a declared evidence
        bound (the library's refusals are re-raised under the device error
        type with their messages);
        :class:`~scpn_reactor_kernels.errors.CadUnavailableError` if the
        optional CAD back-end is absent.
    """
    try:
        require_segments(segments)
    except GeometryError as exc:
        raise DeviceGeometryError(str(exc)) from exc
    reference = build_device_model(configuration, geometry, plasma_radius_m, segments)
    coil = configuration.coil
    coil_radius = coil.coil_radius_m
    coil_length = coil.coil_length_m
    tube_inner = geometry.discharge_tube_inner_radius_m
    tube_outer = geometry.discharge_tube_outer_radius_m
    z_tube_low = 0.0 - geometry.mirror_coil_length_m - geometry.tube_extension_length_m
    z_tube_high = (
        coil_length + geometry.mirror_coil_length_m + geometry.tube_extension_length_m
    )
    try:
        assembly = BrepAssembly(
            (
                annular_tube_brep(
                    tube_inner,
                    tube_outer,
                    z_tube_low,
                    z_tube_high,
                    BODY_DISCHARGE_TUBE,
                    ROLE_VACUUM_BOUNDARY,
                    MATERIAL_DISCHARGE_TUBE_INSULATOR,
                ),
                annular_tube_brep(
                    coil_radius,
                    coil_radius + geometry.coil_wall_thickness_m,
                    0.0,
                    coil_length,
                    BODY_COMPRESSION_COIL,
                    ROLE_COIL,
                    MATERIAL_COIL_CONDUCTOR,
                ),
                annular_tube_brep(
                    coil_radius,
                    coil_radius + geometry.mirror_coil_wall_thickness_m,
                    0.0 - geometry.mirror_coil_length_m,
                    0.0,
                    BODY_MIRROR_COIL_UPSTREAM,
                    ROLE_COIL,
                    MATERIAL_COIL_CONDUCTOR,
                ),
                annular_tube_brep(
                    coil_radius,
                    coil_radius + geometry.mirror_coil_wall_thickness_m,
                    coil_length,
                    coil_length + geometry.mirror_coil_length_m,
                    BODY_MIRROR_COIL_DOWNSTREAM,
                    ROLE_COIL,
                    MATERIAL_COIL_CONDUCTOR,
                ),
                cylinder_solid_brep(
                    tube_outer,
                    z_tube_low - geometry.end_flange_thickness_m,
                    z_tube_low,
                    BODY_END_FLANGE_UPSTREAM,
                    ROLE_VACUUM_BOUNDARY,
                    MATERIAL_FLANGE_WALL,
                ),
                cylinder_solid_brep(
                    tube_outer,
                    z_tube_high,
                    z_tube_high + geometry.end_flange_thickness_m,
                    BODY_END_FLANGE_DOWNSTREAM,
                    ROLE_VACUUM_BOUNDARY,
                    MATERIAL_FLANGE_WALL,
                ),
                cylinder_solid_brep(
                    plasma_radius_m,
                    0.0,
                    coil_length,
                    BODY_PLASMA_COLUMN,
                    ROLE_PLASMA,
                    MATERIAL_PLASMA,
                ),
            )
        )
        faceted = facet_assembly(assembly, linear_deflection_m, angular_deflection_rad)
        bodies = assembly_evidence(
            assembly.bodies,
            (
                tube_inner,
                coil_radius,
                coil_radius,
                coil_radius,
                tube_outer,
                tube_outer,
                plasma_radius_m,
            ),
            faceted,
            reference.meshes,
            linear_deflection_m,
            segments,
        )
    except CadError as exc:
        raise DeviceGeometryError(str(exc)) from exc
    manifest = assembly.manifest()
    extras = {
        "schema": CAD_MODEL_SCHEMA,
        "schema_version": CAD_MODEL_SCHEMA_VERSION,
        "configuration_digest_sha256": configuration.digest_sha256(),
        "geometry_digest_sha256": geometry.digest_sha256(),
        "assembly_manifest_sha256": assembly.manifest_sha256(),
        "units": dict(MODEL_UNITS),
        "non_claims": list(CAD_MODEL_NON_CLAIMS),
        "backend_versions": backend_versions(),
    }
    step_data = _normalised_step_bytes(assembly, extras)
    return DeviceModelCAD(
        configuration_digest_sha256=configuration.digest_sha256(),
        geometry_digest_sha256=geometry.digest_sha256(),
        plasma_radius_m=plasma_radius_m,
        reference_mesh_segments=segments,
        linear_deflection_m=linear_deflection_m,
        angular_deflection_rad=angular_deflection_rad,
        backend_versions=backend_versions(),
        assembly_manifest=manifest,
        step_sha256=_step_bytes_sha256(step_data),
        bodies=bodies,
        step_data=step_data,
        faceted_meshes=faceted,
    )
