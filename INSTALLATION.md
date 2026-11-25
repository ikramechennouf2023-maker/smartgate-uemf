# SmartGate UEMF · nouvelle application

## Contenu du zip

```
app/
  app.py                  point d'entrée : connexion, menus selon le rôle
  style.py                le design (couleurs UEMF, cartes, plaque marocaine, graphiques)
  assets/                 mettre ici logo_uemf.png (et, si tu veux, plan_campus.png)
  vues/
    connexion.py          page de connexion
    securite_direct.py    📺 écran en direct + ouverture manuelle + correction de plaque
    securite.py           🔲 QR dynamique + demandes des visiteurs + vérifier un passe
    barriere.py           📷 caméra (simulation : on envoie une photo)
    visiteur.py           📱 page du visiteur (FR / عربي / EN) + passe QR + destination
    admin_accueil.py      📊 tableau de bord
    admin_vehicules.py    🚗 véhicules autorisés + import CSV / Excel
    admin_liste_noire.py  🚫 liste noire
    admin_journal.py      📋 journal + filtres + export CSV / Excel
    admin_ia.py           🧠 suivi de l'IA
src/
  database.py             base de données (nouvelles tables : liste noire, passes visiteurs)
  decision.py             décision (+ REFUSE pour la liste noire, + photo de chaque passage)
scripts/
  creer_comptes.py        créer les comptes admin et agent1
  donnees_demo.py         remplir l'app avec des données FICTIVES (pour la démo)
.streamlit/config.toml    le thème (dossier caché : Cmd + Shift + . dans le Finder pour le voir)
```

Les autres fichiers de `src/` (config.py, ia.py, detect_plate.py, read_plate.py, format_plate.py) ne changent pas.

## Installation (depuis la racine du projet smartgate-uemf)

```bash
git checkout main && git pull
git checkout -b ikrame/nouvelle-app
pip install openpyxl altair "qrcode[pil]"
```

Copier le contenu du zip dans le projet (remplacer les fichiers existants), puis :

```bash
cp ~/Documents/S7/CNN/industrial-defect-detection/rapport_images/logo_uemf.png app/assets/logo_uemf.png
python scripts/creer_comptes.py
python scripts/donnees_demo.py        # facultatif : données de démonstration
streamlit run app/app.py
```

Pour repartir d'une base vide : supprimer `data/smartgate.db`, puis relancer `creer_comptes.py`.

## Les comptes

| Identifiant | Rôle | Pages |
|---|---|---|
| admin | Administration | Tableau de bord, Véhicules, Liste noire, Journal, Suivi de l'IA + pages Sécurité |
| agent1 | Sécurité | En direct, Visiteurs & QR, Caméra |
| (aucun) | Visiteur | arrive par le QR code : formulaire, puis passe + destination |
