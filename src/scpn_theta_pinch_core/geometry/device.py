# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Theta-Pinch Core — device geometry model

"""Validated device geometry of a linear theta-pinch assembly.

The geometry complements the
:class:`~scpn_theta_pinch_core.configuration.DeviceConfiguration` (which
carries the compression coil and the plasma state) with the device-owned
mechanical envelope: the discharge tube inside the coil bore, the wall
thicknesses of the main and mirror coils, the length of the mirror coils
that flank the main coil, the tube overhang beyond them and the thickness
of the end flanges. The layout is the qualitative arrangement of the
linear theta pinch described by W. E. Quinn et al., "Review of Scyllac
theta-pinch experiments", LA-UR-73-1053 (1973), section VI.A, pp. 13-14
(a straight theta pinch whose main compression coil is flanked by mirror
coils of their own bank, main and mirror coils sharing one bore, with a
discharge tube of smaller bore inside them). Parameter sets are declared
by the caller: the repository's own fixtures are synthetic, and one
anchor fixture carries the dimensions that section prints so the tier can
be checked against a published arrangement. Reproducing a printed
dimension is an anchor, never a claim about that machine.

The coil bore radius and the coil length are not repeated here: they are
the validated configuration's ``coil_radius_m`` and ``coil_length_m``,
checked against this geometry when the model is built. Validation is
fail-closed, serialisation is canonical, and the SHA-256 digest
identifies the exact geometry.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_theta_pinch_core.errors import DeviceGeometryError
from scpn_theta_pinch_core.parameters import require_positive

GEOMETRY_FIELDS: Final = (
    "discharge_tube_inner_radius_m",
    "discharge_tube_wall_thickness_m",
    "tube_extension_length_m",
    "coil_wall_thickness_m",
    "mirror_coil_length_m",
    "mirror_coil_wall_thickness_m",
    "end_flange_thickness_m",
)


def _positive(name: str, value: float) -> float:
    """Apply the shared positivity rule with the geometry error type.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceGeometryError
        If the value is non-finite or not strictly positive.
    """
    try:
        return require_positive(name, value)
    except ValueError as exc:
        raise DeviceGeometryError(str(exc)) from exc


@dataclass(frozen=True, slots=True)
class DeviceGeometry:
    """Validated linear theta-pinch geometry (SI units in the field names).

    Parameters
    ----------
    discharge_tube_inner_radius_m
        Bore radius of the discharge tube; strictly positive.
    discharge_tube_wall_thickness_m
        Radial wall thickness of the discharge tube; strictly positive.
    tube_extension_length_m
        Axial overhang of the discharge tube beyond each mirror coil;
        strictly positive.
    coil_wall_thickness_m
        Radial wall thickness of the main compression coil; strictly
        positive.
    mirror_coil_length_m
        Axial length of each of the two mirror coils; strictly positive.
    mirror_coil_wall_thickness_m
        Radial wall thickness of each mirror coil; strictly positive.
    end_flange_thickness_m
        Axial thickness of the two end flanges; strictly positive.

    Raises
    ------
    DeviceGeometryError
        If any value is non-finite or not strictly positive.
    """

    discharge_tube_inner_radius_m: float
    discharge_tube_wall_thickness_m: float
    tube_extension_length_m: float
    coil_wall_thickness_m: float
    mirror_coil_length_m: float
    mirror_coil_wall_thickness_m: float
    end_flange_thickness_m: float

    def __post_init__(self) -> None:
        """Validate every declared value.

        Raises
        ------
        DeviceGeometryError
            If any value is non-finite or not strictly positive.
        """
        for name in GEOMETRY_FIELDS:
            _positive(name, getattr(self, name))

    @property
    def discharge_tube_outer_radius_m(self) -> float:
        """Outer radius of the discharge tube (bore plus wall)."""
        return self.discharge_tube_inner_radius_m + self.discharge_tube_wall_thickness_m

    def to_record(self) -> dict[str, float]:
        """Project the geometry to a JSON-serialisable record.

        Returns
        -------
        dict[str, float]
            Every declared parameter under its name.
        """
        return {name: getattr(self, name) for name in GEOMETRY_FIELDS}

    def canonical_bytes(self) -> bytes:
        """Serialise the geometry canonically.

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
        """Identify the exact geometry.

        Returns
        -------
        str
            SHA-256 digest of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def _number(record: dict[str, Any], field: str) -> float:
    """Return one required real-number field of a record.

    Parameters
    ----------
    record
        Decoded JSON object.
    field
        Field name to read.

    Returns
    -------
    float
        The field value as a float.

    Raises
    ------
    DeviceGeometryError
        If the field is missing or not a real number (booleans rejected).
    """
    value = record.get(field)
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise DeviceGeometryError(f"{field}: must be a number, got {value!r}")
    return float(value)


def geometry_from_record(record: Any) -> DeviceGeometry:
    """Build a validated geometry from a decoded record.

    Parameters
    ----------
    record
        Decoded JSON object in the shape produced by
        :meth:`DeviceGeometry.to_record`.

    Returns
    -------
    DeviceGeometry
        The fully validated geometry.

    Raises
    ------
    DeviceGeometryError
        If the record shape or any value violates the model; unknown
        fields are refused.
    """
    if not isinstance(record, dict):
        raise DeviceGeometryError("record: must be an object")
    unknown = sorted(set(record) - set(GEOMETRY_FIELDS))
    if unknown:
        raise DeviceGeometryError(f"record: unknown fields {unknown!r}")
    return DeviceGeometry(**{name: _number(record, name) for name in GEOMETRY_FIELDS})


def geometry_from_bytes(data: bytes) -> DeviceGeometry:
    """Build a validated geometry from canonical JSON bytes.

    Parameters
    ----------
    data
        UTF-8 JSON document; NaN and infinity literals are rejected.

    Returns
    -------
    DeviceGeometry
        The fully validated geometry.

    Raises
    ------
    DeviceGeometryError
        If the document is not valid strict JSON or violates the model.
    """

    def _reject_constant(literal: str) -> float:
        raise DeviceGeometryError(
            f"record: non-finite JSON literal {literal!r} is rejected"
        )

    try:
        record = json.loads(data.decode("utf-8"), parse_constant=_reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DeviceGeometryError(f"record: invalid JSON document: {exc}") from exc
    return geometry_from_record(record)
