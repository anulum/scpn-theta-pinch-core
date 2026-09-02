# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Theta-Pinch Core — sharp-boundary state

"""Sharp-boundary operating state of a theta-pinch column.

The declared plasma pressure and compression field of the validated
configuration fix the sharp-boundary beta ``beta = p / (B^2 / 2 mu0)``;
with a declared ion density and ion mass they fix the equal-species ion
temperature ``T = p / (2 n e)``, the Alfvén speed
``v_A = B / sqrt(mu0 n m_i)`` and the end-to-centre Alfvén propagation
time ``tau_A = (L / 2) / v_A`` that the Scyllac review uses to order the
onset of end effects (W. E. Quinn et al., LA-UR-73-1053 (1973), p. 14:
"the time for propagation of an Alfvén wave from the ends of the coil").
Every sharp-boundary relation of this package needs ``0 < beta < 1``;
``beta = 1`` (allowed by the configuration invariant) is refused here,
never clamped.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Final

from scpn_theta_pinch_core.configuration import DeviceConfiguration
from scpn_theta_pinch_core.errors import DeviceConfigurationError
from scpn_theta_pinch_core.parameters import MU0, require_positive

ELEMENTARY_CHARGE_C: Final = 1.602176634e-19
PROTON_MASS_KG: Final = 1.67262192369e-27
DEUTERON_MASS_KG: Final = 3.3435837724e-27


def require_sharp_boundary_beta(beta: float) -> float:
    """Return ``beta`` when strictly inside the sharp-boundary domain.

    Parameters
    ----------
    beta
        Sharp-boundary beta of the operating point.

    Returns
    -------
    float
        The validated beta.

    Raises
    ------
    DeviceConfigurationError
        If ``beta`` is not strictly between zero and one; the relations
        of Quinn et al. (1973) carry ``1 - beta`` denominators.
    """
    if not 0.0 < beta < 1.0:
        raise DeviceConfigurationError(
            f"beta: sharp-boundary relations require 0 < beta < 1, got {beta!r}"
        )
    return beta


@dataclass(frozen=True, slots=True)
class SharpBoundaryState:
    """Operating state derived from the configuration and declared inputs.

    Parameters
    ----------
    beta
        ``p / (B^2 / 2 mu0)``.
    field_t
        Compression field ``B`` in tesla.
    plasma_pressure_pa
        Declared plasma pressure.
    ion_density_per_m3
        Declared ion density ``n``.
    ion_temperature_ev
        ``T = p / (2 n e)`` for equal species.
    alfven_speed_m_s
        ``B / sqrt(mu0 n m_i)``.
    end_alfven_time_s
        ``(L / 2) / v_A`` for the coil length ``L``.
    """

    beta: float
    field_t: float
    plasma_pressure_pa: float
    ion_density_per_m3: float
    ion_temperature_ev: float
    alfven_speed_m_s: float
    end_alfven_time_s: float

    def to_record(self) -> dict[str, Any]:
        """Project the state to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            Every field under its name.
        """
        return {
            "beta": self.beta,
            "field_t": self.field_t,
            "plasma_pressure_pa": self.plasma_pressure_pa,
            "ion_density_per_m3": self.ion_density_per_m3,
            "ion_temperature_ev": self.ion_temperature_ev,
            "alfven_speed_m_s": self.alfven_speed_m_s,
            "end_alfven_time_s": self.end_alfven_time_s,
        }


def sharp_boundary_state(
    configuration: DeviceConfiguration, ion_mass_kg: float, ion_density_per_m3: float
) -> SharpBoundaryState:
    """Evaluate the sharp-boundary state of a validated configuration.

    Parameters
    ----------
    configuration
        Validated theta-pinch configuration.
    ion_mass_kg
        Ion mass; strictly positive.
    ion_density_per_m3
        Declared ion density; strictly positive.

    Returns
    -------
    SharpBoundaryState
        Beta, ion temperature, Alfvén speed and end propagation time.

    Raises
    ------
    DeviceConfigurationError
        If an input is invalid or beta lies outside ``(0, 1)``.
    """
    require_positive("ion_mass_kg", ion_mass_kg)
    require_positive("ion_density_per_m3", ion_density_per_m3)
    beta = require_sharp_boundary_beta(configuration.beta())
    field_t = configuration.coil.coil_field_t
    pressure = configuration.plasma.plasma_pressure_pa
    ion_temperature_ev = pressure / (2.0 * ion_density_per_m3 * ELEMENTARY_CHARGE_C)
    alfven_speed_m_s = field_t / math.sqrt(MU0 * ion_density_per_m3 * ion_mass_kg)
    end_alfven_time_s = (configuration.coil.coil_length_m / 2.0) / alfven_speed_m_s
    return SharpBoundaryState(
        beta=beta,
        field_t=field_t,
        plasma_pressure_pa=pressure,
        ion_density_per_m3=ion_density_per_m3,
        ion_temperature_ev=ion_temperature_ev,
        alfven_speed_m_s=alfven_speed_m_s,
        end_alfven_time_s=end_alfven_time_s,
    )
