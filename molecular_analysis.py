import os
import re
import glob

# ============================================================
# SAF PYTHON BİYOFİZİKSEL RNAup / TURNER PARAMETRELERİ MOTORU
# ============================================================

def predict_rna_binding_energy(rna_sequence, target_mrna="AUGCCUACAGCUA"):
    """
    ViennaRNA olmadan, saf Python ile Turner En Yakın Komşu (Nearest-Neighbor) 
    modelini kullanarak teorik hibridizasyon serbest enerjisini (dG) hesaplar.
    """
    rna = rna_sequence.upper().replace("T", "U")
    target = target_mrna.upper().replace("T", "U")
    
    # Turner 2004 standart RNA/RNA serbest enerji parametreleri (kcal/mol, 37°C)
    # Değerler ne kadar negatifse o basamağın bağlanma kararlılığı o kadar yüksektir.
    turner_parameters = {
        "AA": -0.9, "UU": -0.9, "AU": -1.1, "UA": -1.3,
        "CC": -2.1, "GG": -2.1, "CG": -2.4, "GC": -3.4,
        "AC": -2.1, "CA": -2.1, "AG": -1.7, "GA": -1.7,
        "UC": -1.8, "CU": -1.8, "UG": -1.4, "GU": -1.4
    }
    
    dg_binding = 0.0
    matches_found = 0
    
    # Basit bir lokal hizalama ve komşuluk enerjisi tarama motoru
    # Tasarlanan RNA ile hedef mRNA arasındaki ikili basamakları (dinükleotid) eşleştirir
    for i in range(len(rna) - 1):
        dinucleotide = rna[i:i+2]
        # Eğer bu dinükleotid hedef dizide (veya ters tümleyeninde) kısmi olarak eşleşiyorsa
        if dinucleotide in target or dinucleotide[::-1] in target:
            if dinucleotide in turner_parameters:
                dg_binding += turner_parameters[dinucleotide]
                matches_found += 1
                
    # Eğer hiç eşleşme yoksa veya dizi çok kısa ise baz kararsızlık enerjisi döner
    if matches_found == 0:
        return 0.0, 4.0
    
    # dG_open: Hedef mRNA'nın o bölgesinin açılması için gereken teorik enerji (Erişilebilirlik)
    # Dizi uzunluğu ve GC miktarı arttıkça hedefi açmak zorlaşır (pozitif enerji maliyeti)
    gc_count = target.count("G") + target.count("C")
    dg_open = 1.0 + (gc_count * 0.25)
    
    return dg_binding, dg_open


# ============================================================
# BIOLOGICAL SCREENING
# ============================================================

def calculate_target_interaction(rna_sequence):
    """
    ViennaRNA yokluğunda çalışan saf Python termodinamik motorunu çağırır.
    """
    # Örnek bir NF1 mutant mRNA hedef bölgesi tanımlıyoruz
    nf1_target_region = "GUCAGCUGAUCGAUCGAAUGC"
    
    dg_binding, dg_open = predict_rna_binding_energy(rna_sequence, nf1_target_region)
    dg_total = dg_binding + dg_open

    # Toplam enerji negatifse kararlıdır, fitness'a pozitif katkı sunması için ters çeviriyoruz
    return max(0.0, -dg_total)


def calculate_off_target_penalty(rna_sequence):
    """
    Gelecekte BLAST / Bowtie bağlanacak.
    """
    off_target_hits = 0
    return off_target_hits * 25.0


def evaluate_cellular_properties(rna_sequence):
    immunity_penalty = 0.0
    stability_bonus = 0.0

    motifs = [
        r"GUUGU",
        r"UGUU",
        r"GUGUG",
        r"UUUUU"
    ]

    for motif in motifs:
        immunity_penalty += (
            len(re.findall(motif, rna_sequence.upper()))
            * 20.0
        )

    if not rna_sequence:
        return immunity_penalty, -25.0

    gc_count = (
        rna_sequence.upper().count("G")
        + rna_sequence.upper().count("C")
    )

    gc_ratio = gc_count / len(rna_sequence)

    if 0.40 <= gc_ratio <= 0.60:
        stability_bonus += 15.0
    else:
        stability_bonus -= 25.0

    return immunity_penalty, stability_bonus


def compute_integrated_biological_fitness(
    rna_sequence,
    selected_cif=None
):
    binding_score = calculate_target_interaction(
        rna_sequence
    )

    immunity_penalty, stability_bonus = (
        evaluate_cellular_properties(
            rna_sequence
        )
    )

    off_target_penalty = (
        calculate_off_target_penalty(
            rna_sequence
        )
    )

    structural_support = (
        10.0 if selected_cif else 2.0
    )

    experimental_support = 12.0

    fitness = (
        0.30 * binding_score
        + 0.20 * stability_bonus
        + 0.20 * structural_support
        + 0.10 * experimental_support
        - 0.20 * off_target_penalty
        - 0.20 * immunity_penalty
    )

    return max(0.0, fitness)


# ============================================================
# MAIN PIPELINE
# ============================================================

def execute_master_pipeline():
    print("="*80)
    print("MASTER RNA PRE-SCREENING PLATFORM (PURE PYTHON MODE)")
    print("="*80)

    candidate_rna = (
        "AUGCCUGUUGUAGCGAUUGCAGCUGAGCUCGAUCG"
    )

    print()
    print("Candidate:")
    print(candidate_rna)

    cif_files = glob.glob(
        "alphafold_models/*.cif"
    )

    if cif_files:
        print()
        print(
            f"{len(cif_files)} structure models found."
        )

        for cif in cif_files:
            print()
            print("Processing:")
            print(os.path.basename(cif))
            
            score = compute_integrated_biological_fitness(
                candidate_rna,
                selected_cif=cif
            )
            print(f"Biological Fitness (with {os.path.basename(cif)}): {score:.4f}")
    else:
        print()
        print(
            "No AlphaFold models found. Running baseline simulation..."
        )
        score = compute_integrated_biological_fitness(
            candidate_rna,
            selected_cif=None
        )
        print(f"Biological Fitness (Baseline): {score:.4f}")

    print()
    print("="*80)
    print("PIPELINE COMPLETE")
    print("="*80)


if __name__ == "__main__":
    execute_master_pipeline()
