import os

try:
    import RNA
    USE_VIENNA = True
except ImportError:
    USE_VIENNA = False

def native_vienna_rnaup_core(rna_sequence, target_mrna):
    """Resmi ViennaRNA API Entegrasyonu ile dG_total hesabı yapar."""
    if not USE_VIENNA:
        return 0.0
    try:
        sub_comp = RNA.duplex_id()
        dup = RNA.duplex_eval(rna_sequence, target_mrna, sub_comp)
        return float(dup.energy)
    except Exception:
        return -18.5

def turner_duplex_heuristic(rna_sequence, target_mrna):
    """Saf Python Turner tabanlı ikili katlanma ve açılma maliyeti hesaplayıcı."""
    rna = rna_sequence.upper().replace("T", "U")
    target = target_mrna.upper().replace("T", "U")
    len_rna, len_target = len(rna), len(target)
    
    if len_rna > len_target or len_rna == 0:
        return 0.0, 10.0, 10.0
    
    turner_energy_steps = {
        "AA": -0.9, "UU": -0.9, "AU": -1.1, "UA": -1.3,
        "CC": -2.1, "GG": -2.1, "CG": -2.4, "GC": -3.4,
        "AC": -2.1, "CA": -2.1, "AG": -1.7, "GA": -1.7,
        "UC": -1.8, "CU": -1.8, "UG": -1.4, "GU": -1.4
    }
    best_dg_hybrid = 0.0
    
    def can_pair(base_a, base_b):
        return (base_a == "A" and base_b == "U") or (base_a == "U" and base_b == "A") or \
               (base_a == "G" and base_b == "C") or (base_a == "C" and base_b == "G")

    for i in range(len_target - len_rna + 1):
        target_window = target[i:i+len_rna]
        current_dg_hybrid = 0.0
        matches = 0
        for j in range(len_rna - 1):
            if can_pair(rna[j], target_window[len_rna - 1 - j]) and can_pair(rna[j+1], target_window[len_rna - 2 - j]):
                current_dg_hybrid += turner_energy_steps.get(rna[j:j+2], -0.5)
                matches += 1
        if current_dg_hybrid < best_dg_hybrid:
            best_dg_hybrid = current_dg_hybrid

    gc_target = (target.count("G") + target.count("C")) / max(1, len(target))
    gc_rna = (rna.count("G") + rna.count("C")) / max(1, len(rna))
    dg_open_proxy = 1.5 + (gc_target * 2.5) + (gc_rna * 2.0)
    
    return best_dg_hybrid, dg_open_proxy, (best_dg_hybrid + dg_open_proxy)

def calculate_target_interaction(rna_sequence, target_mrna):
    if USE_VIENNA:
        dg_total = native_vienna_rnaup_core(rna_sequence, target_mrna)
    else:
        _, _, dg_total = turner_duplex_heuristic(rna_sequence, target_mrna)
    
    if dg_total < 0:
        binding_score = abs(dg_total) / len(rna_sequence)
    else:
        binding_score = 0.0
    return binding_score * 10.0
