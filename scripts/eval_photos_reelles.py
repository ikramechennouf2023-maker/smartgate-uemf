import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

"""
Évalue tout le système (lecture + décision) sur des images qu'il n'a jamais vues.
Utilise une base de TEST séparée (data/eval.db) : ta vraie base n'est pas touchée.
Usage (depuis la racine du projet) : python scripts/eval_photos_reelles.py
"""
from pathlib import Path
import cv2
import pandas as pd
import database

database.DB_PATH = Path("data/eval.db")          # base de TEST séparée
if database.DB_PATH.exists():
    database.DB_PATH.unlink()
database.init_db()

from ia import lire_plaque
from decision import decider

DOSSIER = Path("data/photos_reelles")
labels = pd.read_csv(DOSSIER / "labels.csv", dtype=str).fillna("")
labels = labels[labels["plaque_vraie"].str.strip() != ""]       # on ignore les lignes non remplies
if labels.empty:
    sys.exit("❌ labels.csv : aucune plaque_vraie remplie.")

# Les voitures "autorisées" de la base de test = celles dont la décision attendue est OUVRIR
for _, r in labels[labels["decision_attendue"] == "OUVRIR"].iterrows():
    database.ajouter_vehicule(r["plaque_vraie"].strip(), "Test", "étudiant", "2099-12-31")

lignes = []
for _, r in labels.iterrows():
    image = cv2.imread(str(DOSSIER / r["image"]))
    if image is None:
        print(f"⚠️ Image introuvable : {r['image']}")
        continue
    lecture = lire_plaque(image)
    res = decider(lecture)
    lignes.append({
        "image": r["image"],
        "vraie": r["plaque_vraie"].strip(),
        "lue": lecture["plaque"] or "—",
        "plaque_trouvee": lecture["box"] is not None,
        "lecture_juste": lecture["plaque"] == r["plaque_vraie"].strip(),
        "confiance": round(lecture["confiance"], 2),
        "attendue": r["decision_attendue"],
        "obtenue": res["decision"],
    })

df = pd.DataFrame(lignes)
n = len(df)
pd.set_option("display.width", 200)
print(df.to_string(index=False))
print(f"\n📊 Sur {n} images jamais vues :")
print(f"   🔍 Plaque trouvée        : {df['plaque_trouvee'].sum()}/{n} = {df['plaque_trouvee'].mean():.0%}")
print(f"   🔤 Plaque lue exactement : {df['lecture_juste'].sum()}/{n} = {df['lecture_juste'].mean():.0%}")
print(f"   🚦 Bonne décision        : {(df['attendue'] == df['obtenue']).sum()}/{n} = "
      f"{(df['attendue'] == df['obtenue']).mean():.0%}")
dangereuses = df[(df["obtenue"] == "OUVRIR") & (df["attendue"] != "OUVRIR")]
print(f"   🔐 Ouvertures À TORT     : {len(dangereuses)}  (le plus important : doit être 0)")

print("\n🧩 Matrice de confusion des décisions (lignes = attendue, colonnes = obtenue) :")
print(pd.crosstab(df["attendue"], df["obtenue"]))

Path("outputs").mkdir(exist_ok=True)
df.to_csv("outputs/eval_photos_reelles.csv", index=False)
print("\n💾 Détails enregistrés : outputs/eval_photos_reelles.csv")
