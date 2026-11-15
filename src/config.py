"""Réglages de SmartGate UEMF (choisis par des mesures, voir eval_lecteur.py)."""

# Module 1 : contrôle d'accès
SEUIL_DETECTION = 0.25      # confiance minimale pour trouver la plaque
SEUIL_LECTURE = 0.50        # confiance minimale des caractères (choisi sur 227 plaques de test)
CHEMIN_DETECTEUR = "models/plate_detector.pt"
CHEMIN_LECTEUR = "models/char_reader.pt"