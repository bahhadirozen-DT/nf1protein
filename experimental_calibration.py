"""
Module: experimental_calibration.py
Description: Advanced systems pharmacology calibration bridge connecting 
structural ensemble accessibility probabilities directly to dose-response models.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def dynamic_pharmacology_bridge(dose, bottom_floor, top_accessibility, ec50, hill_coeff):
    """
    4PL Hill Equation modified with structural ensemble parameters.
    top_accessibility represents the integrated structural P_access value.
    bottom_floor represents the non-zero stochastic leakage/compensatory reactivation.
    """
    return bottom_floor + (top_accessibility - bottom_floor) / (1.0 + (dose / ec50)**hill_coeff)

def run_calibrated_pipeline():
    print("=" * 80)
    print("🔬 ADVANCED PHARMACOKINETIC BRIDGE: STRUCTURAL ENSEMBLE TO DOWNSTREAM SIGNALING")
    print("=" * 80)

    # 1. Structural Input Connection (Simulating dynamic provenance tracking)
    # Integrated structural accessibility distribution value derived from AF3 SASA/BSA
    integrated_p_access = 0.94  # Top roof governed by structure flexibility
    
    # 2. Heuristic Pseudo-Experimental Benchmark Dataset (With realistic biological noise)
    deneysel_dozlar = np.array([0.0, 0.1, 1.0, 10.0, 50.0, 100.0, 500.0, 1000.0])
    # Biological residual floor integrated: signaling never drops to absolute zero
    pseudo_experimental_signals = np.array([0.94, 0.90, 0.81, 0.54, 0.28, 0.16, 0.09, 0.08])
    # Assumed standard deviation representing wet-lab pipetting/lysis variances
    experimental_errors = np.array([0.02, 0.03, 0.03, 0.04, 0.03, 0.02, 0.02, 0.01])

    print("[-] Fitting pseudo-experimental benchmark data onto the integrated structural topology...")
    
    # 3. Constrained Curve Fitting via Scipy
    # Bounds enforce the biological floor (0.05 - 0.15) and tether the top to structural P_access
    baslangic_tahmini = [0.08, integrated_p_access, 10.0, 1.0]
    parametre_sinirlari = ([0.05, 0.85, 0.1, 0.2], [0.15, 1.0, 100.0, 3.5])

    popt, pcov = curve_fit(
        dynamic_pharmacology_bridge, 
        deneysel_dozlar, 
        pseudo_experimental_signals, 
        p0=baslangic_tahmini,
        bounds=parametre_sinirlari,
        sigma=experimental_errors,
        absolute_sigma=True
    )
    
    bottom_fit, top_fit, ec50_proxy, n_hill = popt
    std_err = np.sqrt(np.diag(pcov))

    print("\n[+] SPEKTRAL KALİBRASYON BAŞARILI | MODEL PARAMETRELERİ:")
    print(f"--> Model-Derived Apparent EC50 Proxy : {ec50_proxy:.2f} ± {std_err[2]:.2f} nM")
    print(f"--> Hill Cooperation Coefficient (nH) : {n_hill:.2f} ± {std_err[3]:.2f}")
    print(f"--> Residual Leakage Floor (Adaptive) : {bottom_fit:.3f}")
    print(f"--> Structural Roof (P_access Limit)  : {top_fit:.3f}")

    # 4. High-Fidelity Semi-Logarithmic Visualization
    plt.figure(figsize=(9, 6.5))
    doz_uzayi = np.logspace(-2, 3.5, 600)
    fit_egrisi = dynamic_pharmacology_bridge(doz_uzayi, *popt)

    # Plot lines & areas
    plt.semilogx(doz_uzayi, fit_egrisi, color='#2ca02c', linewidth=2.5, 
                 label=f'Systems Model Fit ($n_H$: {n_hill:.2f})')
    
    # Error bar integration for high scientific transparency
    plt.errorbar(deneysel_dozlar, pseudo_experimental_signals, yerr=experimental_errors, 
                 fmt='o', color='#d62728', elinewidth=2, capsize=4, ms=6, zorder=5,
                 label='Heuristic Pseudo-Experimental Data ($\pm$ SD)')
    
    # Annotations
    plt.axvline(x=ec50_proxy, color='gray', linestyle=':', alpha=0.8,
                label=f'Model Apparent $EC_{50}$: {ec50_proxy:.2f} nM')
    
    # Highlight the residual leakage layer (The biological compromise floor)
    plt.axhline(y=bottom_fit, color='#ff7f0e', linestyle='--', alpha=0.5, 
                label=f'Adaptive Residual Leakage Floor ({bottom_fit*100:.1f}%)')

    # Styling & Axes Metrology
    plt.title('SRX-RNA01 Conformational Calibration & Dose-Response Model', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('SRX-RNA01 Concentration Log(nM)', fontsize=11)
    plt.ylabel('Relative Signal Intensity ($pERK / tERK$ ratio)', fontsize=11)
    plt.ylim(-0.02, 1.05)
    plt.grid(True, which="both", linestyle=':', alpha=0.4)
    plt.legend(loc='lower left', fontsize=9.5, frameon=True, shadow=False)
    
    # Save step overriding the old idealist graph
    if not os.path.exists('figures'): os.makedirs('figures')
    plt.savefig('figures/experimental_dose_response_calibration.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("\n[+] Kurşun geçirmez yeni grafik 'figures/experimental_dose_response_calibration.png' olarak güncellendi.")
    print("=" * 80)

if __name__ == "__main__":
    run_calibrated_pipeline()
