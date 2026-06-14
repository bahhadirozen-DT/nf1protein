import os
from collections import defaultdict

class TranscriptomeIndex:
    def __init__(self, fasta_path=None):
        self.seed_7mer_counts = defaultdict(int)
        self.seed_8mer_counts = defaultdict(int)
        if fasta_path and os.path.exists(fasta_path):
            self.load_and_index_fasta(fasta_path)
            
    def load_and_index_fasta(self, path):
        current_seq = []
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                if line.startswith(">"):
                    if current_seq:
                        self._index_sequence("".join(current_seq))
                        current_seq = []
                else:
                    current_seq.append(line.upper().replace("T", "U"))
            if current_seq:
                self._index_sequence("".join(current_seq))

    def _index_sequence(self, sequence):
        for i in range(len(sequence) - 6):
            self.seed_7mer_counts[sequence[i:i+7]] += 1
        for i in range(len(sequence) - 7):
            self.seed_8mer_counts[sequence[i:i+8]] += 1

    def calculate_off_target_score(self, rna_sequence):
        """O(1) sürede 7-mer ve 8-mer siRNA seed bölgesi off-target taraması."""
        if len(rna_sequence) < 8: return 100.0
        seq = rna_sequence.upper()
        guide_7mer = seq[1:8]
        guide_8mer = seq[0:8]
        
        COMPLEMENT = {"A": "U", "U": "A", "G": "C", "C": "G"}
        rc_7mer = "".join(COMPLEMENT.get(b, b) for b in reversed(guide_7mer))
        rc_8mer = "".join(COMPLEMENT.get(b, b) for b in reversed(guide_8mer))
        
        hits_7mer = self.seed_7mer_counts.get(rc_7mer, 0)
        hits_8mer = self.seed_8mer_counts.get(rc_8mer, 0)
        return (hits_8mer * 30.0) + (hits_7mer * 15.0)
