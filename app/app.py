"""
SmartGate UEMF : point d'entrée de l'application.
Lancer (depuis la racine du projet) : streamlit run app/app.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
import database
from database import init_db
from style import appliquer_style, carte_utilisateur

st.set_page_config(page_title="SmartGate UEMF", page_icon="🚧", layout="wide",
                   initial_sidebar_state="expanded")
appliquer_style()
init_db()

# Sur le serveur en ligne : créer les comptes si la base est vide
with database.connexion() as conn:
    nb_comptes = conn.execute("SELECT COUNT(*) FROM utilisateurs").fetchone()[0]
if nb_comptes == 0:
    try:
        database.creer_utilisateur("admin", st.secrets["ADMIN_PASSWORD"], "admin")
        database.creer_utilisateur("agent1", st.secrets["AGENT_PASSWORD"], "securite")
    except Exception:
        pass   # pas de secrets (sur le Mac) : on utilise scripts/creer_comptes.py

LOGO = Path(__file__).resolve().parent / "assets" / "logo_uemf.png"
if LOGO.exists():
    st.logo(str(LOGO), size="large")


def se_deconnecter():
    for cle in ["role", "identifiant"]:
        st.session_state.pop(cle, None)
    st.rerun()


# --- toutes les pages (dans app/vues/) ---
connexion  = st.Page("vues/connexion.py", title="Connexion", icon="🔐", url_path="Connexion")
visiteur   = st.Page("vues/visiteur.py", title="Visiteur", icon="📱", url_path="Visiteur")
direct     = st.Page("vues/securite_direct.py", title="En direct", icon="📺", url_path="Direct")
securite   = st.Page("vues/securite.py", title="Visiteurs & QR", icon="🔲", url_path="Securite")
barriere   = st.Page("vues/barriere.py", title="Caméra (simulation)", icon="📷", url_path="Barriere")
tableau    = st.Page("vues/admin_accueil.py", title="Tableau de bord", icon="📊", url_path="Admin")
vehicules  = st.Page("vues/admin_vehicules.py", title="Véhicules autorisés", icon="🚗", url_path="Vehicules")
noire      = st.Page("vues/admin_liste_noire.py", title="Liste noire", icon="🚫", url_path="ListeNoire")
journal    = st.Page("vues/admin_journal.py", title="Journal", icon="📋", url_path="Journal")
suivi_ia   = st.Page("vues/admin_ia.py", title="Suivi de l'IA", icon="🧠", url_path="IA")
sortie     = st.Page(se_deconnecter, title="Se déconnecter", icon="🚪", url_path="Deconnexion")

role = st.session_state.get("role")

if role == "securite":
    menu = st.navigation({"Sécurité": [direct, securite, barriere], "Compte": [sortie]})
elif role == "admin":
    menu = st.navigation({"Administration": [tableau, vehicules, noire, journal, suivi_ia],
                          "Sécurité": [direct, securite, barriere],
                          "Compte": [sortie]})
else:
    menu = st.navigation([connexion, visiteur])     # pas connecté : connexion OU visiteur (QR)

if role:
    carte_utilisateur(st.session_state["identifiant"], role)

menu.run()