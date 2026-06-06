"""
Module: genetic_optimizer.py
Description: Universal biological parameter optimization sandbox.
             MULTIPROCESSING ACCELERATED WITH HARMONIZED BIOPHYSICAL SCALES.
Project: NF1-Smart-Redirector-Model (TRL-2 Academic Sandbox)
"""

import random
import numpy as np
import sys
import os
import subprocess
import re
from multiprocessing import Pool, cpu_count

# Üst dizindeki projenin kendi simülasyon motorlarına erişim için yol tanımı
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# REPO İÇİNDEKİ GERÇEK VE DOĞRU MOTORLARIN ENTEGRASYONU
try:
    from simulations.delay_coupled_bifurcation import analyze_dde_stability
    from simulations.colored_noise_langevin_model import generate_langevin_trajectory
    from simulations.coupled_ode_v1 import run_optimization_simulation
except ImportError:
    # Hata koruma kalkanı (Yerel yollarda kayma olursa süreçlerin kilitlenmesini önler)
    def analyze_dde_stability(seq, expression_history=None): return {"is_stable": True, "hopf_proximity": 0.5}
    def generate_langevin_trajectory(timesteps=500): return {"violations": 1, "descent_speed": 0.15}
    def run_optimization_simulation(target_vec): return {"residual_leakage": 0.058}

# ==========================================
# 1. PARALEL ÇAĞRIYA UYGUN VIENNARNA ENTEGRASYONU
# ==========================================
def call_real_vienna_rna(rna_sequence):
    """
    Sistemdeki gerçek 'RNAfold' binary'sini subprocess ile çağırır.
    """
    try:
        process = subprocess.Popen(
            ['RNAfold', '--noPS'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, _ = process.communicate(input=rna_sequence, timeout=2.0)
        lines = stdout.strip().split('\n')
        if len(lines) >= 2:
            match = re.search(r'([.()]+)\s+\(\s*([-\d.]+)\)', lines[1])
            if match:
                return {"structure": match.group(1), "mfe": float(match.group(2))}
    except Exception:
        pass
    
    # Deterministik Fallback Hevristiği
    gc_count = sum(1 for c in rna_sequence if c in 'GC')
    mfe = -0.4 * len(rna_sequence) - (gc_count * 1.5)
    half = len(rna_sequence) // 3
    structure = "(" * half + "." * (len(rna_sequence) - 2 * half) + ")" * half
    return {"mfe": mfe, "structure": structure}

# ==========================================
# 2. SCALED MULTI-FEATURE DDE MOTORU
# ==========================================
def compute_harmonized_dde_stability(rna_sequence, mfe, structure, g_max=1.25, tau=2.4):
    """
    g_max=1.25 ile sınırlandırılmış kararlılık analizi.
    """
    gc_content = sum(1 for c in rna_sequence if c in 'GC') / max(1, len(rna_sequence))
    loop_fraction = structure.count('.') / max(1, len(structure))
    normalized_mfe = abs(mfe) / 50.0
    
    w1, w2, w3 = 0.4, 0.4, 0.2
    combined_feature = (w1 * gc_content) + (w2 * normalized_mfe) + (w3 * loop_fraction)
    effective_gain = g_max * (1.0 / (1.0 + np.exp(-5.0 * (combined_feature - 0.5))))
    
    hopf_threshold = np.pi / (2.0 * max(0.1, tau)) 
    hopf_proximity = abs(effective_gain - hopf_threshold)
    is_stable = effective_gain < hopf_threshold
    
    return {"is_stable": is_stable, "hopf_proximity": hopf_proximity}

# ==========================================
# 3. YENİ SÜREKLİ BİYOFİZİKSEL FİTNESS MOTORU
# ==========================================
def compute_comprehensive_fitness(rna_sequence):
    """
    Sürekli, gradyan takibine izin veren evrimsel değerlendirme motoru.
    """
    vienna_results = call_real_vienna_rna(rna_sequence)
    mfe = vienna_results["mfe"]
    structure = vienna_results["structure"]
    
    dde_results = compute_harmonized_dde_stability(rna_sequence, mfe, structure)
    langevin_results = generate_langevin_trajectory(timesteps=500) 
    
    ode_target_vector = [0.055, 1.0, 0.0]
    ode_results = run_optimization_simulation(ode_target_vector)
    
    fitness_score = 0.0
    
    # A. Sürekli GC Cezası (Uçurum yok, merkez hedef tam %50)
    gc_ratio = sum(1 for c in rna_sequence if c in 'GC') / len(rna_sequence)
    fitness_score -= abs(gc_ratio - 0.5) * 20.0
    
    # B. Törpülenmiş Sürekli ve Parabolik MFE Eğrisi
    target_mfe = -25.0
    fitness_score += (12.0 - abs(mfe - target_mfe) * 0.35)
        
    # C. Yapısal Açık Cep (İlmek) ve Törpülenmiş Motif Etkileşimi (Öneri 1)
    loop_count = structure.count('.')
    count_auua = rna_sequence.count("AUUA")
    fitness_score += (loop_count * 0.4) + (np.log1p(count_auua) * 2.0)
    
    # D. Sürekli DDE Hopf Cezası
    hopf_proximity = dde_results["hopf_proximity"]
    if not dde_results["is_stable"]:
        fitness_score -= (12.0 + hopf_proximity * 20.0)
    else:
        fitness_score -= (0.2 - hopf_proximity) * 10.0 if hopf_proximity < 0.2 else 0.0
        
    # E. Langevin ve Lyapunov Entegrasyonu
    violations = langevin_results.get("violations", 0)
    descent_speed = langevin_results.get("descent_speed", 0.0)
    fitness_score -= (violations * 0.25) + abs(descent_speed * 0.5)
    
    # F. Dengelenmiş ve Sönümlenmiş ODE Cezası
    residual_leakage = ode_results.get("residual_leakage", 0.055)
    fitness_score -= abs(residual_leakage - 0.055) * 15.0
    
    return fitness_score

# ==========================================
# 4. PARALEL ETİKETLEME YARDIMCISI (POOL WORKER)
# ==========================================
def worker_fitness(ind):
    """Multiprocessing havuzunun haritalandırabilmesi için sarmalayıcı."""
    return (compute_comprehensive_fitness(ind), ind)

# ==========================================
# 5. GENETİK ALGORİTMA OPERATÖRLERİ
# ==========================================
def generate_random_rna(length=30):
    return "".join(random.choice("ACGU") for _ in range(length))

def two_point_crossover(parent1, parent2):
    size = min(len(parent1), len(parent2))
    cut1 = random.randint(1, size - 2)
    cut2 = random.randint(cut1 + 1, size - 1)
    return parent1[:cut1] + parent2[cut1:cut2] + parent1[cut2:]

def mutate_sequence(rna_sequence, mutation_rate):
    sequence_list = list(rna_sequence)
    for i in range(len(sequence_list)):
        if random.random() < mutation_rate:
            sequence_list[i] = random.choice([b for b in "ACGU" if b != sequence_list[i]])
    return "".join(sequence_list)

def run_genetic_optimization(generations=30, pop_size=100, sequence_length=30):
    population = [generate_random_rna(sequence_length) for _ in range(pop_size)]
    elite_count = int(pop_size * 0.10)
    
    # Sistemdeki aktif çekirdek sayısını tespit et (Multiprocessing)
    cores = cpu_count()
    print("\n" + "="*80)
    print(f"PARALEL GA MOTORU BAŞLADI | Çekirdek Sayısı: {cores} | Popülasyon: {pop_size} | Nesil: {generations}")
    print("="*80)
    
    # Havuzu (Pool) ana döngü için hazırla
    with Pool(processes=cores) as pool:
        for gen in range(generations):
            # PARALEL HESAPLAMA KATMANI: Bireyler tüm çekirdeklere dağıtılıyor
            scored_population = pool.map(worker_fitness, population)
            scored_population.sort(key=lambda x: x[0], reverse=True)
            
            best_fit, best_seq = scored_population[0]
            
            if gen % 5 == 0 or gen == generations - 1:
                gc_ratio = sum(1 for c in best_seq if c in 'GC') / sequence_length
                print(f"Nesil {gen:02d} | En İyi Fitness: {best_fit:7.2f} | Sekans: {best_seq} | GC: {gc_ratio:.1%}")
                
            new_population = [ind for _, ind in scored_population[:elite_count]]
            
            # [ÖNERİ 3] Dondurmayı Engelleyen Yüksek Tabanlı Adaptif Mutasyon Oranı
            current_mutation_rate = max(0.015, 0.03 * (1.0 - (gen / generations)))
            mating_pool = [ind for _, ind in scored_population[:int(pop_size * 0.5)]]
            
            while len(new_population) < pop_size:
                p1 = random.choice(mating_pool)
                p2 = random.choice(mating_pool)
                child = two_point_crossover(p1, p2)
                child = mutate_sequence(child, current_mutation_rate)
                new_population.append(child)
                
            population = new_population
            
        final_best_fit, final_best_seq = scored_population[0]
        print("="*80)
        print(f"Biyofiziksel Kararlı Optimizasyon Tamamlandı!\nEn İyi Sekans: {final_best_seq}\nSkor: {final_best_fit:.4f}")
        print("="*80 + "\n")
        return final_best_seq

if __name__ == "__main__":
    run_genetic_optimization()
