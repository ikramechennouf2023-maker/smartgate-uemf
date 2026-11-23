import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))   # pour trouver nos fichiers de src/

import cv2
import numpy as np
import streamlit as st
from database import init_db
from decision import traiter_entree

init_db()
st.title("🚧 Barrière d'entrée")
st.caption("Simulation de la caméra : envoyez la photo d'une voiture.")

fichier = st.file_uploader("Photo de la voiture", type=["jpg", "jpeg", "png"])

if fichier:
    cle = f"{fichier.name}-{fichier.size}"
    # On ne traite chaque photo qu'UNE fois (sinon chaque clic relancerait la lecture et le journal)
    if st.session_state.get("derniere_photo") != cle:
        image = cv2.imdecode(np.frombuffer(fichier.read(), np.uint8), cv2.IMREAD_COLOR)
        with st.spinner("Lecture de la plaque…"):
            st.session_state.resultat = traiter_entree(image)
        st.session_state.image = image
        st.session_state.derniere_photo = cle

    r, image = st.session_state.resultat, st.session_state.image.copy()
    if r["box"]:
        x1, y1, x2, y2 = r["box"]
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 4)

    gauche, droite = st.columns([3, 2])
    gauche.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), use_container_width=True)

    with droite:
        st.metric("Plaque lue", r["plaque"] or "?")
        st.metric("Confiance", f"{r['confiance']:.2f}")
        if r["decision"] == "OUVRIR":
            st.success(f"✅ BARRIÈRE OUVERTE : {r['proprietaire']} ({r['raison']})")
        elif r["decision"] == "VISITEUR":
            st.warning(f"❓ VISITEUR : {r['raison']}")
        else:
            st.error(f"⚠️ AGENT : {r['raison']}")