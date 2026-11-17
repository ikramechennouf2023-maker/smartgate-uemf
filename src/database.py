"""
Étape D : la base de données SQLite de SmartGate UEMF.
4 tables : vehicules, visiteurs, jetons, journal.
"""
import sqlite3
import secrets
import time
from datetime import date, datetime
from pathlib import Path

DB_PATH = Path("data/smartgate.db")


def connexion():
    """Ouvre la base. row_factory → on lit les colonnes par leur nom (ligne["plaque"])."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crée les 4 tables si elles n'existent pas encore."""
    with connexion() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS vehicules (
            plaque        TEXT PRIMARY KEY,      -- ex. 12345-L10-6 (unique)
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
            cree_a    REAL NOT NULL,             -- heure de création (en secondes)
            utilise   INTEGER DEFAULT 0          -- 0 = pas encore utilisé, 1 = utilisé
        );
        CREATE TABLE IF NOT EXISTS journal (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date_heure  TEXT NOT NULL,
            plaque      TEXT,
            decision    TEXT NOT NULL,           -- OUVRIR / VISITEUR / AGENT …
            confiance   REAL
        );
        """)


# ---------- VÉHICULES AUTORISÉS ----------

def ajouter_vehicule(plaque, proprietaire, role, valide_jusqu, handicap=False):
    with connexion() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO vehicules VALUES (?, ?, ?, ?, ?)",
            (plaque, proprietaire, role, valide_jusqu, int(handicap)),
        )


def trouver_vehicule(plaque):
    """Renvoie la ligne du véhicule s'il est autorisé AUJOURD'HUI, sinon None."""
    with connexion() as conn:
        return conn.execute(
            "SELECT * FROM vehicules WHERE plaque = ? AND valide_jusqu >= ?",
            (plaque, date.today().isoformat()),
        ).fetchone()


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
    """L'agent accepte ou refuse : statut = 'accepte' ou 'refuse'."""
    with connexion() as conn:
        conn.execute("UPDATE visiteurs SET statut = ? WHERE id = ?", (statut, id_visiteur))


def visiteur_accepte_aujourdhui(plaque):
    """Le visiteur a-t-il été accepté aujourd'hui ? (pour rouvrir à la sortie, par exemple)"""
    with connexion() as conn:
        return conn.execute(
            "SELECT * FROM visiteurs WHERE plaque = ? AND date = ? AND statut = 'accepte'",
            (plaque, date.today().isoformat()),
        ).fetchone()


def demandes_en_attente():
    with connexion() as conn:
        return conn.execute("SELECT * FROM visiteurs WHERE statut = 'en_attente' ORDER BY id").fetchall()


# ---------- JETONS DU QR DYNAMIQUE ----------

DUREE_JETON = 120   # secondes : un QR est valable 2 minutes


def creer_jeton():
    """Crée un code aléatoire impossible à deviner, et l'enregistre."""
    token = secrets.token_urlsafe(8)
    with connexion() as conn:
        conn.execute("INSERT INTO jetons (token, cree_a) VALUES (?, ?)", (token, time.time()))
    return token


def utiliser_jeton(token):
    """
    Vérifie le jeton et le "consomme" (une seule utilisation).
    Renvoie (True, "ok") ou (False, la raison du refus).
    """
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

def enregistrer_passage(plaque, decision, confiance):
    with connexion() as conn:
        conn.execute(
            "INSERT INTO journal (date_heure, plaque, decision, confiance) VALUES (?, ?, ?, ?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), plaque, decision, confiance),
        )


def derniers_passages(n=20):
    with connexion() as conn:
        return conn.execute("SELECT * FROM journal ORDER BY id DESC LIMIT ?", (n,)).fetchall()