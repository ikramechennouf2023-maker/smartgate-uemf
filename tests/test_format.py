"""
Tests automatiques de format_plate.py
Lancer : python src/test_format.py
"""
import sys
from pathlib import Path

# pour trouver format_plate.py, que ce fichier soit dans src/ ou dans tests/
ici = Path(__file__).resolve().parent
sys.path.insert(0, str(ici))
sys.path.insert(0, str(ici.parent / "src"))

from format_plate import normaliser, est_valide, LETTRES

# La lettre attendue : la vraie lettre arabe si elle est dans LETTRES, sinon "L10", "L12"…
L10 = LETTRES.get("10", "L10")
L12 = LETTRES.get("12", "L12")

# ---------- normaliser : les plaques correctes ----------
assert normaliser(['1','2','3','4','5','10','6']) == f"12345-{L10}-6"
assert normaliser(['4','5','2','1','12','1','5']) == f"4521-{L12}-15"
assert normaliser(['2','2','5','8','10','10','10','1']) == f"2258-{L10}-1"   # lettre répétée → fusionnée

# ---------- normaliser : les plaques impossibles → None ----------
assert normaliser(['1','2','3','4','5','6']) is None             # pas de lettre
assert normaliser(['1','2','10','11','6']) is None               # 2 lettres différentes
assert normaliser(['1','2','3','4','5','6','10','7']) is None    # 6 chiffres avant la lettre
assert normaliser(['1','2','3','10','9','5']) is None            # région 95 (> 89)
assert normaliser(['1','2','3','10']) is None                    # pas de région
assert normaliser([]) is None                                     # rien lu

# ---------- est_valide : vérifier une plaque déjà écrite ----------
assert est_valide("12345-أ-6")
assert est_valide("12345-L10-6")
assert est_valide(f"12345-{L10}-6")
assert not est_valide("12345-6")          # pas de lettre
assert not est_valide("ABC-أ-6")          # pas de chiffres au début
assert not est_valide("123456-أ-6")       # 6 chiffres
assert not est_valide("")                

# ---------- nouveaux cas ----------
assert normaliser(['5','9','7','4','0','1','15','15']) == "597401-WW"          # plaque temporaire
assert normaliser(['1','2','3','4','5','10','6','18']) == f"12345-{L10}-6"     # mot المغرب ignoré
assert normaliser(['1','2','3','4','5','6','7','15','15']) is None             # 7 chiffres → impossible
assert est_valide("597401-WW") # vide

print("✅ Tous les tests passent !")
print(f"   (lettre de la classe '10' : {L10} · classe '12' : {L12})")