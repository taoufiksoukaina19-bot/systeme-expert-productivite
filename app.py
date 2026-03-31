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
    authenticator.logout('Déconnexion', 'sidebar')
    st.sidebar.title(f"👤 {st.session_state['name']}")
    
    st.title("🚀 Mon Organisateur Expert")

    # --- SECTION 1 : AJOUT DE TÂCHE ---
    with st.expander("➕ Ajouter une nouvelle tâche", expanded=False):
        with st.form("form_tache"):
            col1, col2 = st.columns(2)
            with col1:
                nouvelle_tache = st.text_input("Nom de la tâche")
                date_tache = st.date_input("Date")
            with col2:
                duree = st.number_input("Durée estimée (min)", min_value=15, step=15)
                priorite = st.selectbox("Priorité", ["Basse", "Normale", "Haute"])
            
            submit = st.form_submit_button("Enregistrer la tâche")
            
            if submit and nouvelle_tache:
                # Création de la nouvelle ligne
                nouvelle_ligne = pd.DataFrame([{
                    "Tâche": nouvelle_tache, "Date": str(date_tache), 
                    "Durée (min)": duree, "Catégorie": "Travail", 
                    "Priorité": priorite, "Statut": "À faire"
                }])
                # Sauvegarde réelle dans le fichier CSV
                df = pd.concat([df, nouvelle_ligne], ignore_index=True)
                df.to_csv('base_expert.csv', index=False)
                st.success("Tâche ajoutée avec succès !")

    # --- SECTION 2 : TABLEAU DE BORD ---
    # Calcul des statistiques pour l'intérêt de l'organisation
    total_taches = len(df)
    taches_faites = len(df[df['Statut'] == 'Terminé'])
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Tâches", total_taches)
    c2.metric("Terminées", taches_faites)
    c3.metric("Temps total (min)", df['Durée (min)'].sum())

    st.divider()

    # Affichage du tableau interactif
    st.subheader("📋 Liste de mes priorités")
    st.dataframe(df, use_container_width=True)
    
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