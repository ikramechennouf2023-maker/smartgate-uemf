import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'src'))
"""
Affiche 6 exemples de chaque classe '10' à '20' du dataset B,
pour reconnaître quelle lettre arabe correspond à chaque numéro.
"""
from pathlib import Path
import random, cv2, yaml
import matplotlib.pyplot as plt

DS = Path("data/dataset_b")
names = yaml.safe_load(open(DS / "data.yaml"))["names"]
lettres = [i for i, n in enumerate(names) if int(n) >= 10]
crops = {i: [] for i in lettres}

labels = list(DS.glob("*/labels/*.txt"))
random.seed(0)
random.shuffle(labels)

for lab in labels:
    img_path = next((lab.parent.parent / "images" / (lab.stem + e)
                     for e in (".jpg", ".jpeg", ".png")
                     if (lab.parent.parent / "images" / (lab.stem + e)).exists()), None)
    if img_path is None:
        continue
    img = cv2.imread(str(img_path))
    H, W = img.shape[:2]
    for line in open(lab):
        p = line.split()
        if len(p) < 5:
            continue
        c = int(p[0])
        if c not in crops or len(crops[c]) >= 6:
            continue
        xc, yc, w, h = map(float, p[1:5])
        x1, y1 = int((xc - w / 2) * W), int((yc - h / 2) * H)
        x2, y2 = int((xc + w / 2) * W), int((yc + h / 2) * H)
        crop = img[max(0, y1):y2, max(0, x1):x2]
        if crop.size:
            crops[c].append(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
    if all(len(v) >= 6 for v in crops.values()):
        break

fig, axes = plt.subplots(len(lettres), 6, figsize=(8, 1.5 * len(lettres)))
for row, i in enumerate(lettres):
    for j in range(6):
        axes[row][j].axis("off")
        if j < len(crops[i]):
            axes[row][j].imshow(crops[i][j])
    axes[row][0].set_title(f"classe '{names[i]}' ({len(crops[i])} ex.)", fontsize=11, loc="left")
plt.tight_layout()

Path("outputs").mkdir(exist_ok=True)
plt.savefig("outputs/classes_lettres.png", dpi=120)
print("✅ Image enregistrée : outputs/classes_lettres.png")
plt.show()