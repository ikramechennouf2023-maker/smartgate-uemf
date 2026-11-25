import html
from pathlib import Path
import streamlit as st
from database import (dernier_passage, derniers_passages, enregistrer_passage,
                      corriger_plaque, trouver_vehicule, est_liste_noire)
from format_plate import est_valide
from style import en_tete, label, plaque_html, plaque_texte, statut_html, chip, COULEURS_DECISION, LIBELLES

en_tete("Barrière d'entrée", "Mise à jour automatique toutes les 3 secondes", "📺", direct=True)


# ---------- L'écran qui se met à jour tout seul ----------
@st.fragment(run_every=3)
def ecran():
    p = dernier_passage()
    if p is None:
        st.info("⏳ En attente d'une voiture…")
        return
    p = dict(p)
    st.session_state.passage_actif = p

    gauche, droite = st.columns([3, 2], gap="large")
    with gauche:
        label("Caméra · entrée principale")
        if p.get("photo") and Path(p["photo"]).exists():
            st.image(p["photo"], width="stretch")
        else:
            st.markdown('<div class="sg-carte" style="height:320px;display:flex;align-items:center;'
                        'justify-content:center;color:#6B7686;font-size:1.1rem">📷 Pas de photo pour ce passage</div>',
                        unsafe_allow_html=True)

    with droite:
        st.markdown(statut_html(p["decision"], p.get("raison") or ""), unsafe_allow_html=True)
        label("Plaque lue")
        st.markdown(plaque_html(p["plaque"]), unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("Confiance", f"{p['confiance']:.2f}" if p["confiance"] is not None else "—")
        c2.metric("Heure", p["date_heure"][11:16])
        label("Conducteur")
        st.markdown(f'<div class="sg-carte">👤 <b>{html.escape(p.get("proprietaire") or "Inconnu")}</b>'
                    f'{" · agent " + html.escape(p["agent"]) if p.get("agent") else ""}</div>',
                    unsafe_allow_html=True)

    label("Derniers passages")
    puces = ""
    for d in derniers_passages(8)[1:]:
        couleur = COULEURS_DECISION.get(d["decision"], "#2E6FB5")
        puces += chip(f"{d['date_heure'][11:16]} · {plaque_texte(d['plaque'])} · {LIBELLES.get(d['decision'], d['decision'])}", couleur)
    st.markdown(puces or "<span style='color:#6B7686'>—</span>", unsafe_allow_html=True)


ecran()
st.write("")

agent = st.session_state.get("identifiant", "?")
col_ouvrir, col_corriger = st.columns(2, gap="large")

# ---------- 🔓 Ouverture manuelle ----------
with col_ouvrir:
    with st.form("ouvrir", clear_on_submit=True):
        st.markdown("#### 🔓 Ouverture manuelle")
        raison = st.selectbox("Raison", ["Ambulance / urgence", "Livraison",
                                         "Plaque illisible, vérifiée par l'agent", "Autre"])
        precision = st.text_input("Précision (obligatoire si « Autre »)")
        if st.form_submit_button("Ouvrir la barrière", type="primary", width="stretch"):
            if raison == "Autre" and not precision.strip():
                st.warning("Merci de préciser la raison.")
            else:
                p = st.session_state.get("passage_actif") or {}
                enregistrer_passage(p.get("plaque", "?"), "OUVERTURE_MANUELLE", None,
                                    raison=f"{raison} {precision}".strip(),
                                    proprietaire=p.get("proprietaire"), agent=agent)
                st.success("🚧 Barrière ouverte manuellement (enregistré dans le journal).")

# ---------- ✏️ Corriger une plaque mal lue ----------
with col_corriger:
    with st.form("corriger", clear_on_submit=True):
        st.markdown("#### ✏️ Corriger la plaque")
        c1, c2, c3 = st.columns([3, 2, 2])
        numero = c1.text_input("Numéro", placeholder="12345")
        lettre = c2.selectbox("Lettre", ["أ", "ب", "د", "ه", "و", "ط", "ش", "ج", "M", "WW"])
        region = c3.text_input("Région", placeholder="6")
        if st.form_submit_button("Corriger", width="stretch"):
            nouvelle = f"{numero.strip()}-WW" if lettre == "WW" else f"{numero.strip()}-{lettre}-{region.strip()}"
            p = st.session_state.get("passage_actif")
            if not est_valide(nouvelle):
                st.error(f"Format invalide : {nouvelle}")
            elif p is None:
                st.warning("Aucun passage à corriger.")
            else:
                corriger_plaque(p["id"], nouvelle, agent)
                if est_liste_noire(nouvelle):
                    st.error(f"🚫 {nouvelle} est sur la liste noire : ne pas ouvrir.")
                elif (v := trouver_vehicule(nouvelle)):
                    st.success(f"✅ {nouvelle} : {v['proprietaire']} est autorisé(e) → vous pouvez ouvrir.")
                else:
                    st.warning(f"❓ {nouvelle} n'est pas autorisée → visiteur (QR code).")
