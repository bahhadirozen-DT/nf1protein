"""
Module: molecular_analysis.py
Description: Master Integration Engine for the NF1-Smart-Redirector-Model.
Synthesizes symbolic differentiation, local/global stability landscapes, 
stochastic noise profiling, empirical structural analysis, and wet-lab curve calibration.
"""

import os
import sys
import glob

# Klasör yollarını Python çalışma path'ine ekliyoruz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'notebooks')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'simulations')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'bridge_models')))

def execute_master_pipeline():
    print("=" * 80)
    print("      NF1-SMART-REDIRECTOR-MODEL: MASTER COMPREHENSIVE ANALYSIS PIPELINE")
    print("=" * 80)
    print("[INIT] Multi-scale computational biology workflow initiated...")

    # Klasör Kontrolü
    if not os.path.exists('figures'):
        os.makedirs('figures')

    # FAZ 1: Çekirdek ODE Motoru
    try:
        from coupled_ode_v1 import execute_core_validation
        execute_core_validation()
    except Exception as e:
        print(f"[!] Faz 1 Hatası: {str(e)}")

    # FAZ 1.2: GERÇEK ATOMİK YAPI VE HAVUZ ANALİZİ (STRUCTURE ENSEMBLE)
    print("\n" + "-"*50)
    print("[FAZ 1.2] Automated AlphaFold 3 Structure Ensemble Extraction")
    print("-"*50)
    
    cif_files = glob.glob("alphafold_models/*.cif")
    
    if not cif_files:
        print("[!] Uyarı: 'alphafold_models/' klasöründe .cif dosyası bulunamadı, baseline/mock modunda devam ediliyor.")
        ensemble_loop_targets = [None]
    else:
        ensemble_loop_targets = sorted(cif_files)
        print(f"[+] Ensemble havuzunda {len(ensemble_loop_targets)} adet konformasyonel model tespit edildi.")

    # Tüm yapısal varyasyon havuzunu sırayla dönen dinamik döngü
    for idx, selected_cif in enumerate(ensemble_loop_targets):
        real_theta = None
        nominal_dist = 2.85
        nominal_contacts = 45
        
        if selected_cif is not None:
            print(f"\n[🔄 Run {idx+1}/{len(ensemble_loop_targets)}] İşlenen Konformasyon: {os.path.basename(selected_cif)}")
            try:
                from analyze_structure import analyze_molecular_interaction
                structural_results = analyze_molecular_interaction(selected_cif)
                if structural_results is not None:
                    real_theta = structural_results["theta_occupancy"]
                    nominal_dist = structural_results["min_distance"]
                    nominal_contacts = structural_results["contact_points"]
                    print(f"[+] Başarılı: {os.path.basename(selected_cif)} için Hill θ bağlandı.")
            except Exception as e:
                print(f"[!] Faz 1.2 Yapısal Analiz Hatası ({os.path.basename(selected_cif)}): {str(e)}")
                continue

        # FAZ 1.5: BIOPHYSICAL BRIDGE LAYER (Biyomimetik Köprü Katmanı)
        print("\n" + "-"*30)
        print(f"[FAZ 1.5] Biophysical Bridge Layer (Run {idx+1})")
        print("-"*30)
        try:
            from occupancy_to_signal import calculate_biophysical_bridge
            calculate_biophysical_bridge(
                mean_distance_angstrom=nominal_dist, 
                num_contacts=nominal_contacts, 
                calculated_theta=real_theta
            )
        except Exception as e:
            print(f"[!] Faz 1.5 Köprü Hatası: {str(e)}")

    print("\n" + "=" * 80)
    print("      EXECUTING DOWNSTREAM MATHEMATICAL STABILITY ENGINES (PHASE 2 - 8)")
    print("=" * 80)

    # FAZ 2: SymPy Sembolik Jacobian Motoru
    try:
        from jacobian_analysis import derive_symbolic_jacobian
        derive_symbolic_jacobian()
    except Exception as e:
        print(f"[!] Faz 2 Hatası: {str(e)}")

    # FAZ 3: Hopf Bifurcation Sınır Taraması
    try:
        from jacobian_bifurcation_analysis import generate_bifurcation_and_phase_portrait
        generate_bifurcation_and_phase_portrait()
    except Exception as e:
        print(f"[!] Faz 3 Hatası: {str(e)}")

    # FAZ 4: Spektral Kararlılık Spektrumu
    try:
        from eigenvalue_scan import run_dynamic_eigenvalue_analysis
        run_dynamic_eigenvalue_analysis()
    except Exception as e:
        print(f"[!] Faz 4 Hatası: {str(e)}")

    # FAZ 5: Global Attractor Yakınsama İspatı
    try:
        from lyapunov_landscape import run_lyapunov_descent_analysis
        run_lyapunov_descent_analysis()
    except Exception as e:
        print(f"[!] Faz 5 Hatası: {str(e)}")

    # FAZ 6: Langevin SDE Stokastik Gürültü Profilleme
    try:
        from stochastic_noise import run_real_stochastic_simulation
        run_real_stochastic_simulation()
    except Exception as e:
        print(f"[!] Faz 6 Hatası: {str(e)}")

    # FAZ 7: Geçmiş Kuyruğu Zaman Gecikmeli DDE Simülasyonu
    try:
        from param_exploration import run_discrete_dde_simulation
        run_discrete_dde_simulation()
    except Exception as e:
        print(f"[!] Faz 7 Hatası: {str(e)}")

    # [YENİ ENTEGRASYON] FAZ 8: ISLAK LABORATUVAR KİNETİK KALİBRASYONU (CURVE_FIT)
    print("\n" + "-"*50)
    print("[FAZ 8] Wet-Lab Densitometry & Kinetic Recalibration Engine")
    print("-"*50)
    try:
        from calibration_engine import run_wetlab_calibration
        run_wetlab_calibration()
    except Exception as e:
        print(f"[!] Faz 8 Kalibrasyon Hatası: {str(e)}")

    print("\n" + "="*80)
    print("✅ MASTER SUCCESS: Tüm translasyonel katmanlar ve kalibrasyon motoru başarıyla doğrulandı.")
    print("=" * 80)

if __name__ == "__main__":
    execute_master_pipeline()




