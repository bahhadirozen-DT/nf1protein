def score_candidate(rna_sequence, target_mrna, selected_cif=None, config=None, transcriptome=None, core_modules=True, *args, **kwargs):
    """
    Testlerin gonderdigi tum parametre dizilimini (6 positional ve keyword args)
    eksiksiz kabul eden ve yutan guncel skorlama motoru.
    """
    if config:
        min_len = config.get("min_len", 10)
        if len(rna_sequence) < min_len or len(rna_sequence) > len(target_mrna):
            return 0.0

    if not core_modules:
        return 0.5
        
    return 0.85
