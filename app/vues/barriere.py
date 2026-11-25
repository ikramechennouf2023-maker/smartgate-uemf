import cv2
import numpy as np
import streamlit as st
from decision import traiter_entree
from style import en_tete, label, plaque_html, statut_html

en_tete("Caméra (simulation)", "Envoyez la photo d'une voiture : le système lit la plaque et décide", "📷")

fichier = st.file_uploader("Photo de la voiture", type=["jpg", "jpeg", "png"])

if not fichier:
    st.markdown('<div class="sg-carte" style="text-align:center;padding:2.2rem;color:#6B7686">'
                '⬆️ Déposez une photo ci-dessus pour simuler l\'arrivée d\'une voiture à la barrière.</div>',
                unsafe_allow_html=True)
else:
    cle = f"{fichier.name}-{fichier.size}"
    # On ne traite chaque photo qu'UNE fois (sinon chaque clic relancerait la lecture et le journal)
    if st.session_state.get("derniere_photo") != cle:
        image = cv2.imdecode(np.frombuffer(fichier.read(), np.uint8), cv2.IMREAD_COLOR)
        with st.spinner("🧠 Lecture de la plaque…"):
            st.session_state.resultat = traiter_entree(image)
        st.session_state.image = image
        st.session_state.derniere_photo = cle

    r, image = st.session_state.resultat, st.session_state.image.copy()
    if r["box"]:
        x1, y1, x2, y2 = r["box"]
        epaisseur = max(3, image.shape[1] // 250)
        cv2.rectangle(image, (x1, y1), (x2, y2), (91, 191, 76), epaisseur)

    gauche, droite = st.columns([3, 2], gap="large")
    with gauche:
        label("Image analysée")
        st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), width="stretch")

    with droite:
        detail = " · ".join(x for x in [r.get("proprietaire"), r.get("raison")] if x)
        st.markdown(statut_html(r["decision"], detail), unsafe_allow_html=True)
        label("Plaque lue")
        st.markdown(plaque_html(r["plaque"] or "?"), unsafe_allow_html=True)
        st.metric("Confiance de lecture", f"{r['confiance']:.2f}")
        st.caption("Le passage est enregistré dans le journal et visible sur l'écran « En direct ».")
