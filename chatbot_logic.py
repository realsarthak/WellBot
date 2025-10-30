import streamlit as st
from semantic_engine import find_best_match
import pandas as pd
import re
from transformers import MarianMTModel, MarianTokenizer

# --- Re-introducing Translation Models ---
@st.cache_resource
def get_translation_models():
    """Loads and returns the translation models and tokenizers."""
    # English to Hindi
    en_hi_model_name = "Helsinki-NLP/opus-mt-en-hi"
    en_hi_tokenizer = MarianTokenizer.from_pretrained(en_hi_model_name)
    en_hi_model = MarianMTModel.from_pretrained(en_hi_model_name)

    # Hindi to English
    hi_en_model_name = "Helsinki-NLP/opus-mt-hi-en"
    hi_en_tokenizer = MarianTokenizer.from_pretrained(hi_en_model_name)
    hi_en_model = MarianMTModel.from_pretrained(hi_en_model_name)
    
    return {
        "en_hi": (en_hi_model, en_hi_tokenizer),
        "hi_en": (hi_en_model, hi_en_tokenizer)
    }

def translate(text, model, tokenizer):
    """Translates a given text using the specified model and tokenizer."""
    tokens = tokenizer(text, return_tensors="pt", padding=True)
    translated_tokens = model.generate(**tokens)
    return tokenizer.decode(translated_tokens[0], skip_special_tokens=True)

# Load models on startup
MODELS = get_translation_models()

# --- Bilingual Config ---
CONFIG = {
    "greetings_en": ["hello", "hi", "hey", "hii"],
    "greetings_hi": ["नमस्ते", "नमस्ते।", "हैलो", "हेलो"],
    "farewells_en": ["bye", "thanks", "thank you", "ok", "done"],
    "farewells_hi": ["धन्यवाद", "ठीक है", "बाय"],
    
    "responses": {
        "greeting_en": "Hello! I am the Global Wellness Chatbot. How can I assist you today?",
        "greeting_hi": "नमस्ते! मैं ग्लोबल वेलनेस चैटबॉट हूँ। मैं आज आपकी कैसे सहायता कर सकता हूँ?",
        "farewell_en": "You're welcome! Stay healthy and feel free to ask more questions anytime.",
        "farewell_hi": "आपका स्वागत है! स्वस्थ रहें और किसी भी समय और प्रश्न पूछने में संकोch न करें।",
        "fallback_en": "I'm sorry, I don't have information on that specific topic. For any medical diagnosis, please consult a healthcare professional.",
        "fallback_hi": "मुझे क्षमा करें, मेरे पास उस विषय पर जानकारी नहीं है। किसी भी चिकित्सीय निदान के लिए, कृपया एक स्वास्थ्य पेशेवर से परामर्श करें।",
        "disclaimer_en": "⚠️ This is general wellness advice, not a medical diagnosis. Please consult a doctor for accurate guidance.",
        "disclaimer_hi": "⚠️ यह केवल सामान्य जानकारी है, चिकित्सीय निदान नहीं। कृपया सटीक मार्गदर्शन के लिए डॉक्टर से परामर्श लें।"
    }
}

def get_bot_response(user_input):
    """
    Main pipeline for the bot (Multilingual, QA-based).
    1. Detects language.
    2. Checks for simple greetings/farewells.
    3. Uses semantic search to find the best matching question.
    4. Returns the corresponding answer from the CSV, translated if needed.
    """
    user_input_lower = user_input.lower()
    
    # 1. Detect Language
    is_hindi = bool(re.search(r'[^\x00-\x7F]', user_input))
    lang = "hi" if is_hindi else "en"
    
    # 2. Check for Greetings
    if any(greet in user_input_lower for greet in (CONFIG["greetings_en"] + CONFIG["greetings_hi"])):
        return CONFIG["responses"][f"greeting_{lang}"]

    # 3. Check for Farewells
    if any(farewell in user_input_lower for farewell in (CONFIG["farewells_en"] + CONFIG["farewells_hi"])):
        return CONFIG["responses"][f"farewell_{lang}"]

    # 4. Perform Semantic Search. The model is multilingual, so no
    # translation is needed for the query itself.
    best_match_row, score = find_best_match(user_input)
    
    if best_match_row is not None:
        # 5. We found a match! The answer is in English.
        response_en = best_match_row['answer']
        
        if 'source' in best_match_row and pd.notna(best_match_row['source']):
            response_en += f"\n\n*(Source: {best_match_row['source']})*"
    else:
        # 6. No good match was found.
        response_en = CONFIG["responses"][f"fallback_en"]

    # 7. Append the Ethical Disclaimer in English
    response_en += f"\n\n{CONFIG['responses']['disclaimer_en']}"
    
    # 8. Translate the final English response back to Hindi if needed
    if is_hindi:
        model, tokenizer = MODELS["en_hi"]
        final_response = translate(response_en, model, tokenizer)
    else:
        final_response = response_en
    
    return final_response