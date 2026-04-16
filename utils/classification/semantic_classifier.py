from sentence_transformers import SentenceTransformer
from preprocess_text import normalize_text

# Semantic meaning > decisions

"""
if best_score > 0.80:
    execute(intent)
elif best_score > 0.60:
    ask_for_clarification()
else:
    ignore_or_reprompt()
"""

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def turn_words_into_embeddings(text: list[str]):
    embeddings = model.encode(text)

    print(embeddings.shape)

def classify():
    similarities = model.similarity(embeddings, embeddings)
    print(similarities)

turn_words_into_embeddings("Hola, como estas? Esto es una oracion, supongo.")