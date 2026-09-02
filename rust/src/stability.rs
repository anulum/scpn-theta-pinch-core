// SPDX-License-Identifier: AGPL-3.0-or-later
// Commercial license available
// © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
// © Code 2020–2026 Miroslav Šotek. All rights reserved.
// ORCID: 0009-0009-3560-0851
// Contact: www.anulum.li | protoscience@anulum.li
// SCPN Theta-Pinch Core — m = 1 stability kernel

//! Sharp-boundary `m = 1` growth estimate (Quinn et al. 1973, eqs. 4 and
//! 6) and the wall-stabilisation condition derived from eq. (6), identical
//! in operation order to `scpn_theta_pinch_core.physics.stability`.

/// `m = 1` growth-rate estimate.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct M1GrowthEstimate {
    /// Stabilising wall term.
    pub wall_term: f64,
    /// Destabilising `l = 1` term.
    pub l1_term: f64,
    /// Destabilising `l = 0` term.
    pub l0_term: f64,
    /// Sum of the terms.
    pub bracket: f64,
    /// `h v_A sqrt(bracket)` or zero.
    pub growth_rate_per_s: f64,
    /// Whether the bracket is non-positive.
    pub stable: bool,
    /// Eq. (4) estimate.
    pub reduced_growth_rate_per_s: f64,
}

/// Wall-stabilisation condition.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct WallStabilisation {
    /// Declared `a / b`.
    pub radius_ratio: f64,
    /// Required `a / b`.
    pub required_radius_ratio: f64,
    /// Whether the declared ratio reaches the required one.
    pub stabilised: bool,
}

/// Evaluate eq. (6) and the reduced eq. (4) (inputs validated by the floor).
#[must_use]
#[allow(clippy::too_many_arguments)]
pub fn m1_growth_estimate(
    beta: f64,
    alfven_speed_m_s: f64,
    helical_wavenumber_per_m: f64,
    plasma_radius_m: f64,
    coil_radius_m: f64,
    excursion_l1: f64,
    excursion_l0: f64,
    l1_field_ratio: f64,
) -> M1GrowthEstimate {
    let ratio = plasma_radius_m / coil_radius_m;
    let ratio_fourth = (ratio * ratio) * (ratio * ratio);
    let h_a = helical_wavenumber_per_m * plasma_radius_m;
    let delta1_sq = excursion_l1 * excursion_l1;
    let delta0_sq = excursion_l0 * excursion_l0;
    let wall_term = 0.0 - (beta * beta) * ratio_fourth * delta1_sq;
    let l1_term =
        beta * (4.0 - 3.0 * beta) * (2.0 - beta) / (8.0 * (1.0 - beta)) * (h_a * h_a) * delta1_sq;
    let l0_term = beta * (3.0 - 2.0 * beta) * (1.0 - beta) / (2.0 - beta) * delta0_sq;
    let bracket = wall_term + l1_term + l0_term;
    let stable = bracket <= 0.0;
    let growth_rate_per_s = if stable {
        0.0
    } else {
        helical_wavenumber_per_m * alfven_speed_m_s * bracket.sqrt()
    };
    let reduced_growth_rate_per_s =
        (beta * (4.0 - 3.0 * beta) / (2.0 * (1.0 - beta) * (2.0 - beta))).sqrt()
            * alfven_speed_m_s
            * helical_wavenumber_per_m
            * l1_field_ratio;
    M1GrowthEstimate {
        wall_term,
        l1_term,
        l0_term,
        bracket,
        growth_rate_per_s,
        stable,
        reduced_growth_rate_per_s,
    }
}

/// Evaluate the wall-stabilisation condition (inputs validated by the floor).
#[must_use]
pub fn wall_stabilisation(
    beta: f64,
    helical_wavenumber_per_m: f64,
    plasma_radius_m: f64,
    coil_radius_m: f64,
) -> WallStabilisation {
    let h_a = helical_wavenumber_per_m * plasma_radius_m;
    let fourth_power =
        (4.0 - 3.0 * beta) * (2.0 - beta) * (h_a * h_a) / (8.0 * beta * (1.0 - beta));
    let required_radius_ratio = fourth_power.sqrt().sqrt();
    let radius_ratio = plasma_radius_m / coil_radius_m;
    WallStabilisation {
        radius_ratio,
        required_radius_ratio,
        stabilised: radius_ratio >= required_radius_ratio,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn worked_example_gives_point_four() {
        let w = wall_stabilisation(0.8, 0.13 / 0.03, 0.03, 0.1);
        assert!((w.required_radius_ratio - 0.40).abs() <= 0.01);
        assert!(!w.stabilised);
    }

    #[test]
    fn stable_bracket_gives_zero_rate() {
        let g = m1_growth_estimate(0.8, 3.0e5, 4.0, 0.03, 0.05, 1.0, 0.0, 0.01);
        assert!(g.stable);
        assert_eq!(g.growth_rate_per_s, 0.0);
        assert!(g.reduced_growth_rate_per_s > 0.0);
    }
}
