import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Veriyi oku
df_ens = pd.read_csv("ensemble_robustness_matrix.csv")

# İki boyutlu pivot tablolara dönüştür
pivot_mean = df_ens.pivot(index="Sigma", columns="Tau", values="Confinement_Mean")
pivot_std = df_ens.pivot(index="Sigma", columns="Tau", values="Confinement_Std")

# Görselleştirme şablonu (Yan yana iki panel: Mean ve Std)
fig, axes = plt.subplots(1, 2, figsize=(18, 7), sharey=True)
sns.set_style("ticks")

# Panel A: Ortalama Başarı (Her senaryonun genel performansı)
sns.heatmap(pivot_mean, ax=axes[0], cmap="viridis", vmin=0, vmax=1,
            cbar_kws={'label': 'Mean Confinement Score (<S_conf>)'})
axes[0].set_title("A) Attractor Confinement Ensemble Mean", fontsize=13, weight="bold", pad=12)
axes[0].set_xlabel("Memory Constant (τ in steps)", fontsize=11)
axes[0].set_ylabel("Damping / Volatility Coefficient (σ)", fontsize=11)
axes[0].invert_yaxis()

# Panel B: Standart Sapma (Kırılganlık ve Stokastik Hassasiyet)
sns.heatmap(pivot_std, ax=axes[1], cmap="magma", vmin=0, vmax=0.5,
            cbar_kws={'label': 'Standard Deviation (σ_conf)'})
axes[1].set_title("B) Ensemble Standard Deviation (Robustness Check)", fontsize=13, weight="bold", pad=12)
axes[1].set_xlabel("Memory Constant (τ in steps)", fontsize=11)
axes[1].set_ylabel("")
axes[1].invert_yaxis()

plt.suptitle("Multi-Seed Ensemble Robustness Analizi (N=20 Seeds)", fontsize=15, weight="bold", y=0.98)
plt.tight_layout()
plt.savefig("ensemble_robustness_heatmaps.png", dpi=300, bbox_inches="tight")
plt.show()
