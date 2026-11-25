import html
import io
import socket
import time
import qrcode
import streamlit as st
from database import (creer_jeton, demandes_en_attente, accepter_visiteur, changer_statut_visiteur,
                      enregistrer_passage, verifier_passe)
from style import en_tete, label, plaque_html

PERIODE = 30   # un nouveau QR toutes les 30 secondes


def ip_locale():
    """L'adresse du Mac sur le Wi-Fi (pour que le téléphone puisse ouvrir l'application)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "localhost"
    finally:
        s.close()


def image_qr(texte):
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(texte)
    qr.make(fit=True)
    buf = io.BytesIO()
    qr.make_image(fill_color="#0F2747", back_color="white").save(buf, format="PNG")
    return buf.getvalue()


en_tete("Visiteurs & QR code", "Le visiteur scanne le QR, remplit le formulaire, vous validez", "🔲")
base = st.sidebar.text_input("Adresse de l'application (pour le QR)", f"http://{ip_locale()}:8501")

col_qr, col_demandes = st.columns([1, 1.6], gap="large")

# ---------- Le QR dynamique ----------
with col_qr:
    @st.fragment(run_every=1)
    def bloc_qr():
        maintenant = time.time()
        if "jeton" not in st.session_state or maintenant - st.session_state.jeton_cree > PERIODE:
            st.session_state.jeton = creer_jeton()
            st.session_state.jeton_cree = maintenant
        lien = f"{base}/Visiteur?token={st.session_state.jeton}"
        reste = PERIODE - int(maintenant - st.session_state.jeton_cree)

        with st.container(border=True):
            st.markdown("<div style='text-align:center;font-weight:800;font-size:1.15rem;color:#0F2747'>"
                        "Visiteur ? Scannez-moi 📱</div>", unsafe_allow_html=True)
            st.image(image_qr(lien), width="stretch")
            st.progress(max(reste, 0) / PERIODE, text=f"⏱️ Nouveau QR dans {reste} s")
            st.caption("Valable 2 minutes · une seule utilisation")

    bloc_qr()

    with st.container(border=True):
        st.markdown("#### 🎫 Vérifier un passe")
        code = st.text_input("Code du passe visiteur", placeholder="ex. 3FA9C1", label_visibility="collapsed")
        if st.button("Vérifier", width="stretch") and code.strip():
            ok, message = verifier_passe(code)
            (st.success if ok else st.error)(message)

# ---------- Les demandes des visiteurs ----------
with col_demandes:
    @st.fragment(run_every=3)
    def bloc_demandes():
        demandes = demandes_en_attente()
        label(f"Demandes en attente · {len(demandes)}")
        if not demandes:
            st.markdown('<div class="sg-carte" style="text-align:center;padding:2rem;color:#6B7686">'
                        '😌 Aucune demande pour le moment</div>', unsafe_allow_html=True)
        for d in demandes:
            with st.container(border=True):
                info, plaque = st.columns([3, 2])
                info.markdown(f"**🙋 {html.escape(d['nom'])}**  \n🏢 {html.escape(d['batiment'] or '')} · "
                              f"📝 {html.escape(d['motif'] or '')}")
                plaque.markdown(plaque_html(d["plaque"] or "?", petite=True), unsafe_allow_html=True)
                duree = st.select_slider("Durée du passe", options=[1, 2, 3, 4, 8], value=3,
                                         format_func=lambda h: f"{h} h", key=f"d{d['id']}")
                accepter, refuser = st.columns(2)
                if accepter.button("✅ Accepter", key=f"a{d['id']}", type="primary", width="stretch"):
                    accepter_visiteur(d["id"], duree)
                    enregistrer_passage(d["plaque"] or "?", "OUVRIR", None, raison="visiteur accepté",
                                        proprietaire=d["nom"], agent=st.session_state.get("identifiant"))
                    st.rerun()
                if refuser.button("❌ Refuser", key=f"r{d['id']}", width="stretch"):
                    changer_statut_visiteur(d["id"], "refuse")
                    st.rerun()

    bloc_demandes()
