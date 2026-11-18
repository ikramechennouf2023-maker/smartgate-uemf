"""
Étape C : transformer les caractères lus en plaque marocaine et vérifier le format.
Deux formats acceptés :
  - normal     : 1-5 chiffres + 1 lettre + région 1-89   → "12345-أ-6"
  - temporaire : 1-6 chiffres + WW                        → "597401-WW"
"""
import re

# Classes '10' à '20' du dataset B (vérifiées sur outputs/classes_lettres.png)
LETTRES = {
    "10": "أ",
    "11": "ب",
    "12": "و",
    "13": "د",
    "14": "ه",
    "15": "W",      # plaques temporaires WW
    "16": "ط",
    "17": "ش",
    "19": "ج",
    "20": "M",
}
MOT_MAROC = "18"    # le mot « المغرب » écrit sur certaines plaques : à ignorer
CLASSE_W = "15"

PLAQUE_RE = re.compile(r"^\d{1,5}-(?:L\d{2}|[^\d\s-])-\d{1,2}$")   # format normal
PLAQUE_WW_RE = re.compile(r"^\d{1,6}-WW$")                         # format temporaire


def est_lettre(nom):
    """Les classes '10' à '20' sont des lettres ; '0' à '9' sont des chiffres."""
    return int(nom) >= 10


def normaliser(caracteres):
    """
    caracteres : liste triée (gauche → droite) de noms de classes.
    Renvoie la plaque écrite proprement, ou None si le format n'est pas marocain.
    """
    # 0) On enlève le mot « المغرب » (décoratif)
    caracteres = [c for c in caracteres if c != MOT_MAROC]
    if not caracteres:
        return None

    lettres = [c for c in caracteres if est_lettre(c)]
    chiffres = "".join(c for c in caracteres if not est_lettre(c))

    # 1) Plaque TEMPORAIRE : seulement des W (un ou plusieurs) + des chiffres
    if lettres and all(c == CLASSE_W for c in lettres):
        if 1 <= len(chiffres) <= 6:
            return f"{chiffres}-WW"
        return None

    # 2) Plaque NORMALE : fusionner les lettres identiques collées ('10','10' → '10')
    fusion = []
    for c in caracteres:
        if fusion and est_lettre(c) and c == fusion[-1]:
            continue
        fusion.append(c)
    caracteres = fusion

    positions = [i for i, c in enumerate(caracteres) if est_lettre(c)]
    if len(positions) != 1:                      # exactement UNE lettre
        return None

    i = positions[0]
    numero = "".join(caracteres[:i])
    region = "".join(caracteres[i + 1:])

    if not (1 <= len(numero) <= 5 and 1 <= len(region) <= 2):
        return None
    if not (1 <= int(region) <= 89):
        return None

    lettre = LETTRES.get(caracteres[i], f"L{caracteres[i]}")
    return f"{numero}-{lettre}-{region}"


def est_valide(plaque):
    """Vérifie une plaque déjà écrite (ex. saisie dans la base de données)."""
    return bool(plaque) and bool(PLAQUE_RE.match(plaque) or PLAQUE_WW_RE.match(plaque))