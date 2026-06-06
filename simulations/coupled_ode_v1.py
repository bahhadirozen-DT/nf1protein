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

def run_optimization_simulation(target_params):
    """
    Genetik algoritma tarafından çağrılan optimizasyon köprü fonksiyonu.
    target_params: [Theta_high, k_fb, tau_m]
    """
    t = np.linspace(0, 150, 2000)
    initial_conditions = [1.8, 1.2, 0.3, 0.0]
    
    # Varsayılan parametre şablonunu oluşturup GA'dan gelenleri üzerine yazıyoruz
    base_params = {
        'Theta_high': target_params[0], 
        'n': 4, 
        'tau_m': target_params[2], 
        'k_prod': 0.8, 
        'k_deg': 1.0,
        'K_m': 0.5, 
        'k_act': 0.9, 
        'k_fb': target_params[1], 
        'k_ROS': 0.3, 
        'k_clear': 0.4
    }
    
    try:
        solution = odeint(amtp_continuous_core, initial_conditions, t, args=(base_params,))
        KRAS_traj, pERK_traj, _, M_traj = solution.T
        
        # Simülasyon sonundaki (kararlı durumdaki) değerleri ölçüyoruz
        final_kras = KRAS_traj[-1]
        final_perk = pERK_traj[-1]
        
        # Sinyal gürültü ve sızıntı tabanını hesaplama (Biyofiziksel Proxy)
        residual_leakage = float(final_kras / (0.5 + final_kras))
        false_positive_rate = float(np.var(pERK_traj[-500:]) if len(pERK_traj) > 500 else 0.02)
        
        return {
            "residual_leakage": residual_leakage,
            "false_positive_rate": false_positive_rate,
            "final_pERK": final_perk
        }
    except:
        # Hatalı parametre kombinasyonlarında sistemi çökertmemek için kötü bir skor döner
        return {"residual_leakage": 1.0, "false_positive_rate": 1.0, "final_pERK": 5.0}

def execute_core_validation():
    if not os.path.exists('figures'):
        os.makedirs('figures')
    
    # Test için varsayılan değerler
    sample_res = run_optimization_simulation([3.5, 1.8, 2.5])
    print(f"✅ SUCCESS: Test Run - Residual Leakage: {sample_res['residual_leakage']:.4f}")

if __name__ == "__main__":
    execute_core_validation()



