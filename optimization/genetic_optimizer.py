"""
Module: genetic_optimizer.py
Description: Sequence-specific biological parameter exploration using a genetic algorithm.
Optimizes RNA sequences by combining stochastic Langevin dynamics and continuous ODE trajectories.
"""
import random
import numpy as np
import sys
import os

# Üst dizindeki modüllere erişim sağlamak için yol tanımı
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bridge_models.evidence_weighted_calibration import EvidenceWeightedCalibration
from simulations.colored_noise_langevin_model import ColoredNoiseLangevinModel
from simulations.coupled_ode_v1 import run_optimization_simulation

class RNAGeneticOptimizer:
    def __init__(self, sequence_length=30, pop_size=20, mutation_rate=0.06):
        self.sequence_length = sequence_length
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.nucleotides = ['A', 'U', 'G', 'C']
        self.calibration_bridge = EvidenceWeightedCalibration()
        self.population = [self._generate_random_rna() for _ in range(self.pop_size)]
        
        # Matematiksel kararlı durum eşiği (Cubic root: x^3 - 2.3x + 1.9 = 0)
        cubic_coeffs = [1.0, 0.0, -2.3, 1.9]
        all_roots = np.roots(cubic_coeffs)
        real_roots = all_roots[np.isreal(all_roots)].real
        self.target_equilibrium = float(real_roots[0]) # ~ -1.81562
        
    def _generate_random_rna(self):
        return ''.join(random.choice(self.nucleotides) for _ in range(self.sequence_length))
        
    def predict_structural_metrics(self, rna_sequence):
        """
        HEURISTIC BINDING PROXY GENERATOR (TRL-2 Sandbox Standard):
        Maps raw nucleotide sequences into phenomenological parameters using rule-based scoring.
        """
        gc_content = (rna_sequence.count('G') + rna_sequence.count('C')) / len(rna_sequence)
        
        # 1. Diziye Bağlı İstifleme (Stacking Motif) Kuralları
        stacking_pairs = rna_sequence.count('GC') + rna_sequence.count('CG')
        homopolymer_penalty = rna_sequence.count('AAAA') + rna_sequence.count('UUUU') + rna_sequence.count('GGGG')
        
        # 2. İkincil Yapı Proksisi (Watson-Crick ve G-U Wobble Çiftleri)
        half = self.sequence_length // 2
        first_half = rna_sequence[:half]
        second_half_rev = rna_sequence[half:][::-1]
        complementary_matches = 0
        
        for b1, b2 in zip(first_half, second_half_rev):
            if (b1 == 'A' and b2 == 'U') or (b1 == 'U' and b2 == 'A') or \
               (b1 == 'G' and b2 == 'C') or (b1 == 'C' and b2 == 'G'):
                complementary_matches += 1.0
            elif (b1 == 'G' and b2 == 'U') or (b1 == 'U' and b2 == 'G'):
                complementary_matches += 0.5 # G-U Wobble kısmi termodinamik ağırlığı
                
        motif_score = (stacking_pairs * 4.0) + (complementary_matches * 3.0) - (homopolymer_penalty * 8.0)
        
        heuristic_binding_proxy = -40.0 - (gc_content * 50.0) + (motif_score * 0.1)
        interfacial_area_proxy = 800.0 + (gc_content * 500.0) + (motif_score * 2.0)
        
        return min(max(heuristic_binding_proxy, -120.0), 0.0), min(max(interfacial_area_proxy, 400.0), 1500.0)
        
    def _evaluate_single_run(self, rna_sequence):
        """ Hem Langevin (Stokastik) hem de ODE (Sürekli) motorunu koşturan entegre değerlendirme. """
        binding_proxy, area_proxy = self.predict_structural_metrics(rna_sequence)
        constraints = self.calibration_bridge.constrain_parameter_space(binding_proxy, area_proxy, fcc=0.75)
        
        # --- 1. Kolmogorov/Langevin Stokastik Metrikleri ---
        model = ColoredNoiseLangevinModel()
        _, trajectory = model.simulate(tau_eff=constraints["tau_constrained"], sigma_eff=constraints["sigma_constrained"])
        
        steady_state = trajectory[int(len(trajectory) * 0.6):]
        diffs = np.diff(steady_state)
        
        confinement_error = np.mean((steady_state - self.target_equilibrium) ** 2)
        confinement_score = 1.0 / (1.0 + confinement_error)
        trajectory_smoothness = 1.0 / (1.0 + np.var(diffs))
        oscillation_energy = np.mean(diffs ** 2) / 0.01
        divergence_penalty = max(0.0, np.max(np.abs(trajectory)) - 3.5)
        
        # --- 2. Sürekli ODE Entegrasyon Metrikleri ---
        ode_target_vector = [
            float(abs(constraints["tau_constrained"] * 1.5)),  # Theta_high proksisi
            float(abs(constraints["sigma_constrained"] * 4.0)),  # k_fb geri besleme kazancı
            float(constraints["tau_constrained"])                # Dinamik gecikme (tau_m)
        ]
        ode_results = run_optimization_simulation(ode_target_vector)
        
        ode_leakage = ode_results.get("residual_leakage", 1.0)
        ode_penalty = abs(ode_leakage - 0.055) * 5.0 # %5.5 sızıntı tabanından sapma cezası
        
        # --- 3. Birleşik Skor Hesaplama ---
        fitness_score = (2.5 * confinement_score) + (1.5 * trajectory_smoothness) - \
                        (0.4 * oscillation_energy) - (4.0 * divergence_penalty) - ode_penalty
                        
        return fitness_score
        
    def evaluate_fitness(self, rna_sequence, n_evals=3):
        """ Aday dizinin ortalama uygunluğunu hesaplar. """
        eval_scores = [self._evaluate_single_run(rna_sequence) for _ in range(n_evals)]
        return max(0.0001, float(np.mean(eval_scores)))
        
    def evolve(self, generations=10):
        """ Popülasyonu nesiller boyunca evrimleştirir ve skor geçmişini kaydeder. """
        fitness_history = []
        
        if not os.path.exists('figures'):
            os.makedirs('figures')
            
        for gen in range(generations):
            scores = [self.evaluate_fitness(ind) for ind in self.population]
            sorted_indices = np.argsort(scores)[::-1]
            self.population = [self.population[i] for i in sorted_indices]
            
            best_score = max(scores)
            fitness_history.append(best_score)
            
            next_gen = self.population[:2] # Elitizm
            
            while len(next_gen) < self.pop_size:
                p1, p2 = random.choice(self.population[:8]), random.choice(self.population[:8])
                cut = random.randint(5, self.sequence_length - 5)
                child = p1[:cut] + p2[cut:]
                
                child_list = list(child)
                for i in range(len(child_list)):
                    if random.random() < self.mutation_rate:
                        child_list[i] = random.choice(self.nucleotides)
                next_gen.append(''.join(child_list))
                
            self.population = next_gen
            print(f"Generation {gen + 1:02d} | Ensemble Max Fitness: {best_score:.4f} | Champion: {self.population[:3]}...")
            
        # --- OTOMATİK GRAFİK ÜRETİM MOTORU ---
        import matplotlib.pyplot as plt
        plt.figure(figsize=(9, 4.5))
        plt.plot(range(1, generations + 1), fitness_history, color='crimson', marker='o', linewidth=2, label='Ensemble Max Fitness')
        plt.title('Genetic Algorithm Optimization History (TRL-2 Sandbox)', fontsize=12, fontweight='bold', pad=15)
        plt.xlabel('Nesiller (Generations)', fontsize=10)
        plt.ylabel('Uygunluk Skoru (Fitness Score)', fontsize=10)
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.legend(loc='lower right')
        
        plt.savefig('figures/genetic_optimization_convergence.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("[GRAPHICS SUCCESS] 'figures/genetic_optimization_convergence.png' başarıyla üretildi.")
        
        return self.population

if __name__ == "__main__":
    optimizer = RNAGeneticOptimizer(sequence_length=30, pop_size=20, mutation_rate=0.06)
    best_sequences = optimizer.evolve(generations=10)
    print(f"🥇 En İyi Aday Sekans: {best_sequences[:1]}")
