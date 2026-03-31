import streamlit as st

# 1. Test de configuration
try:
    st.set_page_config(page_title="Test Debug", layout="centered")
    st.success("Configuration de la page : OK")
except Exception as e:
    st.error(f"Erreur de configuration : {e}")

# 2. Test de l'état de session (Session State)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.info("Initialisation de la session : OK")

# 3. Formulaire de login simplifié pour diagnostic
st.title("Interface de Connexion")

with st.form("login_form"):
    user = st.text_input("Utilisateur")
    pw = st.text_input("Mot de passe", type="password")
    submit = st.form_submit_button("Se connecter")

    if submit:
        # Vérifie si les variables sont bien capturées
        st.write(f"Tentative de connexion pour : {user}")
        if user == "admin" and pw == "admin": # Test simple
            st.session_state['logged_in'] = True
            st.success("Authentification réussie !")
        else:
            st.error("Identifiants incorrects (Test)")

# 4. Affichage des erreurs système masquées
import sys
with st.expander("Voir les détails techniques du serveur"):
    st.write("Version Python:", sys.version)
    st.write("Arguments système:", sys.argv)
    