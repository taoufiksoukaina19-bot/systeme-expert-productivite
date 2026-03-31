import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import datetime

# 1. Configuration de la page (Look Mobile)
st.set_page_config(
    page_title="Expert Planning",
    page_icon="📅",
    layout="centered", # Important pour le format téléphone
    initial_sidebar_state="collapsed"
)

# 2. Design CSS Personnalisé (Style App Moderne)
st.markdown("""
    <style>
    /* Fond de l'application */
    .stApp { background-color: #f8f9fa; }
    
    /* Style des cartes de tâches */
    .task-card {
        background-color: white;
        padding: 15px;
        border-radius: 15px;
        border-left: 5px solid #007bff;
        margin-bottom: 10px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Style des métriques en haut */
    [data-testid="stMetric"] {
        background-color: white;
        border-radius: 15px;
        padding: 10px;
        border: 1px solid #eeeeee;
    }
    
    /* Boutons arrondis */
    .stButton>button {
        border-radius: 25px;
        width: 100%;
        height: 3em;
        background-color: #007bff;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Authentification
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# Formulaire de login
authenticator.login(location='main')

if st.session_state["authentication_status"]:
    # Barre latérale discrète
    with st.sidebar:
        st.title(f"👋 {st.session_state['name']}")
        authenticator.logout('Déconnexion', 'sidebar')

    # --- CHARGEMENT DES DONNÉES ---
    try:
        df = pd.read_csv('base_expert.csv')
        df['Date'] = pd.to_datetime(df['Date']).dt.date
    except:
        df = pd.DataFrame(columns=["Tâche", "Date", "Durée", "Priorité", "Statut"])

    # --- TITRE PRINCIPAL ---
    st.write(f"### 🚀 Mon Organisateur Expert")
    
    # Onglets pour Mobile
    tab_plan, tab_add = st.tabs(["📅 Mon Planning", "➕ Ajouter"])

    with tab_plan:
        # Résumé Rapide
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Tâches", len(df))
        with col2:
            total_min = df['Durée'].sum() if not df.empty else 0
            st.metric("Total Temps", f"{total_min}m")

        st.divider()

        # Liste des tâches style "Mobile Cards"
        if not df.empty:
            # Trier par date pour l'organisation
            df_sorted = df.sort_values(by='Date')
            
            for index, row in df_sorted.iterrows():
                # Couleur selon priorité
                color = "#ff4b4b" if row['Priorité'] == "Haute" else "#007bff"
                
                st.markdown(f"""
                    <div class="task-card" style="border-left-color: {color};">
                        <div style="display: flex; justify-content: space-between;">
                            <strong>{row['Tâche']}</strong>
                            <span style="font-size: 0.8em; color: gray;">{row['Durée']} min</span>
                        </div>
                        <div style="font-size: 0.85em; margin-top: 5px; color: #555;">
                            🗓️ {row['Date']} | 🚩 {row['Priorité']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Aucune tâche. Cliquez sur '+' pour commencer !")

    with tab_add:
        st.write("#### Nouvelle Tâche")
        with st.form("mobile_form", clear_on_submit=True):
            tache_nom = st.text_input("Nom de la tâche", placeholder="Ex: Révision Anglais")
            tache_date = st.date_input("Date", datetime.date.today())
            
            c1, c2 = st.columns(2)
            with c1:
                tache_duree = st.number_input("Durée (min)", min_value=15, value=30, step=15)
            with c2:
                tache_prio = st.selectbox("Priorité", ["Basse", "Normale", "Haute"], index=1)
            
            submit = st.form_submit_button("Enregistrer")
            
            if submit and tache_nom:
                new_row = pd.DataFrame([{
                    "Tâche": tache_nom,
                    "Date": str(tache_date),
                    "Durée": tache_duree,
                    "Priorité": tache_prio,
                    "Statut": "À faire"
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv('base_expert.csv', index=False)
                st.success("C'est enregistré !")
                st.rerun()

elif st.session_state["authentication_status"] is False:
    st.error('Utilisateur ou mot de passe incorrect.')
elif st.session_state["authentication_status"] is None:
    st.warning('Veuillez entrer vos identifiants.')