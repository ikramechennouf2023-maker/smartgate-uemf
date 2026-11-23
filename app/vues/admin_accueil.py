import streamlit as st

st.title("👩‍💼 Administration · SmartGate UEMF")
st.write(f"Bienvenue, **{st.session_state.get('identifiant', '')}** 👋")
st.info("Bientôt ici : gestion des véhicules, liste noire, journal, tableau de bord et suivi de l'IA.")