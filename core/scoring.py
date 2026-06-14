"""
Module: core/scoring.py
Description: Dedicated scoring engine that separates the calculation of 
sub-biological fitness scores from the master workflow orchestrator.
"""

def score_candidate(rna_sequence, target_mrna, selected_cif, config, transcriptome, core_modules):
    """
    Tüm alt biyolojik skorları konfigürasyon matrisine göre ağırlıklandırıp birleştirir.
    Sorumluluk tamamen molecular_analysis orkestratöründen ayrılmıştır.
    """
    w = config.get("weights", {})
    t = config.get("thresholds", {})
    
    # 1. Uzunluk ve Sınır Kısıtları Kontrolü
    if len(rna_sequence) > len(target_mrna) or len(rna_sequence) < t.get("min_len", 19):
        return 0.0

    # 2. Çekirdek Modüller Yüklüyse Gerçek Hesaplamaları Koştur
    if core_modules and transcriptome:
        # core/ klasörü içindeki diğer modüllerden dinamik import
        from core.binding import calculate_target_interaction, turner_duplex_heuristic
        from core.biology import calculate_advanced_immunity, calculate_rnase_risk, parse_alphafold_cif_interface
        from core.mfe import calculate_self_structure_penalty

        target_binding = calculate_target_interaction(rna_sequence, target_mrna)
        self_folding_penalty = calculate_self_structure_penalty(rna_sequence)
        off_target_penalty = transcriptome.calculate_off_target_score(rna_sequence)
        immunity_penalty = calculate_advanced_immunity(rna_sequence)
        rnase_penalty = calculate_rnase_risk(rna_sequence)
        structure_score = parse_alphafold_cif_interface(selected_cif)
        _, dg_open_proxy, _ = turner_duplex_heuristic(rna_sequence, target_mrna)
    else:
        # Güvenli Fallback Modu (Log uyarısı ana dosyada verilir)
        target_binding, self_folding_penalty = 15.0, 0.0
        off_target_penalty, immunity_penalty, rnase_penalty = 0.0, 0.0, 0.0
        structure_score, dg_open_proxy = 5.0, 3.5

    # 3. Erişilebilirlik ve GC Analizi
    accessibility_score = max(0.0, 10.0 - dg_open_proxy)
    gc_ratio = (rna_sequence.upper().count("G") + rna_sequence.upper().count("C")) / max(1, len(rna_sequence))
    gc_penalty = 25.0 if not (t.get("min_gc", 0.40) <= gc_ratio <= t.get("max_gc", 0.60)) else 0.0

    # 4. Ağırlıklı Matris Birleşimi (Nihai Birleşik Biyolojik Fitness)
    fitness = (
        w.get("target_binding", 0.25) * target_binding
        + w.get("accessibility", 0.20) * accessibility_score
        + w.get("structure_ensemble", 0.15) * structure_score
        - w.get("self_structure_penalty", 0.15) * self_folding_penalty
        - w.get("off_target", 0.10) * off_target_penalty
        - w.get("gc_penalty", 0.10) * gc_penalty
        - w.get("immunity", 0.05) * immunity_penalty
        - w.get("rnase_risk", 0.05) * rnase_penalty
    )
    return max(0.0, fitness)
