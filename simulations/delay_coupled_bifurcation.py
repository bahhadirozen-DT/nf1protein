"""
NF1-Smart-Redirector-Model - Cell-Line Specific Dynamic Delay Attractor Model (DDE-SDE)
Author: Bahadir Ozen Hls Aydemir faz farkı alıntıdır
Year: 2026
Description: Independent simulation sandbox modeling cell-line specific dynamic phase lag 
             and delay-induced Hopf bifurcation boundaries based on tumor aggressive profiles.
"""

import os
import numpy as np
import matplotlib.pyplot as plt

def run_delay_confinement_simulation(
    T=80,
    dt=0.01,
    cell_line="Schwannoma", # "Schwannoma", "MPNST" veya "Custom" seçilebilir
    noise_sigma=0.05,
    activation_time=6.0,
    seed=2026
):
    np.random.seed(seed)
    N = int(T / dt)
    t = np.linspace(0, T, N)

    # State variables
    x = np.zeros(N)
    y = np.zeros(N)

    # Initial conditions
    x[0] = 0.2
    y[0] = 0.1

    # Parameters aligned with topological confinement bounds
    r = 1.0
    R = 1.58
    n_hill = 2.0
    K = 1.0
    K_tau = 1.0  # Gecikme doyum sabiti

    # =========================================================================
    # HÜCRE TİPİNE GÖRE OTO-KALİBRASYON (Cell-Line Specific Parameter Tuning)
    # =========================================================================
    if cell_line == "Schwannoma":
        # Benign/Yavaş döngülü NF1-mutant hücre hattı profili
        tau_baseline = 25  
        tau_max = 65       
        print("[*] Profile Configured: NF1-Mutant Schwannoma (Standard Latency Profile)")
    elif cell_line == "MPNST":
        # Agresif/Hızlı adapte olan malign tümör hattı profili (Daha kısa iletim latansı)
        tau_baseline = 12  
        tau_max = 35       
        print("[*] Profile Configured: Malignant Peripheral Nerve Sheath Tumor - MPNST (Accelerated Latency)")
    else:
        # Varsayılan / Özelleştirilmiş orta hat profili
        tau_baseline = 20
        tau_max = 50
        print("[*] Profile Configured: Custom / Generic Cellular Line")

    for i in range(N - 1):
        current_t = t[i]

        # DURUMA BAĞLI DİNAMİK GECİKME (State-Dependent Dynamic Delay Calculation)
        current_x = x[i]
        if current_x > 0:
            # Hücre tipi parametreleri doğrultusunda anlık sinyal genliğine bağlı dinamik gecikme
            dynamic_tau = int(tau_baseline + tau_max * (current_x**2) / (K_tau**2 + current_x**2))
        else:
            dynamic_tau = int(tau_baseline)

        # DELAYED STATE ACCESS (Dinamik History Buffer geçmiş erişimi)
        if i > dynamic_tau:
            x_tau = x[i - dynamic_tau]
        else:
            x_tau = x[0]

        # STOCHASTIC NOISE (Euler-Maruyama integration step)
        dWx = np.random.normal(0, np.sqrt(dt))
        dWy = np.random.normal(0, np.sqrt(dt))

        # REGIME SWITCHING MECHANICS
        if current_t < activation_time:
            # Unstable runaway oncogenic cascade simulation
            dxdt = y[i]
            dydt = 0.15 * y[i] + 0.05 * x[i]
        else:
            # Non-linear Hill activation and confinement damping
            hill = (x[i]**n_hill) / (K**n_hill + x[i]**n_hill) if x[i] > 0 else 0
            radial_term = (R**2 - x[i]**2 - y[i]**2)

            # Delay-coupled dynamic feedback implementation
            dxdt = y[i]
            dydt = -r * x_tau + radial_term * y[i] * hill

        # EULER-MARUYAMA FINITE DIFFERENCE UPDATE
        x[i+1] = x[i] + dxdt * dt + noise_sigma * dWx
        y[i+1] = y[i] + dydt * dt + noise_sigma * dWy

    return t, x, y, activation_time, R, cell_line

if __name__ == "__main__":
    print("[+] Running Multi-Profile Cell-Line Delay Attractor Simulation...")
    
    # İstediğiniz hücre hattını buradan test edebilirsiniz: "Schwannoma" veya "MPNST"
    target_cell = "MPNST" 
    
    t, x, y, t_act, R_val, active_profile = run_delay_confinement_simulation(
        cell_line=target_cell,
        noise_sigma=0.05,
        activation_time=6.0,
        seed=2026
    )

    pre = t < t_act
    post = t >= t_act

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # 1. TIME SERIES VISUALIZATION
    ax1.plot(t[pre], x[pre], color='crimson', lw=2, label='Runaway Regime')
    ax1.plot(t[post], x[post], color='royalblue', lw=1.8, label=f'Confinement ({active_profile})')
    ax1.axvline(x=t_act, color='purple', linestyle='--', lw=2, label='Activation Onset')
    ax1.set_title(f"Dynamic Delay Stochastic Regulation - {active_profile}")
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Signal Amplitude (x)")
    ax1.grid(True, linestyle=':')
    ax1.legend()

    # 2. PHASE PORTRAIT VISUALIZATION
    ax2.plot(x[pre], y[pre], color='crimson', linestyle=':', lw=1.5, label='Runaway Trajectory')
    ax2.plot(x[post], y[post], color='royalblue', lw=1.5, alpha=0.85, label='Dynamic Attractor Confinement')

    # Overlapping theoretical static boundary
    theta = np.linspace(0, 2*np.pi, 300)
    ax2.plot(R_val*np.cos(theta), R_val*np.sin(theta), 'k--', lw=2, alpha=0.6, label='Theoretical Boundary')
    ax2.set_title(f"Phase Portrait ({active_profile} Profile)")
    ax2.set_xlabel("x (Signal)")
    ax2.set_ylabel("y (Flux Velocity)")
    ax2.grid(True, linestyle=':')
    ax2.legend()

    plt.tight_layout()
    
    output_dir = "figures"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"delay_bifurcation_{active_profile.lower()}.png")
    plt.savefig(output_path, dpi=120)
    print(f"[+] Simulation finished. Chart successfully exported to: {output_path}")
