import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# --- CONFIGURATION ---
st.set_page_config(page_title="Système Expert Pro", layout="wide", page_icon="🚀")

# --- AUTHENTIFICATION ---
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login('main')

if authentication_status:
    st.sidebar.title(f"👤 {name}")
    authenticator.logout('Déconnexion', 'sidebar')
    
    DB_FILE = "base_expert.csv"

    def charger_donnees():
        if os.path.exists(DB_FILE):
            df = pd.read_csv(DB_FILE)
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            if 'User' in df.columns:
                return df[df['User'] == username].copy()
        return pd.DataFrame(columns=["Tâche", "Date", "Durée (min)", "Catégorie", "Priorité", "Statut", "User"])

    def sauvegarder_donnees(df_user):
        if os.path.exists(DB_FILE):
            full_df = pd.read_csv(DB_FILE)
            if 'User' in full_df.columns:
                full_df = full_df[full_df['User'] != username]
            combined = pd.concat([full_df, df_user], ignore_index=True)
            combined.to_csv(DB_FILE, index=False)
        else:
            df_user.to_csv(DB_FILE, index=False)

    if 'df_tasks' not in st.session_state:
        st.session_state.df_tasks = charger_donnees()

    page = st.sidebar.radio("Menu", ["📅 Planification", "📊 Analyses"])

    if page == "📅 Planification":
        st.title("Organiser ma journée")
        with st.form("form_tache", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nom = st.text_input("Nom de la tâche")
                date_t = st.date_input("Date", datetime.now())
                cat = st.selectbox("Catégorie", ["Travail", "Loisir", "Santé", "Maison"])
            with col2:
                duree = st.number_input("Durée (min)", 5, 480, 30)
                prio = st.select_slider("Priorité", ["Basse", "Normale", "URGENT"])
            
            if st.form_submit_button("Ajouter à l'agenda"):
                nouvelle = pd.DataFrame([{
                    "Tâche": nom, "Date": date_t, "Durée (min)": duree,
                    "Catégorie": cat, "Priorité": prio, "Statut": "À faire",
                    "User": username
                }])
                st.session_state.df_tasks = pd.concat([st.session_state.df_tasks, nouvelle], ignore_index=True)
                sauvegarder_donnees(st.session_state.df_tasks)
                st.success("Tâche ajoutée avec succès !")

    else:
        st.title("📊 Mes Analyses & Suivi")
        df = st.session_state.df_tasks
        if not df.empty:
            c1, c2 = st.columns(2)
            c1.metric("Volume Horaire", f"{round(df['Durée (min)'].sum()/60, 1)}h")
            c2.metric("Tâches Urgentes", len(df[df['Priorité'] == "URGENT"]))
            
            edited = st.data_editor(df, use_container_width=True, hide_index=True)
            if st.button("💾 Enregistrer les modifications"):
                sauvegarder_donnees(edited)
                st.session_state.df_tasks = edited
                st.success("Données mises à jour !")
        else:
            st.info("Ajoutez des tâches pour voir vos analyses.")

elif authentication_status == False:
    st.error("Utilisateur ou mot de passe incorrect.")
elif authentication_status == None:
    st.warning("Veuillez vous connecter.")