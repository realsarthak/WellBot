import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer, util

# --- Model and Data loading functions remain cached ---
@st.cache_resource
def load_semantic_model():
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return model

@st.cache_data
def load_and_embed_dataset(_model):
    try:
        df = pd.read_csv("health_dataset.csv", encoding='utf-8-sig')
    except FileNotFoundError:
        st.error("health_dataset.csv not found!")
        return None, None
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return None, None

    if df.empty or len(df.columns) == 0:
        st.error("CSV is empty or has no columns.")
        return None, None

    first_column_name = df.columns[0]
    if 'answer' not in df.columns:
        st.error("CSV must have an 'answer' column.")
        return None, None

    df = df.rename(columns={first_column_name: 'question'})
    question_embeddings = _model.encode(df['question'].tolist(), convert_to_tensor=True)
    return df, question_embeddings

# --- find_best_match function ---
def find_best_match(query):
    """
    Finds the most relevant entry in the dataset for a user's query.
    Loads models and data only when called.
    """
    # --- Load model and data INSIDE the function ---
    model = load_semantic_model()
    dataset, embeddings = load_and_embed_dataset(model)

    if dataset is None or embeddings is None:
        return None, 0

    query_embedding = model.encode(query, convert_to_tensor=True)
    cosine_scores = util.cos_sim(query_embedding, embeddings)
    
    best_match_index = cosine_scores.argmax().item()
    best_score = cosine_scores[0][best_match_index].item()
    
    if best_score < 0.5: # Similarity threshold
        return None, best_score
        
    best_match_row = dataset.iloc[best_match_index]
    return best_match_row, best_score