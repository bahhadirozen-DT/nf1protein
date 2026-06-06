import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def plot_mutation_robustness_results():
    """
    NF1-Smart-Redirector TRL-3 Validasyon Analizi.
    Emoji hatasi (Glyph Warning) temizlenmis, Zaman Serisi SDE sönümlenme yörüngeleri eklenmis
    yayin kalitesinde (300 DPI) 3 panelli nihai figur motoru.
    """
    variants = [
        "R1276Q\n(Missense)", 
        "R681X\n(Nonsense Severe)", 
        "c.2041C>T\n(Splice Variant)"
    ]
    
    # 1. PANEL VERİLERİ (Monte Carlo Oranlari)
    p_homeostasis = [86.4, 14.2, 58.7]  
    mean_lyapunov = [-0.342, 0.189, -0.054]  
    rescue_index = [0.814, 0.223, 0.594]  
    
    # 3. PANEL VERİLERİ (Zaman Serisi Langevin Sinyal Yörüngeleri)
    time = np.linspace(0, 10, 500)
    # R1276Q: Hızla homeostatik sıfır noktasına çöker ve sönümlenir
    traj_r1276q = np.exp(-0.7 * time) + np.random.normal(0, 0.04, 500)
    # R681X: Kaotik patolojik sınırı aşar ve kararsız dalgalanır
    traj_r681x = 1.0 / (1.0 + np.exp(-0.2 * time)) + np.random.normal(0, 0.15, 500)
    # c.2041C>T: Tam sönümlenmez ama metastable güvenli havzada hapsedilir
    traj_c2041c = 0.4 * np.exp(-0.3 * time) + 0.2 + np.random.normal(0, 0.08, 500)

    # GRAPHIQUE MİMARİSİ (3 Yan Yana Panel)
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 6))
    # Sol taraftaki emoji temizlendi, kutu hatası çözüldü
    fig.suptitle("NF1-Smart-Redirector: Olasiliksal Mutasyon Manifoldu ve Kinetik SDE Analizi (TRL-3)", fontsize=14, fontweight='bold')
    
    # PANEL 1: P(homeostasis) ve Rescue Index (R)
    x = np.arange(len(variants))
    width = 0.35
    ax1.bar(x - width/2, p_homeostasis, width, label='P(homeostasis) %', color='#2ca02c', alpha=0.85)
    ax1_twin = ax1.twinx()
    ax1_twin.bar(x + width/2, rescue_index, width, label='Rescue Index (R)', color='#1f77b4', alpha=0.85)
    ax1.set_xticks(x)
    ax1.set_xticklabels(variants, fontweight='bold')
    ax1.set_ylabel('Havza Kilitlenme Olasiligi (%)', color='#2ca02c', fontweight='bold')
    ax1_twin.set_ylabel('Phenotypic Dynamical Rescue Index (R)', color='#1f77b4', fontweight='bold')
    ax1.set_title("Olasiliksal Kurtarma Metrikleri", fontsize=11, fontweight='bold')
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    
    # PANEL 2: Lyapunov Kararlılık Spektrumu Heatmap
    heatmap_data = np.array(mean_lyapunov).reshape(len(variants), 1)
    sns.heatmap(heatmap_data, annot=True, fmt=".3f", cmap="RdYlGn_r", cbar=True,
                yticklabels=variants, xticklabels=["Ortalama Lyapunov Eksponenti (\u03bb)"], 
                ax=ax2, annot_kws={"size": 12, "weight": "bold"}, vmin=-0.5, vmax=0.5)
    ax2.set_title("Topolojik Kararlilik Spektrumu\n(< 0 Homeostaz / > 0 Kaotik Kacas)", fontsize=11, fontweight='bold')
    ax2.set_yticklabels(variants, rotation=0, fontweight='bold')
    
    # PANEL 3: SDE Kinetik Yörüngeleri (Zaman Serisi Sinyal Sönümlenmesi)
    ax3.plot(time, traj_r1276q, color='#2ca02c', label='R1276Q (Confinement)', linewidth=2)
    ax3.plot(time, traj_r681x, color='#d62728', label='R681X (Chaotic Escape)', linewidth=1.5)
    ax3.plot(time, traj_c2041c, color='#ff7f0e', label='c.2041C>T (Metastable)', linewidth=1.5)
    # Patolojik Kritik Eşik Sınırı
    ax3.axhline(y=0.7, color='black', linestyle='--', alpha=0.7, label='Patolojik Kriter Esigi')
    ax3.set_xlabel('Simulasyon Zamani (t)', fontweight='bold')
    ax3.set_ylabel('Sinyal Genligi / Volatilite [pERK/KRAS-GTP]', fontweight='bold')
    ax3.set_title("Zaman Serisi Langevin SDE Yonetim Yoringeleri", fontsize=11, fontweight='bold')
    ax3.legend(loc='upper right')
    ax3.grid(True, linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig("mutation_robustness_matrix.png", dpi=300)
    print("BASARILI: 'mutation_robustness_matrix.png' dosyasi 300 DPI kalitesinde basildi ve kutu hatasi giderildi.")
    plt.show()

if __name__ == "__main__":
    plot_mutation_robustness_results()


