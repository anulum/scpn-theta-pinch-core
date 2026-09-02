# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Theta-Pinch Core — m = 1 stability tests

"""Anchors, identities and refusals of the growth estimate and wall condition."""

from __future__ import annotations

import math

import pytest

from physics_fixtures import configuration, inputs
from scpn_theta_pinch_core.errors import DeviceConfigurationError
from scpn_theta_pinch_core.physics import (
    DEUTERON_MASS_KG,
    m1_growth_estimate,
    sharp_boundary_state,
    toroidal_equilibrium,
    wall_stabilisation,
)


def test_worked_example_of_the_wall_condition() -> None:
    """Reproduce the worked example a = 3 cm, beta = 0.8, h a = 0.13: a/b = 0.4."""
    wall = wall_stabilisation(0.8, 0.13 / 0.03, 0.03, 0.1)
    assert abs(wall.required_radius_ratio - 0.40) <= 0.01
    assert wall.radius_ratio == 0.3
    assert not wall.stabilised
    stabilised = wall_stabilisation(0.8, 0.13 / 0.03, 0.03, 0.07)
    assert stabilised.stabilised


def test_wall_condition_is_the_fourth_root_of_the_derived_form() -> None:
    """The required ratio is ((4-3b)(2-b)(ha)^2/(8b(1-b)))^(1/4)."""
    beta, h, a = 0.6, 8.0, 0.02
    wall = wall_stabilisation(beta, h, a, 0.1)
    fourth = (
        (4.0 - 3.0 * beta) * (2.0 - beta) * (h * a) ** 2 / (8.0 * beta * (1.0 - beta))
    )
    assert abs(wall.required_radius_ratio - fourth**0.25) <= 1.0e-15


def test_scyllac_five_metre_growth_rate_order_of_magnitude() -> None:
    """The source's calculated 1.0 MHz is reproduced within a factor of two.

    Inputs are the source's stated orders of magnitude (B ~ 3.6 T,
    n ~ 2.5e22 m^-3, beta 0.85, equal field ratios with product 0.0064,
    a = 0.7 cm, h = 0.19 /cm); the anchor is deliberately loose because the
    source does not print every input of its own calculation.
    """
    state = sharp_boundary_state(configuration(), DEUTERON_MASS_KG, 2.5e22)
    model = inputs()
    equilibrium = toroidal_equilibrium(
        state.beta,
        model.plasma_radius_m,
        model.major_radius_m,
        model.helical_wavenumber_per_m,
        model.l1_field_ratio,
        model.l0_field_ratio,
    )
    growth = m1_growth_estimate(
        state.beta,
        state.alfven_speed_m_s,
        model.helical_wavenumber_per_m,
        model.plasma_radius_m,
        0.08,
        equilibrium.excursion_l1,
        equilibrium.excursion_l0,
        model.l1_field_ratio,
    )
    assert not growth.stable
    assert 0.5e6 < growth.growth_rate_per_s < 2.0e6
    assert 0.5e6 < growth.reduced_growth_rate_per_s < 2.0e6
    assert growth.wall_term < 0.0 < growth.l1_term
    assert growth.l0_term > 0.0
    assert growth.bracket == growth.wall_term + growth.l1_term + growth.l0_term


def test_growth_rate_is_zero_exactly_at_the_wall_boundary() -> None:
    """With delta_0 = 0 and a/b at the required ratio the bracket vanishes."""
    beta, h, a = 0.7, 10.0, 0.02
    wall = wall_stabilisation(beta, h, a, 0.1)
    coil = a / wall.required_radius_ratio
    growth = m1_growth_estimate(beta, 3.0e5, h, a, coil, 1.0, 0.0, 0.05)
    assert abs(growth.bracket) <= 1.0e-15
    assert growth.growth_rate_per_s == 0.0 or growth.growth_rate_per_s < 1.0e-1
    tighter = m1_growth_estimate(beta, 3.0e5, h, a, coil * 0.99, 1.0, 0.0, 0.05)
    assert tighter.stable
    assert tighter.growth_rate_per_s == 0.0


def test_reduced_estimate_follows_equation_four() -> None:
    """gamma_4 = sqrt(b(4-3b)/(2(1-b)(2-b))) v_A h (B_1/B_0)."""
    beta, va, h = 0.5, 2.0e5, 12.0
    growth = m1_growth_estimate(beta, va, h, 0.01, 0.05, 0.5, -0.1, 0.03)
    expected = (
        math.sqrt(beta * (4 - 3 * beta) / (2 * (1 - beta) * (2 - beta))) * va * h * 0.03
    )
    assert abs(growth.reduced_growth_rate_per_s - expected) <= 1.0e-9
    assert len(growth.to_record()) == 7
    assert len(wall_stabilisation(beta, h, 0.01, 0.05).to_record()) == 3


@pytest.mark.parametrize(
    ("kwargs", "fragment"),
    [
        ({"beta": 0.0}, "0 < beta < 1"),
        ({"alfven_speed_m_s": 0.0}, "alfven_speed_m_s"),
        ({"helical_wavenumber_per_m": -1.0}, "helical_wavenumber_per_m"),
        ({"plasma_radius_m": 0.0}, "plasma_radius_m"),
        ({"coil_radius_m": 0.0}, "coil_radius_m"),
        ({"plasma_radius_m": 0.05}, "smaller than coil_radius_m"),
        ({"excursion_l1": math.nan}, "excursion_l1"),
        ({"excursion_l0": math.inf}, "excursion_l0"),
        ({"l1_field_ratio": 0.0}, "l1_field_ratio"),
    ],
)
def test_growth_inputs_are_validated(kwargs: dict[str, float], fragment: str) -> None:
    """Every growth-estimate input is validated fail-closed."""
    arguments = {
        "beta": 0.7,
        "alfven_speed_m_s": 3.0e5,
        "helical_wavenumber_per_m": 10.0,
        "plasma_radius_m": 0.01,
        "coil_radius_m": 0.05,
        "excursion_l1": 0.5,
        "excursion_l0": -0.1,
        "l1_field_ratio": 0.05,
    }
    arguments.update(kwargs)
    with pytest.raises(DeviceConfigurationError, match=fragment):
        m1_growth_estimate(**arguments)


def test_wall_inputs_are_validated() -> None:
    """The wall condition validates beta, h and the radii."""
    with pytest.raises(DeviceConfigurationError, match="0 < beta < 1"):
        wall_stabilisation(1.0, 10.0, 0.01, 0.05)
    with pytest.raises(DeviceConfigurationError, match="helical_wavenumber_per_m"):
        wall_stabilisation(0.5, 0.0, 0.01, 0.05)
    with pytest.raises(DeviceConfigurationError, match="smaller than coil_radius_m"):
        wall_stabilisation(0.5, 10.0, 0.05, 0.05)
