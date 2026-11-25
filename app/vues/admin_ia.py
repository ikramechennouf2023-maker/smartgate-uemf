import altair as alt
import pandas as pd
import streamlit as st
import config
from database import lire_table
from style import en_tete, kpi, label, style_graphique, plaque_texte, BLEU, VERT, ORANGE, ROUGE, NUIT

en_tete("Suivi de l'IA", "Surveiller la qualité de lecture des plaques au fil du temps", "🧠")

journal = pd.DataFrame(lire_table("journal"))
corrections = pd.DataFrame(lire_table("corrections"))

# On ne garde que les passages lus par la caméra (pas les ouvertures manuelles ni les visiteurs acceptés)
if not journal.empty:
    journal = journal[journal["decision"].isin(["OUVRIR", "VISITEUR", "AGENT", "REFUSE"])
                      & journal["confiance"].notna()]
if journal.empty:
    st.info("Pas encore de lectures de la caméra à analyser.")
    st.stop()

journal["date_heure"] = pd.to_datetime(journal["date_heure"])
journal["jour"] = journal["date_heure"].dt.floor("D")
seuil = config.SEUIL_LECTURE

# ---------- Chiffres clés ----------
c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi("Lectures analysées", len(journal), "📷", NUIT)
with c2:
    kpi("Confiance moyenne", f"{journal['confiance'].mean():.2f}", "🎯", BLEU, f"seuil de décision : {seuil}")
with c3:
    taux = (journal["decision"] == "AGENT").mean()
    kpi("Envoyées à l'agent", f"{taux:.0%}", "⚠️", ORANGE if taux < .25 else ROUGE, "lecture incertaine")
with c4:
    kpi("Corrections de l'agent", len(corrections), "✏️", VERT, "futures données d'entraînement")
st.write("")

par_jour = journal.groupby("jour").agg(confiance=("confiance", "mean"),
                                       agent=("decision", lambda d: (d == "AGENT").mean() * 100),
                                       lectures=("confiance", "size")).reset_index()
par_jour["Jour"] = par_jour["jour"].dt.strftime("%d/%m")

gauche, droite = st.columns(2, gap="large")
with gauche:
    with st.container(border=True):
        label("Confiance moyenne par jour")
        ligne = alt.Chart(par_jour).mark_line(point=alt.OverlayMarkDef(size=70, filled=True, color=BLEU),
                                              strokeWidth=3, color=BLEU, interpolate="monotone").encode(
            x=alt.X("Jour:O", title=None, sort=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("confiance:Q", title=None, scale=alt.Scale(domain=[0, 1])),
            tooltip=["Jour:O", alt.Tooltip("confiance:Q", format=".2f"), "lectures:Q"])
        regle = alt.Chart(pd.DataFrame({"y": [seuil]})).mark_rule(color=ROUGE, strokeDash=[6, 4]).encode(y="y:Q")
        st.altair_chart(style_graphique(ligne + regle), width="stretch")
        st.caption(f"Ligne rouge : seuil de décision ({seuil}). Une baisse peut signaler une caméra sale ou mal orientée.")

with droite:
    with st.container(border=True):
        label("% de lectures envoyées à l'agent")
        barres = alt.Chart(par_jour).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
            x=alt.X("Jour:O", title=None, sort=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("agent:Q", title=None),
            color=alt.condition(alt.datum.agent > 25, alt.value(ROUGE), alt.value(ORANGE)),
            tooltip=["Jour:O", alt.Tooltip("agent:Q", format=".0f", title="% agent")])
        st.altair_chart(style_graphique(barres), width="stretch")
        st.caption("En rouge : plus de 25 % de lectures incertaines ce jour-là.")

gauche, droite = st.columns(2, gap="large")
with gauche:
    with st.container(border=True):
        label("Distribution des confiances")
        histo = alt.Chart(journal).mark_bar(color=BLEU, opacity=.85, cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            x=alt.X("confiance:Q", bin=alt.Bin(maxbins=20), title="Confiance"),
            y=alt.Y("count():Q", title=None))
        regle = alt.Chart(pd.DataFrame({"x": [seuil]})).mark_rule(color=ROUGE, strokeDash=[6, 4], size=2).encode(x="x:Q")
        st.altair_chart(style_graphique(histo + regle, 230), width="stretch")

with droite:
    with st.container(border=True):
        label("Dernières corrections de l'agent")
        if corrections.empty:
            st.caption("Aucune correction pour l'instant.")
        else:
            vue = corrections[["date_heure", "plaque_lue", "plaque_corrigee", "agent"]].head(15).copy()
            vue["plaque_lue"] = vue["plaque_lue"].map(plaque_texte)
            vue["plaque_corrigee"] = vue["plaque_corrigee"].map(plaque_texte)
            st.dataframe(vue,
                         hide_index=True, width="stretch",
                         column_config={"date_heure": "Quand", "plaque_lue": "Lu par l'IA",
                                        "plaque_corrigee": "Corrigé", "agent": "Agent"})
            st.caption("Ces images et leurs vraies plaques pourront servir à réentraîner le lecteur.")
