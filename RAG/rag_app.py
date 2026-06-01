import streamlit as st
import ollama
import chromadb
from chromadb.utils import embedding_functions

# Configuration de la page
st.set_page_config(
    page_title="RAG - Code de la famille du Togo",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ Assistant juridique - Code de la famille du Togo")
st.markdown("Posez vos questions sur le code des personnes et de la famille")

# Chargement de la base vectorielle (une seule fois)
@st.cache_resource
def load_chroma():
    client = chromadb.PersistentClient(path="./chroma_db_code")
    collection = client.get_collection("code_famille")
    return collection

collection = load_chroma()

# Fonction de recherche
def search(query, top_k=3):
    results = collection.query(query_texts=[query], n_results=top_k)
    return results['documents'][0]

# Fonction de génération
def generate_answer(query, context_chunks, model="llama3.2:3b"):
    context = "\n\n---\n\n".join(context_chunks)
    if len(context) > 3000:
        context = context[:3000] + "..."
    
    prompt = f"""Tu es un expert en droit de la famille togolais. 
Réponds à la question en te basant UNIQUEMENT sur le contexte fourni.
Si la réponse n'est pas dans le contexte, dis "Je n'ai pas trouvé cette information dans le code."

### CONTEXTE ###
{context}

### QUESTION ###
{query}

### RÉPONSE ###
"""
    response = ollama.generate(model=model, prompt=prompt, options={'temperature': 0.3})
    return response['response']

# Interface
col1, col2 = st.columns([3, 1])

with col1:
    question = st.text_input("📝 Votre question :", placeholder="Ex: Quel est l'âge minimum pour se marier ?")

with col2:
    top_k = st.slider("Nombre de sources", min_value=1, max_value=5, value=3)

if question:
    with st.spinner("🔍 Recherche en cours..."):
        passages = search(question, top_k=top_k)
        answer = generate_answer(question, passages)
    
    # Affichage de la réponse
    st.markdown("---")
    st.subheader("💡 Réponse")
    st.success(answer)
    
    # Affichage des sources
    with st.expander("📖 Voir les passages utilisés"):
        for i, passage in enumerate(passages):
            st.markdown(f"**Source {i+1} :**")
            st.code(passage, language="text")
            st.markdown("---")

# Sidebar avec informations
with st.sidebar:
    st.markdown("### ℹ️ À propos")
    st.markdown("""
    - **Corpus** : Code des personnes et de la famille du Togo (2012)
    - **Modèle** : Llama 3.2 (3B) via Ollama
    - **Embeddings** : Sentence-BERT
    - **Base vectorielle** : ChromaDB
    """)
    
    st.markdown("### 🎯 Exemples de questions")
    exemples = [
        "Quel est l'âge minimum pour se marier ?",
        "Comment se fait le changement de nom ?",
        "Quelles sont les causes de nullité du mariage ?",
        "Quels sont les droits du conjoint survivant ?",
        "Comment l'enfant né hors mariage est-il reconnu ?"
    ]
    for ex in exemples:
        if st.button(ex, use_container_width=True):
            question = ex
            st.rerun()