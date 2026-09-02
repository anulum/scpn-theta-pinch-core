# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Theta-Pinch Core — level-0 physics record

"""Level-0 physics record of one validated device configuration.

The record composes the published sharp-boundary relations of the Scyllac
review (W. E. Quinn et al., LA-UR-73-1053, 1973) on the validated
:class:`~scpn_theta_pinch_core.configuration.DeviceConfiguration` together
with the declared model inputs the configuration does not carry (ion mass
and density, plasma radius, major radius and helical wavenumber of the
toroidal sector, the ``l = 1`` and ``l = 0`` field ratios, and the end-loss
normalisation point). It serialises canonically with a SHA-256 digest and
states its own non-claims: every number is a closed-form evaluation of a
1973 sharp-boundary model on a synthetic configuration, at
``computational_prototype`` maturity.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_theta_pinch_core.configuration import DeviceConfiguration
from scpn_theta_pinch_core.errors import DeviceConfigurationError
from scpn_theta_pinch_core.parameters import require_positive
from scpn_theta_pinch_core.physics.balance import (
    SharpBoundaryState,
    sharp_boundary_state,
)
from scpn_theta_pinch_core.physics.end_loss import (
    EndLossEstimate,
    EndLossReference,
    end_loss_estimate,
)
from scpn_theta_pinch_core.physics.stability import (
    M1GrowthEstimate,
    WallStabilisation,
    m1_growth_estimate,
    wall_stabilisation,
)
from scpn_theta_pinch_core.physics.toroidal_equilibrium import (
    ToroidalEquilibrium,
    toroidal_equilibrium,
)

LEVEL0_SCHEMA: Final = "scpn.theta-pinch-level0-physics.v1"
LEVEL0_SCHEMA_VERSION: Final = "1.0.0"
LEVEL0_NON_CLAIMS: Final = (
    "closed-form evaluation of the sharp-boundary relations of a 1973 review "
    "on a synthetic configuration",
    "no equilibrium, stability, compression or transport equation is solved",
    "no yield, gain, reactivity, confinement or breakeven statement",
    "no value describes or validates any real machine; the anchors reproduce "
    "numbers printed in the source",
)


@dataclass(frozen=True, slots=True)
class ModelInputs:
    """Declared inputs of the level-0 models beyond the configuration.

    Parameters
    ----------
    ion_mass_kg
        Ion mass; strictly positive.
    ion_density_per_m3
        Declared ion density; strictly positive.
    plasma_radius_m
        Plasma radius ``a``; strictly positive and smaller than the coil
        radius (checked when the record is built).
    major_radius_m
        Major radius ``R`` of the toroidal sector; strictly positive.
    helical_wavenumber_per_m
        ``h`` of the ``l = 1, 0`` fields; strictly positive.
    l1_field_ratio
        ``B_1 / B_0``; strictly positive.
    l0_field_ratio
        ``B_0l / B_0``; strictly positive.
    end_loss_reference
        Normalisation point of the end-loss scaling.

    Raises
    ------
    DeviceConfigurationError
        If any input is non-finite or not strictly positive.
    """

    ion_mass_kg: float
    ion_density_per_m3: float
    plasma_radius_m: float
    major_radius_m: float
    helical_wavenumber_per_m: float
    l1_field_ratio: float
    l0_field_ratio: float
    end_loss_reference: EndLossReference

    def __post_init__(self) -> None:
        """Validate every declared input.

        Raises
        ------
        DeviceConfigurationError
            If any input is non-finite or not strictly positive.
        """
        require_positive("ion_mass_kg", self.ion_mass_kg)
        require_positive("ion_density_per_m3", self.ion_density_per_m3)
        require_positive("plasma_radius_m", self.plasma_radius_m)
        require_positive("major_radius_m", self.major_radius_m)
        require_positive("helical_wavenumber_per_m", self.helical_wavenumber_per_m)
        require_positive("l1_field_ratio", self.l1_field_ratio)
        require_positive("l0_field_ratio", self.l0_field_ratio)

    def to_record(self) -> dict[str, Any]:
        """Project the inputs to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            Every field under its name.
        """
        return {
            "ion_mass_kg": self.ion_mass_kg,
            "ion_density_per_m3": self.ion_density_per_m3,
            "plasma_radius_m": self.plasma_radius_m,
            "major_radius_m": self.major_radius_m,
            "helical_wavenumber_per_m": self.helical_wavenumber_per_m,
            "l1_field_ratio": self.l1_field_ratio,
            "l0_field_ratio": self.l0_field_ratio,
            "end_loss_reference": self.end_loss_reference.to_record(),
        }


@dataclass(frozen=True, slots=True)
class Level0PhysicsRecord:
    """The level-0 models evaluated on one configuration.

    Parameters
    ----------
    configuration_digest_sha256
        Digest of the validated configuration the record was built from.
    inputs
        Declared model inputs.
    state
        Sharp-boundary state.
    equilibrium
        Scyllac toroidal equilibrium relations.
    growth
        ``m = 1`` growth-rate estimate.
    wall
        Wall-stabilisation condition.
    end_loss
        Scaled end-loss time.
    """

    configuration_digest_sha256: str
    inputs: ModelInputs
    state: SharpBoundaryState
    equilibrium: ToroidalEquilibrium
    growth: M1GrowthEstimate
    wall: WallStabilisation
    end_loss: EndLossEstimate

    def to_record(self) -> dict[str, Any]:
        """Project the record to a JSON-serialisable object.

        Returns
        -------
        dict[str, Any]
            Schema identity, non-claims, and every model record.
        """
        return {
            "schema": LEVEL0_SCHEMA,
            "schema_version": LEVEL0_SCHEMA_VERSION,
            "non_claims": list(LEVEL0_NON_CLAIMS),
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "inputs": self.inputs.to_record(),
            "state": self.state.to_record(),
            "equilibrium": self.equilibrium.to_record(),
            "growth": self.growth.to_record(),
            "wall": self.wall.to_record(),
            "end_loss": self.end_loss.to_record(),
        }

    def canonical_bytes(self) -> bytes:
        """Serialise the record canonically.

        Returns
        -------
        bytes
            UTF-8 JSON with sorted keys, minimal separators, and a
            trailing newline; NaN and infinity are never emitted.
        """
        text = json.dumps(
            self.to_record(), sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        return (text + "\n").encode("utf-8")

    def digest_sha256(self) -> str:
        """Identify the exact record.

        Returns
        -------
        str
            SHA-256 digest of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def level0_physics(
    configuration: DeviceConfiguration, inputs: ModelInputs
) -> Level0PhysicsRecord:
    """Evaluate every level-0 model on a validated configuration.

    Parameters
    ----------
    configuration
        Validated device configuration.
    inputs
        Declared model inputs.

    Returns
    -------
    Level0PhysicsRecord
        The composed record.

    Raises
    ------
    DeviceConfigurationError
        If beta lies outside ``(0, 1)`` or the plasma radius is not
        smaller than the coil radius.
    """
    if inputs.plasma_radius_m >= configuration.coil.coil_radius_m:
        raise DeviceConfigurationError(
            "plasma_radius_m: must be smaller than coil_radius_m, got "
            f"{inputs.plasma_radius_m!r} >= {configuration.coil.coil_radius_m!r}"
        )
    state = sharp_boundary_state(
        configuration, inputs.ion_mass_kg, inputs.ion_density_per_m3
    )
    equilibrium = toroidal_equilibrium(
        state.beta,
        inputs.plasma_radius_m,
        inputs.major_radius_m,
        inputs.helical_wavenumber_per_m,
        inputs.l1_field_ratio,
        inputs.l0_field_ratio,
    )
    growth = m1_growth_estimate(
        state.beta,
        state.alfven_speed_m_s,
        inputs.helical_wavenumber_per_m,
        inputs.plasma_radius_m,
        configuration.coil.coil_radius_m,
        equilibrium.excursion_l1,
        equilibrium.excursion_l0,
        inputs.l1_field_ratio,
    )
    wall = wall_stabilisation(
        state.beta,
        inputs.helical_wavenumber_per_m,
        inputs.plasma_radius_m,
        configuration.coil.coil_radius_m,
    )
    end_loss = end_loss_estimate(
        configuration.coil.coil_length_m,
        state.ion_temperature_ev,
        inputs.end_loss_reference,
    )
    return Level0PhysicsRecord(
        configuration_digest_sha256=configuration.digest_sha256(),
        inputs=inputs,
        state=state,
        equilibrium=equilibrium,
        growth=growth,
        wall=wall,
        end_loss=end_loss,
    )
