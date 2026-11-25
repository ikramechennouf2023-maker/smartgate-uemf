import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

"""
Aide pour remplir labels.csv : le script affiche chaque image (et la plaque agrandie),
tu tapes le numéro, tu choisis la lettre par un chiffre (pas besoin de clavier arabe),
puis la région. Tout est enregistré au fur et à mesure.
Usage (depuis la racine du projet) : python scripts/etiqueter_plaques.py
"""
from pathlib import Path
import cv2
import pandas as pd
import matplotlib.pyplot as plt
from format_plate import est_valide

DOSSIER = Path("data/photos_reelles")
FICHIER = DOSSIER / "labels.csv"
LETTRES = {"1": "أ", "2": "ب", "3": "د", "4": "ه", "5": "و", "6": "ط", "7": "ش", "8": "ج", "9": "ي",
           "m": "M", "0": "WW"}

try:
    from detect_plate import PlateDetector, crop_plate
    detecteur = PlateDetector()
except Exception:
    detecteur = None          # si le modèle n'est pas là : on montre seulement l'image entière

labels = pd.read_csv(FICHIER, dtype=str).fillna("")
a_faire = labels.index[labels["plaque_vraie"].str.strip() == ""].tolist()
print(f"✍️ {len(a_faire)} image(s) à étiqueter. (Entrée vide = plaque illisible · q = quitter)\n")
print("Lettres : " + "  ".join(f"{k}={v}" for k, v in LETTRES.items()) + "\n")

plt.ion()
for i in a_faire:
    nom = labels.at[i, "image"]
    image = cv2.imread(str(DOSSIER / nom))
    if image is None:
        print(f"⚠️ {nom} introuvable, ignorée")
        continue

    plt.close("all")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [3, 2]})
    axes[0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)); axes[0].set_title(nom); axes[0].axis("off")
    zoom = image
    if detecteur:
        trouve = detecteur.detect(image)
        if trouve:
            zoom = crop_plate(image, trouve[0], margin=0.15)
    axes[1].imshow(cv2.cvtColor(zoom, cv2.COLOR_BGR2RGB)); axes[1].set_title("Plaque (zoom)"); axes[1].axis("off")
    plt.tight_layout(); plt.show(); plt.pause(0.5)

    while True:
        numero = input(f"[{nom}] Numéro : ").strip()
        if numero.lower() == "q":
            labels.to_csv(FICHIER, index=False, encoding="utf-8")
            sys.exit("💾 Enregistré. À bientôt !")
        if numero == "":
            print("   → illisible, on passe.\n")
            break
        lettre = LETTRES.get(input("         Lettre (chiffre) : ").strip().lower())
        if lettre is None:
            print("   ❌ Lettre inconnue, recommence.")
            continue
        if lettre == "WW":
            plaque = f"{numero}-WW"
        else:
            plaque = f"{numero}-{lettre}-{input('         Région : ').strip()}"
        if not est_valide(plaque):
            print(f"   ❌ Format invalide ({plaque}), recommence.")
            continue
        labels.at[i, "plaque_vraie"] = plaque
        labels.to_csv(FICHIER, index=False, encoding="utf-8")          # enregistré tout de suite
        print(f"   ✅ {plaque}\n")
        break

plt.close("all")
print(f"🎉 Terminé ! {(labels['plaque_vraie'].str.strip() != '').sum()} plaque(s) remplie(s) dans {FICHIER}")
print("👉 Maintenant : python scripts/eval_photos_reelles.py")
