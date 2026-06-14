import os
import re
import glob

# ============================================================
# BIOLOGICAL SCREENING
# ============================================================

def calculate_target_interaction(rna_sequence):
    """
    Gelecekte RNAup / IntaRNA bağlanacak.
    """
    dg_binding = -29.2
    dg_open = 3.8
    dg_total = dg_binding + dg_open
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

    # Boş dizi (empty string) kontrolü - çökme önleyici
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

    # CIF dosyası varsa yapısal destek puanı artar
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
    print("MASTER RNA PRE-SCREENING PLATFORM")
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
            
            # Bulunan CIF dosyalarını fitness hesaplamasına dahil ediyoruz
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
        # CIF yoksa None moduyla baseline hesaplar
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
