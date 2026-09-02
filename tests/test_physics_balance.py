# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Theta-Pinch Core — sharp-boundary state tests

"""Beta domain, derived quantities and refusals of the sharp-boundary state."""

from __future__ import annotations

import math

import pytest

from physics_fixtures import configuration
from scpn_theta_pinch_core.errors import DeviceConfigurationError
from scpn_theta_pinch_core.parameters import MU0
from scpn_theta_pinch_core.physics import (
    DEUTERON_MASS_KG,
    ELEMENTARY_CHARGE_C,
    PROTON_MASS_KG,
    require_sharp_boundary_beta,
    sharp_boundary_state,
)


def test_state_reproduces_the_closed_forms() -> None:
    """Beta, temperature, Alfvén speed and end time follow the stated forms."""
    config = configuration(field_t=3.6, beta=0.85, coil_length_m=5.0)
    state = sharp_boundary_state(config, DEUTERON_MASS_KG, 2.5e22)
    assert abs(state.beta - 0.85) <= 1.0e-15
    assert state.field_t == 3.6
    assert state.plasma_pressure_pa == config.plasma.plasma_pressure_pa
    assert state.ion_density_per_m3 == 2.5e22
    expected_t = config.plasma.plasma_pressure_pa / (2.0 * 2.5e22 * ELEMENTARY_CHARGE_C)
    assert state.ion_temperature_ev == expected_t
    expected_va = 3.6 / math.sqrt(MU0 * 2.5e22 * DEUTERON_MASS_KG)
    assert state.alfven_speed_m_s == expected_va
    assert state.end_alfven_time_s == 2.5 / expected_va
    assert 3.0e5 < state.alfven_speed_m_s < 4.0e5
    assert 5.0e-6 < state.end_alfven_time_s < 1.0e-5


def test_alfven_speed_scales_with_mass_and_density() -> None:
    """Check v_A ∝ m_i^-1/2 and n^-1/2: deuteron speed is proton speed / sqrt(2)."""
    config = configuration()
    proton = sharp_boundary_state(config, PROTON_MASS_KG, 1.0e22).alfven_speed_m_s
    deuteron = sharp_boundary_state(config, DEUTERON_MASS_KG, 1.0e22).alfven_speed_m_s
    denser = sharp_boundary_state(config, PROTON_MASS_KG, 4.0e22).alfven_speed_m_s
    assert abs(deuteron - proton / math.sqrt(DEUTERON_MASS_KG / PROTON_MASS_KG)) <= 1e-9
    assert abs(denser - proton / 2.0) <= 1.0e-9


def test_record_carries_every_field() -> None:
    """The record projection is complete."""
    record = sharp_boundary_state(configuration(), DEUTERON_MASS_KG, 1.0e22).to_record()
    assert set(record) == {
        "beta",
        "field_t",
        "plasma_pressure_pa",
        "ion_density_per_m3",
        "ion_temperature_ev",
        "alfven_speed_m_s",
        "end_alfven_time_s",
    }


@pytest.mark.parametrize("beta", [0.0, 1.0, 1.5, -0.1, math.nan])
def test_beta_outside_the_open_interval_is_refused(beta: float) -> None:
    """The sharp-boundary relations need 0 < beta < 1."""
    with pytest.raises(DeviceConfigurationError, match="0 < beta < 1"):
        require_sharp_boundary_beta(beta)


def test_unity_beta_configuration_is_refused_by_the_state() -> None:
    """A configuration at beta = 1 is valid but has no sharp-boundary state."""
    with pytest.raises(DeviceConfigurationError, match="0 < beta < 1"):
        sharp_boundary_state(configuration(beta=1.0), DEUTERON_MASS_KG, 1.0e22)


@pytest.mark.parametrize("mass", [0.0, -1.0, math.inf])
def test_invalid_mass_is_refused(mass: float) -> None:
    """Ion mass must be finite and strictly positive."""
    with pytest.raises(DeviceConfigurationError, match="ion_mass_kg"):
        sharp_boundary_state(configuration(), mass, 1.0e22)


def test_invalid_density_is_refused() -> None:
    """Ion density must be strictly positive."""
    with pytest.raises(DeviceConfigurationError, match="ion_density_per_m3"):
        sharp_boundary_state(configuration(), DEUTERON_MASS_KG, 0.0)
