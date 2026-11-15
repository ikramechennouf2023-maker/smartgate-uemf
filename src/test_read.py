"""
Teste : détection → découpage → lecture → format, sur les images de data/test/.
"""
from pathlib import Path
import cv2
from detect_plate import PlateDetector, crop_plate
from read_plate import PlateReader
from format_plate import normaliser

TEST_DIR = Path("data/test")
EXTENSIONS = {".jpg", ".jpeg", ".png"}
images = sorted(p for p in TEST_DIR.iterdir() if p.suffix.lower() in EXTENSIONS)

detector = PlateDetector()
reader = PlateReader()

ok = 0
for path in images:
    image = cv2.imread(str(path))
    found = detector.detect(image)
    if found is None:
        print(f"❌ {path.name[:22]:22s} : pas de plaque")
        continue

    box, _ = found
    caracteres, conf = reader.read(crop_plate(image, box))
    plaque = normaliser(caracteres)

    if plaque:
        ok += 1
        print(f"✅ {path.name[:22]:22s} : {plaque:14s} (confiance {conf:.2f})")
    else:
        print(f"⚠️ {path.name[:22]:22s} : format invalide, lu {caracteres} (confiance {conf:.2f})")

print(f"\n📊 Plaques au bon format : {ok} / {len(images)}")