import io
from datetime import date, timedelta
import pandas as pd
import streamlit as st
from database import lire_table
from style import en_tete, LIBELLES, plaque_texte

en_tete("Journal des passages", "Tous les passages à la barrière, avec filtres et export", "📋")

journal = pd.DataFrame(lire_table("journal"))
if journal.empty:
    st.info("Le journal est vide pour l'instant.")
    st.stop()

journal["date_heure"] = pd.to_datetime(journal["date_heure"])

# ---------- Filtres ----------
with st.container(border=True):
    f1, f2, f3 = st.columns([1.3, 1.6, 1.2])
    periode = f1.date_input("Période", value=(date.today() - timedelta(days=6), date.today()))
    decisions = f2.multiselect("Décisions", list(LIBELLES), default=list(LIBELLES),
                               format_func=lambda d: LIBELLES[d])
    recherche = f3.text_input("🔎 Plaque ou nom")

debut, fin = (periode if isinstance(periode, tuple) and len(periode) == 2 else (periode, periode))
vue = journal[(journal["date_heure"].dt.date >= debut) & (journal["date_heure"].dt.date <= fin)
              & journal["decision"].isin(decisions)]
if recherche:
    vue = vue[vue["plaque"].fillna("").str.contains(recherche, case=False)
              | vue["proprietaire"].fillna("").str.contains(recherche, case=False)]

tableau = pd.DataFrame({
    "Date et heure": vue["date_heure"].dt.strftime("%d/%m/%Y %H:%M:%S"),
    "Plaque": vue["plaque"].map(plaque_texte),
    "Décision": vue["decision"].map(LIBELLES).fillna(vue["decision"]),
    "Confiance": vue["confiance"],
    "Conducteur": vue["proprietaire"],
    "Raison": vue["raison"],
    "Agent": vue["agent"],
})
st.dataframe(tableau, width="stretch", hide_index=True, height=460,
             column_config={"Confiance": st.column_config.ProgressColumn(
                 "Confiance", min_value=0.0, max_value=1.0, format="%.2f")})
st.caption(f"{len(tableau)} passage(s)")

# ---------- Export ----------
e1, e2, _ = st.columns([1, 1, 3])
e1.download_button("⬇️ Export CSV", tableau.to_csv(index=False).encode("utf-8-sig"),
                   f"journal_{debut}_{fin}.csv", "text/csv", width="stretch")
try:
    tampon = io.BytesIO()
    tableau.to_excel(tampon, index=False, sheet_name="Journal")
    e2.download_button("⬇️ Export Excel", tampon.getvalue(), f"journal_{debut}_{fin}.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       width="stretch")
except ImportError:
    e2.caption("Pour l'export Excel : `pip install openpyxl`")
