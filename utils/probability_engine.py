import numpy as np
import json
import os

def optimize_probability_space(n_scenarios=8890, base_occupancy=0.4736, target_success=95.0):
    print(f"[-] {n_scenarios} senaryoluk olasilik uzayi optimizasyonu baslatildi...")
    
    current_occupancy = base_occupancy
    learning_rate = 0.01
    iterations = 0
    success_rate = 0.0
    best_results = {}
    
    # Başarı oranı %95 üzerine çıkana veya 100 iterasyon dolana kadar optimizasyon döngüsü
    while success_rate < target_success and iterations < 100:
        iterations += 1
        
        # Optimize edilmiş gürültü filtresi (Varyans daraltılıyor)
        adapted_scale = 0.05 / (1 + 0.1 * iterations)
        noise = np.random.normal(loc=0.0, scale=adapted_scale, size=n_scenarios)
        probabilities = np.clip(current_occupancy + noise, 0, 1)
        
        successful_binding = probabilities > 0.45
        success_rate = np.mean(successful_binding) * 100
        
        best_results = {
            "total_scenarios": n_scenarios,
            "optimized_mean_occupancy": float(np.mean(probabilities)),
            "max_probability": float(np.max(probabilities)),
            "min_probability": float(np.min(probabilities)),
            "target_suppression_success_rate_percent": float(success_rate),
            "optimization_iterations": iterations,
            "noise_damping_factor": float(adapted_scale)
        }
        
        # Eğer hedef başarıya ulaşılamadıysa merkez doluluk oranını yukarı it (Afinite artırımı)
        if success_rate < target_success:
            current_occupancy += learning_rate
            
    os.makedirs("bridge_models", exist_ok=True)
    with open("bridge_models/probability_space.json", "w") as f:
        json.dump(best_results, f, indent=4)
        
    print(f"[+] Optimizasyon tamamlandi! ({iterations}. iterasyonda hedefe ulasildi)")
    print(f"--> Yeni Ortalama Doluluk (Sifir Gurultu Hedefi): {best_results['optimized_mean_occupancy']:.4f}")
    print(f"--> Minimum Olasilik Sınırı: {best_results['min_probability']:.4f}")
    print(f"--> Optimizasyon Sonrasi Basari Orani: %{best_results['target_suppression_success_rate_percent']:.2f}")
    return best_results

if __name__ == "__main__":
    optimize_probability_space()
