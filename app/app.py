"""
SmartGate UEMF : point d'entrée de l'application.
Lancer (depuis la racine du projet) : streamlit run app/app.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import streamlit as st
from database import init_db

st.set_page_config(page_title="SmartGate UEMF", page_icon="🚧", layout="wide")
init_db()


def se_deconnecter():
    for cle in ["role", "identifiant"]:
        st.session_state.pop(cle, None)
    st.rerun()


# --- toutes les pages de l'application (dans app/vues/) ---
connexion = st.Page("vues/connexion.py", title="Connexion", icon="🔐")
visiteur  = st.Page("vues/visiteur.py", title="Visiteur", icon="📱", url_path="Visiteur")
direct    = st.Page("vues/securite_direct.py", title="En direct", icon="📺", url_path="Direct")
securite  = st.Page("vues/securite.py", title="Sécurité", icon="👮", url_path="Securite")
barriere  = st.Page("vues/barriere.py", title="Barrière", icon="🚧", url_path="Barriere")
admin     = st.Page("vues/admin_accueil.py", title="Administration", icon="👩‍💼", url_path="Admin")
sortie    = st.Page(se_deconnecter, title="Se déconnecter", icon="🚪", url_path="Deconnexion")

# --- le menu change selon le rôle ---
role = st.session_state.get("role")

if role == "securite":
    menu = st.navigation({"👮 Sécurité": [direct, securite, barriere], "Compte": [sortie]})
elif role == "admin":
    menu = st.navigation({"👩‍💼 Administration": [admin],
                          "👮 Sécurité": [direct, securite, barriere],
                          "Compte": [sortie]})
else:
    menu = st.navigation([connexion, visiteur])     # pas connecté : connexion OU visiteur (QR)

if role:
    st.sidebar.success(f"Connecté : {st.session_state['identifiant']} ({role})")

menu.run()