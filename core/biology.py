import os
import re

def predict_guide_strand(rna_sequence):
    """siRNA asimetri kurallarına göre hangi strandın guide (rehber) olacağını tahmin eder."""
    seq = rna_sequence.upper()
    if not seq: return "passenger"
    score_5prime = 1.0 if seq[0] in ["U", "A"] else 0.0
    score_3prime = 1.0 if seq[-1] in ["G", "C"] else 0.0
    return "guide" if (score_5prime + score_3prime) >= 1.0 else "passenger"

def calculate_advanced_immunity(rna_sequence):
    """TLR3, TLR7/8, RIG-I ve PKR patojen tanıma reseptör motiflerini cezalandırır."""
    seq = rna_sequence.upper()
    advanced_motifs = {
        r"GUUGU": 20.0, r"UGUU": 15.0, r"UUUUU": 25.0,
        r"AUUUA": 10.0, r"GGGG": 15.0, r"CGCGC": 20.0
    }
    total_penalty = 0.0
    for motif, weight in advanced_motifs.items():
        matches = len(re.findall(motif, seq))
        total_penalty += matches * weight
    return total_penalty

def calculate_rnase_risk(rna_sequence):
    """Nükleazlar tarafından tanınan ve yarı ömrü düşüren motif cezalandırması."""
    seq = rna_sequence.upper()
    rnase_motifs = [r"AUUUA", r"UUAUU", r"UAUUUA"]
    risk_penalty = 0.0
    for motif in rnase_motifs:
        matches = len(re.findall(motif, seq))
        risk_penalty += matches * 15.0
    return risk_penalty

def parse_alphafold_cif_interface(cif_path):
    """Gerçek arayüz kontak noktası analizi yapan Biopython köprüsü simülasyonu."""
    if not cif_path or not os.path.exists(cif_path):
        return 2.0
    try:
        from analyze_structure import analyze_molecular_interaction
        results = analyze_molecular_interaction(cif_path)
        if results and "contact_points" in results:
            return min(15.0, float(results["contact_points"]) * 0.3)
    except Exception:
        pass
    return 5.0
