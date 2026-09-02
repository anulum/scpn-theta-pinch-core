# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Theta-Pinch Core — end-loss scaling

"""Empirical end-loss scaling of linear theta pinches.

W. E. Quinn et al., LA-UR-73-1053 (1973), p. 16 and Table I: the observed
end-loss times of Scylla IV-1, Scylla IV-3 and the linear Scyllac scale as
``tau ∝ L / T_i^(1/2)`` with the coil length ``L`` and the ion temperature
``T_i``, normalised to the linear Scyllac point (``L = 5 m``,
``T_i = 2.7 keV``, ``tau = 11.5 μs``). The scaled values printed in
Table I (2.13 μs for Scylla IV-1 at 1 m and 3.2 keV; 9.67 μs for Scylla
IV-3 at 3 m and 1.4 keV) are the test anchors. This is an empirical
scaling of three 1970s experiments, not a confinement model; the source
itself notes that two theoretical models disagreed with the measured loss
rates.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Final

from scpn_theta_pinch_core.parameters import require_positive


@dataclass(frozen=True, slots=True)
class EndLossReference:
    """Normalisation point of the end-loss scaling.

    Parameters
    ----------
    coil_length_m
        Reference coil length ``L_ref``; strictly positive.
    ion_temperature_ev
        Reference ion temperature; strictly positive.
    loss_time_s
        Reference end-loss time; strictly positive.

    Raises
    ------
    DeviceConfigurationError
        If any value is non-finite or not strictly positive.
    """

    coil_length_m: float
    ion_temperature_ev: float
    loss_time_s: float

    def __post_init__(self) -> None:
        """Validate the reference point.

        Raises
        ------
        DeviceConfigurationError
            If any value is non-finite or not strictly positive.
        """
        require_positive("coil_length_m", self.coil_length_m)
        require_positive("ion_temperature_ev", self.ion_temperature_ev)
        require_positive("loss_time_s", self.loss_time_s)

    def to_record(self) -> dict[str, float]:
        """Project the reference to a JSON-serialisable record.

        Returns
        -------
        dict[str, float]
            Every field under its name.
        """
        return {
            "coil_length_m": self.coil_length_m,
            "ion_temperature_ev": self.ion_temperature_ev,
            "loss_time_s": self.loss_time_s,
        }


SCYLLAC_LINEAR_REFERENCE: Final = EndLossReference(
    coil_length_m=5.0, ion_temperature_ev=2700.0, loss_time_s=11.5e-6
)


@dataclass(frozen=True, slots=True)
class EndLossEstimate:
    """Scaled end-loss time.

    Parameters
    ----------
    coil_length_m
        Coil length of the configuration.
    ion_temperature_ev
        Ion temperature of the operating point.
    loss_time_s
        ``tau_ref (L / L_ref) sqrt(T_ref / T_i)``.
    reference
        The normalisation point used.
    """

    coil_length_m: float
    ion_temperature_ev: float
    loss_time_s: float
    reference: EndLossReference

    def to_record(self) -> dict[str, Any]:
        """Project the estimate to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            Every field under its name.
        """
        return {
            "coil_length_m": self.coil_length_m,
            "ion_temperature_ev": self.ion_temperature_ev,
            "loss_time_s": self.loss_time_s,
            "reference": self.reference.to_record(),
        }


def end_loss_estimate(
    coil_length_m: float, ion_temperature_ev: float, reference: EndLossReference
) -> EndLossEstimate:
    """Scale the reference end-loss time to a configuration.

    Parameters
    ----------
    coil_length_m
        Coil length ``L``; strictly positive.
    ion_temperature_ev
        Ion temperature ``T_i``; strictly positive.
    reference
        Normalisation point.

    Returns
    -------
    EndLossEstimate
        The scaled loss time.

    Raises
    ------
    DeviceConfigurationError
        If an input is invalid.
    """
    require_positive("coil_length_m", coil_length_m)
    require_positive("ion_temperature_ev", ion_temperature_ev)
    loss_time_s = (
        reference.loss_time_s
        * (coil_length_m / reference.coil_length_m)
        * math.sqrt(reference.ion_temperature_ev / ion_temperature_ev)
    )
    return EndLossEstimate(
        coil_length_m=coil_length_m,
        ion_temperature_ev=ion_temperature_ev,
        loss_time_s=loss_time_s,
        reference=reference,
    )
