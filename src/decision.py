"""
Étape E : la décision à la barrière, à partir de la lecture et de la base de données.
"""
import config
from database import trouver_vehicule, visiteur_accepte_aujourdhui, enregistrer_passage

OUVRIR = "OUVRIR"        # ✅ barrière ouverte
VISITEUR = "VISITEUR"    # ❓ inconnu → QR code dynamique à la sécurité
AGENT = "AGENT"          # ⚠️ lecture pas sûre → l'agent vérifie


def decider(lecture):
    """
    lecture = le dictionnaire renvoyé par lire_plaque(image)
    Renvoie {"decision", "raison", "plaque", "confiance", "proprietaire"}
    """
    plaque, conf = lecture["plaque"], lecture["confiance"]
    resultat = {"plaque": plaque, "confiance": conf, "proprietaire": None}

    # Filet ① : la plaque a-t-elle été trouvée et lue au bon format ?
    if lecture["box"] is None:
        return {**resultat, "decision": AGENT, "raison": "aucune plaque trouvée"}
    if plaque is None:
        return {**resultat, "decision": AGENT, "raison": "format de plaque invalide"}

    # Filet ② : la lecture est-elle assez sûre ?
    if conf < config.SEUIL_LECTURE:
        return {**resultat, "decision": AGENT, "raison": f"lecture incertaine ({conf:.2f})"}

    # Filet ③ : la base de données
    vehicule = trouver_vehicule(plaque)
    if vehicule:
        return {**resultat, "decision": OUVRIR,
                "raison": f"{vehicule['role']} autorisé(e)", "proprietaire": vehicule["proprietaire"]}

    visiteur = visiteur_accepte_aujourdhui(plaque)
    if visiteur:
        return {**resultat, "decision": OUVRIR,
                "raison": "visiteur accepté aujourd'hui", "proprietaire": visiteur["nom"]}

    return {**resultat, "decision": VISITEUR, "raison": "plaque inconnue → QR code à la sécurité"}


def traiter_entree(image):
    """Toute la chaîne : photo → lecture → décision → photo sauvegardée → journal."""
    from datetime import datetime
    from pathlib import Path
    import cv2
    from ia import lire_plaque

    lecture = lire_plaque(image)
    resultat = decider(lecture)

    dossier = Path("data/passages")                       # dans data/ → jamais sur GitHub 🔐
    dossier.mkdir(parents=True, exist_ok=True)
    photo = dossier / f"{datetime.now():%Y%m%d_%H%M%S_%f}.jpg"
    cv2.imwrite(str(photo), image)

    enregistrer_passage(resultat["plaque"] or "?", resultat["decision"], resultat["confiance"],
                        raison=resultat["raison"], proprietaire=resultat["proprietaire"], photo=str(photo))
    return {**resultat, "box": lecture["box"]}