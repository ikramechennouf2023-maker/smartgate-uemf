import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

"""
Remplit l'application avec des DONNÉES DE DÉMONSTRATION (fictives) sur les 14 derniers jours,
pour que le tableau de bord et le suivi de l'IA aient quelque chose à montrer.
Usage : python scripts/donnees_demo.py
Pour tout effacer ensuite : supprimer le fichier data/smartgate.db
"""
import random
from datetime import date, datetime, timedelta
from database import init_db, connexion, ajouter_vehicule, ajouter_liste_noire, enregistrer_passage

random.seed(42)
init_db()
LETTRES = ["أ", "ب", "د", "ه", "و", "ط", "ش", "ج"]


def plaque():
    return f"{random.randint(1, 99999)}-{random.choice(LETTRES)}-{random.randint(1, 89)}"


# 1) Véhicules autorisés (fictifs)
vehicules = []
for i in range(1, 41):
    role = "étudiant" if i <= 30 else ("professeur" if i <= 36 else "personnel")
    nom = {"étudiant": f"Étudiant(e) démo {i}", "professeur": f"Professeur démo {i - 30}",
           "personnel": f"Personnel démo {i - 36}"}[role]
    fin = date(date.today().year + 1, 6, 30) if i % 9 else date.today() + timedelta(days=random.randint(-20, 25))
    p = plaque()
    ajouter_vehicule(p, nom, role, fin.isoformat(), handicap=(i % 17 == 0))
    vehicules.append((p, nom, role))

# 2) Liste noire
ajouter_liste_noire(plaque(), "Véhicule signalé volé (démo)", "admin")
ajouter_liste_noire(plaque(), "Personne exclue du campus (démo)", "admin")

# 3) Passages + visiteurs sur 14 jours
HEURES = [7, 8, 8, 8, 9, 9, 10, 11, 12, 13, 13, 14, 14, 15, 16, 17, 18, 19]
BATIMENTS = ["EIDIA", "Bibliothèque", "Restaurant", "Administration", "Autre"]
MOTIFS = ["Rendez-vous", "Conférence", "Livraison", "Visite"]
n_passages = n_visiteurs = 0
visiteurs, corrections = [], []

for jours in range(13, -1, -1):
    jour = date.today() - timedelta(days=jours)
    week_end = jour.weekday() >= 5
    for _ in range(random.randint(10, 20) if week_end else random.randint(45, 85)):
        quand = datetime.combine(jour, datetime.min.time()) + timedelta(
            hours=random.choice(HEURES), minutes=random.randint(0, 59), seconds=random.randint(0, 59))
        if quand > datetime.now():
            continue
        h = quand.strftime("%Y-%m-%d %H:%M:%S")
        tirage = random.random()
        if tirage < 0.72:
            p, nom, role = random.choice(vehicules)
            enregistrer_passage(p, "OUVRIR", round(random.uniform(0.55, 0.98), 2),
                                raison=f"{role} autorisé(e)", proprietaire=nom, date_heure=h)
        elif tirage < 0.84:
            enregistrer_passage(plaque(), "VISITEUR", round(random.uniform(0.5, 0.95), 2),
                                raison="plaque inconnue → QR code à la sécurité", date_heure=h)
            visiteurs.append((f"Visiteur démo {n_visiteurs + 1}", plaque(), random.choice(BATIMENTS),
                          random.choice(MOTIFS), jour.isoformat(), random.choice(["accepte"] * 5 + ["refuse"])))
            n_visiteurs += 1
        elif tirage < 0.97:
            c = round(random.uniform(0.15, 0.49), 2)
            enregistrer_passage("?", "AGENT", c, raison=f"lecture incertaine ({c:.2f})", date_heure=h)
        elif tirage < 0.985:
            enregistrer_passage(plaque(), "REFUSE", round(random.uniform(0.6, 0.95), 2),
                                raison="liste noire : démo", date_heure=h)
        else:
            enregistrer_passage("?", "OUVERTURE_MANUELLE", None, raison="Livraison", agent="agent1", date_heure=h)
        n_passages += 1
for _ in range(6):
    p, _, _ = random.choice(vehicules)
    corrections.append((p[1:], p, "agent1", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

with connexion() as conn:
    conn.executemany("INSERT INTO visiteurs (nom, plaque, batiment, motif, date, statut) VALUES (?,?,?,?,?,?)", visiteurs)
    conn.executemany("INSERT INTO corrections (plaque_lue, plaque_corrigee, agent, date_heure) VALUES (?,?,?,?)", corrections)

print(f"✅ Données de démonstration ajoutées : 40 véhicules, 2 plaques en liste noire, "
      f"{n_passages} passages, {n_visiteurs} visiteurs.")
