# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Theta-Pinch Core — device 3D model record

"""Tier-G1 device 3D model: analytic bodies of one validated design.

The model composes the validated configuration (compression coil), the
validated device geometry (discharge tube, mirror coils, end flanges) and
the declared plasma radius of the level-0 models into seven named, closed,
outward-oriented triangle meshes on the device axis, regenerated
deterministically from the two records and that radius. Its canonical
record carries the schema identity, the units and axis convention, both
source digests, the plasma radius, the segment count, a summary of every
body (counts, volume, area, bounding box, mesh digest) and fixed
non-claims; the SHA-256 of that record identifies the exact model.

The meshes are analytic surfaces: the plasma body is the declared column
of the sharp-boundary models, not an equilibrium boundary, and no body
carries an engineering property. The end flanges are plain closing discs
of the tube bore diameter: in a real assembly the tube passes through its
end hardware, and that simplification is a property of this tier. The
unit circle, the primitives and the mesh contract are consumed from the
pinned shared kernel library (``scpn_reactor_kernels.geometry``, ADR
0007); this module owns only the device composition.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_reactor_kernels.errors import GeometryError
from scpn_reactor_kernels.geometry import (
    TriangleMesh,
    annular_tube,
    cylinder_solid,
    require_segments,
)

from scpn_theta_pinch_core.configuration import DeviceConfiguration
from scpn_theta_pinch_core.errors import DeviceGeometryError
from scpn_theta_pinch_core.geometry.device import DeviceGeometry
from scpn_theta_pinch_core.parameters import require_positive

MODEL_SCHEMA: Final = "scpn.theta-pinch-3d-model.v1"
MODEL_SCHEMA_VERSION: Final = "1.0.0"
MODEL_UNITS: Final = {
    "length": "metre",
    "handedness": "right",
    "axis": "z along the device axis, increasing downstream",
    "origin": "upstream face of the main compression coil at z = 0 on the axis",
}
MODEL_NON_CLAIMS: Final = (
    "analytic surfaces tessellated from a synthetic configuration and geometry",
    "no body is an equilibrium boundary, a CAD solid or an engineering model",
    "no material property, load, field or neutronic quantity is carried",
    "the end flanges are closing discs; tube feed-through hardware is not modelled",
    "no value describes or validates any real machine",
)

ROLE_COIL: Final = "coil"
ROLE_VACUUM_BOUNDARY: Final = "vacuum_boundary"
ROLE_PLASMA: Final = "plasma"
MATERIAL_COIL_CONDUCTOR: Final = "coil_conductor"
MATERIAL_DISCHARGE_TUBE_INSULATOR: Final = "discharge_tube_insulator"
MATERIAL_FLANGE_WALL: Final = "flange_wall"
MATERIAL_PLASMA: Final = "plasma"

BODY_DISCHARGE_TUBE: Final = "discharge_tube"
BODY_COMPRESSION_COIL: Final = "compression_coil"
BODY_MIRROR_COIL_UPSTREAM: Final = "mirror_coil_upstream"
BODY_MIRROR_COIL_DOWNSTREAM: Final = "mirror_coil_downstream"
BODY_END_FLANGE_UPSTREAM: Final = "end_flange_upstream"
BODY_END_FLANGE_DOWNSTREAM: Final = "end_flange_downstream"
BODY_PLASMA_COLUMN: Final = "plasma_column"
BODY_NAMES: Final = (
    BODY_DISCHARGE_TUBE,
    BODY_COMPRESSION_COIL,
    BODY_MIRROR_COIL_UPSTREAM,
    BODY_MIRROR_COIL_DOWNSTREAM,
    BODY_END_FLANGE_UPSTREAM,
    BODY_END_FLANGE_DOWNSTREAM,
    BODY_PLASMA_COLUMN,
)


@dataclass(frozen=True, slots=True)
class DeviceModel3D:
    """The tessellated device model of one configuration and geometry.

    Parameters
    ----------
    configuration_digest_sha256
        Digest of the validated configuration the model was built from.
    geometry_digest_sha256
        Digest of the validated geometry the model was built from.
    plasma_radius_m
        Declared plasma column radius the plasma body was built from.
    segments
        Circumferential segment count used for every body.
    meshes
        The seven bodies in the fixed order of :data:`BODY_NAMES`.

    Raises
    ------
    DeviceGeometryError
        If the body names or their order differ from :data:`BODY_NAMES`.
    """

    configuration_digest_sha256: str
    geometry_digest_sha256: str
    plasma_radius_m: float
    segments: int
    meshes: tuple[TriangleMesh, ...]

    def __post_init__(self) -> None:
        """Validate the body inventory.

        Raises
        ------
        DeviceGeometryError
            If the body names or their order differ from :data:`BODY_NAMES`.
        """
        names = tuple(mesh.name for mesh in self.meshes)
        if names != BODY_NAMES:
            raise DeviceGeometryError(
                f"meshes: bodies must be exactly {BODY_NAMES!r} in order, got {names!r}"
            )

    def to_record(self) -> dict[str, Any]:
        """Project the model to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            Schema identity, units, non-claims, source digests, the plasma
            radius, the segment count and every body summary.
        """
        return {
            "schema": MODEL_SCHEMA,
            "schema_version": MODEL_SCHEMA_VERSION,
            "units": dict(MODEL_UNITS),
            "non_claims": list(MODEL_NON_CLAIMS),
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "geometry_digest_sha256": self.geometry_digest_sha256,
            "plasma_radius_m": self.plasma_radius_m,
            "segments": self.segments,
            "bodies": [mesh.summary_record() for mesh in self.meshes],
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


def build_device_model(
    configuration: DeviceConfiguration,
    geometry: DeviceGeometry,
    plasma_radius_m: float,
    segments: int,
) -> DeviceModel3D:
    """Tessellate the seven bodies of a validated design.

    Parameters
    ----------
    configuration
        Validated theta-pinch configuration; its compression coil fixes the
        shared bore radius and the length of the main coil.
    geometry
        Validated device geometry (discharge tube, coil walls, mirror coils,
        end flanges).
    plasma_radius_m
        Declared plasma column radius ``a``, the quantity the level-0
        models take; strictly positive and smaller than the tube bore.
    segments
        Circumferential segments for every body; at least 8, multiple of 8.

    Returns
    -------
    DeviceModel3D
        The composed model.

    Raises
    ------
    DeviceGeometryError
        If the segment count is invalid (the library's refusal is re-raised
        under the device error type with its message), if the discharge
        tube does not fit inside the coil bore, or if the plasma column is
        not inside the discharge tube.
    """
    try:
        require_segments(segments)
    except GeometryError as exc:
        raise DeviceGeometryError(str(exc)) from exc
    try:
        require_positive("plasma_radius_m", plasma_radius_m)
    except ValueError as exc:
        raise DeviceGeometryError(str(exc)) from exc
    coil = configuration.coil
    if geometry.discharge_tube_outer_radius_m > coil.coil_radius_m:
        raise DeviceGeometryError(
            "discharge_tube_outer_radius_m: must not exceed the coil bore radius "
            f"{coil.coil_radius_m!r}, got "
            f"{geometry.discharge_tube_outer_radius_m!r}"
        )
    if plasma_radius_m >= geometry.discharge_tube_inner_radius_m:
        raise DeviceGeometryError(
            "plasma_radius_m: must be smaller than "
            "discharge_tube_inner_radius_m, got "
            f"{plasma_radius_m!r} >= {geometry.discharge_tube_inner_radius_m!r}"
        )
    coil_radius = coil.coil_radius_m
    coil_length = coil.coil_length_m
    tube_outer = geometry.discharge_tube_outer_radius_m
    z_tube_low = 0.0 - geometry.mirror_coil_length_m - geometry.tube_extension_length_m
    z_tube_high = (
        coil_length + geometry.mirror_coil_length_m + geometry.tube_extension_length_m
    )
    bodies = (
        (
            BODY_DISCHARGE_TUBE,
            ROLE_VACUUM_BOUNDARY,
            MATERIAL_DISCHARGE_TUBE_INSULATOR,
            annular_tube(
                geometry.discharge_tube_inner_radius_m,
                tube_outer,
                z_tube_low,
                z_tube_high,
                segments,
            ),
        ),
        (
            BODY_COMPRESSION_COIL,
            ROLE_COIL,
            MATERIAL_COIL_CONDUCTOR,
            annular_tube(
                coil_radius,
                coil_radius + geometry.coil_wall_thickness_m,
                0.0,
                coil_length,
                segments,
            ),
        ),
        (
            BODY_MIRROR_COIL_UPSTREAM,
            ROLE_COIL,
            MATERIAL_COIL_CONDUCTOR,
            annular_tube(
                coil_radius,
                coil_radius + geometry.mirror_coil_wall_thickness_m,
                0.0 - geometry.mirror_coil_length_m,
                0.0,
                segments,
            ),
        ),
        (
            BODY_MIRROR_COIL_DOWNSTREAM,
            ROLE_COIL,
            MATERIAL_COIL_CONDUCTOR,
            annular_tube(
                coil_radius,
                coil_radius + geometry.mirror_coil_wall_thickness_m,
                coil_length,
                coil_length + geometry.mirror_coil_length_m,
                segments,
            ),
        ),
        (
            BODY_END_FLANGE_UPSTREAM,
            ROLE_VACUUM_BOUNDARY,
            MATERIAL_FLANGE_WALL,
            cylinder_solid(
                tube_outer,
                z_tube_low - geometry.end_flange_thickness_m,
                z_tube_low,
                segments,
            ),
        ),
        (
            BODY_END_FLANGE_DOWNSTREAM,
            ROLE_VACUUM_BOUNDARY,
            MATERIAL_FLANGE_WALL,
            cylinder_solid(
                tube_outer,
                z_tube_high,
                z_tube_high + geometry.end_flange_thickness_m,
                segments,
            ),
        ),
        (
            BODY_PLASMA_COLUMN,
            ROLE_PLASMA,
            MATERIAL_PLASMA,
            cylinder_solid(plasma_radius_m, 0.0, coil_length, segments),
        ),
    )
    meshes = tuple(
        TriangleMesh(
            name=name,
            role=role,
            material_identifier=material,
            vertices=vertices,
            faces=faces,
        )
        for name, role, material, (vertices, faces) in bodies
    )
    return DeviceModel3D(
        configuration_digest_sha256=configuration.digest_sha256(),
        geometry_digest_sha256=geometry.digest_sha256(),
        plasma_radius_m=plasma_radius_m,
        segments=segments,
        meshes=meshes,
    )
