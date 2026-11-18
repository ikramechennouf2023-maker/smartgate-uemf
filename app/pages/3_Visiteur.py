import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import streamlit as st
from database import init_db, utiliser_jeton, ajouter_visiteur, derniere_plaque_inconnue, statut_visiteur

st.set_page_config(page_title="Visiteur · SmartGate", page_icon="👋")
init_db()
st.title("👋 Bienvenue à l'UEMF")

# 1) Vérifier le QR UNE SEULE FOIS (sinon chaque clic "consommerait" le jeton)
if "acces" not in st.session_state:
    token = st.query_params.get("token")
    if not token:
        st.session_state.acces = (False, "Scannez le QR code affiché à la sécurité.")
    else:
        st.session_state.acces = utiliser_jeton(token)

ok, message = st.session_state.acces
if not ok:
    st.error(f"❌ {message}")
    st.stop()                       # on arrête la page ici

# 2) Le formulaire
if "id_visiteur" not in st.session_state:
    with st.form("formulaire"):
        nom = st.text_input("Votre nom")
        plaque = st.text_input("Plaque du véhicule", value=derniere_plaque_inconnue())
        batiment = st.selectbox("Je vais à", ["EIDIA", "Bibliothèque", "Restaurant", "Administration", "Autre"])
        motif = st.selectbox("Motif", ["Rendez-vous", "Conférence", "Livraison", "Visite", "Autre"])
        envoye = st.form_submit_button("Envoyer", type="primary", use_container_width=True)

    if envoye:
        if not nom.strip():
            st.warning("Merci d'indiquer votre nom.")
        else:
            st.session_state.id_visiteur = ajouter_visiteur(nom.strip(), plaque.strip(), batiment, motif)
            st.session_state.batiment = batiment
            st.rerun()

# 3) L'attente de la réponse de l'agent (vérifiée toutes les 2 s)
else:
    @st.fragment(run_every=2)
    def attente():
        statut = statut_visiteur(st.session_state.id_visiteur)
        if statut == "accepte":
            st.success("✅ Demande acceptée : la barrière s'ouvre. Bonne visite !")
            st.info(f"🧭 Guidage vers {st.session_state.batiment} : bientôt disponible (Module 3 de Fati).")
        elif statut == "refuse":
            st.error("❌ Demande refusée. Merci de vous adresser à l'agent de sécurité.")
        else:
            st.info("⏳ Demande envoyée. En attente de la validation de l'agent…")

    attente()