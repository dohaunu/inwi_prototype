import streamlit as st
import pandas as pd 
st.set_page_config(
    page_title="Référentiel B2B",
    layout="wide"
)

st.title("Référentiel B2B")
st.write("Prototype du référentiel clients B2B") 
clients=pd.read_csv("b2b_données_csv/client.csv")
st.subheader("liste des clients")
st.dataframe(clients, use_container_width=True)
client_names=clients["Nom Client"].sort_values().tolist()
selected_client=st.selectbox(
    "Sélectionner un client",
    client_names
)
client_data=clients[
    clients["Nom Client"]==selected_client
]
st.subheader("Informations Client")
st.dataframe(client_data, use_container_width=True)
sites=pd.read_csv("b2b_données_csv/site_client.csv")
sites_inwi=pd.read_csv("b2b_données_csv/site_inwi.csv")
contracts=pd.read_csv("b2b_données_csv/contrat.csv")
equipements_clients=pd.read_csv("b2b_données_csv/equipement_client.csv")
equipements_inwi=pd.read_csv("b2b_données_csv/equipement_inwi.csv")
adduction=pd.read_csv("b2b_données_csv/adduction.csv")

selected_client_row=clients[clients["Nom Client"]==selected_client].iloc[0]
selected_client_id=selected_client_row["Id Client"]

sites_clients=sites[sites["#Id Client"]==selected_client_id]
st.subheader("Sites Clients")
st.dataframe(sites_clients, use_container_width=True)

sites_ids=sites_clients["Id Site Client"].tolist()
client_contracts=contracts[contracts["#Id site client"].isin(sites_ids)]
st.subheader("Contrats Clients")
st.dataframe(client_contracts, use_container_width=True)
#client equipment
contract_ids=client_contracts["Id Contrat"].tolist()
client_equipements=equipements_clients[equipements_clients["#Id Contrat"].isin(contract_ids)]
st.subheader("Equipements Clients")
st.dataframe(client_equipements, use_container_width=True)

#adduction
client_adductions=adduction[adduction["#Contrat"].isin(contract_ids)]
st.subheader("Adductions Clients")
st.dataframe(client_adductions, use_container_width=True)
#inwi equipment
inwi_equipements_ids=client_adductions["#Id Equipement INWI"].dropna().tolist()
client_inwi_equipements=equipements_inwi[equipements_inwi["Id Equipement Inwi"].isin(inwi_equipements_ids)]
st.subheader("Equipements INWI")
st.dataframe(client_inwi_equipements, use_container_width=True)
#inwi sites
inwi_sites_ids=client_adductions["#Id Site INWI"].dropna().tolist()
client_inwi_sites=sites_inwi[sites_inwi["Id Site INWI"].isin(inwi_sites_ids)]
st.subheader("Sites Inwi")
st.dataframe(client_inwi_sites,use_container_width=True)

