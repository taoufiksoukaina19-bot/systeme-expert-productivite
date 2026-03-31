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

# 3. Formulaire de connexion
name, authentication_status, username = authenticator.login('Connexion', 'main')

# 4. Logique d'affichage
if authentication_status:
    # Barre latérale avec bouton de déconnexion et infos
    authenticator.logout('Déconnexion', 'sidebar')
    st.sidebar.title(f"Bienvenue {name}")
    
    st.title("📊 Tableau de Bord Expert")
    
    # Chargement et affichage des données
    try:
        df = pd.read_csv('base_expert.csv')
        
        # Filtres simples
        st.subheader("Vos Tâches")
        status_filter = st.multiselect("Filtrer par Statut", options=df['Statut'].unique(), default=df['Statut'].unique())
        
        filtered_df = df[df['Statut'].isin(status_filter)]
        
        # Affichage du tableau de données
        st.dataframe(filtered_df, use_container_width=True)
        
        # Petit graphique récapitulatif
        st.subheader("Répartition par Catégorie")
        st.bar_chart(df['Catégorie'].value_counts())
        
    except Exception as e:
        st.error(f"Erreur lors du chargement de la base de données : {e}")

elif authentication_status == False:
    st.error('Utilisateur ou mot de passe incorrect.')
elif authentication_status == None:
    st.warning('Veuillez entrer vos identifiants.')