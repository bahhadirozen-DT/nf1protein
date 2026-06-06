"""
Module: stochastic_noise.py
Description: Simulates molecular fluctuations and transcriptional noise within the
NF1-KRAS cascade using Langevin SDE (Euler-Maruyama integration).
"""

import os
import numpy as np
import matplotlib.pyplot as plt

def run_real_stochastic_simulation():
    print("=" * 80)
    print("GERÇEK BİLİMSEL LANGEVIN SDE MOTORU: EULER-MARUYAMA ENTEGRASYONU")
    print("=" * 80)

    # --- Klasör Kontrolü ---
    if not os.path.exists('figures'):
        os.makedirs('figures')

    # --- 1. Simülasyon ve Zaman Parametreleri ---
    T = 50.0            # Toplam simülasyon süresi (saniye)
    N = 500             # Zaman adımı sayısı
    dt = T / N          # dt zaman aralığı (0.1 s)
    t = np.linspace(0, T, N)
    ensemble_size = 1000  # Güvenilir bir istatistik için 10^3 Monte Carlo yörüngesi

    # --- 2. Biyokimyasal Kinetik Parametreler (İdealize Sabitler) ---
    k_prod = 1.2
    k_deg = 0.8
    Km = 0.5
    k_act = 1.5
    k_fb = 0.6
    k_ROS = 0.4
    k_clear = 0.3
    tau_m = 1.0         # Alçak geçiren filtre zaman sabiti
    Theta_high = 2.0    # Kritik sitotoksik eşik tetikleyicisi
    n = 2               # Hill katsayısı

    # İnceleyeceğimiz 3 farklı gürültü seviyesi (Basal, Fizyolojik, Patolojik)
    noise_regimes = [0.05, 0.15, 0.30]
    regime_labels = ["Basal Intracellular", "Physiological Noise", "Pathological Stress"]

    print(f"{'Noise Level (σ)':<15} | {'Microenvironment':<22} | {'Computed Variance':<18} | {'Dynamic FPR'}")
    print("-" * 80)

    # Grafik çizimi için hazırlık
    plt.figure(figsize=(10, 5))
    cytotoxic_threshold = 3.5  # pERK için kritik patolojik eşik limit değeri
    
    # Her gürültü rejimi için Monte Carlo simülasyonunu başlat
    for sigma, label in zip(noise_regimes, regime_labels):
        
        # Tüm yörüngelerin pERK verilerini saklamak için matris (Yörünge x Zaman)
        pERK_trajectories = np.zeros((ensemble_size, N))
        false_positive_counts = 0

        for trial in range(ensemble_size):
            # Başlangıç Koşulları: Sağlıklı homeostaz noktası [KRAS, pERK, ROS, M]
            K, P, R, M = 0.5, 1.45, 0.5, 0.1
            pERK_trajectories[trial, 0] = P
            
            # Zaman Entegrasyon Döngüsü (Euler-Maruyama)
            for j in range(1, N):
                # Sigmoid Regime Blending Mekanizması
                collapse_weight = 1.0 / (1.0 + np.exp(-25 * (M - 0.82)))
                supernova_weight = 1.0 / (1.0 + np.exp(-18 * (M - 0.55)))
                
                diversion_coeff = 1.0 - (0.99 * collapse_weight)
                total_clearance = (k_deg * (1.0 + 3.0 * collapse_weight)) + (3.0 * supernova_weight)
                degradation = (total_clearance * K) / (Km + K) * M
                
                S_t = 0.5 * P + 0.4 * K + 0.1 * R
                Theta_S = (S_t**n) / (Theta_high**n + S_t**n)
                
                # Deterministik Drift (Sürüklenme) Terimleri
                dK_dt = (k_prod * diversion_coeff) - degradation
                dP_dt = k_act * K - (k_fb * M * P)
                dR_dt = k_ROS * K - k_clear * R
                dM_dt = (Theta_S - M) / tau_m
                
                # Stokastik Difüzyon Terimi (Wiener Süreci dW_t)
                dW_P = np.random.normal(0, np.sqrt(dt))
                
                # Euler-Maruyama Güncellemesi (Konsantrasyon negatif olamaz fltresiyle)
                K = max(0, K + dK_dt * dt)
                P = max(0, P + dP_dt * dt + sigma * dW_P) 
                R = max(0, R + dR_dt * dt)
                M = max(0, M + dM_dt * dt)
                
                pERK_trajectories[trial, j] = P
            
            # Eğer pERK simülasyon boyunca toksik eşiği aştıysa Yanlış Pozitif kabul et
            if np.max(pERK_trajectories[trial, :]) > cytotoxic_threshold:
                false_positive_counts += 1

        # İstatistiksel Hesaplamalar (Gerçek dinamik çıktılar)
        computed_variance = np.var(pERK_trajectories[:, -1])  # Son zaman adımındaki varyans
        computed_fpr = (false_positive_counts / ensemble_size) * 100
        
        print(f"σ = {sigma:<11} | {label:<22} | {computed_variance:<18.4f} | {computed_fpr:.3f}%")
        
        # Grafik için fizyolojik gürültü yörüngelerini çiz (Görsel Kanıt)
        if sigma == 0.15:
            mean_trajectory = np.mean(pERK_trajectories, axis=0)
            std_trajectory = np.std(pERK_trajectories, axis=0)
            
            # Rastgele 5 örnek gerçek yörünge çizimi
            for i in range(5):
                plt.plot(t, pERK_trajectories[i, :], color='gray', alpha=0.3, linewidth=1)
                
            plt.plot(t, mean_trajectory, color='#0d47a1', linewidth=2.5, label='Homeostatic Mean [pERK]')
            plt.fill_between(t, mean_trajectory - 2*std_trajectory, mean_trajectory + 2*std_trajectory, 
                             color='#bbdefb', alpha=0.4, label='Physiological Ensembles (±2 SD)')

    # --- 3. Grafik Ayarları ---
    plt.axhline(cytotoxic_threshold, color='#d32f2f', linestyle='--', linewidth=1.5, label=f'Cytotoxic Threshold ({cytotoxic_threshold} μM)')
    plt.title('REAL Langevin SDE Monte Carlo Trajectory Ensemble & Error Bounds', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Time (Seconds)', fontsize=10)
    plt.ylabel('pERK Concentration (μM)', fontsize=10)
    plt.ylim([1.0, 4.0])
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='upper right', fontsize=9)
    
    # Çıktıyı doğrudan ana dizine veya figures klasörüne kaydedebilirsiniz
    plt.savefig('figures/stochastic_noise_trajectories.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("-" * 80)
    print("[SUCCESS] Gerçek SDE çözüldü. 'figures/stochastic_noise_trajectories.png' başarıyla üretildi.")
    print("=" * 80)

if __name__ == "__main__":
    run_real_stochastic_simulation()

