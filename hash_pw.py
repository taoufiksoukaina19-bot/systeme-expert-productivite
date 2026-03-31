import streamlit_authenticator as stauth

# Remplace par les mots de passe que tu veux pour tes utilisateurs
passwords = ['ton_pass_1', 'ton_pass_2']
hashed_passwords = stauth.Hasher(passwords).generate()

print(hashed_passwords)