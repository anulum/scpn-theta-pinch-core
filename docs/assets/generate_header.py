# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN Theta Pinch Core — repository header artwork generator

"""Generate the three README header images (1280x640) for this repository.

Every image is original generated artwork derived from this repository's
own domain surface — the single-turn compression coil with its axial
field and induced azimuthal current, the beta pressure-balance gate,
and the radial implosion sequence. The right-hand text panel states
only facts backed by the repository itself.

Outputs (written next to this script):

- ``repo_header.png`` — the compression coil with axial field, induced
  azimuthal current and radial compression (used by ``README.md``).
- ``repo_header_beta_gate.png`` — the beta saturation curve with the
  hard wall and the low-beta flag region.
- ``repo_header_implosion.png`` — the end-view implosion sequence.

Generation-time tooling only: requires ``numpy`` and ``matplotlib``,
which are deliberately not part of the pinned development lock. Run as
``python3 docs/assets/generate_header.py`` from the repository root.
The output is deterministic (fixed geometry, no random input).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

OUT_DIR = Path(__file__).resolve().parent

BG = "#00050a"
CYAN = "#00ccff"
MAGENTA = "#ff00ff"
STEEL = "#334466"
PROBE = "#66aaff"
RED = "#ff3366"
GREEN = "#3ddc84"

WIDTH_IN, HEIGHT_IN, DPI = 12.8, 6.4, 100

TITLE_METRICS: list[tuple[str, str]] = [
    ("Device Configuration", "theta_pinch · azimuthal-current pinch"),
    ("Hard Invariant", "radial pressure balance · beta <= 1"),
    ("High-Beta Regime", "low beta flagged (Ribe, RMP 47, 1975)"),
    ("Diagnostics & Clocks", "fail-closed vs pinned SPO catalogue"),
    ("Plan Envelope", "v1.1.0 · synthetic · review-only"),
    ("Quality Gates", "100% branch cov · mypy --strict"),
]


def _pyplot() -> Any:
    """Return pyplot configured for headless Agg rendering."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def _glow_cmap() -> Any:
    """Build the family glow colormap (deep navy to cyan)."""
    from matplotlib.colors import LinearSegmentedColormap

    return LinearSegmentedColormap.from_list(
        "scpn_glow",
        ["#00050a", "#001428", "#002d55", "#005588", "#0088bb", "#00ccff"],
    )


def _text_panel(fig: Any, subtitle: str) -> None:
    """Draw the family right-hand text panel onto ``fig``."""
    ax = fig.add_axes([0.62, 0.0, 0.38, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(
        0.08,
        0.84,
        "SCPN",
        color="white",
        fontsize=36,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.745,
        "THETA-PINCH",
        color="white",
        fontsize=27,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.695,
        "CORE",
        color="white",
        fontsize=27,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.635,
        subtitle,
        color=CYAN,
        fontsize=11,
        fontfamily="monospace",
        alpha=0.85,
    )
    ax.plot([0.08, 0.85], [0.595, 0.595], color=STEEL, lw=0.8, alpha=0.5)
    y = 0.535
    for label, value in TITLE_METRICS:
        ax.text(
            0.08,
            y,
            f"▸ {label}",
            color="#6688aa",
            fontsize=9,
            fontfamily="monospace",
            alpha=0.9,
        )
        ax.text(
            0.10,
            y - 0.030,
            value,
            color="#99bbdd",
            fontsize=8,
            fontfamily="monospace",
            alpha=0.7,
        )
        y -= 0.072
    ax.text(
        0.08,
        0.06,
        "© 1996–2026 Miroslav Šotek",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.6,
    )
    ax.text(
        0.08,
        0.03,
        "anulum.li | AGPL-3.0",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.5,
    )


def _art_axes(fig: Any) -> Any:
    """Return the borderless left-hand art axes of ``fig``."""
    ax = fig.add_axes([0.0, 0.0, 0.68, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    return ax


def _save(fig: Any, plt: Any, name: str) -> None:
    """Save ``fig`` to ``name`` inside the assets directory and close it."""
    target = OUT_DIR / name
    fig.savefig(target, dpi=DPI, facecolor=BG, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    print(f"generated {target}")


def horizontal_column(
    ax: Any,
    y_centre: float,
    half_height: float,
    x_start: float,
    x_end: float,
) -> None:
    """Draw a horizontal glowing plasma column."""
    grid_x = np.linspace(x_start, x_end, 200)
    grid_y = np.linspace(
        y_centre - 3.0 * half_height, y_centre + 3.0 * half_height, 120
    )
    mesh_x, mesh_y = np.meshgrid(grid_x, grid_y)
    rho = np.abs(mesh_y - y_centre) / half_height
    ax.contourf(
        mesh_x,
        mesh_y,
        np.exp(-rho * 1.8),
        levels=30,
        cmap=_glow_cmap(),
        alpha=0.85,
    )


def generate_compression_coil() -> None:
    """Generate ``repo_header.png``: the compression-coil device view."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(-2.6, 2.6)

    for rail_y, mark in ((2.0, "x"), (-2.0, "o")):
        ax.plot([0.8, 9.2], [rail_y, rail_y], color=STEEL, lw=4.0, alpha=0.85)
        for coil_x in np.linspace(1.1, 8.9, 12):
            ax.plot(
                [coil_x],
                [rail_y],
                mark,
                color=MAGENTA,
                ms=6,
                mew=1.6,
                alpha=0.85,
            )
    ax.text(
        5.0,
        2.24,
        "single-turn compression coil · I_θ",
        color=MAGENTA,
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )

    horizontal_column(ax, 0.0, 0.55, 1.1, 8.9)

    for arrow_x in (2.2, 4.1, 6.0, 7.9):
        ax.annotate(
            "",
            xy=(arrow_x + 1.0, 0.0),
            xytext=(arrow_x, 0.0),
            arrowprops={"arrowstyle": "->", "color": CYAN, "lw": 1.5, "alpha": 0.85},
        )
    ax.text(
        5.0,
        0.32,
        "B_z",
        color=CYAN,
        fontsize=9,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )

    theta = np.linspace(0.0, 2.0 * np.pi, 200)
    for ring_x in (2.6, 5.0, 7.4):
        ax.plot(
            ring_x + 0.20 * np.sin(theta),
            0.85 * np.cos(theta),
            color="white",
            lw=1.1,
            alpha=0.6,
        )
    ax.text(
        7.95,
        -0.95,
        "J_θ (induced)",
        color="white",
        fontsize=8,
        fontfamily="monospace",
        alpha=0.75,
    )

    for arrow_x in (3.2, 5.0, 6.8):
        for sign in (+1, -1):
            ax.annotate(
                "",
                xy=(arrow_x, sign * 0.75),
                xytext=(arrow_x, sign * 1.55),
                arrowprops={
                    "arrowstyle": "->",
                    "color": PROBE,
                    "lw": 1.3,
                    "alpha": 0.8,
                },
            )
    ax.text(
        2.55,
        1.15,
        "radial compression",
        color=PROBE,
        fontsize=8,
        fontfamily="monospace",
        ha="right",
        alpha=0.9,
    )

    ax.text(
        5.0,
        -2.35,
        "azimuthal current, axial field · the dual of the axial pinch",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "Azimuthal Current, Axial Field")
    _save(fig, plt, "repo_header.png")


def generate_beta_gate() -> None:
    """Generate ``repo_header_beta_gate.png``: the pressure balance."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    ax.plot([1.0, 9.2], [1.7, 1.7], color=STEEL, lw=1.0, alpha=0.7)
    ax.plot([1.0, 1.0], [1.7, 9.1], color=STEEL, lw=1.0, alpha=0.7)
    ax.text(
        8.85,
        1.25,
        "plasma pressure p",
        color="#8899bb",
        fontsize=9.5,
        fontfamily="monospace",
        ha="right",
    )
    ax.text(
        1.15,
        8.85,
        "β = 2μ0·p / B²",
        color="#8899bb",
        fontsize=9.5,
        fontfamily="monospace",
    )

    pressure = np.linspace(0.0, 1.0, 300)
    beta = pressure / (0.18 + pressure * 0.82)
    px = 1.0 + 8.0 * pressure
    py = 1.7 + 6.6 * beta
    ax.plot(px, py, color=CYAN, lw=2.6, alpha=0.95)
    ax.fill_between(px, py, 1.7, color=CYAN, alpha=0.05)

    y_wall = 1.7 + 6.6
    ax.plot([1.0, 9.0], [y_wall, y_wall], color=RED, lw=2.0, alpha=0.9)
    ax.text(
        8.9,
        y_wall + 0.25,
        "β = 1 · HARD",
        color=RED,
        fontsize=8.5,
        fontfamily="monospace",
        ha="right",
        alpha=0.95,
    )

    y_band = 1.7 + 6.6 * 0.7
    ax.fill_between([1.0, 9.0], y_band, y_wall, color=GREEN, alpha=0.07)
    ax.text(
        1.3,
        (y_band + y_wall) / 2,
        "characteristic high-beta regime",
        color=GREEN,
        fontsize=8,
        fontfamily="monospace",
        va="center",
        alpha=0.9,
    )
    ax.fill_between([1.0, 9.0], 1.7, 1.7 + 6.6 * 0.35, color=RED, alpha=0.05)
    ax.text(
        7.6,
        1.7 + 6.6 * 0.18,
        "low beta · flagged",
        color="#ff8899",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )

    ax.text(
        5.0,
        0.75,
        "radial pressure balance checked · Ribe, Rev. Mod. Phys. 47 (1975) 7",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "High Beta By Construction, Checked")
    _save(fig, plt, "repo_header_beta_gate.png")


def generate_implosion() -> None:
    """Generate ``repo_header_implosion.png``: the implosion sequence."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(-3.2, 3.2)

    frames = [
        (1.9, 1.15, 0.30, "fill plasma"),
        (5.0, 0.72, 0.55, "compression"),
        (7.85, 0.38, 0.95, "peak density"),
    ]
    theta = np.linspace(0.0, 2.0 * np.pi, 200)
    for centre_x, radius, gain, label in frames:
        grid_x = np.linspace(centre_x - 1.55, centre_x + 1.55, 110)
        grid_y = np.linspace(-1.7, 1.7, 110)
        mesh_x, mesh_y = np.meshgrid(grid_x, grid_y)
        rho = np.sqrt((mesh_x - centre_x) ** 2 + mesh_y**2) / radius
        ax.contourf(
            mesh_x,
            mesh_y,
            np.exp(-rho * 1.9) * (0.4 + gain),
            levels=24,
            cmap=_glow_cmap(),
            alpha=0.85,
        )
        ax.plot(
            centre_x + radius * np.cos(theta),
            radius * np.sin(theta),
            color=CYAN,
            lw=1.7,
            alpha=0.9,
        )
        ax.plot(
            centre_x + 1.32 * np.cos(theta),
            1.32 * np.sin(theta),
            color=STEEL,
            lw=1.8,
            alpha=0.7,
        )
        ax.text(
            centre_x,
            -2.05,
            label,
            color="#99bbdd",
            fontsize=8,
            fontfamily="monospace",
            ha="center",
            alpha=0.9,
        )
        if label == "compression":
            for angle in np.linspace(0, 2 * np.pi, 8, endpoint=False):
                outer = (centre_x + 1.3 * np.cos(angle), 1.3 * np.sin(angle))
                inner = (centre_x + 0.85 * np.cos(angle), 0.85 * np.sin(angle))
                ax.annotate(
                    "",
                    xy=inner,
                    xytext=outer,
                    arrowprops={
                        "arrowstyle": "->",
                        "color": PROBE,
                        "lw": 1.1,
                        "alpha": 0.8,
                    },
                )

    ax.annotate(
        "",
        xy=(6.35, 2.5),
        xytext=(3.6, 2.5),
        arrowprops={"arrowstyle": "->", "color": STEEL, "lw": 1.2, "alpha": 0.7},
    )
    ax.text(
        5.0,
        2.72,
        "time",
        color="#667799",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )

    ax.text(
        5.0,
        -2.85,
        "fast azimuthal-current implosion · end view of the compression coil",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "The Implosion, Frame By Frame")
    _save(fig, plt, "repo_header_implosion.png")


if __name__ == "__main__":
    generate_compression_coil()
    generate_beta_gate()
    generate_implosion()
