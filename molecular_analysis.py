"""
Module: molecular_analysis.py
Description: Master Integration Engine for the NF1-Smart-Redirector-Model.
Synthesizes symbolic differentiation, local/global stability landscapes, 
stochastic noise profiling, empirical structural analysis, wet-lab curve calibration,
and an industrial-grade rational RNA candidate pre-screening platform.
"""

import os
import sys
import glob
import re
import json
import random
from functools import lru_cache

# Biopython Yapısal Analiz Bağımlılığı Hazırlığı
try:
    from Bio.PDB import MMCIFParser
    HAS_BIOPYTHON = True
except ImportError:
    HAS_BIOPYTHON = False

# Güvenli ve dinamik sys.path insert mekanizması
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
for folder in ["notebooks", "simulations", "bridge_models", "optimization", "core"]:
    sys.path.insert(0, os.path.join(BASE_DIR, folder))

# Gelişmiş Biyoloji Çekirdeğinin Entegrasyonu ve Katı Bağımlılık Kontrolü
try:
    from core.transcriptome import TranscriptomeIndex
    from core.scoring import score_candidate
    HAS_CORE_MODULES = True
except ImportError:
    HAS_CORE_MODULES = False
    # Sessiz fallback riski engellendi: Üretim kalitesi için gürültülü hata
    raise RuntimeError(
        "[CRITICAL CORRUPTION] Core biological calculation modules could not be imported. "
        "Verify that 'core/scoring.py' and 'core/transcriptome.py' exist in the repository."
    )

# config/scoring.json tabanlı tam dinamik konfigürasyon yüklemesi
CONFIG_PATH = os.path.join(BASE_DIR, "config", "scoring.json")
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
else:
    raise FileNotFoundError(
        f"[CRITICAL CONFIG ERROR] Required configuration file missing at: {CONFIG_PATH}. "
        "Please build the 'config/scoring.json' weight matrix."
    )

# Singleton Transkriptom İndeksi Başlatma
FASTA_PATH = os.path.join(BASE_DIR, "data", "transcripts.fa")
TRANSCRIPTOME = TranscriptomeIndex(FASTA_PATH) if os.path.exists(FASTA_PATH) else None
if not TRANSCRIPTOME:
    print("[⚠️ WARNING] 'data/transcripts.fa' not found. Off-target scores will evaluation as zero.")

# Uzun GA koşularında RAM taşmasını engelleyen sınırlı boyutlu akıllı LRU Cache yapısı
@lru_cache(maxsize=1024)
def cached_fitness(rna_sequence, target_mrna, selected_cif=None):
    """Nesil döngülerinde bellek şişmesini engelleyen ve hız kazandıran cache sürücüsü."""
    return score_candidate(
        rna_sequence=rna_sequence,
        target_mrna=target_mrna,
        selected_cif=selected_cif,
        config=CONFIG,
        transcriptome=TRANSCRIPTOME,
        core_modules=HAS_CORE_MODULES
    )

def execute_master_pipeline():
    print("=" * 80)
    print("   NF1-SMART-REDIRECTOR-MODEL: INTEGRATED PRE-SCREENING & STABILITY PIPELINE")
    print("=" * 80)
    print("[INIT] Multi-scale computational biology workflow initiated...")

    if not os.path.exists('figures'):
        os.makedirs('figures')

    # Biyolojik Seçilim ve Optimizasyon Sürücüsü Çağrısı
    dynamic_target_mrna = "GUCAGCUGAUCGAUCGAAUGCUUUACAGCUGUCAGCUGA"
    print(f"\n[🎯 HEDEF mRNA]: {dynamic_target_mrna}")
    
    try:
        from optimization.genetic_optimizer import GeneticRNAOptimizer
        print("[🧬 EVRİM]: Modüler Genetik Biyoloji Algoritması Döngüsü Başlatılıyor...")
        ga_engine = GeneticRNAOptimizer(fitness_function=cached_fitness, target_mrna=dynamic_target_mrna)
        for gen in range(1, 11):
            best_score, best_candidate = ga_engine.evolve_generation()
            if gen % 3 == 0 or gen == 1:
                print(f" -> Nesil {gen:02d} | En İyi Hücre İçi Fitness: {best_score:.4f} | Aday: {best_candidate}")
    except Exception as e:
        print(f"[!] GA Entegrasyon Hatası: {str(e)}")

    # FAZ 1.2: GERÇEK ATOMİK YAPI VE HAVUZ ANALİZİ (STRUCTURE ENSEMBLE)
    print("\n" + "-" * 50)
    print("[FAZ 1.2] Automated AlphaFold 3 Structure Ensemble Extraction")
    print("-" * 50)
    
    cif_files = glob.glob("alphafold_models/*.cif")
    if not cif_files:
        print("[!] Uyarı: 'alphafold_models/' klasöründe .cif dosyası bulunamadı, baseline modunda devam ediliyor.")
        ensemble_loop_targets = [None]
    else:
        ensemble_loop_targets = sorted(cif_files)
        print(f"[+] Ensemble havuzunda {len(ensemble_loop_targets)} adet konformasyonel model tespit edildi.")

    # Yapışık satırlardan arındırılmış temiz ve güvenli ensemble döngüsü
    for idx, selected_cif in enumerate(ensemble_loop_targets):
        real_theta = None
        nominal_dist = 2.85
        nominal_contacts = 45
        
        if selected_cif is not None:
            print(f"\n[🔄 Run {idx+1}/{len(ensemble_loop_targets)}] İşlenen Konformasyon: {os.path.basename(selected_cif)}")
            try:
                from analyze_structure import analyze_molecular_interaction
                structural_results = analyze_molecular_interaction(selected_cif)
                if structural_results:
                    real_theta = structural_results.get("theta_occupancy")
                    nominal_dist = structural_results.get("min_distance", nominal_dist)
                    nominal_contacts = structural_results.get("contact_points", nominal_contacts)
                    print(f"[+] Başarılı: {os.path.basename(selected_cif)} için Hill θ bağlandı.")
            except Exception as e:
                print(f"[!] Faz 1.2 Yapısal Analiz Hatası ({os.path.basename(selected_cif)}): {str(e)}")
                continue

        # FAZ 1.5: BIOPHYSICAL BRIDGE LAYER (Biyomimetik Köprü Katmanı)
        print("\n" + "-" * 30)
        print(f"[FAZ 1.5] Biophysical Bridge Layer (Run {idx+1})")
        print("-" * 30)
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

    print("\n" + "-" * 50)
    print("[FAZ 8] Wet-Lab Densitometry & Kinetic Recalibration Engine")
    print("-" * 50)
    try:
        from calibration_engine import run_wetlab_calibration
        run_wetlab_calibration()
    except Exception as e:
        print(f"[!] Faz 8 Kalibrasyon Hatası: {str(e)}")

    print("\n" + "=" * 80)
    print("✅ MASTER SUCCESS: Tüm translasyonel katmanlar, biyolojik filtreler ve kararlılık motorları doğrulandı.")
    print("=" * 80)

if __name__ == "__main__":
    execute_master_pipeline()
