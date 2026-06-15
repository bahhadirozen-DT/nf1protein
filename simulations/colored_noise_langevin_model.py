"""
Module: colored_noise_langevin_model.py
Description: Solves the Langevin equation with Ornstein-Uhlenbeck colored noise,
             integrating real AF3 structural metrics with dynamic ensemble landscapes.
"""

import os
import glob
import numpy as np
import matplotlib.pyplot as plt

_CACHED_THETA = None
_LANGEVIN_CACHE = {}

def run_langevin_simulation_pipeline(
    target_equilibrium=0.5,
    omega_mut=1.0,
    haddock_score=0.0,
    save_plot=False):

    print(
        "[PIPELINE]",
        "omega=", omega_mut,
        "haddock=", haddock_score
    )

    # 0. ALPHAFOLD & STRUCTURAL INTEGRATION BINDING KÖPRÜSÜ
    global _CACHED_THETA

    try:
        if _CACHED_THETA is None:

            from analyze_structure import analyze_molecular_interaction

            BASE_DIR = os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)
                )
            )

            cif_files = glob.glob(
                os.path.join(
                    BASE_DIR,
                    "alphafold_models",
                    "*.cif"
                )
            )

            if cif_files:

                print(f"[*] AlphaFold yapısal verileri okunuyor: {cif_files[0]}")

                structure_results = analyze_molecular_interaction(cif_files[0])

                _CACHED_THETA = float(structure_results["theta_occupancy"])

            else:

                print("[!] Klasörde .cif dosyası bulunamadı.")
                _CACHED_THETA = 0.65

        theta_native = _CACHED_THETA

    except Exception as e:

        print(f"[!] Köprü bağlantısı kurulamadı ({e})")
        theta_native = 0.65

    # 1. Zaman ve Alan Parametreleri
    T = 50.0
    dt = 0.01
    N = int(T / dt)
    t = np.linspace(0, T, N)
    A_effector = 10.0

    # 2. Biyofiziksel Manzara Parametreleri (Rugged Landscape)
    # (A) alpha scaling fix - use tanh for smoother scaling
    alpha = 1.2 * np.tanh(omega_mut)

    beta = 2.0 * np.log1p(abs(haddock_score))

    c1, k1 = 0.25, 12.0
    c2, k2 = 0.18, 25.0

    # 3. Gelişmiş Ornstein-Uhlenbeck Renkli Gürültü Parametreleri (Colored Noise)
    tau_memory = 0.8 
    sigma_noise = 0.25 
    eta = np.zeros(N) 

    # 4. Olasılıksal Bağlanma Kinetiği (Probabilistic Occupancy Gating)    
    A_redirector_dynamic = np.zeros(N)
    is_bound = True
    k_on = 0.04 
    k_off = 0.02 

    violations = 0
    descent_speed_accumulator = 0.0

    for i in range(N):
        if is_bound:
            if np.random.rand() < k_off * dt: 
                is_bound = False
        else:
            if np.random.rand() < k_on * dt: 
                is_bound = True
        A_redirector_dynamic[i] = 1.0 if is_bound else 0.0

    # 5. Langevin Çözücü (Memory-infused Integration - Accessibility Spectrum)
    theta_rugged = np.zeros(N)
    theta_rugged[0] = theta_native
    # (B) equilibrium drift fix - sync target with native
    target_equilibrium = theta_native
    
    for i in range(1, N):
        curr_theta = theta_rugged[i-1]
        curr_A_red = A_redirector_dynamic[i-1]

        # Ornstein-Uhlenbeck Renkli Gürültü Adımı (Hafıza Güncellemesi)
        dW = np.random.normal(0, np.sqrt(dt))
        deta = -(1.0 / tau_memory) * eta[i-1] * dt + (sigma_noise / tau_memory) * dW
        eta[i] = eta[i-1] + deta

        # Potansiyel Enerji Gradyanı (Hizalanmış Çekici Dinamiği Entegre Edildi)
        base_grad = 2 * alpha * (curr_theta - theta_native) - beta * curr_A_red * np.sin(curr_theta)
        rugged_grad = c1 * k1 * np.cos(k1 * curr_theta) + c2 * k2 * np.cos(k2 * curr_theta)
        # (C) gradient normalization - prevent explosive gradients
        total_gradient = (base_grad + rugged_grad) / (1.0 + np.abs(base_grad) + np.abs(rugged_grad))

        # (D) Langevin step noise fix - adaptive noise scaling
        noise_scale = 0.6 + 0.4 * omega_mut
        dtheta = - total_gradient * dt + noise_scale * eta[i] * np.sqrt(dt)
        theta_rugged[i] = curr_theta + dtheta
        
        # (E) violation logic fix - adaptive threshold
        adaptive_eps = 0.25 + 0.15 * omega_mut
        if abs(theta_rugged[i] - target_equilibrium) > adaptive_eps:
            violations += 1
        descent_speed_accumulator += -total_gradient

    theta_rugged = np.clip(theta_rugged, 0.01, 0.99)
    phi_rugged = A_effector * (1.0 - theta_rugged) / (1 + A_redirector_dynamic)

    # 6. Görselleştirme
    if save_plot:

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(13, 11), sharex=True)

        ax1.plot(t, A_redirector_dynamic, 'r-', alpha=0.7, label='Olasılıksal Rezidans Kinetiği ($A_{redirector}(t)$)')
        ax1.set_ylabel('İnhibitör Durumu', fontsize=10)
        ax1.set_title('Probabilistic Residence Kinetics & Local Concentration Fluctuations', fontsize=12, fontweight='bold')
        ax1.grid(True, linestyle=':', alpha=0.5)
        ax1.legend(loc='upper right')

        ax2.plot(t, theta_rugged, 'g-', alpha=0.8, label='Sağ Model (Memory-infused Colored Noise)')
        ax2.axhline(y=theta_native, color='blue', linestyle='--', label=f'AF3 Yapısal Taban Çizgisi ({theta_native:.2f})')
        ax2.set_ylabel('Erişilebilirlik Spektrumu ($\\theta_{eff}$)', fontsize=10)
        ax2.set_title('Ornstein–Uhlenbeck Renkli Gürültüsü Altında Sürekli Konformasyonel Akış', fontsize=12, fontweight='bold')
        ax2.grid(True, linestyle=':', alpha=0.5)
        ax2.legend(loc='lower right')

        ax3.plot(t, phi_rugged, 'b-', alpha=0.8, label='Efektif Sinyal Akışı ($\\Phi$)')
        ax3.set_xlabel('Zaman (ns)', fontsize=11)
        ax3.set_ylabel('Sinyal Yoğunluğu', fontsize=10)
        ax3.set_title('Nihai Profil: Probabilistic Accessibility Landscape & Ensemble Redistribution', fontsize=12, fontweight='bold')
        ax3.grid(True, linestyle=':', alpha=0.5)
        ax3.legend(loc='upper right')

        plt.tight_layout()

        if not os.path.exists('docs'):
            os.makedirs('docs')

        plt.savefig(
            'docs/ensemble_dynamics_v2.png',
            dpi=300,
            bbox_inches='tight'
        )
        plt.close()

    print(
        "[SIM]",
        "omega=", omega_mut,
        "haddock=", haddock_score,
        "descent=", descent_speed_accumulator / N,
        "violations=", violations   
    )

    return {
        "trajectory": theta_rugged,
        "violations": violations,
        "descent_speed": descent_speed_accumulator / N
    }

# =====================================================================
# GENETİK ALGORİTMA KÖPRÜ BAĞLANTISI (OBJECT INTERFACE WRAPPER)
# =====================================================================
class ColoredNoiseLangevinModel:
    """
    Genetik algoritmanın nesne tabanlı arayüz çağrısını destekleyen sarmalayıcı sınıf.
    """
    def __new__(cls):
        # Pipeline'ı tetikler ve GA'nın beklediği sözlük (dict) çıktısını döndürür
        return run_langevin_simulation_pipeline(
            target_equilibrium=-1.8,
            save_plot=True
        )

# =====================================================================
# BACKWARD COMPATIBILITY WRAPPER
# =====================================================================

def solve_sde(*args, **kwargs):

    global _LANGEVIN_CACHE

    omega_mut = kwargs.get("omega_mut", 1.0)
    haddock_score = kwargs.get("haddock_score", 0.0)

    key = (
        round(float(omega_mut), 3),
        round(float(haddock_score), 2)
    )

    if key in _LANGEVIN_CACHE:
        return _LANGEVIN_CACHE[key]

    print(
        "[DEBUG]",
        "omega=", omega_mut,
        "haddock=", haddock_score
    )

    result = run_langevin_simulation_pipeline(
        target_equilibrium=0.5,
        omega_mut=omega_mut,
        haddock_score=haddock_score,
        save_plot=False
    )

    trajectory = result["trajectory"]

    # (G) homeostasis window fix - check last 200 timesteps
    window = trajectory[-200:]
    target_eq = 0.5
    homeostasis_metric = np.mean(np.abs(window - target_eq))

    # (F) descent sign bug fix - keep original sign
    lambda_max = result["descent_speed"]

    # Stability control - prevent NaN propagation
    if np.isnan(lambda_max):
        lambda_max = 0.0

    output = (
        trajectory,
        float(lambda_max)
    )

    _LANGEVIN_CACHE[key] = output

    return output
