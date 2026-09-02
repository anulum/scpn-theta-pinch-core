// SPDX-License-Identifier: AGPL-3.0-or-later
// Commercial license available
// © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
// © Code 2020–2026 Miroslav Šotek. All rights reserved.
// ORCID: 0009-0009-3560-0851
// Contact: www.anulum.li | protoscience@anulum.li
// SCPN Theta-Pinch Core — end-loss scaling kernel

//! Empirical end-loss scaling `tau ∝ L / T_i^(1/2)` (Quinn et al. 1973,
//! Table I), identical in operation order to
//! `scpn_theta_pinch_core.physics.end_loss.end_loss_estimate`.

/// Scale the reference end-loss time (inputs validated by the floor).
#[must_use]
pub fn end_loss_time(
    coil_length_m: f64,
    ion_temperature_ev: f64,
    reference_length_m: f64,
    reference_temperature_ev: f64,
    reference_loss_time_s: f64,
) -> f64 {
    reference_loss_time_s
        * (coil_length_m / reference_length_m)
        * (reference_temperature_ev / ion_temperature_ev).sqrt()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn table_one_rows_within_one_percent() {
        let iv1 = end_loss_time(1.0, 3200.0, 5.0, 2700.0, 11.5e-6);
        assert!((iv1 - 2.13e-6).abs() / 2.13e-6 < 0.01);
        let iv3 = end_loss_time(3.0, 1400.0, 5.0, 2700.0, 11.5e-6);
        assert!((iv3 - 9.67e-6).abs() / 9.67e-6 < 0.01);
    }
}
