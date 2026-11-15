"""
Étape C : transformer les caractères lus en plaque marocaine et vérifier le format.
Ex. ['1','2','3','4','5','10','6']  →  "12345-أ-6"
"""
import re

# Classes '10' à '20' du dataset = les lettres arabes.
# ⚠️ À COMPLÉTER quand on aura vérifié le tableau des classes.
# En attendant, une lettre inconnue s'écrit "L10", "L11", ...
LETTRES = {
    # "10": "أ",
    # "11": "ب",
}

# Format d'une plaque déjà écrite : 1-5 chiffres, tiret, une lettre (ou L10..L20), tiret, 1-2 chiffres
PLAQUE_RE = re.compile(r"^\d{1,5}-(?:L\d{2}|[^\d\s-])-\d{1,2}$")


def est_lettre(nom):
    """Les classes '10' à '20' sont des lettres, '0' à '9' sont des chiffres."""
    return int(nom) >= 10


def normaliser(caracteres):
    """
    caracteres : liste triée de noms de classes, ex. ['1','2','3','4','5','10','6']
    Renvoie "12345-أ-6"  (ou "12345-L10-6" si la lettre n'est pas encore connue)
    Renvoie None si ça ne respecte pas le format marocain.
    """
        # Fusionner les lettres identiques collées (ex. '10','10','10' → '10')
    fusion = []
    for c in caracteres:
        if fusion and est_lettre(c) and c == fusion[-1]:
            continue
        fusion.append(c)
    caracteres = fusion
    positions_lettres = [i for i, c in enumerate(caracteres) if est_lettre(c)]

    # 1) il faut exactement UNE lettre
    if len(positions_lettres) != 1:
        return None

    i = positions_lettres[0]
    numero = "".join(caracteres[:i])          # avant la lettre
    region = "".join(caracteres[i + 1:])      # après la lettre

    # 2) 1 à 5 chiffres avant, 1 à 2 chiffres après
    if not (1 <= len(numero) <= 5 and 1 <= len(region) <= 2):
        return None

    # 3) la région existe (1 à 89)
    if not (1 <= int(region) <= 89):
        return None

    lettre = LETTRES.get(caracteres[i], f"L{caracteres[i]}")
    return f"{numero}-{lettre}-{region}"


def est_valide(plaque):
    """Vérifie une plaque déjà écrite, ex. pour une saisie dans la base de données."""
    return bool(plaque) and bool(PLAQUE_RE.match(plaque))