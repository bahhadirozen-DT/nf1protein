import numpy as np
import scipy.stats as stats

from simulations.colored_noise_langevin_model import solve_sde
from bridge_models.evidence_weighted_calibration import (
    load_haddock_score_from_json
)

TRUE_SCORE, TRUE_STD = load_haddock_score_from_json()

MUTATION_MANIFOLD = {
    "R1276Q (Missense - GAP Domain)": {
        "evidence": "strong",
        "omega_prior": stats.beta(6, 4),
        "haddock_score": TRUE_SCORE,
        "haddock_std": TRUE_STD
    },
    "R681X (Nonsense - Severe)": {
        "evidence": "strong",
        "omega_prior": stats.beta(1, 18),
        "haddock_score": 0.0,
        "haddock_std": 0.0
    },
    "c.2041C>T (Splice - Exon Skip)": {
        "evidence": "moderate",
        "omega_prior": stats.beta(3, 9),
        "haddock_score": TRUE_SCORE * 0.58,
        "haddock_std": TRUE_STD * 1.5
    }
}

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

def compute_homeostasis_probability(
    trajectory,
    target=0.5,
    tolerance=0.20
):
    trajectory = np.asarray(trajectory)

    if len(trajectory) < 2000:
        window = trajectory
    else:
        window = trajectory[-2000:]

    mean_theta = np.mean(window)

    return float(
        abs(mean_theta - target) < tolerance
    )

def compute_lambda_component(mean_lambda):
    """
    Negatif Lyapunov = daha stabil
    Pozitif Lyapunov = daha kaotik
    """
    return sigmoid(-25.0 * mean_lambda)

def run_probabilistic_screening(iterations=100):
    print("🔬 RUNNING: Data-Driven Mutation-Aware Pathology Manifold")
    print("=" * 65)

    for mut_name, meta in MUTATION_MANIFOLD.items():
        homeostasis_hits = 0
        lyapunov_pool = []

        sampled_omegas = meta["omega_prior"].rvs(iterations)

        if meta["haddock_std"] > 0:
            sampled_scores = np.random.normal(
                loc=meta["haddock_score"],
                scale=meta["haddock_std"],
                size=iterations
            )
        else:
            sampled_scores = np.zeros(iterations)

        for omega, score in zip(sampled_omegas, sampled_scores):
            trajectory, lambda_max = solve_sde(
                omega_mut=float(omega),
                haddock_score=float(score)
            )

            lyapunov_pool.append(float(lambda_max))

            homeostasis_hits += compute_homeostasis_probability(
                trajectory,
                target=0.5,
                tolerance=0.20
            )

        p_homeostasis = homeostasis_hits / float(iterations)
        mean_lambda = float(np.mean(lyapunov_pool))
        lambda_component = compute_lambda_component(mean_lambda)

        r_score = (
            0.5 * lambda_component +
            0.5 * p_homeostasis
        )

        print()
        print("DEBUG:", mut_name)
        print("min lambda =", np.min(lyapunov_pool))
        print("mean lambda =", mean_lambda)
        print("max lambda =", np.max(lyapunov_pool))
        print("lambda_component =", lambda_component)
        print("p_homeostasis =", p_homeostasis)

        print(
            f"▶ Varyant: {mut_name} "
            f"[Kanit Duzeyi: {meta['evidence'].upper()}]"
        )
        print(
            f"  └─ Olasiliksal Kurtarma P(homeostasis): "
            f"%{100.0 * p_homeostasis:.2f}"
        )
        print(
            f"  └─ Ortalama Lyapunov Kararliligi: "
            f"{mean_lambda:.4f}"
        )
        print(
            f"  └─ Phenotypic Dynamical Rescue Index (R): "
            f"{r_score:.4f}"
        )

if __name__ == "__main__":
    run_probabilistic_screening()
