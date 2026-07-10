import numpy as np
import json
import os

def generate_probability_space(n_scenarios=8890, base_occupancy=0.4736):
    print(f"[-] {n_scenarios} farkli hucresel olasilik senaryosu hesaplaniyor...")
    
    # Hücre içi stokastik gürültü (Gauss Dağılımı)
    noise = np.random.normal(loc=0.0, scale=0.05, size=n_scenarios)
    probabilities = np.clip(base_occupancy + noise, 0, 1)
    
    # %45 doluluk eşiğini aşan başarılı senaryolar
    successful_binding = probabilities > 0.45
    success_rate = np.mean(successful_binding) * 100
    
    results = {
        "total_scenarios": n_scenarios,
        "mean_occupancy": float(np.mean(probabilities)),
        "max_probability": float(np.max(probabilities)),
        "min_probability": float(np.min(probabilities)),
        "target_suppression_success_rate_percent": float(success_rate)
    }
    
    os.makedirs("bridge_models", exist_ok=True)
    with open("bridge_models/probability_space.json", "w") as f:
        json.dump(results, f, indent=4)
        
    print(f"[+] Olasilik motoru tamamlandi!")
    print(f"--> Toplam Senaryo: {n_scenarios}")
    print(f"--> Ortalama Doluluk: {results['mean_occupancy']:.4f}")
    print(f"--> Maksimum Olasilik: {results['max_probability']:.4f}")
    print(f"--> Minimum Olasilik: {results['min_probability']:.4f}")
    print(f"--> Hedef Bastirma Basari Orani: %{results['target_suppression_success_rate_percent']:.2f}")
    return results

if __name__ == "__main__":
    generate_probability_space()
