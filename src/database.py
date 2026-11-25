"""
La base de données SQLite de SmartGate UEMF.
Tables : vehicules, visiteurs, jetons, journal, utilisateurs, corrections, liste_noire.
"""
import hashlib
import hmac
import os
import secrets
import sqlite3
import time
from datetime import date, datetime, timedelta
from pathlib import Path

DB_PATH = Path("data/smartgate.db")


def connexion():
    """Ouvre la base. row_factory → on lit les colonnes par leur nom (ligne["plaque"])."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _maintenant():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _ajouter_colonnes(conn, table, colonnes):
    """Migration : ajoute les colonnes manquantes à une table existante (sans rien effacer)."""
    existantes = {ligne["name"] for ligne in conn.execute(f"PRAGMA table_info({table})")}
    for nom, type_ in colonnes:
        if nom not in existantes:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {nom} {type_}")


def init_db():
    """Crée les tables si elles n'existent pas, et ajoute les colonnes manquantes."""
    with connexion() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS vehicules (
            plaque        TEXT PRIMARY KEY,      -- ex. 12345-أ-6 (unique)
            proprietaire  TEXT NOT NULL,
            role          TEXT NOT NULL,         -- étudiant / professeur / personnel
            valide_jusqu  TEXT NOT NULL,         -- date de fin d'autorisation (AAAA-MM-JJ)
            handicap      INTEGER DEFAULT 0      -- 1 = autorisé sur les places ♿
        );
        CREATE TABLE IF NOT EXISTS visiteurs (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nom       TEXT NOT NULL,
            plaque    TEXT,
            batiment  TEXT,
            motif     TEXT,
            date      TEXT NOT NULL,             -- jour de la visite
            statut    TEXT DEFAULT 'en_attente'  -- en_attente / accepte / refuse
        );
        CREATE TABLE IF NOT EXISTS jetons (
            token     TEXT PRIMARY KEY,
            cree_a    REAL NOT NULL,
            utilise   INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS journal (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date_heure  TEXT NOT NULL,
            plaque      TEXT,
            decision    TEXT NOT NULL,           -- OUVRIR / VISITEUR / AGENT / REFUSE / OUVERTURE_MANUELLE
            confiance   REAL
        );
        CREATE TABLE IF NOT EXISTS utilisateurs (
            identifiant   TEXT PRIMARY KEY,
            mot_de_passe  TEXT NOT NULL,         -- l'EMPREINTE, jamais le mot de passe en clair
            role          TEXT NOT NULL,         -- securite / admin
            actif         INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS corrections (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            id_passage       INTEGER,
            plaque_lue       TEXT,
            plaque_corrigee  TEXT,
            photo            TEXT,
            agent            TEXT,
            date_heure       TEXT
        );
        CREATE TABLE IF NOT EXISTS liste_noire (
            plaque     TEXT PRIMARY KEY,
            raison     TEXT,
            ajoutee_le TEXT,
            par        TEXT
        );
        """)
        _ajouter_colonnes(conn, "journal", [("raison", "TEXT"), ("proprietaire", "TEXT"),
                                            ("photo", "TEXT"), ("agent", "TEXT")])
        _ajouter_colonnes(conn, "visiteurs", [("pass_code", "TEXT"), ("pass_expire", "TEXT")])


def lire_table(nom, ordre="rowid DESC", limite=None):
    """Lit toute une table (pour les tableaux et graphiques de l'administration)."""
    if nom not in {"vehicules", "visiteurs", "journal", "corrections", "liste_noire"}:
        raise ValueError(nom)
    requete = f"SELECT * FROM {nom} ORDER BY {ordre}" + (f" LIMIT {int(limite)}" if limite else "")
    with connexion() as conn:
        return [dict(l) for l in conn.execute(requete).fetchall()]


# ---------- VÉHICULES AUTORISÉS ----------

def ajouter_vehicule(plaque, proprietaire, role, valide_jusqu, handicap=False):
    with connexion() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO vehicules VALUES (?, ?, ?, ?, ?)",
            (plaque, proprietaire, role, valide_jusqu, int(handicap)),
        )


def supprimer_vehicule(plaque):
    with connexion() as conn:
        conn.execute("DELETE FROM vehicules WHERE plaque = ?", (plaque,))


def trouver_vehicule(plaque):
    """Renvoie la ligne du véhicule s'il est autorisé AUJOURD'HUI, sinon None."""
    with connexion() as conn:
        return conn.execute(
            "SELECT * FROM vehicules WHERE plaque = ? AND valide_jusqu >= ?",
            (plaque, date.today().isoformat()),
        ).fetchone()


# ---------- LISTE NOIRE ----------

def ajouter_liste_noire(plaque, raison, par):
    with connexion() as conn:
        conn.execute("INSERT OR REPLACE INTO liste_noire VALUES (?, ?, ?, ?)",
                     (plaque, raison, _maintenant(), par))


def retirer_liste_noire(plaque):
    with connexion() as conn:
        conn.execute("DELETE FROM liste_noire WHERE plaque = ?", (plaque,))


def est_liste_noire(plaque):
    with connexion() as conn:
        return conn.execute("SELECT * FROM liste_noire WHERE plaque = ?", (plaque,)).fetchone()


# ---------- VISITEURS ----------

def ajouter_visiteur(nom, plaque, batiment, motif):
    """Une nouvelle demande de visiteur (statut : en_attente). Renvoie son numéro."""
    with connexion() as conn:
        cur = conn.execute(
            "INSERT INTO visiteurs (nom, plaque, batiment, motif, date) VALUES (?, ?, ?, ?, ?)",
            (nom, plaque, batiment, motif, date.today().isoformat()),
        )
        return cur.lastrowid


def changer_statut_visiteur(id_visiteur, statut):
    with connexion() as conn:
        conn.execute("UPDATE visiteurs SET statut = ? WHERE id = ?", (statut, id_visiteur))


def accepter_visiteur(id_visiteur, duree_heures=3):
    """L'agent accepte : on crée un PASSE (code à 6 caractères) valable quelques heures."""
    code = secrets.token_hex(3).upper()
    expire = (datetime.now() + timedelta(hours=duree_heures)).strftime("%Y-%m-%d %H:%M:%S")
    with connexion() as conn:
        conn.execute("UPDATE visiteurs SET statut = 'accepte', pass_code = ?, pass_expire = ? WHERE id = ?",
                     (code, expire, id_visiteur))
    return code


def trouver_visiteur(id_visiteur):
    with connexion() as conn:
        return conn.execute("SELECT * FROM visiteurs WHERE id = ?", (id_visiteur,)).fetchone()


def statut_visiteur(id_visiteur):
    v = trouver_visiteur(id_visiteur)
    return v["statut"] if v else None


def verifier_passe(code):
    """Pour l'agent, à la sortie : le passe est-il valable ? → (ok, message)"""
    code = code.strip().upper().split(":")[-1]          # accepte "3FA9C1" ou "SMARTGATE-PASS:3FA9C1"
    with connexion() as conn:
        v = conn.execute("SELECT * FROM visiteurs WHERE pass_code = ?", (code,)).fetchone()
    if v is None:
        return False, "Passe inconnu"
    if v["pass_expire"] and v["pass_expire"] < _maintenant():
        return False, f"Passe expiré ({v['nom']}, depuis {v['pass_expire'][11:16]})"
    return True, f"Passe valable : {v['nom']} · {v['plaque'] or '?'} · jusqu'à {v['pass_expire'][11:16]}"


def visiteur_accepte_aujourdhui(plaque):
    """Le visiteur a-t-il un passe encore valable aujourd'hui ?"""
    with connexion() as conn:
        return conn.execute(
            "SELECT * FROM visiteurs WHERE plaque = ? AND date = ? AND statut = 'accepte' "
            "AND (pass_expire IS NULL OR pass_expire >= ?)",
            (plaque, date.today().isoformat(), _maintenant()),
        ).fetchone()


def demandes_en_attente():
    with connexion() as conn:
        return conn.execute("SELECT * FROM visiteurs WHERE statut = 'en_attente' ORDER BY id").fetchall()


# ---------- JETONS DU QR DYNAMIQUE ----------

DUREE_JETON = 120   # secondes : un QR est valable 2 minutes


def creer_jeton():
    token = secrets.token_urlsafe(8)
    with connexion() as conn:
        conn.execute("INSERT INTO jetons (token, cree_a) VALUES (?, ?)", (token, time.time()))
    return token


def utiliser_jeton(token):
    """Vérifie le jeton et le "consomme" (une seule utilisation). → (ok, message)"""
    with connexion() as conn:
        ligne = conn.execute("SELECT * FROM jetons WHERE token = ?", (token,)).fetchone()
        if ligne is None:
            return False, "QR code inconnu"
        if ligne["utilise"]:
            return False, "QR code déjà utilisé"
        if time.time() - ligne["cree_a"] > DUREE_JETON:
            return False, "QR code expiré, scannez à nouveau"
        conn.execute("UPDATE jetons SET utilise = 1 WHERE token = ?", (token,))
        return True, "ok"


# ---------- JOURNAL DES PASSAGES ----------

def enregistrer_passage(plaque, decision, confiance, raison=None, proprietaire=None, photo=None,
                        agent=None, date_heure=None):
    """Enregistre un passage et renvoie son numéro."""
    with connexion() as conn:
        cur = conn.execute(
            "INSERT INTO journal (date_heure, plaque, decision, confiance, raison, proprietaire, photo, agent) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (date_heure or _maintenant(), plaque, decision, confiance, raison, proprietaire, photo, agent),
        )
        return cur.lastrowid


def derniers_passages(n=20):
    with connexion() as conn:
        return conn.execute("SELECT * FROM journal ORDER BY id DESC LIMIT ?", (n,)).fetchall()


def dernier_passage():
    with connexion() as conn:
        return conn.execute("SELECT * FROM journal ORDER BY id DESC LIMIT 1").fetchone()


def derniere_plaque_inconnue(minutes=10):
    """La dernière plaque classée VISITEUR à la barrière (pour pré-remplir le formulaire)."""
    with connexion() as conn:
        ligne = conn.execute(
            "SELECT plaque, date_heure FROM journal WHERE decision = 'VISITEUR' ORDER BY id DESC LIMIT 1"
        ).fetchone()
    if ligne:
        quand = datetime.strptime(ligne["date_heure"], "%Y-%m-%d %H:%M:%S")
        if datetime.now() - quand < timedelta(minutes=minutes):
            return ligne["plaque"]
    return ""


def corriger_plaque(id_passage, nouvelle_plaque, agent):
    """L'agent corrige une plaque mal lue : on garde l'ancienne ET la nouvelle (pour l'IA)."""
    with connexion() as conn:
        p = conn.execute("SELECT * FROM journal WHERE id = ?", (id_passage,)).fetchone()
        conn.execute(
            "INSERT INTO corrections (id_passage, plaque_lue, plaque_corrigee, photo, agent, date_heure) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (id_passage, p["plaque"] if p else None, nouvelle_plaque, p["photo"] if p else None,
             agent, _maintenant()),
        )
        conn.execute("UPDATE journal SET plaque = ?, raison = ? WHERE id = ?",
                     (nouvelle_plaque, f"plaque corrigée par {agent}", id_passage))


# ---------- UTILISATEURS (connexion) ----------

def _empreinte(mot_de_passe, sel=None):
    """Empreinte d'un mot de passe (PBKDF2, 200 000 tours). Le 'sel' rend chaque empreinte unique."""
    sel = sel or os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", mot_de_passe.encode(), sel, 200_000)
    return sel.hex() + "$" + h.hex()


def creer_utilisateur(identifiant, mot_de_passe, role):
    with connexion() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO utilisateurs (identifiant, mot_de_passe, role, actif) VALUES (?, ?, ?, 1)",
            (identifiant, _empreinte(mot_de_passe), role),
        )


def verifier_connexion(identifiant, mot_de_passe):
    """Renvoie le rôle ('securite' / 'admin') si c'est correct, sinon None."""
    with connexion() as conn:
        ligne = conn.execute(
            "SELECT * FROM utilisateurs WHERE identifiant = ? AND actif = 1", (identifiant,)
        ).fetchone()
    if ligne is None:
        return None
    sel = bytes.fromhex(ligne["mot_de_passe"].split("$")[0])
    if hmac.compare_digest(_empreinte(mot_de_passe, sel), ligne["mot_de_passe"]):
        return ligne["role"]
    return None
