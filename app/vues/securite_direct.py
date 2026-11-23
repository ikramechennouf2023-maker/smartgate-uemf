import streamlit as st
from pathlib import Path
from database import dernier_passage, enregistrer_passage, corriger_plaque, trouver_vehicule
from format_plate import est_valide

st.title("📺 En direct · Barrière d'entrée")

AFFICHAGE = {
    "OUVRIR":             ("success", "✅ BARRIÈRE OUVERTE"),
    "VISITEUR":           ("warning", "❓ VISITEUR : QR code à la sécurité"),
    "AGENT":              ("error",   "⚠️ VÉRIFICATION PAR L'AGENT"),
    "OUVERTURE_MANUELLE": ("info",    "🔓 OUVERTURE MANUELLE"),
}


@st.fragment(run_every=3)
def ecran():
    p = dernier_passage()
    if p is None:
        st.info("⏳ En attente d'une voiture…")
        return
    p = dict(p)
    st.session_state.passage_actif = p

    gauche, droite = st.columns([3, 2])
    if p.get("photo") and Path(p["photo"]).exists():
        gauche.image(p["photo"], use_container_width=True)
    else:
        gauche.info("📷 Pas de photo")

    with droite:
        st.metric("Plaque", p["plaque"])
        st.metric("Confiance", f"{p['confiance']:.2f}" if p["confiance"] is not None else "—")
        st.write(f"👤 **{p.get('proprietaire') or 'Inconnu'}**")
        st.caption(f"🕒 {p['date_heure']} · {p.get('raison') or ''}")
        type_, texte = AFFICHAGE.get(p["decision"], ("info", p["decision"]))
        getattr(st, type_)(f"### {texte}")


ecran()
st.divider()

agent = st.session_state.get("identifiant", "?")
col_ouvrir, col_corriger = st.columns(2)

with col_ouvrir:
    with st.form("ouvrir", clear_on_submit=True):
        st.subheader("🔓 Ouverture manuelle")
        raison = st.selectbox("Raison", ["Ambulance / urgence", "Livraison",
                                         "Plaque illisible, vérifiée par l'agent", "Autre"])
        precision = st.text_input("Précision (obligatoire si « Autre »)")
        if st.form_submit_button("Ouvrir la barrière", type="primary", use_container_width=True):
            if raison == "Autre" and not precision.strip():
                st.warning("Merci de préciser la raison.")
            else:
                p = st.session_state.get("passage_actif") or {}
                enregistrer_passage(p.get("plaque", "?"), "OUVERTURE_MANUELLE", None,
                                    raison=f"{raison} {precision}".strip(), agent=agent)
                st.success("🚧 Barrière ouverte manuellement (noté dans le journal).")

with col_corriger:
    with st.form("corriger", clear_on_submit=True):
        st.subheader("✏️ Corriger la plaque")
        c1, c2, c3 = st.columns([3, 2, 2])
        numero = c1.text_input("Numéro", placeholder="12345")
        lettre = c2.selectbox("Lettre", ["أ", "ب", "د", "ه", "و", "ط", "ش", "ج", "M", "WW"])
        region = c3.text_input("Région", placeholder="6")
        if st.form_submit_button("Corriger", use_container_width=True):
            nouvelle = f"{numero.strip()}-WW" if lettre == "WW" else f"{numero.strip()}-{lettre}-{region.strip()}"
            p = st.session_state.get("passage_actif")
            if not est_valide(nouvelle):
                st.error(f"❌ Format invalide : {nouvelle}")
            elif p is None:
                st.warning("Aucun passage à corriger.")
            else:
                corriger_plaque(p["id"], nouvelle, agent)
                v = trouver_vehicule(nouvelle)
                if v:
                    st.success(f"✅ {nouvelle} : {v['proprietaire']} est autorisé(e) → vous pouvez ouvrir.")
                else:
                    st.warning(f"❓ {nouvelle} n'est pas autorisée → visiteur (QR code).")