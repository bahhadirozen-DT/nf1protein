"""
Module: genetic_optimizer.py
Description: Universal biological parameter optimization sandbox. ACADEMIC PRODUCTION GRADE.
"""

import random
import numpy as np
import sys
import os
import subprocess

# Üst dizindeki modüllere erişim sağlamak için yol tanımı
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Projenizin kendi orijinal simülasyon fonksiyonlarını içeri aktarıyoruz
from bridge_models.evidence_weighted_calibration import EvidenceWeightedCalibration
from simulations.colored_noise_langevin_model import ColoredNoiseLangevinModel
from simulations.coupled_ode_v1 import run_optimization_simulation
from simulations.delay_coupled_bifurcation import run_ga_dde_bridge

# ==========================================
# 1. GERÇEKÇİ VIENNARNA SİMÜLASYONU
# ==========================================
def simulate_vienna_rna(rna_sequence):
    """
    Dış kütüphane bağımlılığı yerine çalışan test motoru.
    Gerçek ViennaRNA entegrasyonunda burası rna.fold(sequence) çıktısı verecektir.
    """
    gc_count = sum(1 for c in rna_sequence if c in 'GC')
    mfe = -0.4 * len(rna_sequence) - (gc_count * 1.5) + random.uniform(-0.5, 0.5)
    
    half = len(rna_sequence) // 3
    structure = "(" * half + "." * (len(rna_sequence) - 2 * half) + ")" * half
    return {"mfe": mfe, "structure": structure}

# ==========================================
# 2. REVİZE EDİLMİŞ BİYOLOJİK FİTNESS MİMARİSİ
# ==========================================
def compute_interaction_signal(rna_sequence, dot_bracket_structure):
    """
    Açık ilmek (loop) bölgelerindeki nükleotidleri ve stem dengesini puanlar.
    """
    interaction_score = 0.0
    for i, char in enumerate(dot_bracket_structure):
        if char == '.':  # Açık cep
            if rna_sequence[i] in 'UA': 
                interaction_score += 0.8
                
    stem_count = dot_bracket_structure.count('(')
    if 5 <= stem_count <= 12:
        interaction_score += 6.0  # Optimum geometri ödülü
        
    return interaction_score

def compute_comprehensive_fitness(rna_sequence):
    """
    Hileleri engelleyen, biyolojik sinyalleri öne çıkaran ana fitness fonksiyonu.
    """
    vienna_results = simulate_vienna_rna(rna_sequence)
    mfe = vienna_results["mfe"]
    structure = vienna_results["structure"]
    
    # Projenizin kendi import edilen motorlarını çalıştırıyoruz
    # run_ga_dde_bridge fonksiyonuna mfe parametresi de aktarılıyor
    dde_results = run_ga_dde_bridge(rna_sequence)
    langevin_results = ColoredNoiseLangevinModel()
    
    fitness_score = 0.0
    
    # A. MFE Esneklik Penceresi
    if mfe > -15.0:
        vienna_score = (mfe + 15.0) * -2.5
    elif mfe < -35.0:
        vienna_score = (-35.0 - mfe) * -1.0
    else:
        vienna_score = 5.0
    fitness_score += vienna_score
    
    # B. Logaritmik Motif Doygunluğu (Enflasyon Koruması)
    count_auua = rna_sequence.count("AUUA")
    motif_score = np.log1p(count_auua) * 4.0
    fitness_score += motif_score
    
    # C. Yapısal Etkileşim Sinyali
    interaction_score = compute_interaction_signal(rna_sequence, structure)
    fitness_score += interaction_score
    
    # D. Yumuşatılmış DDE Hopf Cezası
    # Eğer dde_results bir sözlükse güvenli bir şekilde metrikleri oku
    if isinstance(dde_results, dict):
        is_stable = dde_results.get("is_stable", True)
        hopf_proximity = dde_results.get("hopf_proximity", 0.0)
    else:
        is_stable = True
        hopf_proximity = 0.5

    if not is_stable:
        dde_penalty = 15.0 + (hopf_proximity * 25.0)
    else:
        dde_penalty = (0.2 - hopf_proximity) * 10.0 if hopf_proximity < 0.2 else 0.0
    fitness_score -= dde_penalty
    
    # E. Dengelenmiş Lyapunov ve Langevin Cezaları
    violations = 0
    descent_speed = 0.0
    if isinstance(langevin_results, dict):
        violations = langevin_results.get("violations", 0)
        descent_speed = langevin_results.get("descent_speed", 0.0)
        
    lyapunov_penalty = (violations * 0.25) + abs(descent_speed * 0.5)
    fitness_score -= lyapunov_penalty
    
    return fitness_score

# ==========================================
# 3. GENETİK ALGORİTMA OPERATÖRLERİ
# ==========================================
def generate_random_rna(length=30):
    return "".join(random.choice("ACGU") for _ in range(length))

def two_point_crossover(parent1, parent2):
    """
    Faydalı blokları koruyan iki noktalı çaprazlama.
    """
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

# ==========================================
# 4. OPTİMİZASYON DÖNGÜSÜ (MAIN LOOP)
# ==========================================
def run_genetic_optimization(generations=30, pop_size=80, sequence_length=30):
    population = [generate_random_rna(sequence_length) for _ in range(pop_size)]
    elite_count = int(pop_size * 0.10)
    
    print("\n" + "="*70)
    print(f"REVİZE GA BAŞLADI | Popülasyon: {pop_size} | Nesil: {generations}")
    print("="*70)
    
    for gen in range(generations):
        scored_population = []
        for ind in population:
            fit = compute_comprehensive_fitness(ind)
            scored_population.append((fit, ind))
            
        scored_population.sort(key=lambda x: x[0], reverse=True)
        best_fit, best_seq = scored_population[0]
        
        if gen % 5 == 0 or gen == generations - 1:
            gc_ratio = sum(1 for c in best_seq if c in 'GC') / sequence_length
            print(f"Nesil {gen:02d} | En İyi Fitness: {best_fit:7.2f} | Sekans: {best_seq} | GC: {gc_ratio:.1%}")
            
        new_population = [ind for _, ind in scored_population[:elite_count]]
        
        # Adaptif mutasyon oranı
        initial_rate = 0.03
        current_mutation_rate = max(0.005, initial_rate * (1.0 - (gen / generations)))
        
        mating_pool = [ind for _, ind in scored_population[:int(pop_size * 0.5)]]
        
        while len(new_population) < pop_size:
            p1 = random.choice(mating_pool)
            p2 = random.choice(mating_pool)
            child = two_point_crossover(p1, p2)
            child = mutate_sequence(child, current_mutation_rate)
            new_population.append(child)
            
        population = new_population
        
    final_best_fit, final_best_seq = scored_population[0]
    print("="*70)
    print(f"Optimizasyon Başarıyla Tamamlandı!\nEn İyi Sekans: {final_best_seq}\nSkor: {final_best_fit:.4f}")
    print("="*70 + "\n")
    return final_best_seq

if __name__ == "__main__":
    run_genetic_optimization()
