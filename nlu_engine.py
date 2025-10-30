import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print(
        "Spacy model 'en_core_web_sm' not found. "
        "Please run 'python -m spacy download en_core_web_sm' in your terminal."
    )
    nlp = None

HEALTH_KEYWORDS = [
    "headache", "fever", "cold", "flu", "cough", "cut", "burn", "sprain",
    "stomach", "pain", "ache"
]

def extract_health_entities(text):
    if not nlp:
        return []
    doc = nlp(text.lower())
    entities = set()
    for keyword in HEALTH_KEYWORDS:
        if keyword in text.lower():
            entities.add(keyword)
    return list(entities)