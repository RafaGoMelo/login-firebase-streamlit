import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth
import pyrebase

# Configuração do Pyrebase (pegue no Firebase → Configurações do App Web)
firebaseConfig = {
  "apiKey": "SUA_API_KEY",
  "authDomain": "SEU_PROJETO.firebaseapp.com",
  "projectId": "SEU_PROJETO",
  "storageBucket": "SEU_PROJETO.appspot.com",
  "messagingSenderId": "ID",
  "appId": "ID"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth_py = firebase.auth()

# Inicializa Firebase Admin
cred = credentials.Certificate("serviceAccountKey.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ------------------ LOGIN ------------------
st.title("🔑 Login no Painel BI")

choice = st.selectbox("Login / Cadastro", ["Login", "Cadastro"])

email = st.text_input("Email")
password = st.text_input("Senha", type="password")

if choice == "Cadastro":
    role = st.selectbox("Papel", ["usuario", "admin"])  # define se é admin ou usuário
    if st.button("Cadastrar"):
        try:
            user = auth_py.create_user_with_email_and_password(email, password)
            uid = user["localId"]

            # Salva no Firestore o papel do usuário
            db.collection("usuarios").document(uid).set({
                "email": email,
                "role": role
            })
            st.success("Usuário cadastrado com sucesso! Agora faça login.")
        except Exception as e:
            st.error(f"Erro: {e}")

elif choice == "Login":
    if st.button("Entrar"):
        try:
            user = auth_py.sign_in_with_email_and_password(email, password)
            uid = user["localId"]

            # Busca papel no Firestore
            doc = db.collection("usuarios").document(uid).get()
            if doc.exists:
                role = doc.to_dict()["role"]
                st.success(f"Login feito! Papel: {role}")

                # Redireciona para painel de acordo com papel
                if role == "admin":
                    st.subheader("📊 Painel Administrativo")
                    st.write("Aqui o admin pode gerenciar usuários e dados.")
                else:
                    st.subheader("📈 Painel do Usuário")
                    st.write("Aqui o usuário acessa os gráficos do Oceanos.")
            else:
                st.error("Usuário não encontrado no Firestore!")
        except Exception as e:
            st.error(f"Erro: {e}")
