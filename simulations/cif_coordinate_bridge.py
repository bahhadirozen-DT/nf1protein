import numpy as np
from Bio.PDB.MMCIFParser import MMCIFParser

def calculate_center_of_mass(residues):
    """Seçilen aminoasit/nükleotit kalıntılarının kütle merkezini hesaplar."""
    total_mass = 0.0
    center_of_mass = np.array([0.0, 0.0, 0.0])
    
    # Basit bir atomik kütle matrisi (Geliştirilebilir)
    mass_dict = {'C': 12.011, 'N': 14.007, 'O': 15.999, 'S': 32.06, 'P': 30.974, 'H': 1.008}
    
    for residue in residues:
        for atom in residue.get_atoms():
            element = atom.element
            mass = mass_dict.get(element, 12.011) # Varsayılan karbon kütlesi
            center_of_mass += atom.get_coord() * mass
            total_mass += mass
            
    if total_mass == 0:
        return np.array([0.0, 0.0, 0.0])
    return center_of_mass / total_mass

def extract_real_theta_init(cif_path, protein_chain='A', rna_chain='B'):
    """
    AlphaFold .cif dosyasından protein ve RNA arasındaki gerçek geometrik 
    erişim/sapma açısını (theta_init) hesaplar.
    """
    parser = MMCIFParser(QUIET=True)
    structure = parser.get_structure("AF3_Model", cif_path)
    model = structure[0]
    
    # 1. Zincirleri Yakala
    try:
        p_residues = list(model[protein_chain].get_residues())
        r_residues = list(model[rna_chain].get_residues())
    except KeyError:
        print(f"[!] Hata: {protein_chain} veya {rna_chain} zincirleri bulunamadı. Varsayılan açı atanıyor.")
        return np.radians(30) # Yedek varsayılan başlangıç açısı
        
    # 2. Kütle Merkezlerini (Center of Mass - COM) Hesapla
    com_protein = calculate_center_of_mass(p_residues)
    com_rna = calculate_center_of_mass(r_residues)
    
    # 3. Protein ve RNA arasındaki yönelim vektörünü kur
    vector_interaction = com_rna - com_protein
    
    # 4. Doğal downstream sinyal aksı (Varsayılan Z ekseni olarak indirgenmiştir)
    # Gerçek biyolojide bu, RAF-RBD bağlanma doğrultusudur.
    z_axis = np.array([0.0, 0.0, 1.0])
    
    # İki vektör arasındaki açıyı hesapla (Dot Product yöntemi)
    dot_product = np.dot(vector_interaction, z_axis)
    norm_interaction = np.linalg.norm(vector_interaction)
    norm_z = np.linalg.norm(z_axis)
    
    cos_theta = dot_product / (norm_interaction * norm_z)
    theta_rad = np.arccos(np.clip(cos_theta, -1.0, 1.0))
    
    # Açıyı 0-90 derece arasına kısıtla (Aksiyel simetri)
    if theta_rad > np.pi / 2:
        theta_rad = np.pi - theta_rad
        
    print(f"[✓] AlphaFold Koordinat Analizi Başarılı!")
    print(f"    -> Protein COM: {com_protein}")
    print(f"    -> RNA COM: {com_rna}")
    print(f"    -> Ölçülen Gerçek Başlangıç Açısı: {np.degrees(theta_rad):.2f}°")
    
    return theta_rad

if __name__ == "__main__":
    # Test çalıştırması için dosya yolu (alphafold_models klasöründeki model_0)
    cif_file_path = "../alphafold_models/fold_2026_05_15_18_38_model_0.cif"
    
    # Varsayılan zincirler: Protein için 'A', Sentetik RNA (SRX-RNA01) için 'B'
    theta_init = extract_real_theta_init(cif_file_path, protein_chain='A', rna_chain='B')
