# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Theta-Pinch Core — toroidal equilibrium tests

"""Anchors, identities and refusals of the Scyllac toroidal equilibrium."""

from __future__ import annotations

import math

import pytest

from scpn_theta_pinch_core.errors import DeviceConfigurationError
from scpn_theta_pinch_core.physics import toroidal_equilibrium

FIGURE_TWO_MEASURED_PRODUCT = -0.0064


def test_figure_two_point_is_reproduced_within_ten_percent() -> None:
    """The 5-m sector point of Fig. 2 (beta 0.85, a 0.7 cm, R 2.375 m, h 0.19 /cm)."""
    equilibrium = toroidal_equilibrium(0.85, 0.007, 2.375, 19.0, 0.08, 0.08)
    required = equilibrium.required_field_ratio_product
    assert required < 0.0
    assert (
        abs(required - FIGURE_TWO_MEASURED_PRODUCT) / abs(FIGURE_TWO_MEASURED_PRODUCT)
        < 0.10
    )


def test_required_product_closed_form_identity() -> None:
    """The required field-ratio product equals -4(1-b)(1-b/2)/((3-2b) h R)."""
    beta, a, big_r, h = 0.7, 0.01, 3.0, 12.0
    equilibrium = toroidal_equilibrium(beta, a, big_r, h, 0.05, 0.05)
    closed = -4.0 * (1.0 - beta) * (1.0 - beta / 2.0) / ((3.0 - 2.0 * beta) * h * big_r)
    assert abs(equilibrium.required_field_ratio_product - closed) <= 1.0e-15
    assert equilibrium.required_excursion_product == 0.0 - 2.0 / (
        (3.0 - 2.0 * beta) * (h * h) * a * big_r
    )


def test_balance_is_unity_at_the_required_product() -> None:
    """Declaring ratios whose product is the required one balances the forces."""
    beta, a, big_r, h = 0.8, 0.02, 2.0, 15.0
    probe = toroidal_equilibrium(beta, a, big_r, h, 1.0, 1.0)
    magnitude = math.sqrt(abs(probe.required_field_ratio_product))
    balanced = toroidal_equilibrium(beta, a, big_r, h, magnitude, magnitude)
    assert abs(balanced.balance_ratio - 1.0) <= 1.0e-12
    assert abs(
        balanced.excursion_product - balanced.required_excursion_product
    ) <= 1.0e-12 * abs(balanced.required_excursion_product)
    assert balanced.auxiliary_field_ratio == magnitude * magnitude / 4.0


def test_excursions_follow_their_definitions() -> None:
    """delta_1 and delta_0 are the quotient forms of the evidence record."""
    beta, a, h = 0.6, 0.01, 10.0
    equilibrium = toroidal_equilibrium(beta, a, 1.0, h, 0.04, 0.02)
    assert equilibrium.excursion_l1 == 0.04 / ((h * a) * (1.0 - beta / 2.0))
    assert equilibrium.excursion_l0 == 0.0 - 0.02 / (2.0 * (1.0 - beta))
    assert equilibrium.excursion_l0 < 0.0 < equilibrium.excursion_l1
    assert equilibrium.balance_ratio > 0.0
    assert equilibrium.required_excursion_product < 0.0


def test_record_carries_every_field() -> None:
    """The record projection is complete."""
    record = toroidal_equilibrium(0.5, 0.01, 1.0, 10.0, 0.1, 0.1).to_record()
    assert len(record) == 7


@pytest.mark.parametrize(
    ("kwargs", "fragment"),
    [
        ({"beta": 1.0}, "0 < beta < 1"),
        ({"plasma_radius_m": 0.0}, "plasma_radius_m"),
        ({"major_radius_m": -1.0}, "major_radius_m"),
        ({"helical_wavenumber_per_m": math.nan}, "helical_wavenumber_per_m"),
        ({"l1_field_ratio": 0.0}, "l1_field_ratio"),
        ({"l0_field_ratio": -0.1}, "l0_field_ratio"),
    ],
)
def test_invalid_inputs_are_refused(kwargs: dict[str, float], fragment: str) -> None:
    """Every input is validated fail-closed."""
    arguments = {
        "beta": 0.8,
        "plasma_radius_m": 0.01,
        "major_radius_m": 2.0,
        "helical_wavenumber_per_m": 10.0,
        "l1_field_ratio": 0.05,
        "l0_field_ratio": 0.05,
    }
    arguments.update(kwargs)
    with pytest.raises(DeviceConfigurationError, match=fragment):
        toroidal_equilibrium(**arguments)
