"""
Teste la détection + le découpage sur toutes les photos de data/test/.
Les résultats sont enregistrés dans outputs/.
"""
from pathlib import Path
import cv2
from detect_plate import PlateDetector, crop_plate

TEST_DIR = Path("data/test")
OUT_DIR = Path("outputs/detection")
OUT_DIR.mkdir(parents=True, exist_ok=True)

detector = PlateDetector()
images = sorted(TEST_DIR.glob("*.jpg")) + sorted(TEST_DIR.glob("*.jpeg")) + sorted(TEST_DIR.glob("*.png"))

found = 0
for path in images:
    image = cv2.imread(str(path))              # lire la photo
    result = detector.detect(image)

    if result is None:
        print(f"❌ {path.name} : aucune plaque trouvée")
        continue

    box, conf = result
    found += 1
    print(f"✅ {path.name} : plaque trouvée (confiance {conf:.2f}) en {box}")

    # 1) photo avec le rectangle vert
    x1, y1, x2, y2 = box
    annotated = image.copy()
    cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 4)
    cv2.putText(annotated, f"LP {conf:.2f}", (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
    cv2.imwrite(str(OUT_DIR / f"box_{path.name}"), annotated)

    # 2) la plaque découpée
    plate = crop_plate(image, box)
    cv2.imwrite(str(OUT_DIR / f"plate_{path.name}"), plate)

print(f"\n📊 Plaques trouvées : {found} / {len(images)}")