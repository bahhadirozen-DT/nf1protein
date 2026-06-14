"""
FAST JACOBIAN ANALYSIS
Lightweight symbolic stability engine
"""

import os
import sympy as sp


def derive_symbolic_jacobian():

    if not os.path.exists("figures"):
        os.makedirs("figures")

    # State variables
    K, P, R, M = sp.symbols("KRAS pERK ROS M")

    # Parameters
    Th, n, tau = sp.symbols("Theta_high n tau_m")
    k_prod, k_deg, Km = sp.symbols("k_prod k_deg K_m")
    k_act, k_fb, k_ROS, k_clear = sp.symbols(
        "k_act k_fb k_ROS k_clear"
    )

    # Sigmoid regime transitions
    suppression_high_weight = 1 / (
        1 + sp.exp(-25 * (M - 0.82))
    )

    suppression_low_weight = 1 / (
        1 + sp.exp(-18 * (M - 0.55))
    )

    diversion_coeff = (
        1 - 0.99 * suppression_high_weight
    )

    total_clearance = (
        k_deg * (1 + 3 * suppression_high_weight)
        + 3 * suppression_low_weight
    )

    degradation = (
        total_clearance * K / (Km + K) * M
    )

    # Composite stress function
    S_t = 0.5 * P + 0.4 * K + 0.1 * R

    Theta_S = (
        S_t**n /
        (Th**n + S_t**n)
    )

    # ODE system
    f1 = k_prod * diversion_coeff - degradation
    f2 = k_act * K - k_fb * M * P
    f3 = k_ROS * K - k_clear * R
    f4 = (Theta_S - M) / tau

    equations = [f1, f2, f3, f4]
    states = [K, P, R, M]

    print("=" * 80)
    print("=== FAST SYMBOLIC JACOBIAN ANALYSIS ===")
    print("=" * 80)

    Jacobian_matrix = sp.Matrix(
        [
            [sp.diff(f, x) for x in states]
            for f in equations
        ]
    )

    print("[+] Jacobian oluşturuldu.")

    j_trace = Jacobian_matrix.trace()

    print("[+] Trace hesaplandı.")

    # ---------------------------------------------------
    # FAST NUMERICAL EIGENVALUE APPROXIMATION
    # ---------------------------------------------------

    print("[+] Sayısal özdeğer yaklaşımı hesaplanıyor...")

    sample_values = {
        K: 1.0,
        P: 1.0,
        R: 1.0,
        M: 0.5,
        Th: 1.0,
        n: 2.0,
        tau: 2.0,
        k_prod: 1.0,
        k_deg: 0.5,
        Km: 1.0,
        k_act: 1.0,
        k_fb: 0.5,
        k_ROS: 0.3,
        k_clear: 0.4,
    }

    J_numeric = Jacobian_matrix.subs(
        sample_values
    ).evalf()

    eigenvalues = J_numeric.eigenvals()

    print("[+] Özdeğerler hesaplandı.")

    report_path = (
        "figures/jacobian_symbolic_report.txt"
    )

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write("=" * 60 + "\n")
        f.write(
            "FAST JACOBIAN ANALYSIS REPORT\n"
        )
        f.write("=" * 60 + "\n\n")

        f.write("JACOBIAN MATRIX\n\n")

        for i in range(4):
            for j in range(4):

                f.write(
                    f"J[{i},{j}]\n"
                )

                f.write(
                    str(
                        Jacobian_matrix[i, j]
                    )
                )

                f.write("\n\n")

        f.write("TRACE(J)\n")
        f.write(str(j_trace))
        f.write("\n\n")

        f.write(
            "NUMERICAL EIGENVALUES\n"
        )

        f.write(
            str(eigenvalues)
        )

    print("\n[SUCCESS]")
    print(
        f"Rapor kaydedildi: {report_path}"
    )

    print("=" * 80)

    return Jacobian_matrix


if __name__ == "__main__":
    derive_symbolic_jacobian()
