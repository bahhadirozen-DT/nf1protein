import re
from core.binding import calculate_target_interaction, turner_duplex_heuristic
from core.mfe import calculate_self_structure_penalty
from core.biology import calculate_advanced_immunity, calculate_rnase_risk

def score_candidate(rna_sequence, target_mrna, config=None, transcriptome=None):
    """
    shRNA ve antiparalel hedef etkileşimlerini dinamik olarak puanlar.
    """
    # Eğer tek zincirli bir yapı geldiyse ve içinde popüler shRNA ilmeği varsa ayrıştır
    shrna_loop = "UUCAAGAGA"
    if shrna_loop in rna_sequence:
        parts = rna_sequence.split(shrna_loop)
        guide_strand = parts[0]
        # Biyofiziksel hesaplama için sadece aktif rehber sarmalı baz al
        working_seq = guide_strand
    else:
        working_seq = rna_sequence

    # Antiparalel reverse complement doğrulamasıyla hedef etkileşimini hesapla
    complement = {'A': 'U', 'U': 'A', 'G': 'C', 'C': 'G', 'T': 'A'}
    rev_target = "".join(complement.get(base, base) for base in reversed(target_mrna))
    
    # Skorlama metriklerini çalıştır
    target_binding = calculate_target_interaction(working_seq, rev_target)
    self_folding_penalty = calculate_self_structure_penalty(working_seq)
    
    # Opsiyonel transcriptome kontrolleri
    off_target_penalty = 0.0
    if transcriptome:
        off_target_penalty = transcriptome.calculate_off_target_score(working_seq)
        
    immunity_penalty = calculate_advanced_immunity(working_seq)
    rnase_penalty = calculate_rnase_risk(working_seq)
    
    # Global skor formülü (Düşük enerji, yüksek bağlanma afinitesi)
    total_score = target_binding - (self_folding_penalty * 1.5) - off_target_penalty - immunity_penalty
    
    return {
        "total_score": round(total_score, 4),
        "target_binding": round(target_binding, 4),
        "self_folding_penalty": round(self_folding_penalty, 4),
        "rnase_risk": rnase_penalty
    }
