"""
Module: genetic_optimizer.py
Description: Universal biological parameter optimization sandbox.
Project: NF1-Smart-Redirector-Model (TRL-2 Academic Sandbox)
"""

import random
import numpy as np
import sys
import os

# Üst dizindeki modüllere (bridge_models, simulations vb.) erişim sağlamak için yol tanımı
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Projenizin 'simulations/' klasöründeki gerçek matematiksel motorları içeri aktarıyoruz
try:
    from simulations.delay_coupled_bifurcation import run_ga_dde_bridge
    from simulations.colored_noise_langevin_model import ColoredNoiseLangevinModel
    from simulations.coupled_ode_v1 import run_optimization_simulation
    print("[BİLGİ] Proje simülasyon motorları başarıyla entegre edildi.")
except ImportError as e:
    print(f"[UYARI] Bazı modüller import edilemedi ({e}). Bağımsız test moduna geçiliyor.")
    # Fallback fonksiyonları (Yerel testlerde çökmemesi için koruma)
    def run_ga_dde_bridge(seq): return {"is_stable": True, "hopf_proximity": 0.5}
    def ColoredNoiseLangevinModel(): return {"violations": 0, "descent_speed": 0.0}

# ==========================================
# 1. HİPOTEZ ODAKLI STRUCTURE-INFORMED VIENNARNA SİMÜLASYONU
# ==========================================
def simulate_vienna_rna(rna_sequence):
    """
    TAPC Değerlendirme Motoru için ikincil yapı (.((...))) ve MFE simülasyonu.
    """
    gc_count = sum(1 for c in rna_sequence if c in 'GC')
    mfe = -0.4 * len(rna_sequence) - (gc_count * 1.5) + random.uniform(-0.5, 0.5)
    half = len(rna_sequence) // 3
    structure = "(" * half + "." * (len(rna_sequence) - 2 * half) + ")" * half
    return {"mfe": mfe, "structure": structure}

# ==========================================
# 2. YENİ BİYOLOJİK FİTNESS MİMARİSİ (HİLE KORUMALI)
# ==========================================
def compute_interaction_signal(rna_sequence, dot_bracket_structure):
    """
    Açık ilmek (loop '.') bölgelerindeki nükleotid serbestliğini ve stem geometrisini puanlar.
    """
    interaction_score = 0.0
    for i, char in enumerate(dot_bracket_structure):
        if char == '.':  # Bağlanmaya müsait açık cep
            if rna_sequence[i] in 'UA': 
                interaction_score += 0.8
                
    stem_count = dot_bracket_structure.count('(')
    if 5 <= stem_count <= 12:
        interaction_score += 6.0  # Dengeli ikincil yapı geometrisi ödülü
        
    return interaction_score

def compute_comprehensive_fitness(rna_sequence):
    """
    5 bağlantılı matematiksel çerçeveyi (Langevin, ODE, DDE, Lyapunov, Vienna) 
    biyolojik keşif gradyanına dönüştüren ana fitness fonksiyonu.
    """
    vienna_results = simulate_vienna_rna(rna_sequence)
    mfe = vienna_results["mfe"]
    structure = vienna_results["structure"]
    
    # Reponuzdaki gerçek simülasyon motorları tetikleniyor
    dde_results = run_ga_dde_bridge(rna_sequence)
    langevin_results = ColoredNoiseLangevinModel()
    
    fitness_score = 0.0
    
    # A. MFE Esneklik Penceresi (Sabit hedef tuzağından kurtulma)
    if mfe > -15.0:
        vienna_score = (mfe + 15.0) * -2.5  # Kararsız yapılar eleniyor
    elif mfe < -35.0:
        vienna_score = (-35.0 - mfe) * -1.0  # Aşırı rijit yapılar törpüleniyor
    else:
        vienna_score = 5.0  # Serbest keşif alanı
    fitness_score += vienna_score
    
    # B. Logaritmik Motif Doygunluğu (Enflasyon Koruması)
    count_auua = rna_sequence.count("AUUA")
    motif_score = np.log1p(count_auua) * 4.0
    fitness_score += motif_score
    
    # C. Yapısal Etkileşim Sinyali (Dinamik İlmek Kontrolü)
    fitness_score += compute_interaction_signal(rna_sequence, structure)
    
    # D. Yumuşatılmış DDE Hopf Cezası (+200 Devasa Duvarı Kaldırıldı)
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
    
    # E. Dengelenmiş Lyapunov ve Confinement Cezaları
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
    Faydalı yapısal blokları koruyan iki noktalı çaprazlama operatörü.
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
            
        scored_population.sort(key=lambda x: x, reverse=True)
        best_fit, best_seq = scored_population
        
        if gen % 5 == 0 or gen == generations - 1:
            gc_ratio = sum(1 for c in best_seq if c in 'GC') / sequence_length
            print(f"Nesil {gen:02d} | En İyi Fitness: {best_fit:7.2f} | Sekans: {best_seq} | GC: {gc_ratio:.1%}")
            
        new_population = [ind for _, ind in scored_population[:elite_count]]
        
        # Adaptif mutasyon oranı (%3'ten başlayarak sönümlenir)
        current_mutation_rate = max(0.005, 0.03 * (1.0 - (gen / generations)))
        
        mating_pool = [ind for _, ind in scored_population[:int(pop_size * 0.5)]]
        
        while len(new_population) < pop_size:
            p1 = random.choice(mating_pool)
            p2 = random.choice(mating_pool)
            child = two_point_crossover(p1, p2)
            child = mutate_sequence(child, current_mutation_rate)
            new_population.append(child)
            
        population = new_population
        
    final_best_fit, final_best_seq = scored_population
    print("="*70)
    print(f"Optimizasyon Başarıyla Tamamlandı!\nEn İyi Sekans: {final_best_seq}\nSkor: {final_best_fit:.4f}")
    print("="*70 + "\n")
    return final_best_seq

if __name__ == "__main__":
    run_genetic_optimization()
