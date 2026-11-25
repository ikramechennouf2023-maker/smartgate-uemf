import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

"""
Crée (ou réinitialise) les comptes de l'application.
Usage (depuis la racine du projet) : python scripts/creer_comptes.py
"""
from getpass import getpass
from database import init_db, creer_utilisateur

init_db()
for identifiant, role in [("admin", "admin"), ("agent1", "securite")]:
    mdp = getpass(f"Mot de passe pour {identifiant} ({role}) : ")
    creer_utilisateur(identifiant, mdp, role)
    print(f"✅ Compte créé : {identifiant} → rôle {role}")
