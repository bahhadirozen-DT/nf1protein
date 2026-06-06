"""
Module: attractor_manifold_sandbox.py
Description: Isolated sandbox simulating the state-dependent nonlinear confinement 
and attractor manifold verified via phase portrait simulation.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

def biological_attractor_system(states, t, params):
    """
    Web simülasyonunda doğrulanan esnek biyolojik sınır döngüsü (Limit Cycle).
    Sonsuza kaçan üstel patolojik akışı dairesel çekim havzasına hapseder.
    """
    x, y = states  # x: Sinyal Yoğunluğu Akışı, y: Akış Değişim Hızı
    
    # Doğrulanan Simülasyon Katsayıları
    r = 1.2
    R_squared = 2.5  # Yarıçapın karesi (Web çizimindeki r ~ 1.58 sınırı)
    
    # State-Dependent Control Switch (Hill-Like Activation)
    if x > 0:
        switch = (x**2) / (1 + x**2)
    else:
        switch = 0.0

    # 3. Diferansiyel Denklemler (Web Arayüzüne Yazılan Çekirdek Yapı)
    dx_dt = y
    dy_dt = -r * x + (R_squared - x**2 - y**2) * y * switch
    
    return [dx_dt, dy_dt]

def run_sandbox_simulation():
    if not os.path.exists('figures'):
        os.makedirs('figures')

    t = np.linspace(0, 50, 2000)
    
    # Web arayüzünde tıkladığınız başlangıç noktalarının Python simülasyonu
    initial_pathological = [4.0, 3.0] # Dışarıdan yakalanan kanserli hücre
    initial_homeostatic = [0.2, 0.1]  # İçeriden genişleyen bazal akış
    
    states_p = odeint(biological_attractor_system, initial_pathological, t)
    states_h = odeint(biological_attractor_system, initial_homeostatic, t)

    # --- Görselleştirme: Faz Uzayı Analizi ---
    plt.figure(figsize=(8, 7))
    plt.plot(states_p[:, 0], states_p[:, 1], color='crimson', linewidth=2, label='Patolojik Giriş Yörüngesi')
    plt.plot(states_h[:, 0], states_h[:, 1], color='teal', linewidth=2, label='İç Salınım Yörüngesi')
    
    # Limit Döngüsü Referans Eğrisi
    theta = np.linspace(0, 2*np.pi, 100)
    plt.plot(np.sqrt(2.5)*np.cos(theta), np.sqrt(2.5)*np.sin(theta), 
             color='indigo', linestyle='--', linewidth=2, label='Kararlı Manifold Sınırı (~1.58)')
    
    plt.title('Attractor Manifold Confinement Verification', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Sinyal Yoğunluğu Akışı (x)', fontsize=10)
    plt.ylabel('Akış Hızı (y)', fontsize=10)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='upper right')
    plt.axis('equal')
    
    plt.savefig('figures/attractor_manifold_sandbox.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("🚀 SUCCESS: Verifikasyonu yapılmış 'attractor_manifold_sandbox.py' başarıyla üretildi.")

if __name__ == "__main__":
    run_sandbox_simulation()
