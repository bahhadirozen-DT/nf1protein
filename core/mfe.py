def nussinov_max_pairs(rna_sequence):
    """Dinamik Programlama (DP) Nussinov algoritması ile maksimum iç bağ sayısını bulur."""
    seq = rna_sequence.upper().replace("T", "U")
    n = len(seq)
    if n < 5:
        return 0
    dp = [[0] * n for _ in range(n)]
    
    def can_pair(a, b):
        return (a == "A" and b == "U") or (a == "U" and b == "A") or \
               (a == "G" and b == "C") or (a == "C" and b == "G")

    for k in range(4, n):
        for i in range(n - k):
            j = i + k
            unpaired_j = dp[i][j-1]
            paired_ij = dp[i+1][j-1] + 1 if can_pair(seq[i], seq[j]) else 0
            bifurcation = 0
            for t in range(i + 1, j):
                if dp[i][t] + dp[t+1][j] > bifurcation:
                    bifurcation = dp[i][t] + dp[t+1][j]
            dp[i][j] = max(unpaired_j, paired_ij, bifurcation)
    return dp[0][n-1]

def calculate_self_structure_penalty(rna_sequence):
    """Güçlü hairpin veya stem-loop oluşturan adayları cezalandırır."""
    if not rna_sequence:
        return 0.0
    max_pairs = nussinov_max_pairs(rna_sequence)
    ratio = max_pairs / (len(rna_sequence) / 2.0)
    if ratio > 0.60:
        return ratio * 40.0
    return 0.0
