# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Theta-Pinch Core — theta-pinch parameter model

"""Validated parameter objects of a theta-pinch configuration.

The derived quantity implements one standard result and nothing more:
the magnetic pressure ``p_B = B^2 / (2 mu0)`` of the compression field
(standard magnetostatics). It is a rough consistency instrument with
documented applicability bounds; no claim about any real machine follows
from it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

from scpn_theta_pinch_core.errors import DeviceConfigurationError

MU0: Final = 4.0e-7 * math.pi


def require_finite(name: str, value: float) -> float:
    """Return ``value`` when finite, otherwise fail closed.

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
    DeviceConfigurationError
        If ``value`` is NaN or infinite; non-finite input is rejected,
        never clamped.
    """
    if not math.isfinite(value):
        raise DeviceConfigurationError(f"{name}: must be finite, got {value!r}")
    return value


def require_positive(name: str, value: float) -> float:
    """Return ``value`` when finite and strictly positive.

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
    DeviceConfigurationError
        If ``value`` is non-finite or not strictly positive.
    """
    require_finite(name, value)
    if value <= 0.0:
        raise DeviceConfigurationError(
            f"{name}: must be strictly positive, got {value!r}"
        )
    return value


@dataclass(frozen=True, slots=True)
class CompressionCoil:
    """Compression-coil parameters of a theta pinch.

    Parameters
    ----------
    coil_field_t
        Peak axial compression field ``B`` in tesla; strictly positive.
    coil_radius_m
        Coil radius in metres; strictly positive.
    coil_length_m
        Coil length in metres; strictly positive.

    Raises
    ------
    DeviceConfigurationError
        If any parameter is non-finite or not strictly positive.
    """

    coil_field_t: float
    coil_radius_m: float
    coil_length_m: float

    def __post_init__(self) -> None:
        """Validate the compression-coil invariants.

        Raises
        ------
        DeviceConfigurationError
            If any parameter is non-finite or not strictly positive.
        """
        require_positive("coil_field_t", self.coil_field_t)
        require_positive("coil_radius_m", self.coil_radius_m)
        require_positive("coil_length_m", self.coil_length_m)

    def magnetic_pressure_pa(self) -> float:
        """Magnetic pressure of the validated compression field.

        Returns
        -------
        float
            ``p_B = B^2 / (2 mu0)`` in pascals.
        """
        return self.coil_field_t**2 / (2.0 * MU0)


@dataclass(frozen=True, slots=True)
class PlasmaState:
    """Declared plasma state of a theta-pinch configuration.

    Parameters
    ----------
    plasma_pressure_pa
        Declared peak plasma pressure in pascals; strictly positive.

    Raises
    ------
    DeviceConfigurationError
        If the pressure is non-finite or not strictly positive.
    """

    plasma_pressure_pa: float

    def __post_init__(self) -> None:
        """Validate the plasma-state invariants.

        Raises
        ------
        DeviceConfigurationError
            If the pressure is non-finite or not strictly positive.
        """
        require_positive("plasma_pressure_pa", self.plasma_pressure_pa)
