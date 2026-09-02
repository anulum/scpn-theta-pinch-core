// SPDX-License-Identifier: AGPL-3.0-or-later
// Commercial license available
// © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
// © Code 2020–2026 Miroslav Šotek. All rights reserved.
// ORCID: 0009-0009-3560-0851
// Contact: www.anulum.li | protoscience@anulum.li
// SCPN Theta-Pinch Core — sharp-boundary state kernel

//! Sharp-boundary state (Quinn et al. 1973, p. 14 for the Alfvén end
//! propagation time), operation-for-operation identical to
//! `scpn_theta_pinch_core.physics.balance.sharp_boundary_state`.

use crate::{ELEMENTARY_CHARGE_C, MU0};

/// Sharp-boundary operating state (SI units in the names).
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct SharpBoundaryState {
    /// `p / (B^2 / 2 mu0)`.
    pub beta: f64,
    /// `p / (2 n e)` in electronvolts.
    pub ion_temperature_ev: f64,
    /// `B / sqrt(mu0 n m_i)`.
    pub alfven_speed_m_s: f64,
    /// `(L / 2) / v_A`.
    pub end_alfven_time_s: f64,
}

/// Evaluate the sharp-boundary state.
///
/// Inputs are validated by the Python floor (finite, strictly positive,
/// `0 < beta < 1`); the kernel assumes them.
#[must_use]
pub fn sharp_boundary_state(
    coil_field_t: f64,
    coil_length_m: f64,
    plasma_pressure_pa: f64,
    ion_mass_kg: f64,
    ion_density_per_m3: f64,
) -> SharpBoundaryState {
    let magnetic_pressure_pa = coil_field_t * coil_field_t / (2.0 * MU0);
    let beta = plasma_pressure_pa / magnetic_pressure_pa;
    let ion_temperature_ev = plasma_pressure_pa / (2.0 * ion_density_per_m3 * ELEMENTARY_CHARGE_C);
    let alfven_speed_m_s = coil_field_t / (MU0 * ion_density_per_m3 * ion_mass_kg).sqrt();
    let end_alfven_time_s = (coil_length_m / 2.0) / alfven_speed_m_s;
    SharpBoundaryState {
        beta,
        ion_temperature_ev,
        alfven_speed_m_s,
        end_alfven_time_s,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn beta_and_temperature_close() {
        let b = 3.6;
        let n = 2.5e22;
        let p = 0.85 * b * b / (2.0 * MU0);
        let s = sharp_boundary_state(b, 5.0, p, 3.343_583_772_4e-27, n);
        assert!((s.beta - 0.85).abs() <= 1.0e-15);
        let t_ev = p / (2.0 * n * ELEMENTARY_CHARGE_C);
        assert_eq!(s.ion_temperature_ev, t_ev);
        assert!(s.alfven_speed_m_s > 3.0e5 && s.alfven_speed_m_s < 4.0e5);
        assert!((s.end_alfven_time_s - 2.5 / s.alfven_speed_m_s).abs() <= 1.0e-20);
    }
}
