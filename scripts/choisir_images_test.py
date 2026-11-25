import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

"""
1) Compare chaque image du nouveau dataset avec TOUTES les images du dataset d'entraînement (Naima).
2) Écarte les doublons.
3) Copie 25 images vraiment nouvelles dans data/photos_reelles + crée labels.csv.
Usage (depuis la racine du projet) : python scripts/choisir_images_test.py
"""
import random
from pathlib import Path
import cv2
import numpy as np

ENTRAINEMENT = Path("data/dataset_a")              # le dataset de Naima
NOUVEAU = Path("data/dataset_independant")         # le dataset de chine-jackyie
DEST = Path("data/photos_reelles")
SEUIL = 20                                          # moins de 20 différences sur 256 = doublon
EXT = {".jpg", ".jpeg", ".png"}


def empreinte(chemin, miroir=False):
    """Empreinte de 256 cases (0/1) : chaque pixel est-il plus clair que son voisin de gauche ?"""
    img = cv2.imread(str(chemin), cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    if miroir:
        img = cv2.flip(img, 1)
    petit = cv2.resize(img, (17, 16), interpolation=cv2.INTER_AREA)
    return (petit[:, 1:] > petit[:, :-1]).flatten()


images_a = [p for p in ENTRAINEMENT.rglob("*") if p.suffix.lower() in EXT]
images_n = [p for p in NOUVEAU.rglob("*") if p.suffix.lower() in EXT]
print(f"📦 Dataset d'entraînement : {len(images_a)} images · nouveau dataset : {len(images_n)} images")
if not images_a or not images_n:
    sys.exit("❌ Un des deux dossiers est vide : vérifie data/dataset_a et data/dataset_independant")

A = np.array([e for e in (empreinte(p) for p in images_a) if e is not None])

nouvelles, doublons = [], []
for p in images_n:
    e, e_miroir = empreinte(p), empreinte(p, miroir=True)
    if e is None:
        continue
    distance = min((A != e).sum(axis=1).min(), (A != e_miroir).sum(axis=1).min())
    (doublons if distance < SEUIL else nouvelles).append((p, distance))

print(f"🔁 Doublons trouvés (déjà vus à l'entraînement) : {len(doublons)}")
print(f"✅ Images vraiment nouvelles : {len(nouvelles)}")
for p, d in doublons[:3]:
    print(f"   exemple de doublon : {p.name} (distance {d})")

random.seed(0)
choix = random.sample(nouvelles, min(25, len(nouvelles)))
DEST.mkdir(parents=True, exist_ok=True)
lignes = ["image,plaque_vraie,decision_attendue"]
for i, (p, _) in enumerate(choix, 1):
    nom = f"img_{i:02d}.jpg"
    cv2.imwrite(str(DEST / nom), cv2.imread(str(p)))
    lignes.append(f"{nom},," + ("OUVRIR" if i % 2 else "VISITEUR"))
(DEST / "labels.csv").write_text("\n".join(lignes) + "\n", encoding="utf-8")
print(f"\n📁 {len(choix)} images copiées dans {DEST} + labels.csv à compléter ✍️")
