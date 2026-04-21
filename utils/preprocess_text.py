import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def _select_word_stemming() -> str:
    pass

def _delete_repeated_words():
    pass

def normalize_text(text: str) -> str:
    nltk.download('stopwords')
    nltk.download('punkt')
    
    lower_text = text.lower()

    tokenized_text = nltk.word_tokenize(lower_text)

    stop_words = set(stopwords.words('spanish'))
    filtered_text = [x for x in tokenized_text if x not in stop_words]

    print(tokenized_text)

    return filtered_text


text = "Hola, ¿cómo estás? Estoy bien, últimamente he visto muy pocas series en comparación con anos anteriores. ¡Qué lástima!"
normalized_text = normalize_text(text)
print(normalized_text)