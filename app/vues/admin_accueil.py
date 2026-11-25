from datetime import date, timedelta
import altair as alt
import pandas as pd
import streamlit as st
from database import lire_table
from style import (en_tete, kpi, label, style_graphique, echelle_decisions, LIBELLES,
                   BLEU, VERT, ORANGE, ROUGE, NUIT)

en_tete("Tableau de bord", "Activité de la barrière d'entrée de l'UEMF", "📊")

journal = pd.DataFrame(lire_table("journal"))
visiteurs = pd.DataFrame(lire_table("visiteurs"))
vehicules = pd.DataFrame(lire_table("vehicules"))

if journal.empty:
    st.info("Aucun passage pour l'instant. Envoyez des photos depuis la page « Caméra », "
            "ou lancez `python scripts/donnees_demo.py` pour remplir l'application avec des données de démonstration.")
    st.stop()

journal["date_heure"] = pd.to_datetime(journal["date_heure"])
journal["jour"] = journal["date_heure"].dt.date
journal["heure"] = journal["date_heure"].dt.hour
journal["Décision"] = journal["decision"].map(LIBELLES).fillna(journal["decision"])

# ---------- Choix de la période ----------
periode = st.segmented_control("Période", ["Aujourd'hui", "7 jours", "30 jours"], default="7 jours",
                               label_visibility="collapsed") or "7 jours"
debut = date.today() - timedelta(days={"Aujourd'hui": 0, "7 jours": 6, "30 jours": 29}[periode])
j = journal[journal["jour"] >= debut]

# ---------- Les chiffres clés ----------
total = len(j)
auto = int((j["decision"] == "OUVRIR").sum())
agent = int((j["decision"] == "AGENT").sum())
visites = int((j["decision"] == "VISITEUR").sum())
refus = int((j["decision"] == "REFUSE").sum())
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    kpi("Passages", total, "🚗", NUIT, periode.lower())
with c2:
    kpi("Ouvertures", auto, "✅", VERT, f"{auto / total:.0%} des passages" if total else "")
with c3:
    kpi("Visiteurs", visites, "🙋", ORANGE, "via le QR code")
with c4:
    kpi("Vérif. agent", agent, "⚠️", ROUGE, f"{agent / total:.0%} des passages" if total else "")
with c5:
    kpi("Autorisés", len(vehicules), "🪪", BLEU, f"{refus} refus · liste noire")

st.write("")

# ---------- Les graphiques ----------
gauche, droite = st.columns([1.6, 1], gap="large")

with gauche:
    with st.container(border=True):
        label("Passages par jour")
        par_jour = j.groupby(["jour", "Décision"]).size().reset_index(name="Passages")
        par_jour["Jour"] = pd.to_datetime(par_jour["jour"]).dt.strftime("%d/%m")
        graphe = alt.Chart(par_jour).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
            x=alt.X("Jour:O", title=None, sort=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Passages:Q", title=None),
            color=alt.Color("Décision:N", scale=echelle_decisions(), title=None),
            tooltip=["Jour:O", "Décision:N", "Passages:Q"],
        )
        st.altair_chart(style_graphique(graphe), width="stretch")

with droite:
    with st.container(border=True):
        label("Répartition des décisions")
        rep = j.groupby("Décision").size().reset_index(name="Passages")
        donut = alt.Chart(rep).mark_arc(innerRadius=62, cornerRadius=6, padAngle=0.02).encode(
            theta="Passages:Q",
            color=alt.Color("Décision:N", scale=echelle_decisions(), title=None,
                            legend=alt.Legend(orient="bottom", columns=3)),
            tooltip=["Décision:N", "Passages:Q"],
        )
        st.altair_chart(style_graphique(donut), width="stretch")

gauche, droite = st.columns([1.6, 1], gap="large")

with gauche:
    with st.container(border=True):
        label("Heures d'affluence")
        par_heure = j.groupby("heure").size().reindex(range(6, 23), fill_value=0).reset_index(name="Passages")
        aire = alt.Chart(par_heure).mark_area(
            line={"color": BLEU, "strokeWidth": 2.5},
            color=alt.Gradient(gradient="linear", x1=1, x2=1, y1=1, y2=0,
                               stops=[alt.GradientStop(color="#FFFFFF", offset=0),
                                      alt.GradientStop(color=BLEU, offset=1)]),
            interpolate="monotone", opacity=.8,
        ).encode(x=alt.X("heure:O", title="Heure"), y=alt.Y("Passages:Q", title=None),
                 tooltip=["heure:O", "Passages:Q"])
        st.altair_chart(style_graphique(aire, 230), width="stretch")

with droite:
    with st.container(border=True):
        label("Visiteurs par bâtiment")
        if visiteurs.empty:
            st.caption("Aucun visiteur pour l'instant.")
        else:
            vb = visiteurs.groupby("batiment").size().reset_index(name="Visiteurs")
            barres = alt.Chart(vb).mark_bar(cornerRadiusEnd=6, color=ORANGE).encode(
                y=alt.Y("batiment:N", sort="-x", title=None), x=alt.X("Visiteurs:Q", title=None),
                tooltip=["batiment:N", "Visiteurs:Q"])
            st.altair_chart(style_graphique(barres, 230), width="stretch")
