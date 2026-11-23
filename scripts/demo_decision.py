import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'src'))
"""
Démo de l'étape E : on autorise 2 voitures des images de test, puis on passe TOUTES les images à la barrière.
"""
from pathlib import Path
from collections import Counter
import cv2
from database import init_db, ajouter_vehicule
from ia import lire_plaque
from decision import traiter_entree

init_db()
images = sorted(p for p in Path("data/test").iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})

# 1) On "inscrit" les 2 premières plaques bien lues comme autorisées (pour la démo)
inscrites = 0
for p in images:
    lecture = lire_plaque(cv2.imread(str(p)))
    if lecture["plaque"] and inscrites < 2:
        ajouter_vehicule(lecture["plaque"], f"Étudiant démo {inscrites + 1}", "étudiant", "2027-06-30")
        print(f"📝 Inscrite dans la base : {lecture['plaque']}")
        inscrites += 1

# 2) Toutes les voitures passent à la barrière
print("\n🚧 Passages à la barrière :")
icones = {"OUVRIR": "✅", "VISITEUR": "❓", "AGENT": "⚠️"}
compte = Counter()
for p in images:
    r = traiter_entree(cv2.imread(str(p)))
    compte[r["decision"]] += 1
    print(f"{icones[r['decision']]} {p.name[:22]:22s} {str(r['plaque']):14s} → {r['decision']:8s} ({r['raison']})")

print("\n📊 Bilan :", dict(compte))