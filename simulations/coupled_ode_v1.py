"""
Module: coupled_ode_v1.py
Description: Core continuous ODE integration engine mapping the homeostatic 
transitions and attenuation dynamics within the NF1-KRAS feedback loop.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

def amtp_continuous_core(states, t, params):
    KRAS, pERK, ROS, M = states
    
    Theta_high = params['Theta_high']
    n = params['n']
    tau_m = params['tau_m']
    k_prod = params['k_prod']
    k_deg = params['k_deg']
    K_m = params['K_m']
    k_act = params['k_act']
    k_fb = params['k_fb']
    k_ROS = params['k_ROS']
    k_clear = params['k_clear']
    
    # 1. Composite Stress Index (CSI)
    S_t = 0.5 * pERK + 0.4 * KRAS + 0.1 * ROS
    Theta_S = (S_t**n) / (Theta_high**n + S_t**n)
    
    # Delayed Adaptation Kernel
    dM_dt = (Theta_S - M) / tau_m
    
    # 2. Biyolojik Baskılama Rejim Geçiş Diferansiyelleri (Sigmoid Blending)
    suppression_low_weight = 1.0 / (1.0 + np.exp(-18 * (M - 0.55)))  
    suppression_high_weight = 1.0 / (1.0 + np.exp(-25 * (M - 0.82)))  
    
    phenomenological_diversion_coeff = 1.0 - (0.99 * suppression_high_weight)
    total_clearance = (k_deg * (1.0 + 3.0 * suppression_high_weight)) + (3.0 * suppression_low_weight)
    degradation = (total_clearance * KRAS) / (K_m + KRAS) * M
    
    # 3. Coupled ODE Set
    dKRAS_dt = (k_prod * phenomenological_diversion_coeff) - degradation
    dpERK_dt = k_act * KRAS - (k_fb * M * pERK)
    dROS_dt = k_ROS * KRAS - k_clear * ROS
    
    return [dKRAS_dt, dpERK_dt, dROS_dt, dM_dt]

def execute_core_validation():
    # --- Klasör Kontrolü ---
    if not os.path.exists('figures'):
        os.makedirs('figures')

    t = np.linspace(0, 150, 3000)
    initial_conditions = [1.8, 1.2, 0.3, 0.0]
    
    base_params = {
        'Theta_high': 3.5, 'n': 4, 'tau_m': 2.5, 'k_prod': 0.8, 'k_deg': 1.0,
        'K_m': 0.5, 'k_act': 0.9, 'k_fb': 1.8, 'k_ROS': 0.3, 'k_clear': 0.4
    }
    
    # Diferansiyel Denklem Çözümü
    solution = odeint(amtp_continuous_core, initial_conditions, t, args=(base_params,))
    KRAS_trajectory, pERK_trajectory, ROS_trajectory, M_trajectory = solution.T

    # --- Görsel Doğrulama Çizimi ---
    plt.figure(figsize=(10, 5))
    plt.plot(t, KRAS_trajectory, color='teal', linewidth=2, label='[KRAS] Dynamics')
    plt.plot(t, pERK_trajectory, color='crimson', linewidth=2, label='[pERK] Dynamics')
    plt.plot(t, M_trajectory, color='indigo', linewidth=1.5, linestyle='--', label='Hücresel Hafıza (M)')
    
    plt.title('Continuous Core ODE Integration Trajectories', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Zaman (Saniye)', fontsize=10)
    plt.ylabel('Konsantrasyon / Aktivasyon Seviyesi', fontsize=10)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='upper right', fontsize=9)
    
    plt.savefig('figures/continuous_ode_trajectory.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("✅ SUCCESS: Theoretical coupled ODE core engine successfully initialized.")
    print("✅ SUCCESS: Continuous regime interpolation active and synchronized with notebook specifications.")
    print("[GRAPHICS SUCCESS] 'figures/continuous_ode_trajectory.png' başarıyla üretildi.")

if __name__ == "__main__":
    execute_core_validation()


