from datetime import date, timedelta
import pandas as pd
import streamlit as st
from database import lire_table, ajouter_vehicule, supprimer_vehicule
from format_plate import est_valide
from style import en_tete, kpi, label, plaque_texte, BLEU, VERT, ORANGE, ROUGE

en_tete("Véhicules autorisés", "Étudiants, professeurs et personnel qui peuvent entrer", "🚗")

LETTRES = ["أ", "ب", "د", "ه", "و", "ط", "ش", "ج", "M", "WW"]
ROLES = ["étudiant", "professeur", "personnel"]

df = pd.DataFrame(lire_table("vehicules", ordre="proprietaire"))
aujourdhui = date.today().isoformat()
dans_30j = (date.today() + timedelta(days=30)).isoformat()

# ---------- Chiffres clés ----------
c1, c2, c3, c4 = st.columns(4)
if df.empty:
    valides = expirent = expires = 0
else:
    valides = int((df["valide_jusqu"] >= aujourdhui).sum())
    expirent = int(((df["valide_jusqu"] >= aujourdhui) & (df["valide_jusqu"] <= dans_30j)).sum())
    expires = int((df["valide_jusqu"] < aujourdhui).sum())
with c1:
    kpi("Véhicules", len(df), "🚗", BLEU)
with c2:
    kpi("Autorisations valides", valides, "✅", VERT)
with c3:
    kpi("Expirent sous 30 jours", expirent, "⏳", ORANGE, "à renouveler")
with c4:
    kpi("Expirées", expires, "⛔", ROUGE)
st.write("")

onglet_liste, onglet_ajout, onglet_import = st.tabs(["📋 Liste", "➕ Ajouter", "📥 Importer (CSV / Excel)"])

# ---------- 📋 La liste ----------
with onglet_liste:
    if df.empty:
        st.info("Aucun véhicule pour l'instant : ajoutez-en ou importez une liste.")
    else:
        f1, f2, f3 = st.columns([2, 1, 1])
        recherche = f1.text_input("🔎 Rechercher (nom ou plaque)", placeholder="ex. Chennouf ou 12345")
        role = f2.selectbox("Rôle", ["Tous"] + ROLES)
        etat = f3.selectbox("État", ["Tous", "Valides", "Expirent bientôt", "Expirées"])

        vue = df.copy()
        if recherche:
            vue = vue[vue["proprietaire"].str.contains(recherche, case=False, na=False)
                      | vue["plaque"].str.contains(recherche, case=False, na=False)]
        if role != "Tous":
            vue = vue[vue["role"] == role]
        if etat == "Valides":
            vue = vue[vue["valide_jusqu"] >= aujourdhui]
        elif etat == "Expirent bientôt":
            vue = vue[(vue["valide_jusqu"] >= aujourdhui) & (vue["valide_jusqu"] <= dans_30j)]
        elif etat == "Expirées":
            vue = vue[vue["valide_jusqu"] < aujourdhui]

        vue = vue.assign(État=vue["valide_jusqu"].map(
            lambda d: "⛔ expirée" if d < aujourdhui else ("⏳ bientôt" if d <= dans_30j else "✅ valide")),
            handicap=vue["handicap"].map(lambda h: "♿" if h else ""), plaque=vue["plaque"].map(plaque_texte))
        st.dataframe(
            vue[["plaque", "proprietaire", "role", "valide_jusqu", "État", "handicap"]],
            width="stretch", hide_index=True,
            column_config={"plaque": "Plaque", "proprietaire": "Propriétaire", "role": "Rôle",
                           "valide_jusqu": "Valide jusqu'au", "handicap": "♿"},
        )
        st.caption(f"{len(vue)} véhicule(s) affiché(s)")

        with st.expander("🗑️ Supprimer un véhicule"):
            choix = st.selectbox("Véhicule", list(df["plaque"]), format_func=lambda p: f"{plaque_texte(p)} · {df.set_index('plaque').loc[p, 'proprietaire']}")
            confirmer = st.checkbox("Je confirme la suppression")
            if st.button("Supprimer", disabled=not confirmer):
                supprimer_vehicule(choix)
                st.success("Véhicule supprimé.")
                st.rerun()

# ---------- ➕ Ajouter ----------
with onglet_ajout:
    with st.form("ajout", clear_on_submit=True):
        label("Plaque")
        p1, p2, p3 = st.columns([3, 2, 2])
        numero = p1.text_input("Numéro", placeholder="12345")
        lettre = p2.selectbox("Lettre", LETTRES)
        region = p3.text_input("Région", placeholder="6")
        label("Propriétaire")
        a1, a2 = st.columns([2, 1])
        nom = a1.text_input("Nom complet")
        role = a2.selectbox("Rôle", ROLES)
        b1, b2 = st.columns(2)
        fin = b1.date_input("Autorisé jusqu'au", value=date(date.today().year + 1, 6, 30))
        handicap = b2.checkbox("♿ Autorisé sur les places handicapées")
        if st.form_submit_button("Ajouter le véhicule", type="primary", width="stretch"):
            plaque = f"{numero.strip()}-WW" if lettre == "WW" else f"{numero.strip()}-{lettre}-{region.strip()}"
            if not est_valide(plaque):
                st.error(f"Plaque invalide : {plaque}")
            elif not nom.strip():
                st.error("Le nom est obligatoire.")
            else:
                ajouter_vehicule(plaque, nom.strip(), role, fin.isoformat(), handicap)
                st.success(f"✅ {plaque} ajoutée pour {nom.strip()}.")

# ---------- 📥 Importer ----------
with onglet_import:
    st.markdown("Le fichier doit contenir les colonnes : **plaque**, **proprietaire**, **role**, "
                "**valide_jusqu** (AAAA-MM-JJ) et, en option, **handicap** (0 ou 1).")
    modele = pd.DataFrame([{"plaque": "12345-أ-6", "proprietaire": "Nom Prénom", "role": "étudiant",
                            "valide_jusqu": f"{date.today().year + 1}-06-30", "handicap": 0}])
    st.download_button("⬇️ Télécharger un modèle (CSV)", modele.to_csv(index=False).encode("utf-8-sig"),
                       "modele_vehicules.csv", "text/csv")

    fichier = st.file_uploader("Fichier CSV ou Excel", type=["csv", "xlsx"])
    if fichier:
        try:
            lu = pd.read_csv(fichier) if fichier.name.endswith(".csv") else pd.read_excel(fichier)
        except Exception as e:
            st.error(f"Impossible de lire le fichier : {e}")
            st.stop()
        lu.columns = [c.strip().lower() for c in lu.columns]
        manquantes = {"plaque", "proprietaire", "role", "valide_jusqu"} - set(lu.columns)
        if manquantes:
            st.error(f"Colonnes manquantes : {', '.join(sorted(manquantes))}")
        else:
            lu["plaque"] = lu["plaque"].astype(str).str.strip()
            lu["valide_jusqu"] = pd.to_datetime(lu["valide_jusqu"], errors="coerce").dt.date.astype(str)
            lu["Vérification"] = [
                "✅" if est_valide(p) and d != "NaT" and str(n).strip() else "❌"
                for p, d, n in zip(lu["plaque"], lu["valide_jusqu"], lu["proprietaire"])
            ]
            bons = lu[lu["Vérification"] == "✅"]
            st.dataframe(lu, width="stretch", hide_index=True)
            st.caption(f"{len(bons)} ligne(s) valide(s) · {len(lu) - len(bons)} ligne(s) avec une erreur (❌, ignorée(s))")
            if st.button(f"📥 Importer {len(bons)} véhicule(s)", type="primary", disabled=bons.empty):
                for _, r in bons.iterrows():
                    ajouter_vehicule(r["plaque"], str(r["proprietaire"]).strip(), str(r["role"]).strip(),
                                     r["valide_jusqu"], bool(int(r.get("handicap", 0) or 0)))
                st.success(f"✅ {len(bons)} véhicule(s) importé(s).")
                st.balloons()
