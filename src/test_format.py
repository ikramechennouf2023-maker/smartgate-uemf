import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from format_plate import normaliser, est_valide

# --- normaliser ---
assert normaliser(['1','2','3','4','5','10','6']) == "12345-L10-6"
assert normaliser(['4','5','2','1','12','1','5']) == "4521-L12-15"
assert normaliser(['1','2','3','4','5','6']) is None            # pas de lettre
assert normaliser(['1','2','10','11','6']) is None              # 2 lettres
assert normaliser(['1','2','3','4','5','6','10','7']) is None   # 6 chiffres avant
assert normaliser(['1','2','3','10','9','5']) is None           # région 95
assert normaliser([]) is None                                    # rien lu

# --- est_valide ---
assert est_valide("12345-أ-6")
assert est_valide("12345-L10-6")
assert not est_valide("12345-6")
assert not est_valide("ABC-أ-6")
assert not est_valide("")
assert normaliser(['2','2','5','8','10','10','10','1']) == "2258-L10-1"   # lettre répétée

print("✅ Tous les tests passent !")