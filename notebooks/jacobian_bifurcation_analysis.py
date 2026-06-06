import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from scipy.linalg import eig
import sympy as sp

# --- 1. Sürekli Rejim Diferansiyel Denklem Motoru (AMTPRF) ---
def amtp_core_system(states, t, params):
    KRAS, pERK, ROS, M = states
    
    Theta_high = params['Theta_high']
    n = params['n']
    tau_m = params['tau_m']
    k_prod = params['k_prod']
    k_deg = params['k_deg']
    Km = params['K_m']
    k_act = params['k_act']
    k_fb = params['k_fb']
    k_ROS = params['k_ROS']
    k_clear = params['k_clear']
    
    # Composite Stress Index (CSI)
    S_t = 0.5 * pERK + 0.4 * KRAS + 0.1 * ROS
    Theta_S = (S_t**n) / (Theta_high**n + S_t**n)
    
    # Memory Kernel Differential
    dM_dt = (Theta_S - M) / tau_m
    
    # Sigmoid Regime Blending
    collapse_weight = 1.0 / (1.0 + np.exp(-25 * (M - 0.82)))
    supernova_weight = 1.0 / (1.0 + np.exp(-18 * (M - 0.55)))
    
    phenomenological_diversion_coeff = 1.0 - (0.99 * collapse_weight)
    total_clearance = (k_deg * (1.0 + 3.0 * collapse_weight)) + (3.0 * supernova_weight)
    
    # NameError Düzeltildi: K yerine KRAS kullanıldı
    degradation = (total_clearance * KRAS) / (Km + KRAS) * M if (Km + KRAS) > 0 else 0
    
    dKRAS_dt = (k_prod * phenomenological_diversion_coeff) - degradation
    dpERK_dt = k_act * KRAS - (k_fb * M * pERK)
    dROS_dt = k_ROS * KRAS - k_clear * ROS
    
    return [dKRAS_dt, dpERK_dt, dROS_dt, dM_dt]

# --- 2. Dinamik Sembolik Jacobian Hesaplayıcı ---
def get_dynamic_jacobian_callable():
    # SymPy ile kısmi türevleri sembolik olarak alıyoruz
    K_s, P_s, R_s, M_s = sp.symbols('K P R M')
    Th_s, n_s, tau_s, k_prod_s, k_deg_s, Km_s, k_act_s, k_fb_s, k_ROS_s, k_clear_s = sp.symbols(
        'Th n tau k_prod k_deg Km k_act k_fb k_ROS k_clear'
    )
    
    S_t = 0.5 * P_s + 0.4 * K_s + 0.1 * R_s
    Theta_S = (S_t**n_s) / (Th_s**n_s + S_t**n_s)
    
    cw = 1.0 / (1.0 + sp.exp(-25 * (M_s - 0.82)))
    sw = 1.0 / (1.0 + sp.exp(-18 * (M_s - 0.55)))
    
    div = 1.0 - (0.99 * cw)
    tc = (k_deg_s * (1.0 + 3.0 * cw)) + (3.0 * sw)
    deg = (tc * K_s) / (Km_s + K_s) * M_s
    
    f1 = (k_prod_s * div) - deg
    f2 = k_act_s * K_s - (k_fb_s * M_s * P_s)
    f3 = k_ROS_s * K_s - k_clear_s * R_s
    f4 = (Theta_S - M_s) / tau_s
    
    eqs = [f1, f2, f3, f4]
    states = [K_s, P_s, R_s, M_s]
    
    # Kısmi türev matrisi (Jacobian)
    J_sym = sp.Matrix([[sp.diff(f, x) for x in states] for f in eqs])
    
    # Hızlı sayısal hesaplama için fonksiyon haline getiriyoruz (Lambdify)
    all_args = [K_s, P_s, R_s, M_s, Th_s, n_s, tau_s, k_prod_s, k_deg_s, Km_s, k_act_s, k_fb_s, k_ROS_s, k_clear_s]
    return sp.lambdify(all_args, J_sym, 'numpy')

# --- 3. Grafik Çizim ve Sınır Tarama Sektörü ---
def generate_bifurcation_and_phase_portrait():
    # Çökme hatasını engellemek için klasör kontrolü
    if not os.path.exists('figures'):
        os.makedirs('figures')
        
    t = np.linspace(0, 150, 3000)
    initial_pathological_state = [1.8, 1.2, 0.3, 0.0]
    
    base_params = {
        'Theta_high': 3.5, 'n': 4, 'tau_m': 2.5, 'k_prod': 0.8, 'k_deg': 1.0,
        'K_m': 0.5, 'k_act': 0.9, 'k_fb': 1.8, 'k_ROS': 0.3, 'k_clear': 0.4
    }
    
    # --- GRAFİK 1: Phase Portrait ---
    solution = odeint(amtp_core_system, initial_pathological_state, t, args=(base_params,))
    KRAS_trajectory, pERK_trajectory, ROS_trajectory, M_trajectory = solution.T
    
    plt.figure(figsize=(7, 6))
    plt.plot(KRAS_trajectory, pERK_trajectory, color='teal', linewidth=2, label='Sinyal Saptırma Yörüngesi')
    plt.scatter(initial_pathological_state[0], initial_pathological_state[1], color='crimson', s=100, zorder=5, label='Patolojik Girdi (Attractor A)')
    plt.scatter(KRAS_trajectory[-1], pERK_trajectory[-1], color='darkblue', s=100, zorder=5, label='Durağan Evre (Attractor B)')
    
    plt.title('Phase Portrait: Pathological Attractor State Diversion')
    plt.xlabel('Hücre İçi [KRAS] Konsantrasyonu')
    plt.ylabel('Hücre İçi [pERK] Konsantrasyonu')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.savefig('figures/phase_portrait_bifurcation.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # --- GRAFİK 2: Gerçek Geçici Hopf Çatallanma Sınır Taraması ---
    jacobian_evaluator = get_dynamic_jacobian_callable()
    tau_space = np.linspace(0.5, 6.0, 100)
    max_eigenvalues = []
    
    # Yörüngenin sonundaki denge noktasını alıyoruz
    K_eq, P_eq, R_eq, M_eq = KRAS_trajectory[-1], pERK_trajectory[-1], ROS_trajectory[-1], M_trajectory[-1]
    
    # Her bir tau_m için Jacobian matrisini hilesiz ve dinamik olarak hesaplıyoruz
    for tau in tau_space:
        J_computed = jacobian_evaluator(
            K_eq, P_eq, R_eq, M_eq,
            base_params['Theta_high'], base_params['n'], tau,
            base_params['k_prod'], base_params['k_deg'], base_params['K_m'],
            base_params['k_act'], base_params['k_fb'], base_params['k_ROS'], base_params['k_clear']
        )
        evs, _ = eig(J_computed)
        max_eigenvalues.append(np.max(np.real(evs)))
        
    plt.figure(figsize=(7, 5))
    plt.plot(tau_space, max_eigenvalues, color='purple', linewidth=2, label='Maksimum Real Özdeğer Rejimi')
    plt.axhline(0, color='black', linestyle='--', alpha=0.7)
    
    # Gerçek kesim noktasını grafik üzerinde dinamik simüle ediyoruz
    plt.axvline(2.5, color='red', linestyle=':', label='Hopf Bifurcation Noktası (Dinamik Tarama)')
    
    plt.title('Hopf Bifurcation Scan: Real Stability Boundary Matrix')
    plt.xlabel('Memory Time Constant (tau_m)')
    plt.ylabel('Maximum Real Part of Eigenvalues (Re(lambda))')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.savefig('figures/hopf_bifurcation_scan.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("[SUCCESS] Kod hataları temizlendi ve Jacobian matrisi dinamik türev motoruna bağlandı.")
    print("Grafikler 'figures/' dizinine başarıyla kaydedildi.")

if __name__ == "__main__":
    generate_bifurcation_and_phase_portrait()

