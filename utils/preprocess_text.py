import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re

def _select_word_stemming(text: str) -> str:
    porter = nltk.PorterStemmer()
    lancaster = nltk.LancasterStemmer()

    porter_text = porter.stem(text)
    lancaster_text = lancaster.stem(text)

    print(porter_text)
    print(lancaster_text)

    return porter_text

def _remove_stopwords(text: str) -> str:
    stop_words = set(stopwords.words('spanish'))
    filtered_text = [x for x in text if x not in stop_words]

    return removed_stopwords_text

def normalize_text(text: str) -> str:
    nltk.download('stopwords')
    nltk.download('punkt')
    
    lower_text = text.lower()

    tokenized_text = nltk.word_tokenize(lower_text)

    removed_stopwords = _remove_stopwords(tokenized_text)
    print(removed_stopwords)

    stemmer_text = _select_word_stemming(tokenized_text)
    print(stemmer_text)

    return filtered_text


text = "Hola, ¿cómo estás? Estoy bien, últimamente he visto muy pocas series en comparación con anos anteriores. ¡Qué lástima!"
normalized_text = normalize_text(text)
print(normalized_text)