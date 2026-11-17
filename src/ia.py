"""
La partie IA du Module 1 : une photo → une plaque lue.
Fonction à utiliser partout : lire_plaque(image)
"""
from detect_plate import PlateDetector, crop_plate
from read_plate import PlateReader
from format_plate import normaliser
import config

_detecteur = None
_lecteur = None


def _modeles():
    """Charge les 2 modèles UNE SEULE FOIS (c'est lent), puis les réutilise."""
    global _detecteur, _lecteur
    if _detecteur is None:
        _detecteur = PlateDetector(config.CHEMIN_DETECTEUR, conf=config.SEUIL_DETECTION)
        _lecteur = PlateReader(config.CHEMIN_LECTEUR)
    return _detecteur, _lecteur


def lire_plaque(image):
    """
    Renvoie un dictionnaire :
      {"plaque": "12345-L10-6" ou None,
       "confiance": 0.91,
       "box": (x1, y1, x2, y2) ou None,
       "caracteres": ['1','2','3','4','5','10','6']}
    """
    detecteur, lecteur = _modeles()

    trouve = detecteur.detect(image)
    if trouve is None:
        return {"plaque": None, "confiance": 0.0, "box": None, "caracteres": []}

    box, _ = trouve
    caracteres, confiance = lecteur.read(crop_plate(image, box))
    return {
        "plaque": normaliser(caracteres),     # None si le format n'est pas marocain
        "confiance": confiance,
        "box": box,
        "caracteres": caracteres,
    }