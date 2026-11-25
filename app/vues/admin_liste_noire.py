import html
import pandas as pd
import streamlit as st
from database import lire_table, ajouter_liste_noire, retirer_liste_noire
from format_plate import est_valide
from style import en_tete, label, plaque_html

en_tete("Liste noire", "Plaques interdites : la barrière reste fermée et l'agent est alerté", "🚫")

LETTRES = ["أ", "ب", "د", "ه", "و", "ط", "ش", "ج", "M", "WW"]
gauche, droite = st.columns([1, 1.5], gap="large")

with gauche:
    with st.form("noire", clear_on_submit=True):
        st.markdown("#### ➕ Ajouter une plaque")
        p1, p2, p3 = st.columns([3, 2, 2])
        numero = p1.text_input("Numéro", placeholder="12345")
        lettre = p2.selectbox("Lettre", LETTRES)
        region = p3.text_input("Région", placeholder="6")
        raison = st.selectbox("Raison", ["Véhicule signalé volé", "Personne exclue du campus",
                                         "Infractions répétées", "Autre"])
        precision = st.text_input("Précision (facultatif)")
        if st.form_submit_button("Ajouter à la liste noire", type="primary", width="stretch"):
            plaque = f"{numero.strip()}-WW" if lettre == "WW" else f"{numero.strip()}-{lettre}-{region.strip()}"
            if not est_valide(plaque):
                st.error(f"Plaque invalide : {plaque}")
            else:
                ajouter_liste_noire(plaque, f"{raison} {precision}".strip(), st.session_state.get("identifiant"))
                st.success(f"🚫 {plaque} ajoutée à la liste noire.")

with droite:
    liste = lire_table("liste_noire", ordre="ajoutee_le DESC")
    label(f"Plaques interdites · {len(liste)}")
    if not liste:
        st.markdown('<div class="sg-carte" style="text-align:center;padding:2rem;color:#6B7686">'
                    'Aucune plaque sur la liste noire.</div>', unsafe_allow_html=True)
    for n in liste:
        with st.container(border=True):
            a, b, c = st.columns([2, 3, 1])
            a.markdown(plaque_html(n["plaque"], petite=True), unsafe_allow_html=True)
            b.markdown(f"**{html.escape(n['raison'] or '')}**  \n"
                       f"<span style='color:#6B7686;font-size:.85rem'>le {n['ajoutee_le'][:16]} · par "
                       f"{html.escape(n['par'] or '?')}</span>", unsafe_allow_html=True)
            if c.button("Retirer", key=f"ret{n['plaque']}"):
                retirer_liste_noire(n["plaque"])
                st.rerun()
