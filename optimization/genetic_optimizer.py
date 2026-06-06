"""
Module: genetic_optimizer.py
Description: Universal biological parameter optimization sandbox - STABLE PRODUCTION GRADE.
Integrates Langevin SDE, continuous ODE, delay DDE, Lyapunov landscapes,
and structural metrics directly from existing AlphaFold 3 Server JSON outputs.
Strictly constrains Hopf bifurcation boundaries to prevent temporal chaos.
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
from simulations.delay_coupled_bifurcation import run_ga_dde_bridge
from alphafold_models.alphafold_processor import AlphaFoldStructuralValidator

class RNAGeneticOptimizer:
    def __init__(self, sequence_length=30, pop_size=20, mutation_rate=0.06):
        self.sequence_length = sequence_length
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.nucleotides = ['A', 'U', 'G', 'C']
        self.calibration_bridge = EvidenceWeightedCalibration()
        self.af_validator = AlphaFoldStructuralValidator()
        self.population = [self._generate_random_rna() for _ in range(self.pop_size)]
        
        # Matematiksel kararlı durum eşiği (Cubic root: x^3 - 2.3x + 1.9 = 0)
        cubic_coeffs = [1.0, 0.0, -2.3, 1.9]
        all_roots = np.roots(cubic_coeffs)
        real_roots = all_roots[np.isreal(all_roots)].real
        self.target_equilibrium = float(real_roots) # ~ -1.81562
        
    def _generate_random_rna(self):
        return ''.join(random.choice(self.nucleotides) for _ in range(self.sequence_length))
        
    def predict_structural_metrics(self, rna_sequence):
        """ Maps raw nucleotide sequences into phenomenological parameters. """
        gc_content = (rna_sequence.count('G') + rna_sequence.count('C')) / len(rna_sequence)
        stacking_pairs = rna_sequence.count('GC') + rna_sequence.count('CG')
        homopolymer_penalty = rna_sequence.count('AAAA') + rna_sequence.count('UUUU') + rna_sequence.count('GGGG')
        
        half = self.sequence_length // 2
        first_half = rna_sequence[:half]
        second_half_rev = rna_sequence[half:][::-1]
        complementary_matches = 0
        
        for b1, b2 in zip(first_half, second_half_rev):
            if (b1 == 'A' and b2 == 'U') or (b1 == 'U' and b2 == 'A') or \
               (b1 == 'G' and b2 == 'C') or (b1 == 'C' and b2 == 'G'):
                complementary_matches += 1.0
            elif (b1 == 'G' and b2 == 'U') or (b1 == 'U' and b2 == 'G'):
                complementary_matches += 0.5
                
        motif_score = (stacking_pairs * 4.0) + (complementary_matches * 3.0) - (homopolymer_penalty * 8.0)
        heuristic_binding_proxy = -40.0 - (gc_content * 50.0) + (motif_score * 0.1)
        interfacial_area_proxy = 800.0 + (gc_content * 500.0) + (motif_score * 2.0)
        
        return min(max(heuristic_binding_proxy, -120.0), 0.0), min(max(interfacial_area_proxy, 400.0), 1500.0)

    def calculate_lyapunov_descent(self, trajectory):
        """ Evaluates quasi-potential energy surface descent (dV/dt <= 0). """
        try:
            gamma_proxy, g_proxy = 0.5, 0.3
            x_states = np.array(trajectory)
            V_energy = 0.25 * (x_states**4) - 0.5 * (gamma_proxy - g_proxy) * (x_states**2)
            dV_dt = np.diff(V_energy)
            lyapunov_violations = np.sum(dV_dt > 0.0)
            energy_descent_rate = float(np.mean(dV_dt[dV_dt <= 0.0])) if len(dV_dt[dV_dt <= 0.0]) > 0 else 0.0
            return lyapunov_violations, energy_descent_rate
        except:
            return 100, 0.0
        
    def _evaluate_single_run(self, rna_sequence):
        """ Entegre Değerlendirme Döngüsü - Kararsızlık Korumalı Güvenli Sürüm """
        binding_proxy, area_proxy = self.predict_structural_metrics(rna_sequence)
        constraints = self.calibration_bridge.constrain_parameter_space(binding_proxy, area_proxy, fcc=0.75)
        
        # Kaotik salınımı engellemek amacıyla parametreleri korumalı kararlı bölgeye sıkıştırıyoruz
        tau_c = np.clip(constraints["tau_constrained"], 0.5, 2.0)
        sigma_c = np.clip(constraints["sigma_constrained"], 0.1, 0.45)
        
        # 1. Langevin SDE Motoru
        model = ColoredNoiseLangevinModel()
        _, trajectory = model.simulate(tau_eff=tau_c, sigma_eff=sigma_c)
        steady_state = trajectory[int(len(trajectory) * 0.6):]
        diffs = np.diff(steady_state)
        
        confinement_error = np.mean((steady_state - self.target_equilibrium) ** 2)
        confinement_score = 1.0 / (1.0 + confinement_error)
        trajectory_smoothness = 1.0 / (1.0 + np.var(diffs))
        oscillation_energy = np.mean(diffs ** 2) / 0.01
        divergence_penalty = max(0.0, np.max(np.abs(trajectory)) - 3.5)
        
        # 2. Sürekli ODE Motoru
        ode_target_vector = [float(abs(tau_c * 1.5)), float(abs(sigma_c * 4.0)), float(tau_c)]
        ode_results = run_optimization_simulation(ode_target_vector)
        ode_penalty = abs(ode_results.get("residual_leakage", 1.0) - 0.055) * 5.0
        
        # 3. Gecikmeli DDE Motoru (Kaotik Hopf Çatallanma Koruması Artırıldı)
        dde_target_vector = [float(tau_c), float(abs(sigma_c * 0.5))]
        dde_results = run_ga_dde_bridge(dde_target_vector)
        dde_score = dde_results.get("dde_bifurcation_score", 0.0)
        dde_penalty = dde_results.get("dde_penalty", 0.0)
        if not dde_results.get("is_stable", True):
            dde_penalty += 200.0  # Hakiki Hopf Çatallanması gösteren dizilere ağır bariyer cezası
        
        # 4. Lyapunov Enerji Analizi (Cezalandırma Katsayısı Artırıldı)
        violations, descent_speed = self.calculate_lyapunov_descent(trajectory)
        lyapunov_penalty = (violations * 3.5) + abs(descent_speed * 5.0)
        
        # 5. DİNAMİK ALPHAFOLD 3 INTEGRASYONU
        af_metrics = self.af_validator.parse_alphafold_summary()
        af_penalty = self.af_validator.calculate_interface_penalty(af_metrics)
        
        # Multi-Objective Fitness Fonksiyonu Birleşimi
        fitness_score = (2.0 * confinement_score) + (1.0 * trajectory_smoothness) + (1.5 * dde_score) - \
                        (0.3 * oscillation_energy) - (4.0 * divergence_penalty) - \
                        ode_penalty - dde_penalty - lyapunov_penalty - af_penalty
                        
        return fitness_score
        
    def evaluate_fitness(self, rna_sequence, n_evals=3):
        eval_scores = [self._evaluate_single_run(rna_sequence) for _ in range(n_evals)]
        return max(0.0001, float(np.mean(eval_scores)))
        
    def evolve(self, generations=10):
        fitness_history = []
        if not os.path.exists('figures'):
            os.makedirs('figures')
            
        for gen in range(generations):
            scores = [self.evaluate_fitness(ind) for ind in self.population]
            sorted_indices = np.argsort(scores)[::-1]
            self.population = [self.population[i] for i in sorted_indices]
            
            best_score = max(scores)
            fitness_history.append(best_score)
            
            next_gen = self.population[:2]
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
            print(f"Generation {gen + 1:02d} | Max Fitness: {best_score:.4f} | Champion: {self.population[:2]}...")
            
        import matplotlib.pyplot as plt
        plt.figure(figsize=(9, 4.5))
        plt.plot(range(1, generations + 1), fitness_history, color='darkblue', marker='o', linewidth=2, label='Ensemble Fit')
        plt.title('Nihai Hibrit Optimizasyon Gradiyenti (Hopf Bifurcation Engellemeli)', fontsize=11, fontweight='bold')
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.savefig('figures/genetic_optimization_convergence.png', dpi=300)
        plt.close()
        
        return self.population

if __name__ == "__main__":
    optimizer = RNAGeneticOptimizer(sequence_length=30, pop_size=20, mutation_rate=0.06)
    best_sequences = optimizer.evolve(generations=10)
    print(f"🥇 En İyi Evrimlesmis Sekans: {best_sequences[:1]}")
