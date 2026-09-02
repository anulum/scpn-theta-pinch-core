# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Theta-Pinch Core — m = 1 stability and wall stabilisation

"""Sharp-boundary ``m = 1`` growth rate and wall stabilisation.

W. E. Quinn et al., LA-UR-73-1053 (1973), eq. (6):
``gamma^2 = h^2 v_A^2 [ -beta^2 (a/b)^4 delta_1^2
+ beta (4 - 3 beta)(2 - beta) / (8 (1 - beta)) h^2 a^2 delta_1^2
+ beta (3 - 2 beta)(1 - beta) / (2 - beta) delta_0^2 ]``,
the first term being the wall-stabilising ``l = 1`` dipole term and the
others the destabilising ``l = 1`` and ``l = 0`` terms; the reduced eq.
(4) ``gamma^2 ~ beta (4 - 3 beta) / (2 (1 - beta)(2 - beta)) v_A^2 h^2
(B_1 / B_0)^2``; and the wall-stabilisation condition obtained from eq.
(6) with the ``l = 0`` term dropped and the wall term made dominant,
``(a/b)^4 >= (4 - 3 beta)(2 - beta) (h a)^2 / (8 beta (1 - beta))``.
The source prints eq. (8) without the ``8 beta`` factor, but its worked
example (``a = 3 cm, beta = 0.8, h a = 0.13`` giving ``a/b = 0.4``) is
reproduced only by the form derived from eq. (6), which is therefore the
implemented one; the example is the test anchor. Growth rates are
estimates of a 1973 sharp-boundary model, not eigenvalue solutions.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from scpn_theta_pinch_core.errors import DeviceConfigurationError
from scpn_theta_pinch_core.parameters import require_positive
from scpn_theta_pinch_core.physics.balance import require_sharp_boundary_beta


@dataclass(frozen=True, slots=True)
class M1GrowthEstimate:
    """Sharp-boundary ``m = 1`` growth-rate estimate.

    Parameters
    ----------
    wall_term
        ``-beta^2 (a/b)^4 delta_1^2`` (stabilising, non-positive).
    l1_term
        ``beta (4 - 3 beta)(2 - beta) / (8 (1 - beta)) h^2 a^2 delta_1^2``.
    l0_term
        ``beta (3 - 2 beta)(1 - beta) / (2 - beta) delta_0^2``.
    bracket
        Sum of the three terms.
    growth_rate_per_s
        ``h v_A sqrt(bracket)`` when the bracket is positive, else zero.
    stable
        Whether the bracket is non-positive.
    reduced_growth_rate_per_s
        Eq. (4) estimate for the declared ``B_1 / B_0``.
    """

    wall_term: float
    l1_term: float
    l0_term: float
    bracket: float
    growth_rate_per_s: float
    stable: bool
    reduced_growth_rate_per_s: float

    def to_record(self) -> dict[str, Any]:
        """Project the estimate to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            Every field under its name.
        """
        return {
            "wall_term": self.wall_term,
            "l1_term": self.l1_term,
            "l0_term": self.l0_term,
            "bracket": self.bracket,
            "growth_rate_per_s": self.growth_rate_per_s,
            "stable": self.stable,
            "reduced_growth_rate_per_s": self.reduced_growth_rate_per_s,
        }


@dataclass(frozen=True, slots=True)
class WallStabilisation:
    """Wall-stabilisation condition of the ``l = 1`` driven ``m = 1`` mode.

    Parameters
    ----------
    radius_ratio
        Declared ``a / b`` (plasma radius over coil radius).
    required_radius_ratio
        ``((4 - 3 beta)(2 - beta) (h a)^2 / (8 beta (1 - beta)))^(1/4)``.
    stabilised
        Whether ``a / b`` reaches the required ratio.
    """

    radius_ratio: float
    required_radius_ratio: float
    stabilised: bool

    def to_record(self) -> dict[str, Any]:
        """Project the condition to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            Every field under its name.
        """
        return {
            "radius_ratio": self.radius_ratio,
            "required_radius_ratio": self.required_radius_ratio,
            "stabilised": self.stabilised,
        }


def _require_radii(plasma_radius_m: float, coil_radius_m: float) -> None:
    """Validate the plasma and coil radii and their ordering.

    Raises
    ------
    DeviceConfigurationError
        If either radius is invalid or the plasma is not inside the coil.
    """
    require_positive("plasma_radius_m", plasma_radius_m)
    require_positive("coil_radius_m", coil_radius_m)
    if plasma_radius_m >= coil_radius_m:
        raise DeviceConfigurationError(
            "plasma_radius_m: must be smaller than coil_radius_m, got "
            f"{plasma_radius_m!r} >= {coil_radius_m!r}"
        )


def m1_growth_estimate(
    beta: float,
    alfven_speed_m_s: float,
    helical_wavenumber_per_m: float,
    plasma_radius_m: float,
    coil_radius_m: float,
    excursion_l1: float,
    excursion_l0: float,
    l1_field_ratio: float,
) -> M1GrowthEstimate:
    """Evaluate eq. (6) and the reduced eq. (4) of Quinn et al. (1973).

    Parameters
    ----------
    beta
        Sharp-boundary beta, strictly inside ``(0, 1)``.
    alfven_speed_m_s
        Alfvén speed ``v_A``; strictly positive.
    helical_wavenumber_per_m
        ``h``; strictly positive.
    plasma_radius_m, coil_radius_m
        ``a`` and ``b`` with ``a < b``.
    excursion_l1, excursion_l0
        ``delta_1`` and ``delta_0`` from the toroidal equilibrium; finite.
    l1_field_ratio
        ``B_1 / B_0`` for the reduced estimate; strictly positive.

    Returns
    -------
    M1GrowthEstimate
        The three terms, the bracket, the growth rate and the disposition.

    Raises
    ------
    DeviceConfigurationError
        If any input is invalid.
    """
    require_sharp_boundary_beta(beta)
    require_positive("alfven_speed_m_s", alfven_speed_m_s)
    require_positive("helical_wavenumber_per_m", helical_wavenumber_per_m)
    _require_radii(plasma_radius_m, coil_radius_m)
    require_positive("l1_field_ratio", l1_field_ratio)
    for name, value in (("excursion_l1", excursion_l1), ("excursion_l0", excursion_l0)):
        if not math.isfinite(value):
            raise DeviceConfigurationError(f"{name}: must be finite, got {value!r}")
    ratio = plasma_radius_m / coil_radius_m
    ratio_fourth = (ratio * ratio) * (ratio * ratio)
    h_a = helical_wavenumber_per_m * plasma_radius_m
    delta1_sq = excursion_l1 * excursion_l1
    delta0_sq = excursion_l0 * excursion_l0
    wall_term = 0.0 - (beta * beta) * ratio_fourth * delta1_sq
    l1_term = (
        beta
        * (4.0 - 3.0 * beta)
        * (2.0 - beta)
        / (8.0 * (1.0 - beta))
        * (h_a * h_a)
        * delta1_sq
    )
    l0_term = beta * (3.0 - 2.0 * beta) * (1.0 - beta) / (2.0 - beta) * delta0_sq
    bracket = wall_term + l1_term + l0_term
    stable = bracket <= 0.0
    growth_rate_per_s = (
        0.0
        if stable
        else helical_wavenumber_per_m * alfven_speed_m_s * math.sqrt(bracket)
    )
    reduced_growth_rate_per_s = (
        math.sqrt(beta * (4.0 - 3.0 * beta) / (2.0 * (1.0 - beta) * (2.0 - beta)))
        * alfven_speed_m_s
        * helical_wavenumber_per_m
        * l1_field_ratio
    )
    return M1GrowthEstimate(
        wall_term=wall_term,
        l1_term=l1_term,
        l0_term=l0_term,
        bracket=bracket,
        growth_rate_per_s=growth_rate_per_s,
        stable=stable,
        reduced_growth_rate_per_s=reduced_growth_rate_per_s,
    )


def wall_stabilisation(
    beta: float,
    helical_wavenumber_per_m: float,
    plasma_radius_m: float,
    coil_radius_m: float,
) -> WallStabilisation:
    """Evaluate the wall-stabilisation condition derived from eq. (6).

    Parameters
    ----------
    beta
        Sharp-boundary beta, strictly inside ``(0, 1)``.
    helical_wavenumber_per_m
        ``h``; strictly positive.
    plasma_radius_m, coil_radius_m
        ``a`` and ``b`` with ``a < b``.

    Returns
    -------
    WallStabilisation
        The declared and required radius ratios and the disposition.

    Raises
    ------
    DeviceConfigurationError
        If any input is invalid.
    """
    require_sharp_boundary_beta(beta)
    require_positive("helical_wavenumber_per_m", helical_wavenumber_per_m)
    _require_radii(plasma_radius_m, coil_radius_m)
    h_a = helical_wavenumber_per_m * plasma_radius_m
    fourth_power = (
        (4.0 - 3.0 * beta) * (2.0 - beta) * (h_a * h_a) / (8.0 * beta * (1.0 - beta))
    )
    required_radius_ratio = math.sqrt(math.sqrt(fourth_power))
    radius_ratio = plasma_radius_m / coil_radius_m
    return WallStabilisation(
        radius_ratio=radius_ratio,
        required_radius_ratio=required_radius_ratio,
        stabilised=radius_ratio >= required_radius_ratio,
    )
