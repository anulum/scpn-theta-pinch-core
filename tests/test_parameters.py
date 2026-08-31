# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Theta-Pinch Core — parameter model tests

"""Every validation branch of the theta-pinch parameter model.

All parameter sets in this module are synthetic fixtures; none describes
any real machine.
"""

from __future__ import annotations

import math

import pytest

from scpn_theta_pinch_core.errors import DeviceConfigurationError
from scpn_theta_pinch_core.parameters import (
    MU0,
    CompressionCoil,
    PlasmaState,
    require_finite,
    require_positive,
)


def synthetic_coil(**overrides: float) -> CompressionCoil:
    """Build a valid synthetic compression coil with optional overrides."""
    values: dict[str, float] = {
        "coil_field_t": 1.0,
        "coil_radius_m": 0.1,
        "coil_length_m": 1.0,
    }
    values.update(overrides)
    return CompressionCoil(**values)


def test_require_finite_accepts_and_rejects() -> None:
    """The finite guard returns the value and rejects NaN and infinity."""
    assert require_finite("x", 1.5) == 1.5
    for bad in (math.nan, math.inf, -math.inf):
        with pytest.raises(DeviceConfigurationError, match="x: must be finite"):
            require_finite("x", bad)


def test_require_positive_accepts_and_rejects() -> None:
    """The positive guard returns the value and rejects zero and below."""
    assert require_positive("x", 0.1) == 0.1
    for bad in (0.0, -2.0):
        with pytest.raises(DeviceConfigurationError, match="strictly positive"):
            require_positive("x", bad)
    with pytest.raises(DeviceConfigurationError, match="must be finite"):
        require_positive("x", math.nan)


def test_magnetic_pressure_formula() -> None:
    """The magnetic pressure follows ``B^2 / (2 mu0)`` exactly."""
    assert synthetic_coil().magnetic_pressure_pa() == pytest.approx(1.0 / (2.0 * MU0))


@pytest.mark.parametrize(
    ("overrides", "fragment"),
    [
        ({"coil_field_t": 0.0}, "coil_field_t"),
        ({"coil_radius_m": -1.0}, "coil_radius_m"),
        ({"coil_length_m": 0.0}, "coil_length_m"),
        ({"coil_field_t": math.nan}, "coil_field_t"),
    ],
)
def test_invalid_coil_is_rejected(overrides: dict[str, float], fragment: str) -> None:
    """Each compression-coil violation is rejected with its field name."""
    with pytest.raises(DeviceConfigurationError, match=fragment):
        synthetic_coil(**overrides)


def test_valid_plasma_state_constructs() -> None:
    """A valid plasma-state declaration constructs unchanged."""
    assert PlasmaState(plasma_pressure_pa=3.0e5).plasma_pressure_pa == 3.0e5


def test_invalid_plasma_state_is_rejected() -> None:
    """Non-positive pressures are rejected."""
    with pytest.raises(DeviceConfigurationError, match="plasma_pressure_pa"):
        PlasmaState(plasma_pressure_pa=0.0)
    with pytest.raises(DeviceConfigurationError, match="plasma_pressure_pa"):
        PlasmaState(plasma_pressure_pa=math.inf)
