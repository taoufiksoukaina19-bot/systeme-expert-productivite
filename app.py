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

    # --- ÉTAPE 1 : CHARGEMENT PRIORITAIRE ---
    # On définit df ici pour qu'il soit disponible partout en dessous
    try:
        df = pd.read_csv('base_expert.csv')
    except Exception:
        # Si le fichier n'existe pas encore, on crée une structure vide
        df = pd.DataFrame(columns=["Tâche", "Date", "Durée (min)", "Catégorie", "Priorité", "Statut"])

    # --- ÉTAPE 2 : FORMULAIRE D'AJOUT ---
    with st.expander("➕ Ajouter une nouvelle tâche", expanded=False):
        with st.form("form_tache"):
            c1, c2 = st.columns(2)
            with c1:
                nouvelle_tache = st.text_input("Quelle est la tâche ?")
                date_tache = st.date_input("Pour quand ?")
            with c2:
                duree = st.number_input("Durée (min)", min_value=15, step=15)
                priorite = st.selectbox("Importance", ["Basse", "Normale", "Haute"])
            
            submit = st.form_submit_button("Ajouter à mon planning")
            
            if submit and nouvelle_tache:
                nouvelle_ligne = pd.DataFrame([{
                    "Tâche": nouvelle_tache, 
                    "Date": str(date_tache), 
                    "Durée (min)": duree, 
                    "Catégorie": "Révision", 
                    "Priorité": priorite, 
                    "Statut": "À faire"
                }])
                # Maintenant df existe forcément, donc plus d'erreur NameError !
                df = pd.concat([df, nouvelle_ligne], ignore_index=True)
                df.to_csv('base_expert.csv', index=False)
                st.success("Tâche enregistrée !")
                st.rerun()

    # --- ÉTAPE 3 : TABLEAU DE BORD ---
    st.divider()
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Tâches totales", len(df))
    col_b.metric("Temps requis", f"{df['Durée (min)'].sum()} min")
    col_c.metric("Priorités Hautes", len(df[df['Priorité'] == 'Haute']) if 'Priorité' in df.columns else 0)

    st.subheader("📋 Ma liste de travail")
    st.dataframe(df, use_container_width=True)

elif st.session_state["authentication_status"] is False:
    st.error('Utilisateur ou mot de passe incorrect.')
elif st.session_state["authentication_status"] is None:
    st.warning('Veuillez entrer vos identifiants.')