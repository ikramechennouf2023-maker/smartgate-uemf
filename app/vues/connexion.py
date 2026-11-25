import base64
from pathlib import Path
import streamlit as st
from database import verifier_connexion
from style import cacher_menu

cacher_menu()
st.markdown("<div style='height:3vh'></div>", unsafe_allow_html=True)

LOGO = Path(__file__).resolve().parents[1] / "assets" / "logo_uemf.png"
logo_html = ""
if LOGO.exists():
    b64 = base64.b64encode(LOGO.read_bytes()).decode()
    logo_html = f"<img src='data:image/png;base64,{b64}' style='height:64px;margin-bottom:.6rem'>"

gauche, droite = st.columns([1.15, 1], gap="large")

# ---------- Panneau de présentation ----------
with gauche:
    st.markdown("""
    <div class="sg-hero">
      <span class="badge">🎓 UNIVERSITÉ EUROMED DE FÈS</span>
      <h1>SmartGate<br>UEMF</h1>
      <p>Contrôle d'accès intelligent : la caméra lit la plaque, l'IA décide, la barrière s'ouvre.</p>
      <div class="atout"><span>🧠</span><div><b>2 réseaux de neurones (YOLOv8)</b>
          <small>trouver la plaque, puis lire chaque caractère arabe et latin</small></div></div>
      <div class="atout"><span>🔲</span><div><b>QR code dynamique pour les visiteurs</b>
          <small>change toutes les 30 secondes, utilisable une seule fois</small></div></div>
      <div class="atout"><span>🛡️</span><div><b>L'humain décide en cas de doute</b>
          <small>lecture incertaine → vérification par l'agent</small></div></div>
      <div class="chiffres">
        <div><b>97,9 %</b><small>plaques trouvées (mAP50)</small></div>
        <div><b>95 %</b><small>caractères bien lus</small></div>
        <div><b>&lt; 0,1 s</b><small>par voiture</small></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ---------- Formulaire de connexion ----------
with droite:
    st.markdown("<div style='height:2.2rem'></div>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='text-align:center'>{logo_html}"
        "<div style='font-size:1.9rem;font-weight:800;color:#0F2747'>Bon retour 👋</div>"
        "<div style='color:#6B7686;margin-bottom:1.2rem'>Connectez-vous à votre espace</div></div>",
        unsafe_allow_html=True,
    )

    with st.form("connexion"):
        identifiant = st.text_input("Identifiant", placeholder="ex. agent1")
        mot_de_passe = st.text_input("Mot de passe", type="password", placeholder="••••••••")
        valider = st.form_submit_button("Se connecter  →", type="primary", width="stretch")

    if valider:
        role = verifier_connexion(identifiant.strip(), mot_de_passe)
        if role:
            st.session_state.role = role
            st.session_state.identifiant = identifiant.strip()
            st.rerun()
        else:
            st.error("Identifiant ou mot de passe incorrect.")

    st.markdown(
        "<div style='text-align:center;color:#6B7686;margin-top:1rem;font-size:.9rem'>"
        "📱 Vous êtes visiteur ? Scannez le QR code affiché au poste de sécurité.</div>",
        unsafe_allow_html=True,
    )
