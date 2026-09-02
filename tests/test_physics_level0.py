# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Theta-Pinch Core — level-0 record tests

"""Composition, identity, wiring and refusals of the level-0 record."""

from __future__ import annotations

import dataclasses
import hashlib
import json
from typing import Any

import pytest

from physics_fixtures import configuration, inputs
from scpn_theta_pinch_core import (
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    Level0PhysicsRecord,
    ModelInputs,
    level0_physics,
)
from scpn_theta_pinch_core.errors import DeviceConfigurationError


def test_record_composes_every_model_and_is_canonical() -> None:
    """The record carries the configuration digest and every model record."""
    config = configuration()
    record = level0_physics(config, inputs())
    assert isinstance(record, Level0PhysicsRecord)
    projected = record.to_record()
    assert projected["schema"] == LEVEL0_SCHEMA
    assert projected["schema_version"] == LEVEL0_SCHEMA_VERSION
    assert projected["non_claims"] == list(LEVEL0_NON_CLAIMS)
    assert projected["configuration_digest_sha256"] == config.digest_sha256()
    assert set(projected) == {
        "schema",
        "schema_version",
        "non_claims",
        "configuration_digest_sha256",
        "inputs",
        "state",
        "equilibrium",
        "growth",
        "wall",
        "end_loss",
    }
    data = record.canonical_bytes()
    assert data.endswith(b"\n")
    assert json.loads(data) == projected
    assert record.digest_sha256() == hashlib.sha256(data).hexdigest()
    assert level0_physics(config, inputs()).digest_sha256() == record.digest_sha256()


def test_models_are_consistent_with_each_other() -> None:
    """The growth estimate uses the equilibrium excursions and the state's v_A."""
    record = level0_physics(configuration(), inputs())
    assert record.growth.growth_rate_per_s > 0.0
    assert record.end_loss.ion_temperature_ev == record.state.ion_temperature_ev
    assert record.end_loss.coil_length_m == 5.0
    assert record.wall.radius_ratio == 0.007 / 0.08


def test_inputs_record_and_validation() -> None:
    """Every declared input is projected and validated."""
    model = inputs()
    record = model.to_record()
    assert record["end_loss_reference"]["coil_length_m"] == 5.0
    assert set(record) == {
        "ion_mass_kg",
        "ion_density_per_m3",
        "plasma_radius_m",
        "major_radius_m",
        "helical_wavenumber_per_m",
        "l1_field_ratio",
        "l0_field_ratio",
        "end_loss_reference",
    }
    for field in (
        "ion_mass_kg",
        "ion_density_per_m3",
        "plasma_radius_m",
        "major_radius_m",
        "helical_wavenumber_per_m",
        "l1_field_ratio",
        "l0_field_ratio",
    ):
        overrides: dict[str, Any] = {field: 0.0}
        with pytest.raises(DeviceConfigurationError, match=field):
            dataclasses.replace(model, **overrides)
    assert isinstance(model, ModelInputs)


def test_plasma_must_fit_inside_the_coil() -> None:
    """A plasma radius at or above the coil radius is refused."""
    with pytest.raises(DeviceConfigurationError, match="smaller than coil_radius_m"):
        level0_physics(configuration(coil_radius_m=0.007), inputs())


def test_unity_beta_is_refused_by_the_record() -> None:
    """A beta = 1 configuration has no sharp-boundary record."""
    with pytest.raises(DeviceConfigurationError, match="0 < beta < 1"):
        level0_physics(configuration(beta=1.0), inputs())
