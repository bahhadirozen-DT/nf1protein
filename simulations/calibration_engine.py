"""
Module: simulations/calibration_engine.py
Fast experimental calibration engine
"""

import os
import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as plt


def signaling_decay_model(t, k_decay, alpha_adaptation):
    """
    Simple damped signaling model
    """
    return np.exp(-k_decay * t) * (
        1.0 + alpha_adaptation * np.sin(t)
    )


def run_wetlab_calibration():

    print("=" * 80)
    print("EXPERIMENTAL CALIBRATION ENGINE")
    print("=" * 80)

    # Experimental Western Blot data
    t_experimental = np.array(
        [0.0, 2.0, 4.0, 6.0, 12.0, 24.0, 48.0],
        dtype=float
    )

    perk_relative_density = np.array(
        [1.0, 0.72, 0.45, 0.31, 0.15, 0.08, 0.02],
        dtype=float
    )

    print("[+] Western Blot data loaded")

    # Initial guesses
    initial_guesses = [0.1, 0.1]

    popt, pcov = opt.curve_fit(
        signaling_decay_model,
        t_experimental,
        perk_relative_density,
        p0=initial_guesses,
        maxfev=10000
    )

    best_k_decay = float(popt[0])
    best_alpha = float(popt[1])

    perr = np.sqrt(np.diag(pcov))

    k_decay_err = float(perr[0])
    alpha_err = float(perr[1])

    print("\nCALIBRATION RESULTS")
    print("-" * 60)

    print(
        f"k_decay = {best_k_decay:.6f} ± {k_decay_err:.6f}"
    )

    print(
        f"alpha   = {best_alpha:.6f} ± {alpha_err:.6f}"
    )

    # Create output directory
    os.makedirs("figures", exist_ok=True)

    # Smooth fit curve
    t_fine = np.linspace(0, 48, 500)

    plt.figure(figsize=(8, 5))

    plt.scatter(
        t_experimental,
        perk_relative_density,
        label="Experimental Data"
    )

    plt.plot(
        t_fine,
        signaling_decay_model(
            t_fine,
            best_k_decay,
            best_alpha
        ),
        linewidth=2,
        label="Curve Fit"
    )

    plt.xlabel("Time (hours)")
    plt.ylabel("Relative pERK signal")
    plt.title("Western Blot Calibration")
    plt.grid(True)
    plt.legend()

    graph_path = (
        "figures/western_blot_calibration_fit.png"
    )

    plt.savefig(
        graph_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"\n[+] Figure saved: {graph_path}"
    )

    print("=" * 80)

    return {
        "k_decay": best_k_decay,
        "alpha": best_alpha,
        "k_decay_error": k_decay_err,
        "alpha_error": alpha_err
    }


if __name__ == "__main__":
    run_wetlab_calibration()
