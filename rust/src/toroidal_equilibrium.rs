// SPDX-License-Identifier: AGPL-3.0-or-later
// Commercial license available
// © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
// © Code 2020–2026 Miroslav Šotek. All rights reserved.
// ORCID: 0009-0009-3560-0851
// Contact: www.anulum.li | protoscience@anulum.li
// SCPN Theta-Pinch Core — Scyllac toroidal equilibrium kernel

//! Sharp-boundary `l = 1, 0` toroidal equilibrium (Quinn et al. 1973, p. 2,
//! eqs. 3 and 7), identical in operation order to
//! `scpn_theta_pinch_core.physics.toroidal_equilibrium.toroidal_equilibrium`.

/// Dimensionless equilibrium quantities.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct ToroidalEquilibrium {
    /// `delta_1`.
    pub excursion_l1: f64,
    /// `delta_0` (negative).
    pub excursion_l0: f64,
    /// `delta_1 delta_0`.
    pub excursion_product: f64,
    /// `-2 / ((3 - 2 beta) h^2 a R)` (eq. 7).
    pub required_excursion_product: f64,
    /// `F_1,0 / F_R`.
    pub balance_ratio: f64,
    /// Required `B_1 B_0l / B_0^2`.
    pub required_field_ratio_product: f64,
    /// `B_1 B_0l / (4 B_0^2)`.
    pub auxiliary_field_ratio: f64,
}

/// Evaluate the equilibrium relations (inputs validated by the floor).
#[must_use]
pub fn toroidal_equilibrium(
    beta: f64,
    plasma_radius_m: f64,
    major_radius_m: f64,
    helical_wavenumber_per_m: f64,
    l1_field_ratio: f64,
    l0_field_ratio: f64,
) -> ToroidalEquilibrium {
    let h_a = helical_wavenumber_per_m * plasma_radius_m;
    let three_minus = 3.0 - 2.0 * beta;
    let excursion_l1 = l1_field_ratio / (h_a * (1.0 - beta / 2.0));
    let excursion_l0 = 0.0 - l0_field_ratio / (2.0 * (1.0 - beta));
    let excursion_product = excursion_l1 * excursion_l0;
    let required_excursion_product = 0.0
        - 2.0
            / (three_minus
                * (helical_wavenumber_per_m * helical_wavenumber_per_m)
                * plasma_radius_m
                * major_radius_m);
    let balance_ratio = excursion_product / required_excursion_product;
    let required_field_ratio_product = 0.0
        - 4.0 * (1.0 - beta) * (1.0 - beta / 2.0)
            / (three_minus * helical_wavenumber_per_m * major_radius_m);
    let auxiliary_field_ratio = l1_field_ratio * l0_field_ratio / 4.0;
    ToroidalEquilibrium {
        excursion_l1,
        excursion_l0,
        excursion_product,
        required_excursion_product,
        balance_ratio,
        required_field_ratio_product,
        auxiliary_field_ratio,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn figure_two_point_is_reproduced_within_ten_percent() {
        let e = toroidal_equilibrium(0.85, 0.007, 2.375, 19.0, 0.08, 0.08);
        assert!((e.required_field_ratio_product - (-0.0064)).abs() / 0.0064 < 0.10);
        assert!(e.excursion_l0 < 0.0);
    }
}
