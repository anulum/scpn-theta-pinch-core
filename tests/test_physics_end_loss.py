# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Theta-Pinch Core — end-loss scaling tests

"""Table I anchors, scaling exponents and refusals of the end-loss estimate."""

from __future__ import annotations

import math

import pytest

from scpn_theta_pinch_core.errors import DeviceConfigurationError
from scpn_theta_pinch_core.physics import (
    SCYLLAC_LINEAR_REFERENCE,
    EndLossReference,
    end_loss_estimate,
)


@pytest.mark.parametrize(
    ("length_m", "temperature_ev", "scaled_s"),
    [(1.0, 3200.0, 2.13e-6), (3.0, 1400.0, 9.67e-6), (5.0, 2700.0, 11.50e-6)],
)
def test_table_one_rows_within_one_percent(
    length_m: float, temperature_ev: float, scaled_s: float
) -> None:
    """Scylla IV-1, Scylla IV-3 and the linear Scyllac rows of Table I."""
    estimate = end_loss_estimate(length_m, temperature_ev, SCYLLAC_LINEAR_REFERENCE)
    assert abs(estimate.loss_time_s - scaled_s) / scaled_s < 0.01


def test_scaling_exponents() -> None:
    """Tau ∝ L and tau ∝ T^-1/2 exactly."""
    base = end_loss_estimate(2.0, 1000.0, SCYLLAC_LINEAR_REFERENCE).loss_time_s
    doubled = end_loss_estimate(4.0, 1000.0, SCYLLAC_LINEAR_REFERENCE).loss_time_s
    hotter = end_loss_estimate(2.0, 4000.0, SCYLLAC_LINEAR_REFERENCE).loss_time_s
    assert abs(doubled - 2.0 * base) <= 1.0e-20
    assert abs(hotter - base / 2.0) <= 1.0e-20


def test_reference_point_is_the_scaled_identity() -> None:
    """At the reference point the scaled time is the reference time."""
    reference = EndLossReference(
        coil_length_m=2.0, ion_temperature_ev=500.0, loss_time_s=3.0e-6
    )
    estimate = end_loss_estimate(2.0, 500.0, reference)
    assert estimate.loss_time_s == 3.0e-6
    record = estimate.to_record()
    assert record["reference"] == reference.to_record()
    assert set(record) == {
        "coil_length_m",
        "ion_temperature_ev",
        "loss_time_s",
        "reference",
    }


@pytest.mark.parametrize(
    "field", ["coil_length_m", "ion_temperature_ev", "loss_time_s"]
)
def test_reference_fields_are_validated(field: str) -> None:
    """Every reference field must be finite and strictly positive."""
    values = {
        "coil_length_m": 5.0,
        "ion_temperature_ev": 2700.0,
        "loss_time_s": 11.5e-6,
    }
    values[field] = 0.0
    with pytest.raises(DeviceConfigurationError, match=field):
        EndLossReference(**values)


def test_estimate_inputs_are_validated() -> None:
    """Length and temperature must be strictly positive."""
    with pytest.raises(DeviceConfigurationError, match="coil_length_m"):
        end_loss_estimate(0.0, 1000.0, SCYLLAC_LINEAR_REFERENCE)
    with pytest.raises(DeviceConfigurationError, match="ion_temperature_ev"):
        end_loss_estimate(1.0, math.nan, SCYLLAC_LINEAR_REFERENCE)
