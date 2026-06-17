```python
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
    tolerance=0.15
):
    """
    Son 200 adımın gerçekten homeostatik bölgede olup olmadığını ölç.
    """

    window = trajectory[-200:]

    mean_distance = np.mean(np.abs(window - target))
    fluctuation = np.std(window)

    stable_mean = mean_distance < tolerance
    stable_noise = fluctuation < 0.10

    return float(stable_mean and stable_noise)


def compute_lambda_component(mean_lambda):
    """
    Negatif Lyapunov = stabil
    Pozitif Lyapunov = kaotik
    """

    return sigmoid(-mean_lambda * 25.0)


def run_probabilistic_screening(iterations=500):

    print("🔬 RUNNING: Data-Driven Mutation-Aware Pathology Manifold")
    print("=================================================================")

    for mut_name, meta in MUTATION_MANIFOLD.items():

        homeostasis_hits = 0
        lyapunov_pool = []

        sampled_omegas = meta["omega_prior"].rvs(iterations)

        if meta["haddock_std"] > 0:

            sampled_scores = np.random.normal(
                meta["haddock_score"],
                meta["haddock_std"],
                iterations
            )

        else:

            sampled_scores = np.zeros(iterations)

        for i in range(iterations):

            omega = sampled_omegas[i]
            score = sampled_scores[i]

            trajectory, lambda_max = solve_sde(
                omega_mut=omega,
                haddock_score=score
            )

            lyapunov_pool.append(lambda_max)

            homeostasis_hits += compute_homeostasis_probability(
                trajectory,
                target=0.5,
                tolerance=0.15
            )

        p_homeostasis = homeostasis_hits / iterations

        mean_lambda = float(np.mean(lyapunov_pool))

        lambda_component = compute_lambda_component(
            mean_lambda
        )

        r_score = (
            0.5 * lambda_component +
            0.5 * p_homeostasis
        )

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
            f"%{p_homeostasis*100:.2f}"
        )

        print(
            f"  └─ Ortalama Lyapunov Kararliligi: "
            f"{mean_lambda:.4f}"
        )

        print(
            f"  └─ Phenotypic Dynamical Rescue Index (R): "
            f"{r_score:.4f}\n"
        )


if __name__ == "__main__":
    run_probabilistic_screening()
```
