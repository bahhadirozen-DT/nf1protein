# notebooks/global_confinement_validation.py
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Üst dizindeki simulations modülünü import edebilmek için path ayarı
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simulations.confinement_analyzer import GlobalStabilityEngine

if __name__ == "__main__":
    engine = GlobalStabilityEngine()
    x_space = np.linspace(-2.5, 2.5, 250)
    y_space = np.linspace(-2.5, 2.5, 250)
    X, Y = np.meshgrid(x_space, y_space)

    V_dot_map = engine.calculate_lyapunov_derivative(X, Y)

    noise_levels = [0.4, 0.9, 1.6]
    escape_results = {sigma: engine.run_stochastic_escape_test(sigma=sigma) for sigma in noise_levels}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # GRAFİK 1: Lyapunov Türev Analizi
    contour = ax1.contourf(X, Y, V_dot_map, levels=30, cmap='coolwarm', vmin=-10, vmax=10)
    cbar = fig.colorbar(contour, ax=ax1)
    cbar.set_label(r'Lyapunov Derivative $\dot{V}(x,y)$', rotation=270, labelpad=15)

    theta = np.linspace(0, 2*np.pi, 200)
    ellipse_x = engine.R * np.sqrt(engine.gamma) * np.cos(theta)
    ellipse_y = (engine.R / np.sqrt(engine.gamma)) * np.sin(theta)
    ax1.plot(ellipse_x, ellipse_y, 'k--', lw=2, label='Attractor Valley Floor')
    ax1.set_title(r"Global Stability: $\dot{V}$ Dissipation Zones")
    ax1.set_xlabel("Signaling Amplitude (x)")
    ax1.set_ylabel("Activity Flux Velocity (y)")
    ax1.legend()

    # GRAFİK 2: Stres Testi
    labels = [f"Extreme 1\n(sigma={noise_levels[0]})", f"Extreme 2\n(sigma={noise_levels[1]})", f"Breakdown\n(sigma={noise_levels[2]})"]
    values = [escape_results[noise_levels[0]], escape_results[noise_levels[1]], escape_results[noise_levels[2]]]

    ax2.bar(labels, values, color=['#34a853', '#1a73e8', '#d93025'], width=0.5)
    ax2.set_title("Stochastic Basin Escape Probability (Stress Test)")
    ax2.set_ylabel("Escape Probability (%)")
    ax2.set_ylim([0, 105])
    ax2.grid(True, linestyle=':', axis='y')

    for i, v in enumerate(values):
        ax2.text(i, v + 2, f"{v:.1f}%", ha='center', fontweight='bold')

    plt.tight_layout()
    # Çıktıyı doğrudan figures klasörünüze kaydeder
    plt.savefig('figures/global_confinement_proof.png', dpi=300)
    print("[BAŞARILI] Analiz tamamlandı. Grafik 'figures/global_confinement_proof.png' adresine kaydedildi.")
    plt.show()
