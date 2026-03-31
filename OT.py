import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# --- CONFIGURATION ET AUTHENTIFICATION ---
st.set_page_config(page_title="Système Expert Productivité", layout="wide", page_icon="🚀")

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Affichage du login
name, authentication_status, username = authenticator.login('main')

if authentication_status:
    # --- BARRE LATÉRALE ---
    st.sidebar.title(f"👋 Bienvenue {name}")
    authenticator.logout('Déconnexion', 'sidebar')
    
    DB_FILE = "base_expert.csv"

    # --- FONCTIONS DE DONNÉES (MODIFIÉES POUR MULTI-UTILISATEUR) ---
    def charger_donnees():
        if os.path.exists(DB_FILE):
            df = pd.read_csv(DB_FILE)
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            # Sécurité : on ne garde que les tâches de l'utilisateur connecté
            if 'User' not in df.columns: df['User'] = username
            return df[df['User'] == username]
        return pd.DataFrame(columns=["Tâche", "Date", "Durée (min)", "Catégorie", "Priorité", "Statut", "User"])

    def sauvegarder_donnees(df_to_save):
        # On charge tout le CSV existant pour ne pas écraser les données des autres
        if os.path.exists(DB_FILE):
            full_df = pd.read_csv(DB_FILE)
            # On retire les anciennes données de cet utilisateur spécifique
            full_df = full_df[full_df['User'] != username]
            # On ajoute les nouvelles
            combined = pd.concat([full_df, df_to_save], ignore_index=True)
            combined.to_csv(DB_FILE, index=False)
        else:
            df_to_save.to_csv(DB_FILE, index=False)

    if 'df_tasks' not in st.session_state:
        st.session_state.df_tasks = charger_donnees()

    page = st.sidebar.radio("Navigation", ["➕ Planification", "📊 Analyses & Suivi"])

    # --- PAGE 1 : PLANIFICATION ---
    if page == "➕ Planification":
        st.title("📅 Organiser mes journées")
        
        with st.form("expert_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                nom = st.text_input("Nom de l'engagement")
                date_deb = st.date_input("Date", datetime.now())
                cat = st.selectbox("Catégorie", ["Travail", "Loisir", "Santé", "Maison"])
            with c2:
                duree = st.number_input("Durée (min)", min_value=5, value=30, step=5)
                prio = st.select_slider("Priorité", options=["Basse", "Normale", "URGENT"])
                repetition = st.number_input("Répéter (jours)", min_value=1, value=1)
            
            submit = st.form_submit_button("Ajouter à l'emploi du temps")

        if submit and nom:
            nouvelles_lignes = []
            for i in range(repetition):
                nouvelles_lignes.append({
                    "Tâche": nom, "Date": date_deb + timedelta(days=i),
                    "Durée (min)": duree, "Catégorie": cat,
                    "Priorité": prio, "Statut": "À faire",
                    "User": username  # On lie la tâche à l'utilisateur
                })
            
            new_df = pd.DataFrame(nouvelles_lignes)
            st.session_state.df_tasks = pd.concat([st.session_state.df_tasks, new_df], ignore_index=True)
            sauvegarder_donnees(st.session_state.df_tasks)
            st.success("Engagement enregistré !")

    # --- PAGE 2 : ANALYSES & SUIVI ---
    else:
        st.title("📊 Ma Productivité Personnelle")
        df = st.session_state.df_tasks
        
        if df.empty:
            st.info("Aucune tâche enregistrée.")
        else:
            # Stats rapides
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Heures", round(df['Durée (min)'].sum()/60, 1))
            col2.metric("Tâches Terminées", len(df[df['Statut'] == "Terminé"]))
            col3.metric("Urgences", len(df[df['Priorité'] == "URGENT"]))

            # Éditeur de données
            edited_df = st.data_editor(df, use_container_width=True, hide_index=True)
            if st.button("💾 Sauvegarder les modifications"):
                st.session_state.df_tasks = edited_df
                sauvegarder_donnees(edited_df)
                st.toast("Mis à jour !")

elif authentication_status == False:
    st.error('Utilisateur ou mot de passe incorrect')
elif authentication_status == None:
    st.warning('Veuillez vous connecter pour accéder à vos données')