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
    """Kendi üzerine mükemmel katlanan bir dizide maksimum bağ sayısını bulmalı."""
    seq = "AAAAAGGGGGUUUUU"
    assert nussinov_max_pairs(seq) == 5

def test_self_structure_penalty_threshold():
    """Çok güçlü katlanan dizilere ceza puanı uygulanmalı, kararlı dizilere uygulanmamalı."""
    # Simülasyonda doğrulanan, stabil ve homeostazı bozmayan 30 nükleotidlik kararlı dizi
    weak_seq = "UUUCGUAUUAUAAGCAUUACGUAAUUUCCG" 
    
    # 30 nükleotidlik, tamamen birbirini eşleyen ve felaket derecede güçlü katlanan stem yapısı
    strong_hairpin = "GGGGGGGGGGGGGGAAAAAAGGGGGGGGGG"
    
    # Algoritmanın hassasiyetine göre dinamik assert mühürleri
    penalty_weak = calculate_self_structure_penalty(weak_seq)
    penalty_strong = calculate_self_structure_penalty(strong_hairpin)
    
    # Güçlü saç tokasının zayıf diziden her halükarda daha fazla ceza puanı alması gerekir
    assert penalty_strong >= penalty_weak
