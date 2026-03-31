import streamlit as st
import streamlit_authenticator as stauth
import yaml
import pandas as pd
from yaml.loader import SafeLoader

# Configuration de la page
st.set_page_config(page_title="Dashboard Expert", layout="wide")

# 1. Chargement de la configuration d'authentification
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# 2. Initialisation de l'authentificateur
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# --- CORRECTION ICI ---
# La nouvelle version n'accepte plus ('Connexion', 'main')
# On utilise maintenant des arguments nommés
authenticator.login(location='main')

# 4. Logique d'affichage
if st.session_state["authentication_status"]:
    # Barre latérale
    authenticator.logout('Déconnexion', 'sidebar')
    st.sidebar.title(f"Bienvenue {st.session_state['name']}")
    
    st.title("📊 Tableau de Bord Expert")
    
    # Création d'une base de données de test si le fichier CSV n'existe pas
    try:
        df = pd.read_csv('base_expert.csv')
    except:
        # Données de secours pour éviter que l'app plante au premier test
        data = {
            'Tâche': ['Analyse', 'Réunion', 'Rapport'],
            'Statut': ['En cours', 'Terminé', 'En attente'],
            'Catégorie': ['Tech', 'Admin', 'Tech']
        }
        df = pd.DataFrame(data)
    
    # Filtres simples
    st.subheader("Vos Tâches")
    status_filter = st.multiselect("Filtrer par Statut", options=df['Statut'].unique(), default=df['Statut'].unique())
    
    filtered_df = df[df['Statut'].isin(status_filter)]
    st.dataframe(filtered_df, use_container_width=True)
    
    # Graphique
    st.subheader("Répartition par Catégorie")
    st.bar_chart(df['Catégorie'].value_counts())

elif st.session_state["authentication_status"] is False:
    st.error('Utilisateur ou mot de passe incorrect.')
elif st.session_state["authentication_status"] is None:
    st.warning('Veuillez entrer vos identifiants.')