# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Theta-Pinch Core — Scyllac toroidal equilibrium

"""Sharp-boundary ``l = 1, 0`` toroidal equilibrium of a theta-pinch sector.

The relations are those reproduced in W. E. Quinn et al., "Review of
Scyllac theta-pinch experiments", LA-UR-73-1053 (1973), p. 2 and eqs.
(3) and (7), after Ribe and Rosenbluth (1970) and Freidberg (1971): the
plasma excursions ``delta_1 = (B_1 / B_0) / (h a (1 - beta/2))`` and
``delta_0 = -(B_0l / B_0) / (2 (1 - beta))`` produced by the ``l = 1``
helical and ``l = 0`` bumpy fields, the equilibrating force
``F_1,0 = beta (3 - 2 beta) B_0^2 h^2 a^3 delta_1 delta_0 / 8`` against the
toroidal drift force ``F_R = beta B_0^2 a^2 / (4 R)``, the equilibrium
condition ``delta_1 delta_0 = -2 / ((3 - 2 beta) h^2 a R)`` (eq. 7) and the
auxiliary fields ``B_v / B_0 = B_1,2 / B_0 = B_1 B_0l / (4 B_0^2)``. Only
dimensionless quantities and the force ratio are reported, so the unit
system of the source's force prefactors never enters. The scanned source
is typographically ambiguous about the excursion definitions; the
quotient forms above are the ones that reproduce Fig. 2 of the source
(see the evidence record), which is the test anchor.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from scpn_theta_pinch_core.parameters import require_positive
from scpn_theta_pinch_core.physics.balance import require_sharp_boundary_beta


@dataclass(frozen=True, slots=True)
class ToroidalEquilibrium:
    """Sharp-boundary toroidal equilibrium quantities (dimensionless).

    Parameters
    ----------
    excursion_l1
        ``delta_1`` for the declared ``l = 1`` field ratio.
    excursion_l0
        ``delta_0`` for the declared ``l = 0`` field ratio (negative).
    excursion_product
        ``delta_1 delta_0`` for the declared ratios.
    required_excursion_product
        ``-2 / ((3 - 2 beta) h^2 a R)`` for equilibrium (eq. 7).
    balance_ratio
        ``delta_1 delta_0`` over its required value; unity at equilibrium.
    required_field_ratio_product
        ``B_1 B_0l / B_0^2`` that satisfies the equilibrium condition.
    auxiliary_field_ratio
        ``B_v / B_0 = B_1,2 / B_0`` of eq. (3) for the declared ratios.
    """

    excursion_l1: float
    excursion_l0: float
    excursion_product: float
    required_excursion_product: float
    balance_ratio: float
    required_field_ratio_product: float
    auxiliary_field_ratio: float

    def to_record(self) -> dict[str, Any]:
        """Project the equilibrium to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            Every field under its name.
        """
        return {
            "excursion_l1": self.excursion_l1,
            "excursion_l0": self.excursion_l0,
            "excursion_product": self.excursion_product,
            "required_excursion_product": self.required_excursion_product,
            "balance_ratio": self.balance_ratio,
            "required_field_ratio_product": self.required_field_ratio_product,
            "auxiliary_field_ratio": self.auxiliary_field_ratio,
        }


def toroidal_equilibrium(
    beta: float,
    plasma_radius_m: float,
    major_radius_m: float,
    helical_wavenumber_per_m: float,
    l1_field_ratio: float,
    l0_field_ratio: float,
) -> ToroidalEquilibrium:
    """Evaluate the sharp-boundary toroidal equilibrium relations.

    Parameters
    ----------
    beta
        Sharp-boundary beta, strictly inside ``(0, 1)``.
    plasma_radius_m
        Plasma radius ``a``; strictly positive.
    major_radius_m
        Major radius ``R`` of the toroidal sector; strictly positive.
    helical_wavenumber_per_m
        ``h = 2 pi / lambda`` of the ``l = 1, 0`` fields; strictly positive.
    l1_field_ratio
        ``B_1 / B_0``; strictly positive.
    l0_field_ratio
        ``B_0l / B_0``; strictly positive.

    Returns
    -------
    ToroidalEquilibrium
        The excursions, the equilibrium products and the force ratio.

    Raises
    ------
    DeviceConfigurationError
        If any input is invalid.
    """
    require_sharp_boundary_beta(beta)
    require_positive("plasma_radius_m", plasma_radius_m)
    require_positive("major_radius_m", major_radius_m)
    require_positive("helical_wavenumber_per_m", helical_wavenumber_per_m)
    require_positive("l1_field_ratio", l1_field_ratio)
    require_positive("l0_field_ratio", l0_field_ratio)
    h_a = helical_wavenumber_per_m * plasma_radius_m
    three_minus = 3.0 - 2.0 * beta
    excursion_l1 = l1_field_ratio / (h_a * (1.0 - beta / 2.0))
    excursion_l0 = 0.0 - l0_field_ratio / (2.0 * (1.0 - beta))
    excursion_product = excursion_l1 * excursion_l0
    required_excursion_product = 0.0 - 2.0 / (
        three_minus
        * (helical_wavenumber_per_m * helical_wavenumber_per_m)
        * plasma_radius_m
        * major_radius_m
    )
    balance_ratio = excursion_product / required_excursion_product
    required_field_ratio_product = 0.0 - 4.0 * (1.0 - beta) * (1.0 - beta / 2.0) / (
        three_minus * helical_wavenumber_per_m * major_radius_m
    )
    auxiliary_field_ratio = l1_field_ratio * l0_field_ratio / 4.0
    return ToroidalEquilibrium(
        excursion_l1=excursion_l1,
        excursion_l0=excursion_l0,
        excursion_product=excursion_product,
        required_excursion_product=required_excursion_product,
        balance_ratio=balance_ratio,
        required_field_ratio_product=required_field_ratio_product,
        auxiliary_field_ratio=auxiliary_field_ratio,
    )
