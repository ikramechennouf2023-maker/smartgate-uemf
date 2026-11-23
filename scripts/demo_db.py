import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'src'))
from database import *

init_db()
print("✅ Base créée : data/smartgate.db")

# 1) Véhicules autorisés
ajouter_vehicule("12345-L10-6", "Ikrame Chennouf", "étudiante", "2027-06-30")
ajouter_vehicule("67890-L11-1", "Pr. Elmoutaoukil", "professeur", "2027-06-30", handicap=False)
ajouter_vehicule("11111-L12-5", "Ancien étudiant", "étudiant", "2025-06-30")   # expiré !

for p in ["12345-L10-6", "11111-L12-5", "99999-L13-9"]:
    v = trouver_vehicule(p)
    print(f"🚗 {p} → {'✅ autorisé : ' + v['proprietaire'] if v else '❌ pas autorisé'}")

# 2) QR dynamique
t = creer_jeton()
print(f"\n🔲 Jeton créé : {t}")
print("   1re utilisation :", utiliser_jeton(t))
print("   2e utilisation  :", utiliser_jeton(t))
print("   jeton inventé   :", utiliser_jeton("ABCDEF"))

# 3) Visiteur
vid = ajouter_visiteur("M. Alami", "4521-L12-15", "EIDIA", "rendez-vous")
print(f"\n🙋 Demandes en attente : {[d['nom'] for d in demandes_en_attente()]}")
changer_statut_visiteur(vid, "accepte")
print(f"✅ Visiteur accepté aujourd'hui ? {visiteur_accepte_aujourdhui('4521-L12-15') is not None}")

# 4) Journal
enregistrer_passage("12345-L10-6", "OUVRIR", 0.91)
enregistrer_passage("99999-L13-9", "VISITEUR", 0.74)
print("\n📝 Journal :")
for ligne in derniers_passages():
    print(f"   {ligne['date_heure']}  {ligne['plaque']:12s}  {ligne['decision']:9s}  {ligne['confiance']}")