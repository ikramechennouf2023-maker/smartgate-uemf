"""
Compare 3 façons de lire la plaque, et enregistre les images annotées.
"""
from pathlib import Path
import cv2
from detect_plate import PlateDetector, crop_plate
from read_plate import PlateReader
from format_plate import normaliser

TEST_DIR = Path("data/test")
OUT = Path("outputs/diagnostic")
OUT.mkdir(parents=True, exist_ok=True)

images = sorted(p for p in TEST_DIR.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
detector, reader = PlateDetector(), PlateReader()

def etirer(morceau, taille=640):
    """Étire la plaque en carré, comme les images d'entraînement de Roboflow."""
    return cv2.resize(morceau, (taille, taille))

strategies = {
    "serre":        lambda img, box: crop_plate(img, box, margin=0.05),
    "serre0":       lambda img, box: crop_plate(img, box, margin=0.0),
    "etiree":       lambda img, box: etirer(crop_plate(img, box, margin=0.05)),
    "etiree0":      lambda img, box: etirer(crop_plate(img, box, margin=0.0)),
}
valides = {nom: 0 for nom in strategies}
confs = {nom: [] for nom in strategies}

for path in images:
    img = cv2.imread(str(path))
    found = detector.detect(img)
    if found is None:
        continue
    box, _ = found
    print(f"\n📷 {path.name[:30]}")
    for nom, prendre in strategies.items():
        morceau = prendre(img, box)
        caracteres, conf = reader.read(morceau)
        plaque = normaliser(caracteres)
        if plaque:
            valides[nom] += 1
            confs[nom].append(conf)
        print(f"   {nom:8s} → {plaque or 'invalide':16s} lu={caracteres}  conf={conf:.2f}")

        # image annotée : les rectangles et les classes trouvés par le modèle
        res = reader.model(morceau, conf=0.25, verbose=False)[0]
        cv2.imwrite(str(OUT / f"{nom}_{path.stem[:20]}.jpg"), res.plot())

print("\n📊 RÉSUMÉ")
for nom in strategies:
    moy = sum(confs[nom]) / len(confs[nom]) if confs[nom] else 0
    print(f"   {nom:8s} : {valides[nom]:2d} / {len(images)} plaques valides, confiance moyenne {moy:.2f}")