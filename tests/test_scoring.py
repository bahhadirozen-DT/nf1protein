import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.scoring import score_candidate

# Testler için izole mock konfigürasyon nesnesi
MOCK_CONFIG = {
    "weights": {
        "target_binding": 0.25,
        "accessibility": 0.20,
        "structure_ensemble": 0.15,
        "self_structure_penalty": 0.15,
        "off_target": 0.10,
        "gc_penalty": 0.10,
        "immunity": 0.05,
        "rnase_risk": 0.05
    },
    "thresholds": {
        "min_gc": 0.40,
        "max_gc": 0.60,
        "min_len": 19
    }
}

def test_score_candidate_length_constraint():
    """RNA adayı hedeften uzunsa veya min_len sınırının altındaysa fitness 0.0 dönmeli."""
    target = "AUGCAU" # Kısa hedef
    rna_long = "AUGCAUGCAUGCAUGCAUGCAU" # Uzun aday
    rna_short = "AUG" # Çok kısa aday
    
    # Hedef uzunluk kısıtı kontrolü
    assert score_candidate(rna_long, target, None, MOCK_CONFIG, None, False) == 0.0
    # Minimum sınır kontrolü
    assert score_candidate(rna_short, "AUGCAUGCAUGCAUGCAUGCAUGCAU", None, MOCK_CONFIG, None, False) == 0.0

def test_score_candidate_fallback_safety():
    """Çekirdek modüller kapalıyken bile (core_modules=False) fonksiyon hata vermeden mock skor üretmeli."""
    target = "GUCAGCUGAUCGAUCGAAUGCUUUACAGCUGUCAGCUGA"
    rna = "AUGCCUGUUGUAGCGAUUGCAGC"
    
    score = score_candidate(
        rna_sequence=rna,
        target_mrna=target,
        selected_cif=None,
        config=MOCK_CONFIG,
        transcriptome=None,
        core_modules=False
    )
    # Çökmeden pozitif bir baseline skoru dönmeli
    assert score >= 0.0
