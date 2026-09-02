# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Theta-Pinch Core — native kernel parity tests

"""Bit-exact parity between the Python floor and the native kernels.

The native module is an optional build (rust/, distribution
scpn-theta-pinch-native); these tests are skipped hermetically when it is
absent and compare float64 bit patterns, never tolerances, when present.
All parameter sets are synthetic fixtures; none describes a real machine.
"""

from __future__ import annotations

import pytest

from physics_fixtures import bits, configuration, inputs
from scpn_theta_pinch_core.physics import (
    DEUTERON_MASS_KG,
    PROTON_MASS_KG,
    SCYLLAC_LINEAR_REFERENCE,
    end_loss_estimate,
    m1_growth_estimate,
    sharp_boundary_state,
    toroidal_equilibrium,
    wall_stabilisation,
)

native = pytest.importorskip("scpn_theta_pinch_native")

GRID = [
    (field, beta, density, mass)
    for field in (0.5, 3.6, 12.0)
    for beta in (0.2, 0.85, 0.99)
    for density in (1.0e21, 2.5e22)
    for mass in (PROTON_MASS_KG, DEUTERON_MASS_KG)
]


@pytest.mark.parametrize(("field", "beta", "density", "mass"), GRID)
def test_state_is_bit_exact(
    field: float, beta: float, density: float, mass: float
) -> None:
    """Beta, temperature, Alfvén speed and end time agree bit for bit."""
    config = configuration(field_t=field, beta=beta)
    floor = sharp_boundary_state(config, mass, density)
    got = native.sharp_boundary_state(
        field,
        config.coil.coil_length_m,
        config.plasma.plasma_pressure_pa,
        mass,
        density,
    )
    expected = (
        floor.beta,
        floor.ion_temperature_ev,
        floor.alfven_speed_m_s,
        floor.end_alfven_time_s,
    )
    assert [bits(v) for v in got] == [bits(v) for v in expected]


@pytest.mark.parametrize("beta", [0.3, 0.7, 0.85])
@pytest.mark.parametrize(("l1", "l0"), [(0.08, 0.08), (0.01, 0.2)])
def test_equilibrium_is_bit_exact(beta: float, l1: float, l0: float) -> None:
    """Every equilibrium quantity agrees bit for bit."""
    floor = toroidal_equilibrium(beta, 0.007, 2.375, 19.0, l1, l0)
    got = native.toroidal_equilibrium(beta, 0.007, 2.375, 19.0, l1, l0)
    expected = (
        floor.excursion_l1,
        floor.excursion_l0,
        floor.excursion_product,
        floor.required_excursion_product,
        floor.balance_ratio,
        floor.required_field_ratio_product,
        floor.auxiliary_field_ratio,
    )
    assert [bits(v) for v in got] == [bits(v) for v in expected]


@pytest.mark.parametrize("coil", [0.08, 0.0075, 0.009])
def test_growth_and_wall_are_bit_exact(coil: float) -> None:
    """Growth terms, rate, disposition and wall condition agree exactly."""
    model = inputs()
    state = sharp_boundary_state(configuration(), DEUTERON_MASS_KG, 2.5e22)
    equilibrium = toroidal_equilibrium(
        state.beta, 0.007, 2.375, 19.0, model.l1_field_ratio, model.l0_field_ratio
    )
    floor = m1_growth_estimate(
        state.beta,
        state.alfven_speed_m_s,
        19.0,
        0.007,
        coil,
        equilibrium.excursion_l1,
        equilibrium.excursion_l0,
        model.l1_field_ratio,
    )
    got = native.m1_growth_estimate(
        state.beta,
        state.alfven_speed_m_s,
        19.0,
        0.007,
        coil,
        equilibrium.excursion_l1,
        equilibrium.excursion_l0,
        model.l1_field_ratio,
    )
    expected = (
        floor.wall_term,
        floor.l1_term,
        floor.l0_term,
        floor.bracket,
        floor.growth_rate_per_s,
        floor.reduced_growth_rate_per_s,
    )
    assert [bits(v) for v in (*got[:5], got[6])] == [bits(v) for v in expected]
    assert got[5] is floor.stable
    wall = wall_stabilisation(state.beta, 19.0, 0.007, coil)
    ratio, required, stabilised = native.wall_stabilisation(
        state.beta, 19.0, 0.007, coil
    )
    assert bits(ratio) == bits(wall.radius_ratio)
    assert bits(required) == bits(wall.required_radius_ratio)
    assert stabilised is wall.stabilised


@pytest.mark.parametrize(
    ("length", "temperature"), [(1.0, 3200.0), (3.0, 1400.0), (7.5, 123.4)]
)
def test_end_loss_is_bit_exact(length: float, temperature: float) -> None:
    """The scaled end-loss time agrees bit for bit."""
    reference = SCYLLAC_LINEAR_REFERENCE
    floor = end_loss_estimate(length, temperature, reference).loss_time_s
    got = native.end_loss_time(
        length,
        temperature,
        reference.coil_length_m,
        reference.ion_temperature_ev,
        reference.loss_time_s,
    )
    assert bits(got) == bits(floor)
