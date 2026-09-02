// SPDX-License-Identifier: AGPL-3.0-or-later
// Commercial license available
// © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
// © Code 2020–2026 Miroslav Šotek. All rights reserved.
// ORCID: 0009-0009-3560-0851
// Contact: www.anulum.li | protoscience@anulum.li
// SCPN Theta-Pinch Core — native level-0 physics kernels

//! Native level-0 device-physics kernels of SCPN Theta-Pinch Core.
//!
//! Every function mirrors one closed-form evaluation of the pure-Python
//! floor in `scpn_theta_pinch_core.physics` with the identical operation
//! order, so the IEEE-754 double results agree bit for bit. The kernels
//! use only `+`, `-`, `*`, `/` and `sqrt` (all correctly rounded); the
//! fourth root of the wall-stabilisation condition is `sqrt(sqrt(x))` on
//! both sides. Nothing here solves an equation and no value describes a
//! real machine; the design record is ADR 0005 of the repository.

pub mod balance;
pub mod end_loss;
pub mod stability;
pub mod toroidal_equilibrium;

/// Vacuum permeability `mu0 = 4e-7 pi`, evaluated as the Python floor does.
pub const MU0: f64 = 4.0e-7 * std::f64::consts::PI;
/// Elementary charge in coulombs (exact SI 2019 value).
pub const ELEMENTARY_CHARGE_C: f64 = 1.602_176_634e-19;

#[cfg(feature = "python")]
mod python {
    use pyo3::prelude::*;

    /// Sharp-boundary state, see `crate::balance::sharp_boundary_state`.
    #[pyfunction]
    fn sharp_boundary_state(
        coil_field_t: f64,
        coil_length_m: f64,
        plasma_pressure_pa: f64,
        ion_mass_kg: f64,
        ion_density_per_m3: f64,
    ) -> (f64, f64, f64, f64) {
        let s = crate::balance::sharp_boundary_state(
            coil_field_t,
            coil_length_m,
            plasma_pressure_pa,
            ion_mass_kg,
            ion_density_per_m3,
        );
        (
            s.beta,
            s.ion_temperature_ev,
            s.alfven_speed_m_s,
            s.end_alfven_time_s,
        )
    }

    /// Toroidal equilibrium tuple, see `crate::toroidal_equilibrium::toroidal_equilibrium`.
    #[pyfunction]
    fn toroidal_equilibrium(
        beta: f64,
        plasma_radius_m: f64,
        major_radius_m: f64,
        helical_wavenumber_per_m: f64,
        l1_field_ratio: f64,
        l0_field_ratio: f64,
    ) -> (f64, f64, f64, f64, f64, f64, f64) {
        let e = crate::toroidal_equilibrium::toroidal_equilibrium(
            beta,
            plasma_radius_m,
            major_radius_m,
            helical_wavenumber_per_m,
            l1_field_ratio,
            l0_field_ratio,
        );
        (
            e.excursion_l1,
            e.excursion_l0,
            e.excursion_product,
            e.required_excursion_product,
            e.balance_ratio,
            e.required_field_ratio_product,
            e.auxiliary_field_ratio,
        )
    }

    /// m = 1 growth estimate, see `crate::stability::m1_growth_estimate`.
    #[pyfunction]
    #[allow(clippy::too_many_arguments)]
    fn m1_growth_estimate(
        beta: f64,
        alfven_speed_m_s: f64,
        helical_wavenumber_per_m: f64,
        plasma_radius_m: f64,
        coil_radius_m: f64,
        excursion_l1: f64,
        excursion_l0: f64,
        l1_field_ratio: f64,
    ) -> (f64, f64, f64, f64, f64, bool, f64) {
        let g = crate::stability::m1_growth_estimate(
            beta,
            alfven_speed_m_s,
            helical_wavenumber_per_m,
            plasma_radius_m,
            coil_radius_m,
            excursion_l1,
            excursion_l0,
            l1_field_ratio,
        );
        (
            g.wall_term,
            g.l1_term,
            g.l0_term,
            g.bracket,
            g.growth_rate_per_s,
            g.stable,
            g.reduced_growth_rate_per_s,
        )
    }

    /// Wall stabilisation, see `crate::stability::wall_stabilisation`.
    #[pyfunction]
    fn wall_stabilisation(
        beta: f64,
        helical_wavenumber_per_m: f64,
        plasma_radius_m: f64,
        coil_radius_m: f64,
    ) -> (f64, f64, bool) {
        let w = crate::stability::wall_stabilisation(
            beta,
            helical_wavenumber_per_m,
            plasma_radius_m,
            coil_radius_m,
        );
        (w.radius_ratio, w.required_radius_ratio, w.stabilised)
    }

    /// Scaled end-loss time, see `crate::end_loss::end_loss_time`.
    #[pyfunction]
    fn end_loss_time(
        coil_length_m: f64,
        ion_temperature_ev: f64,
        reference_length_m: f64,
        reference_temperature_ev: f64,
        reference_loss_time_s: f64,
    ) -> f64 {
        crate::end_loss::end_loss_time(
            coil_length_m,
            ion_temperature_ev,
            reference_length_m,
            reference_temperature_ev,
            reference_loss_time_s,
        )
    }

    /// Python module `scpn_theta_pinch_native`.
    #[pymodule]
    fn scpn_theta_pinch_native(m: &Bound<'_, PyModule>) -> PyResult<()> {
        m.add_function(wrap_pyfunction!(sharp_boundary_state, m)?)?;
        m.add_function(wrap_pyfunction!(toroidal_equilibrium, m)?)?;
        m.add_function(wrap_pyfunction!(m1_growth_estimate, m)?)?;
        m.add_function(wrap_pyfunction!(wall_stabilisation, m)?)?;
        m.add_function(wrap_pyfunction!(end_loss_time, m)?)?;
        Ok(())
    }
}
