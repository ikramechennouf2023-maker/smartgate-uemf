"""
Évalue le lecteur de caractères sur le TEST du dataset B (plaques avec les vraies réponses),
et aide à choisir le seuil de confiance.
"""
from pathlib import Path
from difflib import SequenceMatcher
import cv2, yaml
from read_plate import PlateReader
from format_plate import normaliser

DS = Path("data/dataset_b")
names = yaml.safe_load(open(DS / "data.yaml"))["names"]     # index → nom de classe
reader = PlateReader()


def verite(label_file):
    """Les vraies classes de la plaque, triées de gauche à droite (selon le centre x)."""
    boites = []
    for line in open(label_file):
        p = line.split()
        if len(p) >= 5:
            boites.append((float(p[1]), names[int(p[0])]))
    return [nom for _, nom in sorted(boites)]


exactes, valides, similarite, total = 0, 0, 0.0, 0
erreurs = []
resultats = []          # (confiance, juste ?, format valide ?)

for img_path in sorted((DS / "test" / "images").iterdir()):
    label = DS / "test" / "labels" / (img_path.stem + ".txt")
    if not label.exists():
        continue

    vrai = verite(label)
    lu, conf = reader.read(cv2.imread(str(img_path)), etirer=False)   # déjà en 640×640

    plaque_lue, plaque_vraie = normaliser(lu), normaliser(vrai)
    juste = (lu == vrai) or (plaque_lue is not None and plaque_lue == plaque_vraie)
    resultats.append((conf, juste, plaque_lue is not None))

    total += 1
    if lu == vrai:
        exactes += 1
    elif len(erreurs) < 10:
        erreurs.append((img_path.name[:25], vrai, lu))
    if plaque_lue:
        valides += 1
    similarite += SequenceMatcher(None, vrai, lu).ratio()

print(f"📊 Plaques lues EXACTEMENT  : {exactes} / {total}  = {exactes/total:.1%}")
print(f"📊 Plaques au format valide : {valides} / {total}  = {valides/total:.1%}")
print(f"📊 Caractères corrects (≈)  : {similarite/total:.1%}")

print("\n🔎 Exemples d'erreurs (vrai → lu) :")
for nom, v, l in erreurs:
    print(f"   {nom} : {v} → {l}")

print("\n🎚️ Choix du seuil  (A = confiance seule  |  B = confiance + FORMAT valide)")
print("   seuil |  A acceptées  A justes |  B acceptées  B justes")
for seuil in [0.3, 0.4, 0.5, 0.6, 0.7]:
    a = [j for c, j, f in resultats if c >= seuil]
    b = [j for c, j, f in resultats if c >= seuil and f]
    print(f"   {seuil:4.2f}  | {len(a)/len(resultats):10.1%} {sum(a)/max(len(a),1):9.1%} |"
          f" {len(b)/len(resultats):10.1%} {sum(b)/max(len(b),1):9.1%}")