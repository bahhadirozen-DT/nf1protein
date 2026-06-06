"""
Module: delay_coupled_bifurcation.py
Description: Resolves discrete History Delay DDE trajectories mapping cell adaptation curves.
             Tracks phase lag and delay-induced Hopf bifurcation boundaries.
"""

import numpy as np
import matplotlib.pyplot as plt
import os

def run_delay_confinement_simulation(steps=2000, dt=0.01, seed=42, cellular_libido="Schwannoma", activation_libido=True):
    """
    Stokastik Gecikmeli Diferansiyel Denklem (SDE-DDE) Zaman Serisi Çözücü.
    Hücre içi sinyal iletimindeki translasyonel gecikmeleri simüle eder.
    """
    np.random.seed(seed)
    
    # Tümör agresiflik profillerine bağlı hücresel kalibrasyon parametreleri
    if cellular_libido == "Schwannoma":
        tau_baseline = 2.00
        tau_max = 2.36
        gamma = 0.5
        g = 0.3
        sigma_noise = 0.50
    else:  # MPNST (Aggressive Core)
        tau_baseline = 1.20
        tau_max = 1.85
        gamma = 0.7
        g = 0.55
        sigma_noise = 0.75
        
    if not activation_libido:
        sigma_noise = 0.10  # Kontrol grubu için gürültü bastırma
        
    total_time_steps = steps
    t_arr = np.arange(0, total_time_steps) * dt
    
    X = np.zeros(total_time_steps)
    Y = np.zeros(total_time_steps)
    
    X[0] = 1.0
    Y[0] = 0.1
    
    max_delay_steps = int(tau_max / dt) + 5
    history_buffer_X = list(np.ones(max_delay_steps) * X[0])
    
    for i in range(1, total_time_steps):
        current_x = X[i-1]
        K_tau = 1.5
        tau_eff = tau_baseline + (tau_max - tau_baseline) * (current_x**2 / (K_tau**2 + current_x**2))
        delay_index = int(tau_eff / dt)
        
        if delay_index < len(history_buffer_X):
            x_delayed = history_buffer_X[-delay_index]
        else:
            x_delayed = history_buffer_X[0]
            
        # Doğrusal olmayan diferansiyel denklemler (Drift bileşenleri)
        dX = (-gamma * X[i-1] + g * x_delayed) * dt
        dY = (-1.2 * Y[i-1] + 0.5 * X[i-1]) * dt
        
        # Stokastik Wiener gürültü adımı (Euler-Maruyama)
        dW = np.random.normal(0, np.sqrt(dt))
        noise_increment = sigma_noise * dW
        
        X[i] = X[i-1] + dX + noise_increment
        Y[i] = Y[i-1] + dY
        
        history_buffer_X.append(X[i])
        if len(history_buffer_X) > max_delay_steps:
            history_buffer_X.pop(0)
            
    return t_arr, X, Y

def analyze_dde_stability(rna_sequence, expression_history=None, tau=2.4, g_max=8.5):
    """
    Gecikmeli geri besleme altındaki RNA ekspresyon stabilitesini inceler.
    Hopf bariyeri tespiti yapar.
    """
    dde_results = {
        "is_stable": True,
        "hopf_proximity": 0.0,
        "bifurcation_type": None,
        "residual_leakage": 0.0
    }
    
    gc_content = sum(1 for c in rna_sequence if c in 'GC') / max(1, len(rna_sequence))
    effective_gain = g_max * (1.0 / (1.0 + np.exp(-10.0 * (gc_content - 0.5))))
    
    hopf_threshold = np.pi / (2.0 * max(0.1, tau))
    dde_results["hopf_proximity"] = abs(effective_gain - hopf_threshold)
    
    if effective_gain >= hopf_threshold:
        dde_results["is_stable"] = False
        dde_results["bifurcation_type"] = "Supercritical Hopf"
    else:
        if dde_results["hopf_proximity"] < 0.15:
            dde_results["bifurcation_type"] = "Damped Oscillations (Near Critical)"
            
    if not dde_results["is_stable"]:
        dde_results["residual_leakage"] = 0.85 + (effective_gain * 0.05)
    else:
        dde_results["residual_leakage"] = 0.055 + (dde_results["hopf_proximity"] * 0.1)
        
    return dde_results

# =====================================================================
# GENETİK ALGORİTMA KÖPRÜ BAĞLANTISI VE GELİŞMİŞ GÖRSELLEŞTİRME
# =====================================================================
def run_ga_dde_bridge(rna_sequence, cell_line="Schwannoma", activation_status=True):
    """
    Genetik algoritma için sarmalayıcı köprü fonksiyonu.
    Giriş sekansını analiz eder ve tüm zaman serisi görselleştirmesini üretir.
    """
    dde_results = analyze_dde_stability(rna_sequence)
    
    # Zaman serisi simülasyonunu koştur
    t_arr, X, Y = run_delay_confinement_simulation(steps=2000, dt=0.01, seed=42, cellular_libido=cell_line, activation_libido=activation_status)
    
    # Dinamik Grafik Çizim ve Görselleştirme Bloğu (Orijinal Kod Yapısı)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 1. TAPC Sinyal Genliği Zaman Serisi Grafiği
    ax1.plot(t_arr, X, color='#1f77b4', alpha=0.8, label=f'Signal X ({cell_line})')
    ax1.axhline(y=1.5, color='r', linestyle='--', label='Pathological Boundary')
    ax1.axhline(y=-1.5, color='r', linestyle='--')
    ax1.set_title(f"Dynamic Phase Delay Confinement Regulation [{cell_line}]")
    ax1.set_xlabel("Time Amplitude (s)")
    ax1.set_ylabel("Signal Trajectory State")
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend()
    
    # 2. Faz Portresi Çekici Topolojisi Grafiği
    ax2.plot(X, Y, color='#e377c2', alpha=0.6, label='Conformational Attractor Trajectory')
    ax2.set_title("Topological Phase Space Attractor Boundaries")
    ax2.set_xlabel("Signal Amplitude X")
    ax2.set_ylabel("Flux Velocity Y")
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend()
    
    plt.tight_layout()
    
    # Görselleri figures klasörüne otomatik kaydetme mantığı
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, f"dde_confinement_{cell_line}.png")
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"[BAŞARILI] DDE Simülasyonu tamamlandı. Grafik kaydedildi: {output_path}")
    return dde_results

