import html
import io
from pathlib import Path
import qrcode
import streamlit as st
from database import utiliser_jeton, ajouter_visiteur, derniere_plaque_inconnue, trouver_visiteur
from style import cacher_menu, plaque_html

cacher_menu()          # sur le téléphone du visiteur : pas de menu

# ---------- Les textes dans 3 langues ----------
TEXTES = {
    "fr": dict(titre="Bienvenue à l'UEMF", sous="Présentez-vous pour accéder au campus",
               nom="Votre nom complet", plaque="Plaque du véhicule", batiment="Je vais à", motif="Motif",
               envoyer="Envoyer ma demande", vide="Merci d'indiquer votre nom.",
               attente="Demande envoyée", attente2="En attente de la validation de l'agent…",
               ok="Demande acceptée", ok2="La barrière s'ouvre. Bonne visite !",
               non="Demande refusée", non2="Merci de vous adresser à l'agent de sécurité.",
               passe="Votre passe visiteur", passe2="Montrez-le à la sortie · valable jusqu'à",
               aller="Votre destination", carte="Ouvrir dans Google Maps", erreur="Accès impossible"),
    "ar": dict(titre="مرحبا بكم في الجامعة الأورومتوسطية بفاس", sous="عرّفوا بأنفسكم للدخول إلى الحرم الجامعي",
               nom="الاسم الكامل", plaque="رقم لوحة السيارة", batiment="الوجهة", motif="سبب الزيارة",
               envoyer="إرسال الطلب", vide="المرجو إدخال الاسم.",
               attente="تم إرسال الطلب", attente2="في انتظار موافقة عون الأمن…",
               ok="تم قبول الطلب", ok2="الحاجز يُفتح. زيارة سعيدة!",
               non="تم رفض الطلب", non2="المرجو التوجه إلى عون الأمن.",
               passe="بطاقة الزائر", passe2="أظهرها عند الخروج · صالحة إلى غاية",
               aller="وجهتك", carte="فتح في خرائط Google", erreur="الدخول غير ممكن"),
    "en": dict(titre="Welcome to UEMF", sous="Introduce yourself to access the campus",
               nom="Your full name", plaque="Vehicle plate", batiment="I am going to", motif="Reason",
               envoyer="Send my request", vide="Please enter your name.",
               attente="Request sent", attente2="Waiting for the security agent…",
               ok="Request accepted", ok2="The barrier is opening. Enjoy your visit!",
               non="Request declined", non2="Please contact the security agent.",
               passe="Your visitor pass", passe2="Show it when leaving · valid until",
               aller="Your destination", carte="Open in Google Maps", erreur="Access denied"),
}
BATIMENTS = {"EIDIA": ("EIDIA", "EIDIA", "EIDIA"), "Bibliothèque": ("Bibliothèque", "المكتبة", "Library"),
             "Restaurant": ("Restaurant", "المطعم", "Restaurant"),
             "Administration": ("Administration", "الإدارة", "Administration"), "Autre": ("Autre", "أخرى", "Other")}
MOTIFS = {"Rendez-vous": ("Rendez-vous", "موعد", "Appointment"), "Conférence": ("Conférence", "مؤتمر", "Conference"),
          "Livraison": ("Livraison", "توصيل", "Delivery"), "Visite": ("Visite", "زيارة", "Visit"),
          "Autre": ("Autre", "أخرى", "Other")}
IDX = {"fr": 0, "ar": 1, "en": 2}

# ---------- Choix de la langue ----------
_, col_langue = st.columns([3, 1])
langue = col_langue.segmented_control("Langue", ["fr", "ar", "en"], default="fr",
                                      format_func=lambda l: {"fr": "FR", "ar": "ع", "en": "EN"}[l],
                                      label_visibility="collapsed") or "fr"
T, i = TEXTES[langue], IDX[langue]
if langue == "ar":
    st.markdown("<style>.block-container{direction:rtl;text-align:right}</style>", unsafe_allow_html=True)

st.markdown(
    f'<div class="sg-entete"><div class="sg-icone">👋</div><div><div class="sg-titre">{T["titre"]}</div>'
    f'<div class="sg-sous-titre">{T["sous"]}</div></div></div>', unsafe_allow_html=True)


def carte_statut(classe, icone, titre, detail):
    st.markdown(f'<div class="sg-statut {classe}"><span class="ic">{icone}</span>'
                f'<div>{titre}<small>{detail}</small></div></div>', unsafe_allow_html=True)


# ---------- 1) Vérifier le QR UNE SEULE FOIS ----------
if "acces" not in st.session_state:
    token = st.query_params.get("token")
    st.session_state.acces = utiliser_jeton(token) if token else (False, "Scannez le QR code affiché à la sécurité.")

ok, message = st.session_state.acces
if not ok:
    carte_statut("sg-agent", "⛔", T["erreur"], html.escape(message))
    st.stop()

# ---------- 2) Le formulaire ----------
if "id_visiteur" not in st.session_state:
    with st.form("formulaire"):
        nom = st.text_input(T["nom"])
        plaque = st.text_input(T["plaque"], value=derniere_plaque_inconnue())
        batiment = st.selectbox(T["batiment"], list(BATIMENTS), format_func=lambda b: BATIMENTS[b][i])
        motif = st.selectbox(T["motif"], list(MOTIFS), format_func=lambda m: MOTIFS[m][i])
        envoye = st.form_submit_button(T["envoyer"], type="primary", width="stretch")
    if envoye:
        if not nom.strip():
            st.warning(T["vide"])
        else:
            st.session_state.id_visiteur = ajouter_visiteur(nom.strip(), plaque.strip(), batiment, motif)
            st.rerun()

# ---------- 3) L'attente, puis le passe ----------
else:
    @st.fragment(run_every=2)
    def suivi():
        v = trouver_visiteur(st.session_state.id_visiteur)
        statut = v["statut"] if v else None
        if statut == "refuse":
            carte_statut("sg-agent", "❌", T["non"], T["non2"])
            return
        if statut != "accepte":
            carte_statut("sg-manuel", "⏳", T["attente"], T["attente2"])
            return

        carte_statut("sg-ok", "✅", T["ok"], T["ok2"])

        # --- Le passe personnel (QR) ---
        with st.container(border=True):
            st.markdown(f"<div style='text-align:center;font-weight:800;font-size:1.2rem;color:#0F2747'>"
                        f"🎫 {T['passe']}</div>", unsafe_allow_html=True)
            buf = io.BytesIO()
            qr = qrcode.QRCode(box_size=10, border=2)
            qr.add_data(f"SMARTGATE-PASS:{v['pass_code']}")
            qr.make(fit=True)
            qr.make_image(fill_color="#0F2747", back_color="white").save(buf, format="PNG")
            _, milieu, _ = st.columns([1, 2, 1])
            milieu.image(buf.getvalue(), width="stretch")
            st.markdown(
                f"<div style='text-align:center'><div style='font-size:1.8rem;font-weight:800;letter-spacing:6px;"
                f"color:#0F2747'>{v['pass_code']}</div><div style='color:#6B7686'>{T['passe2']} "
                f"<b>{(v['pass_expire'] or '')[11:16]}</b></div></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center;margin-top:.6rem'>{plaque_html(v['plaque'] or '?', petite=True)}"
                        f"</div>", unsafe_allow_html=True)

        # --- La destination ---
        with st.container(border=True):
            st.markdown(f"#### 🧭 {T['aller']} : {BATIMENTS.get(v['batiment'], (v['batiment'],) * 3)[i]}")
            plan = Path(__file__).resolve().parents[1] / "assets" / "plan_campus.png"
            if plan.exists():
                st.image(str(plan), width="stretch")
            st.link_button(f"🗺️ {T['carte']}",
                           "https://www.google.com/maps/search/?api=1&query=Universit%C3%A9+Euromed+de+F%C3%A8s",
                           width="stretch")

    suivi()
