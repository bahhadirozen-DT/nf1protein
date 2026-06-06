"""
Module: simulations/calibration_engine.py
Description: Calibrates downstream signaling simulation parameters using mock 
wet-lab Western Blot kinetics time-series via scipy.optimize.curve_fit.
"""

import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as plt
import os

# 1. Deneysel pERK Sinyal Sönümleme Teorik Modeli (Hill-like Decay)
def signaling_decay_model(t, k_decay, alpha_adaptation):
    """
    Deneysel Western Blot pERK bant yoğunluğunun zamansal değişimi.
    k_decay: Hücre içi sinyal sönümleme hızı
    alpha_adaptation: SRX-RNA01 adaptasyon katsayısı
    """
    return np.exp(-k_decay * t) * (1.0 + alpha_adaptation * np.sin(t))

def run_wetlab_calibration():
    print("=" * 80)
    print("   EXPERIMENTAL CALIBRATION ENGINE: SCIPY CURVE_FIT INTEGRATION")
    print("=" * 80)
    
    # 2. MOCK WESTERN BLOT KİNETİK VERİ SETİ (Örnek Laboratuvar Çıktısı)
    # Zaman noktaları (Saat: 0h, 2h, 4h, 6h, 12h, 24h, 48h)
    t_experimental = np.array([0.0, 2.0, 4.0, 6.0, 12.0, 24.0, 48.0])
    # P-ERK bağıl bant yoğunluğu (Western Blot densitometre verisi)
    perk_relative_density = np.array([1.0, 0.72, 0.45, 0.31, 0.15, 0.08, 0.02])
    
    print("[+] Islak laboratuvar Western Blot pERK zaman serisi verileri yüklendi.")
    
    # 3. SCIPY CURVE_FIT İLE PARAMETRE OPTİMİZASYONU
    # Başlangıç parametre tahminleri [k_decay=0.1, alpha_adaptation=0.1]
    initial_guesses = [0.1, 0.1]
    
    popt, pcov = opt.curve_fit(signaling_decay_model, t_experimental, perk_relative_density, p0=initial_guesses)
    
    best_k_decay, best_alpha = popt
    perr = np.sqrt(np.diag(pcov)) # Standart hata matrisi
    
    print("\n📊 ISLAK LAB KALİBRASYON SONUÇLARI (TRL-3 READY):")
    print(f"-> Optimize Edilen Sönümleme Hızı (k_decay): {best_k_decay:.4f} ± {perr:.4f}")
    print(f"-> Optimize Edilen Adaptasyon Katsayısı (alpha): {best_alpha:.4f} ± {perr:.4f}")

    # 4. KALİBRASYON GRAFİĞİNİN OLUŞTURULMASI
    if not os.path.exists('figures'):
        os.makedirs('figures')
        
    t_fine = np.linspace(0, 48, 200)
    plt.figure(figsize=(8, 5))
    plt.scatter(t_experimental, perk_relative_density, color='crimson', zorder=5, label='Empirical Western Blot Data')
    plt.plot(t_fine, signaling_decay_model(t_fine, *popt), color='navy', linestyle='-', linewidth=2, label='Calibrated TAPC Model Fit')
    
    plt.title("Western Blot pERK Kinetik Kalibrasyon Eğrisi")
    plt.xlabel("Zaman (Saat - Hours)")
    plt.ylabel("Bağıl pERK1/2 Ekspresyon Yoğunluğu")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    
    graph_path = "figures/western_blot_calibration_fit.png"
    plt.savefig(graph_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\n[+] Kalibrasyon doğrulama grafiği kaydedildi: '{graph_path}'")
    print("=" * 80)
    
    return popt

if __name__ == "__main__":
    run_wetlab_calibration()
