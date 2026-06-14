# path: bridge_models/biological_constraints.py
import re

def get_biological_fitness(rna_sequence, target_mrna_seq=""):
    """
    RNA adayının hücre içinde çalışabilme skorunu hesaplar.
    """
    # 1. HEDEFE BAĞLANMA VE ERİŞİLEBİLİRLİK (Örn: RNAup mantığı)
    # Gerçek uygulamada buraya ViennaRNA veya IntaRNA subprocess çağrıları gelir.
    binding_score = 25.0  # Varsayılan baz skor (-dG_total üzerinden)

    # 2. İMMÜN AKTİVASYON CEZASI (TLR7/8, RIG-I tehlikeli motifleri)
    immunity_penalty = 0
    danger_motifs = [r"GUUGU", r"UGUU", r"GUGUG"]
    for motif in danger_motifs:
        matches = len(re.findall(motif, rna_sequence))
        immunity_penalty += matches * 20.0  # Her tehlikeli motif için ağır ceza

    # 3. STABİLİTE VE GC DENGESİ
    stability_bonus = 0
    gc_count = rna_sequence.count('G') + rna_sequence.count('C')
    gc_ratio = gc_count / len(rna_sequence) if len(rna_sequence) > 0 else 0
    if 0.40 <= gc_ratio <= 0.60:
        stability_bonus += 15.0
    else:
        stability_bonus -= 20.0

    # 4. OFF-TARGET VE ÖZGÜLLÜK CEZASI (Örn: Bowtie/BLAST entegrasyonu)
    off_target_penalty = 0.0  # Hizalama skoruna göre artırılır

    # Biyolojik Ağırlıklandırılmış Toplam Fitness
    bio_score = (
        0.4 * binding_score +
        0.2 * stability_bonus -
        0.2 * immunity_penalty -
        0.2 * off_target_penalty
    )
    return max(0.0, bio_score)
