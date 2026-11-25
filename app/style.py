"""
Le style de SmartGate UEMF : police, couleurs, cartes, bandeaux, plaque marocaine, graphiques.
"""
import html
import altair as alt
import streamlit as st

NUIT, BLEU, CIEL, VERT, ORANGE, ROUGE, GRIS = (
    "#0F2747", "#2E6FB5", "#6FA8E8", "#3FA45B", "#F0A23B", "#D9483B", "#6B7686")

COULEURS_DECISION = {
    "OUVRIR": VERT, "VISITEUR": ORANGE, "AGENT": ROUGE,
    "REFUSE": "#7A1F1F", "OUVERTURE_MANUELLE": BLEU,
}
LIBELLES = {
    "OUVRIR": "✅ Ouvert", "VISITEUR": "❓ Visiteur", "AGENT": "⚠️ Agent",
    "REFUSE": "🚫 Refusé", "OUVERTURE_MANUELLE": "🔓 Manuelle",
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Cairo:wght@500;700&display=swap');

/* ================= BASE ================= */
html, body, .stApp, p, li, label, input, textarea, select, button, h1, h2, h3, h4, h5, h6,
[data-testid="stMarkdownContainer"], [data-testid="stMetricValue"], [data-testid="stMetricLabel"],
[data-testid="stSidebarNav"] span, [data-baseweb="select"] div, [data-baseweb="tab"] {
    font-family: 'Poppins', 'Cairo', sans-serif !important;
}
/* les icônes de Streamlit gardent LEUR police (sinon on voit leur nom en texte) */
[data-testid="stIconMaterial"], .material-symbols-rounded, span[class*="material-symbols"] {
    font-family: 'Material Symbols Rounded' !important;
}
.stApp {
    background:
        radial-gradient(1200px 500px at 100% -10%, rgba(46,111,181,.10), transparent 60%),
        radial-gradient(900px 400px at -10% 110%, rgba(63,164,91,.08), transparent 60%),
        #F4F7FC;
}
#MainMenu, footer, [data-testid="stDecoration"] { display: none !important; }
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1280px; }
h1, h2, h3 { color: #0F2747; letter-spacing: -.3px; }

@keyframes sgMonte { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
@keyframes sgPulse { 0%,100% { box-shadow: 0 0 0 0 rgba(255,255,255,.0), 0 14px 30px rgba(0,0,0,.16); }
                     50% { box-shadow: 0 0 0 8px rgba(255,255,255,.18), 0 14px 30px rgba(0,0,0,.16); } }
@keyframes sgPoint { 0%,100% { opacity: 1; } 50% { opacity: .25; } }

/* ================= MENU DE GAUCHE ================= */
[data-testid="stSidebar"] {
    background: linear-gradient(185deg, #0F2747 0%, #173A6B 55%, #1F4F8F 100%);
    border-right: none;
}
[data-testid="stSidebar"] * { color: #EEF3FB !important; }
[data-testid="stSidebarNav"] a { border-radius: 12px; margin: 3px 6px; padding: .45rem .7rem; transition: all .2s; }
[data-testid="stSidebarNav"] a:hover { background: rgba(255,255,255,.10); }
[data-testid="stSidebarNav"] a[aria-current="page"] { background: rgba(255,255,255,.18); font-weight: 600; }
[data-testid="stSidebar"] input { color: #0F2747 !important; }

/* ================= BOUTONS ================= */
.stButton > button, [data-testid="stFormSubmitButton"] > button, .stDownloadButton > button, .stLinkButton > a {
    border-radius: 14px !important; font-weight: 600 !important; padding: .62rem 1.2rem !important;
    border: 1px solid #DCE4F0 !important; transition: all .2s ease !important;
}
.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #2E6FB5, #1F4F8F) !important; border: none !important; color: #fff !important;
}
.stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-2px); box-shadow: 0 10px 22px rgba(15,39,71,.18) !important;
}

/* ================= CARTES ================= */
[data-testid="stForm"], [data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,.92); border: 1px solid #E6ECF5 !important; border-radius: 20px !important;
    box-shadow: 0 10px 30px rgba(15,39,71,.06); animation: sgMonte .45s ease both;
}
[data-testid="stForm"] { padding: 1.5rem 1.6rem; }
[data-testid="stMetric"] {
    background: #FFFFFF; border: 1px solid #E6ECF5; border-radius: 16px; padding: .85rem 1.1rem;
    box-shadow: 0 4px 14px rgba(15,39,71,.05);
}
[data-testid="stImage"] img { border-radius: 18px; box-shadow: 0 14px 34px rgba(15,39,71,.18); }
[data-testid="stDataFrame"] { border-radius: 16px; overflow: hidden; border: 1px solid #E6ECF5; }
[data-testid="stTabs"] button[role="tab"] { font-weight: 600; }
[data-testid="stFileUploaderDropzone"] { border-radius: 18px; border: 2px dashed #B9C9E2; background: #FAFCFF; }
.stTextInput input, .stDateInput input, [data-baseweb="select"] > div { border-radius: 12px !important; }

/* ================= BANDEAU DE TITRE ================= */
.sg-entete {
    position: relative; overflow: hidden; display: flex; align-items: center; gap: 1.1rem; color: #fff;
    background: linear-gradient(120deg, #0F2747 0%, #1F4F8F 55%, #2E6FB5 100%);
    padding: 1.35rem 1.8rem; border-radius: 24px; margin-bottom: 1.5rem;
    box-shadow: 0 18px 40px rgba(15,39,71,.25); animation: sgMonte .5s ease both;
}
.sg-entete::after {
    content: ""; position: absolute; right: -60px; top: -80px; width: 260px; height: 260px;
    border-radius: 50%; background: radial-gradient(circle, rgba(111,168,232,.45), transparent 70%);
}
.sg-entete .sg-icone {
    font-size: 2.1rem; background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.2);
    border-radius: 18px; padding: .35rem .7rem; backdrop-filter: blur(6px);
}
.sg-entete .sg-titre { font-size: 1.7rem; font-weight: 800; line-height: 1.15; }
.sg-entete .sg-sous-titre { opacity: .82; font-size: .93rem; margin-top: .2rem; }
.sg-entete .sg-direct {
    margin-left: auto; z-index: 1; display: flex; align-items: center; gap: .45rem; font-size: .8rem;
    font-weight: 700; letter-spacing: 1.5px; background: rgba(217,72,59,.95); padding: .35rem .8rem; border-radius: 999px;
}
.sg-entete .sg-direct i { width: 8px; height: 8px; border-radius: 50%; background: #fff; animation: sgPoint 1.2s infinite; }

/* ================= PETITS ÉLÉMENTS ================= */
.sg-carte {
    background: #FFFFFF; border: 1px solid #E6ECF5; border-radius: 18px; padding: 1rem 1.2rem;
    box-shadow: 0 6px 20px rgba(15,39,71,.06); margin-bottom: .8rem; animation: sgMonte .45s ease both;
}
.sg-label { color: #6B7686; font-size: .74rem; font-weight: 700; text-transform: uppercase;
            letter-spacing: 1.6px; margin: .5rem 0 .55rem; }
.sg-kpi {
    background: #FFFFFF; border: 1px solid #E6ECF5; border-radius: 20px; padding: 1.05rem 1.2rem;
    box-shadow: 0 8px 24px rgba(15,39,71,.06); display: flex; gap: .9rem; align-items: center;
    animation: sgMonte .45s ease both; min-height: 112px;
}
.sg-kpi .ic { width: 50px; height: 50px; border-radius: 16px; display: flex; align-items: center;
              justify-content: center; font-size: 1.5rem; flex-shrink: 0; }
.sg-kpi .val { font-size: 1.7rem; font-weight: 800; color: #0F2747; line-height: 1.1; }
.sg-kpi .tit { font-size: .8rem; color: #6B7686; font-weight: 600; }
.sg-kpi .sous { font-size: .75rem; color: #8A94A6; }
.sg-chip {
    display: inline-flex; align-items: center; gap: .35rem; padding: .28rem .7rem; border-radius: 999px;
    font-size: .8rem; font-weight: 600; margin: 0 .35rem .35rem 0; border: 1px solid transparent;
}
.sg-utilisateur {
    display: flex; align-items: center; gap: .7rem; background: rgba(255,255,255,.10);
    border: 1px solid rgba(255,255,255,.16); border-radius: 16px; padding: .7rem .8rem; margin: .3rem 0 .8rem;
}
.sg-utilisateur .av { width: 38px; height: 38px; border-radius: 12px; background: linear-gradient(135deg,#6FA8E8,#3FA45B);
                      display: flex; align-items: center; justify-content: center; font-weight: 800; }
.sg-utilisateur small { display: block; opacity: .75; font-size: .75rem; }

/* ================= PLAQUE MAROCAINE ================= */
.sg-plaque {
    display: inline-flex; align-items: center; gap: .95rem; direction: ltr;
    background: linear-gradient(180deg, #FFFFFF 0%, #F1F3F6 100%); color: #111827;
    border: 4px solid #111827; border-radius: 12px; padding: .45rem 1.35rem;
    font-family: 'Poppins', 'Cairo', sans-serif; font-size: 2.3rem; font-weight: 800; letter-spacing: 3px;
    box-shadow: inset 0 0 0 3px #FFFFFF, 0 12px 26px rgba(0,0,0,.18); margin-bottom: 1rem;
}
.sg-plaque .sep { width: 4px; height: 2.4rem; background: #111827; border-radius: 2px; }
.sg-plaque.petite { font-size: 1.05rem; padding: .15rem .6rem; border-width: 2px; gap: .45rem; letter-spacing: 1px;
                    margin: 0; box-shadow: none; }
.sg-plaque.petite .sep { height: 1.1rem; width: 2px; }

/* ================= GRANDE CARTE DE DÉCISION ================= */
.sg-statut {
    display: flex; align-items: center; gap: 1rem; color: #fff; border-radius: 22px;
    padding: 1.2rem 1.5rem; margin-bottom: 1rem; font-size: 1.4rem; font-weight: 800;
    animation: sgMonte .4s ease both, sgPulse 2.4s ease-in-out infinite;
}
.sg-statut .ic { font-size: 2.5rem; }
.sg-statut small { display: block; font-size: .88rem; font-weight: 500; opacity: .92; }
.sg-ok       { background: linear-gradient(135deg, #2E8B4A, #4CBF6A); }
.sg-visiteur { background: linear-gradient(135deg, #D9822B, #F2B544); }
.sg-agent    { background: linear-gradient(135deg, #B8322A, #E5604F); }
.sg-manuel   { background: linear-gradient(135deg, #1F4F8F, #2E6FB5); }
.sg-refuse   { background: linear-gradient(135deg, #3B0D0D, #8E2B2B); }

/* ================= PAGE DE CONNEXION ================= */
.sg-hero {
    position: relative; overflow: hidden; min-height: 520px; border-radius: 28px; padding: 2.4rem; color: #fff;
    background: linear-gradient(150deg, #0F2747 0%, #1F4F8F 60%, #2E6FB5 100%);
    box-shadow: 0 24px 50px rgba(15,39,71,.28); animation: sgMonte .5s ease both;
}
.sg-hero::before, .sg-hero::after { content: ""; position: absolute; border-radius: 50%; }
.sg-hero::before { width: 340px; height: 340px; right: -120px; bottom: -120px; background: radial-gradient(circle, rgba(63,164,91,.45), transparent 70%); }
.sg-hero::after { width: 260px; height: 260px; left: -90px; top: -90px; background: radial-gradient(circle, rgba(111,168,232,.35), transparent 70%); }
.sg-hero .badge { display: inline-block; background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.22);
                  border-radius: 999px; padding: .3rem .85rem; font-size: .78rem; font-weight: 600; letter-spacing: 1px; }
.sg-hero h1 { color: #fff; font-size: 2.6rem; font-weight: 800; margin: 1rem 0 .4rem; line-height: 1.1; }
.sg-hero p { opacity: .85; font-size: 1rem; max-width: 460px; }
.sg-hero .atout { display: flex; gap: .8rem; align-items: flex-start; margin-top: 1rem; position: relative; z-index: 1; }
.sg-hero .atout span { font-size: 1.3rem; background: rgba(255,255,255,.14); border-radius: 12px; padding: .2rem .5rem; }
.sg-hero .atout b { display: block; }
.sg-hero .atout small { opacity: .78; }
.sg-hero .chiffres { display: flex; gap: 1.6rem; margin-top: 2rem; position: relative; z-index: 1; }
.sg-hero .chiffres b { font-size: 1.6rem; display: block; }
.sg-hero .chiffres small { opacity: .75; font-size: .78rem; }
</style>
"""

STATUTS = {
    "OUVRIR":             ("sg-ok",       "✅", "Barrière ouverte"),
    "VISITEUR":           ("sg-visiteur", "❓", "Visiteur · QR code à la sécurité"),
    "AGENT":              ("sg-agent",    "⚠️", "Vérification par l'agent"),
    "OUVERTURE_MANUELLE": ("sg-manuel",   "🔓", "Ouverture manuelle"),
    "REFUSE":             ("sg-refuse",   "🚫", "Accès refusé"),
}


def appliquer_style():
    """À appeler une fois, dans app.py : habille toute l'application."""
    st.markdown(CSS, unsafe_allow_html=True)


def cacher_menu():
    """Cache le menu de gauche (page de connexion, page visiteur sur téléphone)."""
    st.markdown('<style>[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],'
                '[data-testid="collapsedControl"], [data-testid="stExpandSidebarButton"],'
                '[data-testid="stSidebarCollapseButton"] { display: none !important; }</style>',
                unsafe_allow_html=True)


def en_tete(titre, sous_titre="", icone="🚧", direct=False):
    """Le bandeau de titre en dégradé, en haut de chaque page."""
    badge = '<div class="sg-direct"><i></i>EN DIRECT</div>' if direct else ""
    st.markdown(
        f'<div class="sg-entete"><div class="sg-icone">{icone}</div>'
        f'<div><div class="sg-titre">{html.escape(titre)}</div>'
        f'<div class="sg-sous-titre">{html.escape(sous_titre)}</div></div>{badge}</div>',
        unsafe_allow_html=True,
    )


def label(texte):
    st.markdown(f'<div class="sg-label">{html.escape(texte)}</div>', unsafe_allow_html=True)


def carte(contenu_html):
    st.markdown(f'<div class="sg-carte">{contenu_html}</div>', unsafe_allow_html=True)


def kpi(titre, valeur, icone, couleur=BLEU, sous=""):
    """Une carte de chiffre clé (tableau de bord)."""
    st.markdown(
        f'<div class="sg-kpi"><div class="ic" style="background:{couleur}1F;color:{couleur}">{icone}</div>'
        f'<div><div class="tit">{html.escape(titre)}</div><div class="val">{html.escape(str(valeur))}</div>'
        f'<div class="sous">{html.escape(sous)}</div></div></div>',
        unsafe_allow_html=True,
    )


def plaque_texte(plaque):
    """Plaque en texte simple, affichée dans le bon ordre même avec une lettre arabe (12345-ب-6)."""
    return (plaque or "?").replace("-", "\u200e-\u200e")


def plaque_html(plaque, petite=False):
    """Dessine la plaque comme une vraie plaque marocaine : 12345 ┃ ب ┃ 6"""
    parties = plaque.split("-") if plaque and plaque != "?" else ["? ? ?"]
    contenu = '<span class="sep"></span>'.join(f"<span>{html.escape(p)}</span>" for p in parties)
    return f'<div class="sg-plaque{" petite" if petite else ""}">{contenu}</div>'


def statut_html(decision, detail=""):
    """La grande carte colorée de la décision."""
    classe, icone, texte = STATUTS.get(decision, ("sg-manuel", "ℹ️", decision))
    return (f'<div class="sg-statut {classe}"><span class="ic">{icone}</span>'
            f'<div>{texte}<small>{html.escape(detail or "")}</small></div></div>')


def chip(texte, couleur=BLEU):
    return (f'<span class="sg-chip" style="background:{couleur}1A;color:{couleur};'
            f'border-color:{couleur}40">{html.escape(texte)}</span>')


def carte_utilisateur(identifiant, role):
    """Petite carte de l'utilisateur connecté, en haut du menu."""
    nom_role = {"admin": "Administration", "securite": "Agent de sécurité"}.get(role, role)
    st.sidebar.markdown(
        f'<div class="sg-utilisateur"><div class="av">{html.escape(identifiant[:1].upper())}</div>'
        f'<div><b>{html.escape(identifiant)}</b><small>{nom_role}</small></div></div>',
        unsafe_allow_html=True,
    )


def style_graphique(chart, hauteur=260):
    """Applique le style SmartGate à un graphique Altair."""
    return (chart.properties(height=hauteur)
            .configure_view(strokeWidth=0)
            .configure_axis(labelColor=GRIS, titleColor=GRIS, gridColor="#E9EEF6", domain=False,
                            labelFont="Poppins", titleFont="Poppins")
            .configure_legend(labelColor="#1B2433", titleColor=GRIS, labelFont="Poppins", orient="bottom")
            .configure_title(font="Poppins", color="#0F2747", fontSize=14, anchor="start"))


def echelle_decisions():
    noms = list(COULEURS_DECISION)
    return alt.Scale(domain=[LIBELLES[n] for n in noms], range=[COULEURS_DECISION[n] for n in noms])
