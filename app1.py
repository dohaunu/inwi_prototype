from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Référentiel B2B",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path(__file__).parent / "b2b_données_csv"


def load_css(filepath: str) -> None:
    with open(filepath, "r", encoding="utf-8") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)


@st.cache_data
def load_data() -> dict[str, pd.DataFrame]:
    files = {
        "clients": "client.csv",
        "sites": "site_client.csv",
        "contracts": "contrat.csv",
        "client_equipment": "equipement_client.csv",
        "adductions": "adduction.csv",
        "inwi_equipment": "equipement_inwi.csv",
        "inwi_sites": "site_inwi.csv",
    }
    return {
        name: pd.read_csv(DATA_DIR / filename, dtype=str).fillna("")
        for name, filename in files.items()
    }


def related_records(data: dict[str, pd.DataFrame], client_id: str) -> dict[str, pd.DataFrame]:
    client = data["clients"][data["clients"]["Id Client"].eq(client_id)]
    sites = data["sites"][data["sites"]["#Id Client"].eq(client_id)]
    site_ids = sites["Id Site Client"]

    contracts = data["contracts"][
        data["contracts"]["#Id site client"].isin(site_ids)
    ]
    contract_ids = contracts["Id Contrat"]

    client_equipment = data["client_equipment"][
        data["client_equipment"]["#Id Contrat"].isin(contract_ids)
    ]
    adductions = data["adductions"][
        data["adductions"]["#Contrat"].isin(contract_ids)
    ]
    inwi_equipment = data["inwi_equipment"][
        data["inwi_equipment"]["Id Equipement Inwi"].isin(
            adductions["#Id Equipement INWI"]
        )
    ]
    inwi_sites = data["inwi_sites"][
        data["inwi_sites"]["Id Site INWI"].isin(adductions["#Id Site INWI"])
    ]

    return {
        "Client": client,
        "Site client": sites,
        "Équipement client": client_equipment,
        "Contrat": contracts,
        "Adduction": adductions,
        "Équipement INWI": inwi_equipment,
        "Site INWI": inwi_sites,
    }


RECORD_META = {
    "Site client": ("Id Site Client", "FICHE SITE CLIENT"),
    "Équipement client": ("Id Equipement client", "FICHE ÉQUIPEMENT CLIENT"),
    "Contrat": ("Id Contrat", "FICHE CONTRAT"),
    "Adduction": ("Id adduction", "FICHE ADDUCTION"),
    "Équipement INWI": ("Id Equipement Inwi", "FICHE ÉQUIPEMENT INWI"),
    "Site INWI": ("Id Site INWI", "FICHE SITE INWI"),
}


def display_label(column_name: str) -> str:
    """Turn CSV relationship column names into cleaner labels."""
    return column_name.lstrip("#").replace("Id", "ID", 1)


def render_record_detail(section_name: str, record: pd.Series) -> None:
    id_column, eyebrow = RECORD_META[section_name]
    record_id = str(record.get(id_column, "—") or "—")
    rows = "".join(
        (
            '<div class="record-detail-row">'
            f"<span>{escape(display_label(str(column)))}</span>"
            f"<strong>{escape(str(value or '—'))}</strong>"
            "</div>"
        )
        for column, value in record.items()
    )
    st.markdown(
        f"""
        <div class="selected-record">
            <div class="selected-record-head">
                <div>
                    <p>{escape(eyebrow)}</p>
                    <h2>{escape(record_id)}</h2>
                </div>
                <span>ID DE L’ENREGISTREMENT</span>
            </div>
            <div class="selected-record-title">Informations détaillées</div>
            <div class="selected-record-grid">{rows}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


load_css(str(Path(__file__).parent / "style.css"))
data = load_data()
clients = data["clients"]

st.sidebar.markdown(
    """
    <div class="brand-block">
        <div class="brand-mark">◈</div>
        <div><strong>Référentiel B2B</strong></div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="topbar">
        <div><span class="topbar-symbol">◈</span> Référentiel réseau B2B</div>
    </div>
    """,
    unsafe_allow_html=True,
)

search_name = st.text_input(
    "Rechercher un client par nom ou identifiant",
    placeholder="Ex. Argan Digital ou CLI-0003",
    key="client_text_search",
)

client_cities = (
    clients["Adresse Siège"]
    .astype(str)
    .str.rsplit(",", n=1)
    .str[-1]
    .str.strip()
)

with st.expander("Filtres avancés — ville, secteur et technologie"):
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        selected_cities = st.multiselect(
            "Ville du client",
            sorted(value for value in client_cities.unique() if value),
            placeholder="Toutes les villes",
            help="La ville est extraite de l’adresse du siège du client.",
        )
    with filter_col2:
        selected_sectors = st.multiselect(
            "Secteur",
            sorted(
                value
                for value in clients["Secteur d'activité"].unique()
                if value
            ),
            placeholder="Tous les secteurs",
        )
    with filter_col3:
        selected_technologies = st.multiselect(
            "Technologie",
            sorted(
                value
                for value in data["contracts"]["Technologie"].unique()
                if value
            ),
            placeholder="Toutes les technologies",
        )

eligible_client_ids = set(clients["Id Client"])

if selected_sectors:
    sector_client_ids = clients.loc[
        clients["Secteur d'activité"].isin(selected_sectors), "Id Client"
    ]
    eligible_client_ids &= set(sector_client_ids)

if selected_cities:
    city_client_ids = clients.loc[client_cities.isin(selected_cities), "Id Client"]
    eligible_client_ids &= set(city_client_ids)

if selected_technologies:
    technology_site_ids = data["contracts"].loc[
        data["contracts"]["Technologie"].isin(selected_technologies),
        "#Id site client",
    ]
    technology_client_ids = data["sites"].loc[
        data["sites"]["Id Site Client"].isin(technology_site_ids),
        "#Id Client",
    ]
    eligible_client_ids &= set(technology_client_ids)

matches = clients[clients["Id Client"].isin(eligible_client_ids)]

query = search_name.strip()
if query:
    typed_search_mask = (
        matches["Nom Client"].str.contains(
            query,
            case=False,
            na=False,
            regex=False,
        )
        | matches["Id Client"].str.contains(
            query,
            case=False,
            na=False,
            regex=False,
        )
    )
    matches = matches[typed_search_mask]

matches = matches.sort_values("Nom Client")

if matches.empty:
    st.warning("Aucun client ne correspond à la recherche et aux filtres sélectionnés.")
    st.stop()

client_names = clients.set_index("Id Client")["Nom Client"].to_dict()
client_ids = matches["Id Client"].tolist()
if st.session_state.get("selected_client_id") not in client_ids:
    st.session_state["selected_client_id"] = client_ids[0]

selected_client_id = st.selectbox(
    "Choisir un client dans les résultats",
    client_ids,
    format_func=lambda client_id: f"{client_names[client_id]}  ·  {client_id}",
    key="selected_client_id",
    help="Cette liste reste également searchable: ouvrez-la puis commencez à taper.",
)
st.caption(f"{len(client_ids)} client(s) disponible(s) avec les filtres actuels.")

selected_client_row = clients[clients["Id Client"].eq(selected_client_id)].iloc[0]
records = related_records(data, selected_client_id)

st.sidebar.markdown('<p class="nav-caption">NAVIGATION</p>', unsafe_allow_html=True)
section = st.sidebar.radio(
    "Navigation",
    list(records.keys()),
    label_visibility="collapsed",
)
st.sidebar.markdown(
    '<div class="sidebar-footer">Données du référentiel B2B<br>Prototype interne</div>',
    unsafe_allow_html=True,
)

client_name = escape(selected_client_row["Nom Client"])
client_id = escape(selected_client_id)
st.markdown(
    f"""
    <div class="breadcrumb">Référentiel B2B <span>›</span> Clients <span>›</span> {escape(section)}</div>
    <div class="record-header">
        <div>
            <p class="eyebrow">FICHE CLIENT</p>
            <h1>{client_name}</h1>
            <p class="record-id">Identifiant client&nbsp;&nbsp;{client_id}</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

sites = records["Site client"]
contracts = records["Contrat"]
adductions = records["Adduction"]
client_equipment = records["Équipement client"] 

if section == "Client":
    cols = st.columns(4)
    metrics = [
        ("Sites client", len(sites)),
        ("Contrats", len(contracts)),
        ("Équipements", len(client_equipment)),
        ("Adductions", len(adductions)),
    ]
    for column, (label, value) in zip(cols, metrics):
        column.metric(label, value)

    left, right = st.columns([1.05, 1], gap="large")
    with left:
        st.markdown('<div class="section-title">Informations du client</div>', unsafe_allow_html=True)
        details = [
            ("Raison sociale", selected_client_row.get("Raison Sociale", "—")),
            ("Secteur d’activité", selected_client_row.get("Secteur d'activité", "—")),
            ("Adresse du siège", selected_client_row.get("Adresse Siège", "—")),
            ("Contact", selected_client_row.get("Contact Client", "—")),
            ("Téléphone", selected_client_row.get("Téléphone", "—")),
            ("E-mail", selected_client_row.get("Email", "—")),
        ]
        detail_html = "".join(
            f'<div class="detail-row"><span>{escape(str(label))}</span><strong>{escape(str(value or "—"))}</strong></div>'
            for label, value in details
        )
        st.markdown(f'<div class="detail-card">{detail_html}</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-title">Aperçu des contrats</div>', unsafe_allow_html=True)
        preview_columns = ["Id Contrat", "Technologie", "Date MES", "Service (hérité du contrat)"]
        st.dataframe(
            contracts[preview_columns],
            width="stretch",
            hide_index=True,
            height=322,
        )
else:
    current = records[section]
    st.markdown(
        f'<div class="section-title">{escape(section)} <span class="result-count">{len(current)} élément(s)</span></div>',
        unsafe_allow_html=True,
    )
    if current.empty:
        st.info(f"Aucune donnée disponible dans « {section} » pour ce client.")
    else:
        st.caption("Sélectionnez une ligne pour ouvrir sa fiche détaillée.")
        table_event = st.dataframe(
            current,
            width="stretch",
            hide_index=True,
            height=min(650, 72 + len(current) * 36),
            key=f"records_{section}_{selected_client_id}",
            on_select="rerun",
            selection_mode="single-row",
        )
        selected_rows = table_event.selection.rows
        if selected_rows:
            render_record_detail(section, current.iloc[selected_rows[0]])
