import pytest
import sys
import os

# Testlerin core modülünü bulabilmesi için path eklemesi
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.mfe import nussinov_max_pairs, calculate_self_structure_penalty

def test_nussinov_empty_sequence():
    """Boş dizi gönderildiğinde 0 dönmeli."""
    assert nussinov_max_pairs("") == 0
    assert calculate_self_structure_penalty("") == 0.0

def test_nussinov_short_sequence():
    """Minimum loop uzunluğu (5 nt) altındaki diziler katlanamamalı."""
    assert nussinov_max_pairs("AUGC") == 0

def test_nussinov_perfect_hairpin():
    """Kendi üzerine mükemmel katlanan bir dizide maksimum bağ sayısını bulmalı.
    AAAAA-UUUUU -> 5 çift bağ yapabilmeli.
    """
    # Ortada loop açısı için nükleotidler bırakarak test ediyoruz
    seq = "AAAAAGGGGGTTTTT".replace("T", "U") # AAAAAGGGGGUUUUU
    # 5 adet A-U eşleşmesi yakalamalı
    assert nussinov_max_pairs(seq) == 5

def test_self_structure_penalty_threshold():
    """Çok güçlü katlanan dizilere ceza puanı uygulanmalı, kararlı dizilere uygulanmamalı."""
    weak_seq = "AUGCAUGCAUGCAUGC"
    strong_hairpin = "GGGGGGGGAAAAUUUUUUUU" # Aşırı güçlü G-C ve A-U stem yapısı
    
    assert calculate_self_structure_penalty(weak_seq) == 0.0
    assert calculate_self_structure_penalty(strong_hairpin) > 0.0
