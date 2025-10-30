import streamlit as st
import google.generativeai as genai
from google.api_core import client_options
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Keep model loading separate
def load_and_configure_model():
    """
    Configures genai, lists available models for diagnostics, and loads the Gemini model.
    """
    api_key = None
    model_name = 'gemini-1.5-flash-latest' # Target model
    # model_name = 'gemini-pro' # Fallback if flash still fails

    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is empty in Streamlit secrets.")

        logger.info(f"Attempting to configure Google Generative AI for v1 endpoint (generativelanguage.googleapis.com)...")

        opts = client_options.ClientOptions(api_endpoint="generativelanguage.googleapis.com") # v1 endpoint

        genai.configure(
            api_key=api_key,
            client_options=opts
        )

        logger.info("Google Generative AI configured for v1 endpoint attempt.")

        # --- DIAGNOSTIC STEP: List available models ---
        try:
            logger.info("Listing available models after configuration...")
            available_models = [
                m.name for m in genai.list_models()
                if 'generateContent' in m.supported_generation_methods
            ]
            logger.info(f"Available models supporting 'generateContent': {available_models}")

            # Check if our target model is in the list
            if f'models/{model_name}' not in available_models:
                logger.error(f"CRITICAL: Target model '{model_name}' is NOT available via the configured endpoint. Available models: {available_models}")
                # Try falling back to gemini-pro if flash wasn't found
                if model_name == 'gemini-1.5-flash-latest' and 'models/gemini-pro' in available_models:
                    logger.warning("Falling back to gemini-pro as flash model was not found.")
                    model_name = 'gemini-pro'
                else:
                     raise ValueError(f"Target model '{model_name}' not found in available models list. Check API endpoint configuration or model name.")
            else:
                 logger.info(f"Target model '{model_name}' confirmed available via configured endpoint.")

        except Exception as list_e:
            logger.error(f"Could not list models after configuration: {list_e}", exc_info=True)
            # Don't immediately fail, let GenerativeModel try, but log the error
            st.warning(f"Could not verify available models: {list_e}")
        # --- END DIAGNOSTIC STEP ---

        logger.info(f"Attempting to load model: {model_name}")

        model = genai.GenerativeModel(
            model_name, # Use the potentially updated model_name
            safety_settings={
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_MEDIUM_AND_ABABOVE',
            }
        )
        logger.info(f"Model {model_name} loaded successfully.")
        return model

    except KeyError:
        st.error("Error: GOOGLE_API_KEY not found in .streamlit/secrets.toml.")
        logger.error("GOOGLE_API_KEY not found in secrets.")
        return None
    except ValueError as ve:
        st.error(f"Configuration or Model Error: {ve}")
        logger.error(f"Configuration or Model Error: {ve}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred loading the Generative Model: {type(e).__name__} - {e}. Check API key, network, and library versions.")
        logger.error(f"Unexpected error loading model: {e}", exc_info=True)
        return None

# Use st.session_state
if 'genai_model' not in st.session_state:
    st.session_state.genai_model = load_and_configure_model()

# --- generate_response function remains the same ---
def generate_response(context, query, lang="en"):
    model = st.session_state.genai_model
    if model is None:
        logger.warning("Generative model was None in generate_response, attempting reload...")
        st.session_state.genai_model = load_and_configure_model()
        model = st.session_state.genai_model
        if model is None:
             return "Error: The generative AI model could not be loaded. Please check terminal logs."

    language_instruction = "in English." if lang == "en" else "in simple, natural Hindi."
    prompt = f"""
    You are an expert "Global Wellness Assistant."
    Your user is asking about: "{query}"
    You must ONLY use the following trusted "Context" to answer their question.
    Do NOT use any outside knowledge. Do NOT diagnose or give medical advice.
    You must be conversational, empathetic, and clear.
    You must include the safety disclaimer.

    Context:
    "{context}"

    Based only on that context, please provide a helpful answer {language_instruction}
    """
    try:
        response = model.generate_content(prompt)
        if not response.parts:
             if response.prompt_feedback.block_reason:
                 logger.warning(f"Response blocked due to safety settings: {response.prompt_feedback.block_reason}")
                 return "I apologize, but I cannot provide a response on that specific topic due to safety guidelines."
             else:
                 raise ValueError("Received an empty response from the API.")
        return response.text
    except Exception as e:
        logger.error(f"Error during content generation: {e}", exc_info=True)
        st.warning(f"Generative AI error: {type(e).__name__} - {e}")
        # More specific error message based on the diagnostic check
        if "not found for API version v1beta" in str(e) or "Model not found" in str(e):
             return f"Error: The model '{model.model_name}' was not found for the API endpoint the library connected to. Please check terminal logs for available models."
        elif "response was blocked" in str(e).lower():
            return "I apologize, but I cannot provide a response on that specific topic due to safety guidelines."
        else:
            return f"I'm sorry, I encountered an issue generating a response ({type(e).__name__}). Please try again or rephrase your question."