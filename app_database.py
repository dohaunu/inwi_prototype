"""Database-backed version of the B2B Streamlit prototype.

app1.py remains the unchanged CSV version. This module supplies the same
DataFrames from PostgreSQL and then runs the existing UI code.
"""

import os
import runpy
from pathlib import Path

import pandas as pd
import psycopg
from dotenv import load_dotenv


load_dotenv(Path(__file__).parent / ".env")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "b2b_referentiel"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
    "connect_timeout": 5,
}

# Convert PostgreSQL column names to the headers expected by the existing UI.
COLUMN_NAMES = {
    "client": {
        "id_client": "Id Client",
        "nom_client": "Nom Client",
        "adresse_siege": "Adresse Siège",
        "raison_sociale": "Raison Sociale",
        "secteur_activite": "Secteur d'activité",
        "contact_client": "Contact Client",
        "gestionnaire_commercial": "Gestionnaire commercial",
        "fax": "Fax",
        "telephone": "Téléphone",
        "email": "Email",
    },
    "site_client": {
        "id_site_client": "Id Site Client",
        "id_client": "#Id Client",
        "coordonnees_gps": "Coordonnées GPS",
        "type_housing": "Type Housing",
        "adresse_site_client": "Adresse Site Client",
        "ville": "Ville",
        "zi": "ZI",
        "parente": "Parenté",
        "classification": "Classification",
        "niv_accessibilite": "Niv accessibilité",
        "contact_site_client": "Contact Site Client",
    },
    "contrat": {
        "id_contrat": "Id Contrat",
        "id_site_client": "#Id site client",
        "technologie": "Technologie",
        "duree_contrat": "Durée contrat",
        "date_contrat": "Date contrat",
        "date_mes": "Date MES",
        "service_herite_du_contrat": "Service (hérité du contrat)",
        "nbr_adductions": "Nbr Adductions",
    },
    "equipement_client": {
        "id_equipement_client": "Id Equipement client",
        "id_contrat": "#Id Contrat",
    },
    "adduction": {
        "id_adduction": "Id adduction",
        "id_contrat": "#Contrat",
        "id_equipement_inwi": "#Id Equipement INWI",
        "id_site_inwi": "#Id Site INWI",
    },
    "equipement_inwi": {
        "id_equipement_inwi": "Id Equipement Inwi",
        "id_site_inwi": "#Id Site INWI",
    },
    "site_inwi": {"id_site_inwi": "Id Site INWI"},
}

_pandas_read_csv = pd.read_csv


def read_database_table(csv_path, *args, **kwargs) -> pd.DataFrame:
    """Replace CSV reads from app1.py with their corresponding SQL tables."""
    table = Path(csv_path).stem
    if table not in COLUMN_NAMES:
        return _pandas_read_csv(csv_path, *args, **kwargs)

    with psycopg.connect(**DB_CONFIG) as connection:
        
        frame = pd.read_sql_query(f'SELECT * FROM "{table}"', connection)

    return frame.rename(columns=COLUMN_NAMES[table]).fillna("").astype(str)


if not DB_CONFIG["password"]:
    raise RuntimeError("DB_PASSWORD is missing from the .env file")


pd.read_csv = read_database_table
runpy.run_path(str(Path(__file__).parent / "app1.py"), run_name="__main__")
