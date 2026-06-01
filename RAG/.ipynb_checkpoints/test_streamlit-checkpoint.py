import streamlit as st

st.set_page_config(page_title="Test", layout="wide")
st.title("Test Streamlit")
st.write("Si vous voyez ce message, Streamlit fonctionne correctement.")

if st.button("Cliquez-moi"):
    st.success("Ça marche !")