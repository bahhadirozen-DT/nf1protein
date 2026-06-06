import numpy as np
import scipy.stats as stats
from simulations.colored_noise_langevin_model import solve_sde
from bridge_models.evidence_weighted_calibration import load_haddock_score_from_json

# Gerçek HADDOCK simülasyon çıktısını veri tabanına dinamik çekiyoruz
TRUE_SCORE, TRUE_STD = load_haddock_score_from_json()

# Olasılıksal Mutasyon Manifoldu gerçek veri ile kalibre edildi
MUTATION_MANIFOLD = {
    "R1276Q (Missense - GAP Domain)": {
        "evidence": "strong",
        "omega_prior": stats.beta(6, 4),   # Kısmi korunan kalıntı aktivite
        "haddock_score": TRUE_SCORE,       # -62.3
        "haddock_std": TRUE_STD           # 3.0
    },
    "R681X (Nonsense - Severe)": {
        "evidence": "strong",
        "omega_prior": stats.beta(1, 18),  # Ağır fonksiyon kaybı
        "haddock_score": 0.0,              # Yapısal hedef yok
        "haddock_std": 0.0
    },
    "c.2041C>T (Splice - Exon Skip)": {
        "evidence": "moderate",
        "omega_prior": stats.beta(3, 9),   # Kısmen kesilmiş protein yapısı
        "haddock_score": TRUE_SCORE * 0.58, # Gerçek skora bağlı relatif zayıflama
        "haddock_std": TRUE_STD * 1.5
    }
}

def sigmoid(x):
    """Lyapunov olcegini sinirlayarak kaos cezasini normalize eden fonksiyon."""
    return 1.0 / (1.0 + np.exp(-x))

def run_probabilistic_screening(iterations=500):
    print("🔬 RUNNING: Data-Driven Mutation-Aware Pathology Manifold")
    print("=================================================================")
    
    for mut_name, meta in MUTATION_MANIFOLD.items():
        rescue_count = 0
        lyapunov_pool = []
        
        # Gerçek HADDOCK sapmalarına göre Monte Carlo Örneklemesi
        sampled_omegas = meta["omega_prior"].rvs(iterations)
        if meta["haddock_std"] > 0:
            sampled_scores = np.random.normal(meta["haddock_score"], meta["haddock_std"], iterations)
        else:
            sampled_scores = np.zeros(iterations)
        
        for i in range(iterations):
            omega = sampled_omegas[i]
            score = sampled_scores[i]
            
            # Gerçek SDE/Langevin çözücüyü mutasyon parametreleriyle tetikle
            trajectory, lambda_max = solve_sde(omega_mut=omega, haddock_score=score)
            lyapunov_pool.append(lambda_max)
            
            # Confinement Analizi (Homeostatik havzaya kilitlenme kontrolü)
            if np.max(np.abs(trajectory[-100:])) < 0.20:
                rescue_count += 1
                
        p_homeostasis = rescue_count / iterations
        mean_lambda = np.mean(lyapunov_pool)
        
        # Ölçek patlamasını önleyen normalize edilmiş dinamik kurtarma skoru (R)
        r_score = 0.4 * sigmoid(-mean_lambda) + 0.6 * p_homeostasis
        
        print(f"▶ Varyant: {mut_name} [Kanit Duzeyi: {meta['evidence'].upper()}]")
        print(f"  └─ Olasiliksal Kurtarma P(homeostasis): %{p_homeostasis*100:.2f}")
        print(f"  └─ Ortalama Lyapunov Kararliligi: {mean_lambda:.4f}")
        print(f"  └─ Phenotypic Dynamical Rescue Index (R): {r_score:.4f}\n")

if __name__ == "__main__":
    run_probabilistic_screening()
