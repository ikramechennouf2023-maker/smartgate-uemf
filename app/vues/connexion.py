import streamlit as st
from database import verifier_connexion

st.title("🔐 Connexion · SmartGate UEMF")

with st.form("connexion"):
    identifiant = st.text_input("Identifiant")
    mot_de_passe = st.text_input("Mot de passe", type="password")
    valider = st.form_submit_button("Se connecter", type="primary", use_container_width=True)

if valider:
    role = verifier_connexion(identifiant.strip(), mot_de_passe)
    if role:
        st.session_state.role = role
        st.session_state.identifiant = identifiant.strip()
        st.rerun()
    else:
        st.error("❌ Identifiant ou mot de passe incorrect.")

st.caption("Vous êtes visiteur ? Scannez le QR code affiché à la sécurité. 📱")