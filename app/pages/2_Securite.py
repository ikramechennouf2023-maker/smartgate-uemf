import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import io
import socket
import time
import qrcode
import streamlit as st
from database import (init_db, creer_jeton, demandes_en_attente,
                      changer_statut_visiteur, enregistrer_passage, derniers_passages)

st.set_page_config(page_title="Sécurité · SmartGate", page_icon="👮", layout="wide")
init_db()
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
    """Transforme un lien en image de QR code."""
    buf = io.BytesIO()
    qrcode.make(texte).save(buf, format="PNG")
    return buf.getvalue()


st.title("👮 Sécurité · SmartGate UEMF")
base = st.sidebar.text_input("Adresse de l'application", f"http://{ip_locale()}:8501")

col_qr, col_demandes = st.columns([1, 2])

# ---------- Le QR dynamique (se met à jour toute seule chaque seconde) ----------
with col_qr:
    @st.fragment(run_every=1)
    def bloc_qr():
        maintenant = time.time()
        if "jeton" not in st.session_state or maintenant - st.session_state.jeton_cree > PERIODE:
            st.session_state.jeton = creer_jeton()           # nouveau code aléatoire
            st.session_state.jeton_cree = maintenant
        lien = f"{base}/Visiteur?token={st.session_state.jeton}"
        reste = PERIODE - int(maintenant - st.session_state.jeton_cree)

        st.subheader("🔲 Visiteur ? Scannez-moi")
        st.image(image_qr(lien), width=260)
        st.progress(max(reste, 0) / PERIODE, text=f"⏱️ nouveau QR dans {reste} s")
        st.caption(lien)

    bloc_qr()

# ---------- Les demandes des visiteurs (vérifiées toutes les 3 s) ----------
with col_demandes:
    @st.fragment(run_every=3)
    def bloc_demandes():
        st.subheader("🙋 Demandes des visiteurs")
        demandes = demandes_en_attente()
        if not demandes:
            st.info("Aucune demande pour le moment.")
        for d in demandes:
            with st.container(border=True):
                st.write(f"**{d['nom']}** · `{d['plaque'] or '?'}` · {d['batiment']} · {d['motif']}")
                accepter, refuser = st.columns(2)
                if accepter.button("✅ Accepter", key=f"a{d['id']}", use_container_width=True):
                    changer_statut_visiteur(d["id"], "accepte")
                    enregistrer_passage(d["plaque"] or "?", "OUVRIR", None)
                    st.rerun(scope="fragment")
                if refuser.button("❌ Refuser", key=f"r{d['id']}", use_container_width=True):
                    changer_statut_visiteur(d["id"], "refuse")
                    st.rerun(scope="fragment")

        st.subheader("📝 Derniers passages")
        st.dataframe([dict(l) for l in derniers_passages(10)], use_container_width=True, hide_index=True)

    bloc_demandes()